import os
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

import google.generativeai as genai
from google.generativeai.types import BlockedPromptException

from .direct_context import get_receipts_context

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiContextAgent:
    """
    A simple context agent for the Gemini model that fetches receipt data from Firestore
    and uses it as context for answering user queries.
    
    This agent maintains a cache of receipt data that is refreshed periodically to
    ensure the model has access to the latest user data without excessive database queries.
    
    Features:
    - Periodic context refreshing based on configured interval
    - Receipt data formatting optimized for context window
    - Safety settings configuration for the Gemini model
    - Retry mechanism for processing messages
    
    Usage example:
    ```python
    agent = GeminiContextAgent(api_key="your_api_key")
    response = agent.process_message("What are my top 3 merchants by spending?")
    print(response)
    ```
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model_name: str = "gemini-1.5-pro",
        refresh_interval_minutes: int = 15,
        max_receipts: int = 50
    ):
        """
        Initialize the GeminiContextAgent.
        
        Args:
            api_key (Optional[str]): The Google API key. If None, will try to get from environment.
            model_name (str): The Gemini model to use. Default: "gemini-1.5-pro"
            refresh_interval_minutes (int): How often to refresh the context in minutes. Default: 15
            max_receipts (int): Maximum number of receipts to include in context. Default: 50
        
        Raises:
            ValueError: If API key is not provided and not in environment
        """
        # Get API key from environment if not provided
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key must be provided or set in GOOGLE_API_KEY environment variable")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Store configuration
        self.model_name = model_name
        self.refresh_interval = timedelta(minutes=refresh_interval_minutes)
        self.max_receipts = max_receipts
        
        # Initialize context cache
        self.context_cache = None
        self.last_refresh_time = None
        
        # Create the model with safety settings
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            safety_settings=self._get_safety_settings(),
            generation_config={"temperature": 0.2, "top_p": 0.95, "top_k": 40}
        )
        
        # Perform initial context refresh
        self._refresh_context()
        
        logger.info(f"GeminiContextAgent initialized with model {self.model_name}")
    
    def _get_safety_settings(self) -> List[Dict[str, Any]]:
        """
        Get the safety settings for the Gemini model.
        
        Returns:
            List[Dict[str, Any]]: List of safety settings
        """
        # Setting all safety thresholds to the most permissive option
        # For a production system, adjust these settings appropriately
        return [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"
            }
        ]
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt to guide the Gemini model's responses.
        
        Returns:
            str: The system prompt
        """
        return (
            "You are a helpful financial assistant for the FinPal receipt tracking app. "
            "The user is asking about their receipt data. "
            "Use the receipt data context provided to answer their questions accurately. "
            "If you don't know or can't find information in the context, say so. "
            "Be concise, accurate, and professional. "
            "Format currency values as dollars with two decimal places, e.g., $12.34. "
            "When listing merchant names, make sure to use their exact spelling from the receipts. "
            "If asked for the 'top' merchants or categories, use the spending amount as the criteria unless specified otherwise. "
            "For date ranges, use the exact dates from the receipts. "
            "Do not make up information not present in the context data. "
            "Do not tell the user about system internals like context refreshing or API calls."
        )
    
    def _refresh_context(self):
        """
        Fetch fresh receipt data from Firestore and update the context cache.
        
        This method is called automatically when the refresh interval has elapsed.
        """
        try:
            logger.info("Refreshing receipt context")
            self.context_cache = get_receipts_context(limit=self.max_receipts)
            self.last_refresh_time = datetime.now()
            logger.info(f"Context refreshed, length: {len(self.context_cache)} characters")
        except Exception as e:
            logger.error(f"Error refreshing context: {str(e)}")
            # If this is the initial refresh and it failed, set an empty context
            if self.context_cache is None:
                self.context_cache = "No receipt data available."
                self.last_refresh_time = datetime.now()
    
    def _should_refresh_context(self) -> bool:
        """
        Check if the context should be refreshed based on the refresh interval.
        
        Returns:
            bool: True if refresh is needed, False otherwise
        """
        if self.last_refresh_time is None:
            return True
        
        time_since_refresh = datetime.now() - self.last_refresh_time
        return time_since_refresh >= self.refresh_interval
    
    def process_message(self, user_message: str, max_retries: int = 2) -> str:
        """
        Process a user message using the Gemini model with receipt context.
        
        Args:
            user_message (str): The user's message/question
            max_retries (int): Maximum number of retries on failure. Default: 2
            
        Returns:
            str: The model's response
            
        Raises:
            Exception: If message processing fails after retries
        """
        # Refresh context if needed
        if self._should_refresh_context():
            self._refresh_context()
        
        # Prepare the prompt
        system_prompt = self._get_system_prompt()
        
        # Combine system prompt, context, and user message
        prompt = [
            {"role": "user", "parts": [{"text": system_prompt}]},
            {"role": "model", "parts": [{"text": "I understand. I'm ready to help with financial questions based on the receipt data."}]},
            {"role": "user", "parts": [{"text": f"Here is the context of receipt data:\n\n{self.context_cache}"}]},
            {"role": "model", "parts": [{"text": "I've reviewed the receipt data and I'm ready to help you analyze it."}]},
            {"role": "user", "parts": [{"text": user_message}]}
        ]
        
        # Retry logic
        for attempt in range(max_retries + 1):
            try:
                # Get a response from the model
                response = self.model.generate_content(prompt)
                
                # Return the text response
                return response.text
            
            except BlockedPromptException as e:
                logger.error(f"Blocked prompt: {str(e)}")
                return "I'm unable to respond to that request. It may contain sensitive content that I'm designed to avoid."
            
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Attempt {attempt+1} failed: {str(e)}. Retrying...")
                    time.sleep(1)  # Wait a second before retrying
                else:
                    logger.error(f"Failed to process message after {max_retries+1} attempts: {str(e)}")
                    return f"I'm sorry, I encountered a problem when processing your request. Please try again later."
        
        # This should never be reached due to the return in the exception handler
        return "I'm sorry, there was an unexpected error. Please try again."


def test_gemini_context_agent():
    """
    Test function for the GeminiContextAgent.
    """
    try:
        # Initialize the agent
        agent = GeminiContextAgent()
        
        # Process a simple query
        query = "What are my top 3 merchants by spending?"
        print(f"Query: {query}")
        response = agent.process_message(query)
        print(f"Response: {response}")
        
        # Process a different query
        query = "How much did I spend last month?"
        print(f"\nQuery: {query}")
        response = agent.process_message(query)
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")

if __name__ == "__main__":
    test_gemini_context_agent() 