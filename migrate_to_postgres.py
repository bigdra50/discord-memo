#!/usr/bin/env python3
"""
Migration script to transfer data from JSON file to PostgreSQL database
"""

import os
import json
import logging
from database import DatabaseManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('migration')

def migrate_json_to_postgres(json_file_path: str = 'user_data.json'):
    """Migrate data from JSON file to PostgreSQL database"""
    
    # Check if JSON file exists
    if not os.path.exists(json_file_path):
        logger.warning(f"JSON file {json_file_path} not found. Nothing to migrate.")
        return
    
    # Load JSON data
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        logger.info(f"Loaded JSON data from {json_file_path}")
    except Exception as e:
        logger.error(f"Error loading JSON file: {e}")
        return
    
    # Initialize database
    try:
        db = DatabaseManager()
        
        # Test connection
        if not db.test_connection():
            logger.error("Cannot connect to database")
            return
        
        # Initialize schema
        db.initialize_schema()
        logger.info("Database schema initialized")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return
    
    # Migrate data
    total_entries = 0
    successful_entries = 0
    
    for user_id, user_data in json_data.items():
        if not isinstance(user_data, dict):
            logger.warning(f"Skipping invalid data for user {user_id}")
            continue
        
        for key, value in user_data.items():
            total_entries += 1
            if db.set_user_data(user_id, key, str(value)):
                successful_entries += 1
            else:
                logger.error(f"Failed to migrate data for user {user_id}, key {key}")
    
    logger.info(f"Migration completed: {successful_entries}/{total_entries} entries migrated successfully")
    
    # Create backup of original JSON file
    backup_file = f"{json_file_path}.backup"
    try:
        import shutil
        shutil.copy2(json_file_path, backup_file)
        logger.info(f"Backup of original JSON file created: {backup_file}")
    except Exception as e:
        logger.warning(f"Could not create backup file: {e}")

def verify_migration(json_file_path: str = 'user_data.json'):
    """Verify that migration was successful by comparing data"""
    
    if not os.path.exists(json_file_path):
        logger.info("No JSON file to verify against")
        return True
    
    # Load JSON data
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file for verification: {e}")
        return False
    
    # Initialize database
    try:
        db = DatabaseManager()
        if not db.test_connection():
            logger.error("Cannot connect to database for verification")
            return False
    except Exception as e:
        logger.error(f"Error connecting to database for verification: {e}")
        return False
    
    # Verify data
    verification_passed = True
    
    for user_id, user_data in json_data.items():
        if not isinstance(user_data, dict):
            continue
        
        # Get all data for this user from database
        db_user_data = db.get_user_data(user_id)
        
        if db_user_data is None:
            logger.error(f"User {user_id} data not found in database")
            verification_passed = False
            continue
        
        # Compare each key-value pair
        for key, value in user_data.items():
            if key not in db_user_data:
                logger.error(f"Key {key} for user {user_id} not found in database")
                verification_passed = False
            elif db_user_data[key] != str(value):
                logger.error(f"Value mismatch for user {user_id}, key {key}: JSON='{value}', DB='{db_user_data[key]}'")
                verification_passed = False
    
    if verification_passed:
        logger.info("Migration verification passed: All data matches")
    else:
        logger.error("Migration verification failed: Data mismatches found")
    
    return verification_passed

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate Discord Vault data from JSON to PostgreSQL')
    parser.add_argument('--json-file', default='user_data.json', help='Path to JSON file (default: user_data.json)')
    parser.add_argument('--verify-only', action='store_true', help='Only verify existing migration, do not migrate')
    
    args = parser.parse_args()
    
    if args.verify_only:
        verify_migration(args.json_file)
    else:
        migrate_json_to_postgres(args.json_file)
        verify_migration(args.json_file)