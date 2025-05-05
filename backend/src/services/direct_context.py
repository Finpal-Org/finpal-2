"""
Direct Context Service for Firestore Receipt Data

Simple module to fetch receipt data from Firestore for direct context feeding to Gemini
"""

import os
import json
import logging
import time
import tempfile
import requests  # For timeout handling
from typing import Dict, Any, List, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for caching
_db = None
_context_cache = None
_last_refresh_time = 0
_cache_ttl = 30 * 60  # 30 minutes in seconds

# For local development
LOCAL_SERVICE_ACCOUNT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                                  "firebase-key.json")

# Alternative local paths to try
ALTERNATIVE_PATHS = [
    "firebase-key.json",  # In the current directory
    os.path.join("backend", "firebase-key.json"),  # In backend directory
    os.path.join("..", "firebase-key.json"),  # One level up
    os.path.join(os.path.expanduser("~"), "firebase-key.json"),  # In user's home directory
]

def initialize_firebase():
    """Initialize Firebase using Admin SDK with priority on environment variables for cloud deployment."""
    global _db
    if _db is not None:
        return _db
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Check if already initialized
        if firebase_admin._apps:
            _db = firestore.client()
            return _db
            
        # APPROACH 1: Use FIREBASE_CONFIG environment variable (for render.com)
        if "FIREBASE_CONFIG" in os.environ:
            try:
                logger.info("Using FIREBASE_CONFIG environment variable")
                firebase_config_json = os.environ["FIREBASE_CONFIG"]
                
                # Create a temporary file with the JSON content
                fd, temp_path = tempfile.mkstemp(suffix='.json')
                with os.fdopen(fd, 'w') as tmp:
                    tmp.write(firebase_config_json)
                
                cred = credentials.Certificate(temp_path)
                firebase_admin.initialize_app(cred)
                _db = firestore.client()
                
                # Cleanup temp file 
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
                logger.info("Successfully initialized Firebase using FIREBASE_CONFIG environment variable")
                return _db
            except Exception as e:
                logger.error(f"Failed to initialize Firebase with FIREBASE_CONFIG: {str(e)}")
                # Fall through to next approach
        
        # APPROACH 2: Check for Secret File (for render.com)
        secret_file_path = "/etc/secrets/FIREBASE_CONFIG"
        if os.path.exists(secret_file_path):
            try:
                logger.info(f"Using secret file: {secret_file_path}")
                cred = credentials.Certificate(secret_file_path)
                firebase_admin.initialize_app(cred)
                _db = firestore.client()
                logger.info("Successfully initialized Firebase using secret file")
                return _db
            except Exception as e:
                logger.error(f"Failed to initialize Firebase with secret file: {str(e)}")
                # Fall through to next approach
        
        # APPROACH 3: Try the main local file path
        if os.path.exists(LOCAL_SERVICE_ACCOUNT_PATH):
            try:
                logger.info(f"Using local service account file: {LOCAL_SERVICE_ACCOUNT_PATH}")
                cred = credentials.Certificate(LOCAL_SERVICE_ACCOUNT_PATH)
                firebase_admin.initialize_app(cred)
                _db = firestore.client()
                logger.info("Successfully initialized Firebase using local service account file")
                return _db
            except Exception as e:
                logger.error(f"Failed to initialize Firebase with local service account file: {str(e)}")
                # Fall through to try alternative paths
        
        # APPROACH 4: Try alternative local paths
        for path in ALTERNATIVE_PATHS:
            if os.path.exists(path):
                try:
                    logger.info(f"Trying alternative path: {path}")
                    cred = credentials.Certificate(path)
                    firebase_admin.initialize_app(cred)
                    _db = firestore.client()
                    logger.info(f"Successfully initialized Firebase using alternative path: {path}")
                    return _db
                except Exception as e:
                    logger.error(f"Failed to initialize Firebase with alternative path {path}: {str(e)}")
                    # Continue trying other paths
        
        # APPROACH 5: Check for GOOGLE_APPLICATION_CREDENTIALS environment variable
        if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            creds_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            if os.path.exists(creds_path):
                try:
                    logger.info(f"Using GOOGLE_APPLICATION_CREDENTIALS: {creds_path}")
                    # Default credentials will use this env var
                    firebase_admin.initialize_app()
                    _db = firestore.client()
                    logger.info("Successfully initialized Firebase using GOOGLE_APPLICATION_CREDENTIALS")
                    return _db
                except Exception as e:
                    logger.error(f"Failed to initialize Firebase with GOOGLE_APPLICATION_CREDENTIALS: {str(e)}")
        
        # No valid configuration found
        logger.error("No valid Firebase configuration found. Please set FIREBASE_CONFIG environment variable or provide a firebase-key.json file.")
        raise FileNotFoundError("No valid Firebase configuration found")
            
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
        raise ValueError(f"Failed to initialize Firebase Admin: {str(e)}")

