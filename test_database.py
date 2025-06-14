#!/usr/bin/env python3
"""
Test script for database connection and basic operations
"""

import os
import logging
from database import DatabaseManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('test_database')

def test_database_connection():
    """Test database connection and basic operations"""
    
    logger.info("Starting database connection test...")
    
    # Check environment variables
    required_vars = ['PGHOST', 'PGDATABASE', 'PGUSER', 'PGPASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Set these environment variables:")
        for var in missing_vars:
            logger.info(f"export {var}=your_value_here")
        return False
    
    try:
        # Initialize database manager
        db = DatabaseManager()
        
        # Test connection
        logger.info("Testing database connection...")
        if not db.test_connection():
            logger.error("Database connection test failed")
            return False
        logger.info("✓ Database connection successful")
        
        # Initialize schema
        logger.info("Initializing database schema...")
        db.initialize_schema()
        logger.info("✓ Database schema initialized")
        
        # Test basic operations
        test_user_id = "test_user_123"
        test_key = "test_key"
        test_value = "test_value"
        
        # Test set operation
        logger.info("Testing set operation...")
        if not db.set_user_data(test_user_id, test_key, test_value):
            logger.error("Set operation failed")
            return False
        logger.info("✓ Set operation successful")
        
        # Test get operation
        logger.info("Testing get operation...")
        retrieved_value = db.get_user_data(test_user_id, test_key)
        if retrieved_value != test_value:
            logger.error(f"Get operation failed: expected '{test_value}', got '{retrieved_value}'")
            return False
        logger.info("✓ Get operation successful")
        
        # Test get all data for user
        logger.info("Testing get all data operation...")
        all_data = db.get_user_data(test_user_id)
        if not isinstance(all_data, dict) or test_key not in all_data:
            logger.error("Get all data operation failed")
            return False
        logger.info("✓ Get all data operation successful")
        
        # Test count operation
        logger.info("Testing count operation...")
        count = db.get_user_data_count(test_user_id)
        if count != 1:
            logger.error(f"Count operation failed: expected 1, got {count}")
            return False
        logger.info("✓ Count operation successful")
        
        # Test update operation
        logger.info("Testing update operation...")
        new_value = "updated_test_value"
        if not db.set_user_data(test_user_id, test_key, new_value):
            logger.error("Update operation failed")
            return False
        
        retrieved_value = db.get_user_data(test_user_id, test_key)
        if retrieved_value != new_value:
            logger.error(f"Update verification failed: expected '{new_value}', got '{retrieved_value}'")
            return False
        logger.info("✓ Update operation successful")
        
        # Test delete operation
        logger.info("Testing delete operation...")
        if not db.delete_user_data(test_user_id, test_key):
            logger.error("Delete operation failed")
            return False
        
        retrieved_value = db.get_user_data(test_user_id, test_key)
        if retrieved_value is not None:
            logger.error(f"Delete verification failed: expected None, got '{retrieved_value}'")
            return False
        logger.info("✓ Delete operation successful")
        
        # Final count check
        count = db.get_user_data_count(test_user_id)
        if count != 0:
            logger.error(f"Final count check failed: expected 0, got {count}")
            return False
        logger.info("✓ Final count check successful")
        
        logger.info("🎉 All database tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    exit(0 if success else 1)