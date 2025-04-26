"""
Direct Context Service for Firestore Receipt Data

Simple module to fetch receipt data from Firestore for direct context feeding to Gemini
"""

import os
import json
import logging
import time
import importlib.util
from typing import Dict, Any, List, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for caching
_db = None
_context_cache = None
_last_refresh_time = 0
_cache_ttl = 30 * 60  # 30 minutes in seconds

# Hardcoded Firebase config from frontend
FIREBASE_CONFIG = {
  "apiKey": "AIzaSyAeSN-aBItuUN21fnbsklwdNrMCMNjWjJE",
  "authDomain": "finpal-5d6e8.firebaseapp.com",
  "projectId": "finpal-5d6e8",
  "storageBucket": "finpal-5d6e8.firebasestorage.app",
  "messagingSenderId": "446406693977",
  "appId": "1:446406693977:web:517d41f2c0e7a0cf880d48",
  "measurementId": "G-0N6KLHTSQZ"
}

def initialize_firebase():
    """Initialize Firebase using Admin SDK and the ready FIREBASE_CONFIG dict as service account JSON."""
    global _db
    if _db is not None:
        return _db
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        if firebase_admin._apps:
            _db = firestore.client()
            return _db
        cred = credentials.Certificate(FIREBASE_CONFIG)
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        logger.info("Firestore client created successfully using Admin SDK and ready config")
        return _db
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

def fetch_receipt_context(limit: int = 100, force_refresh: bool = False) -> str:
    """
    Fetch raw receipt data from Firestore for context feeding.
    Uses caching to avoid unnecessary database calls.
    
    Args:
        limit: Maximum number of receipts to retrieve (default: 100)
        force_refresh: Force refresh the cache even if not expired
        
    Returns:
        str: Raw receipt data formatted as text
    """
    global _context_cache, _last_refresh_time
    
    try:
        # Check if we have a cached version and if it's still valid
        if not force_refresh and _context_cache is not None:
            # Check if we need to update based on database changes
            if not check_for_updates():
                logger.info("Using cached receipt context (no updates found)")
                return _context_cache
        
        # Initialize Firebase
        db = initialize_firebase()
        
        # Query receipts collection using client SDK
        receipts_ref = db.collection("receipts")
        # Note: Client SDK has different query syntax than Admin SDK
        receipts_docs = receipts_ref.order_by("createdTime", "desc").limit(limit).get()
        
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

# Simpler test function
if __name__ == "__main__":
    context = fetch_receipt_context(limit=5)
    print(context) 