def check_for_updates() -> bool:
    """
    Check if there are any updates in the receipts collection since last refresh
    
    Returns:
        bool: True if updates found, False otherwise
    """
    try:
        db = initialize_firebase()
        
        global _last_refresh_time
        
        # If the cache is empty or TTL expired, force update
        if _context_cache is None or (time.time() - _last_refresh_time) > _cache_ttl:
            return True
            
        # For client SDK version, we'll just use the TTL check
        # since client SDK query syntax is different from Admin SDK
        return False
        
    except Exception as e:
        logger.error(f"Error checking for updates: {str(e)}")
        # On error, assume update needed
        return True

def fetch_receipt_context(limit: int = 300, force_refresh: bool = False, user_id: str = None) -> str:
    """
    Fetches receipts from Firestore and formats them for context.
    Uses caching to avoid unnecessary database calls.
    
    Args:
        limit: Maximum number of receipts to fetch
        force_refresh: Whether to force a refresh of the cache
        user_id: Optional user ID to filter receipts by
        
    Returns:
        Formatted receipt context string
    """
    global _context_cache, _last_refresh_time
    
    # Use cached version if available and not forcing refresh
    if not force_refresh and _context_cache is not None and time.time() - _last_refresh_time < _cache_ttl:
        logger.info("Using cached receipt context")
        return _context_cache
        
    try:
        # Initialize Firebase with timeout safety
        max_retries = 3
        retry_count = 0
        db = None
        
        while retry_count < max_retries:
            try:
                # Set a shorter timeout for the initialization
                db = initialize_firebase()
                break  # Successfully initialized, exit the loop
            except Exception as e:
                retry_count += 1
                logger.warning(f"Firebase initialization attempt {retry_count} failed: {str(e)}")
                if retry_count >= max_retries:
                    logger.error(f"Failed to initialize Firebase after {max_retries} attempts")
                    # If we have a cached version, return that on initialization error
                    if _context_cache is not None:
                        logger.info("Using cached receipt context due to initialization error")
                        return _context_cache
                    return "Error connecting to database after multiple attempts."
                # Wait before retrying
                time.sleep(1)
        
        from firebase_admin import firestore
        
        # Query receipts collection using client SDK with a timeout
        try:
            receipts_ref = db.collection("receipts")
            
            # Create base query
            query = receipts_ref.order_by("createdTime", direction=firestore.Query.DESCENDING)
            
            # Filter by user_id if provided
            if user_id:
                query = query.where("user_id", "==", user_id)
            
            # Limit results
            query = query.limit(limit)
            
            # Execute query with timeout
            receipts_docs = query.get(timeout=60)
        except Exception as e:
            logger.error(f"Error querying receipts: {str(e)}")
            # If we have a cached version, return that on query error
            if _context_cache is not None:
                logger.info("Using cached receipt context due to query error")
                return _context_cache
            return f"Error retrieving receipt data: {str(e)}"

        # Simple text format of all receipts without processing
        context = "USER RECEIPT DATA:\n\n"
        
        for doc in receipts_docs:
            data = doc.to_dict()
            context += f"Receipt ID: {doc.id}\n"
            
            # Add basic receipt fields without processing
            for key, value in data.items():
                if key == 'items' and isinstance(value, list):
                    context += f"Items: {[item.get('description', 'Unknown') for item in value]}\n"
                elif not isinstance(value, (dict, list)):
                    context += f"{key}: {value}\n"
            
            context += "-" * 40 + "\n\n"
        
        # Update cache and timestamp
        _context_cache = context
        _last_refresh_time = time.time()
        
        logger.info(f"Retrieved and cached {len(receipts_docs)} receipts for context")
        return context
        
    except Exception as e:
        logger.error(f"Error fetching receipts for context: {str(e)}")
        # If we have a cached version, return that on error
        if _context_cache is not None:
            logger.info("Using cached receipt context due to error")
            return _context_cache
        return f"Error retrieving receipt data: {str(e)}"

# Simple test function
if __name__ == "__main__":
    context = fetch_receipt_context(limit=5)
    print(context) 