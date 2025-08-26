"""
File handling utilities for saving and loading data
"""

import pandas as pd
import os
from datetime import datetime
from typing import List, Dict

class FileHandler:
    def __init__(self):
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            'data/output',
            'data/output/logs',
            'data/input'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def save_to_csv(self, data: List[Dict], filename: str):
        """Save data to CSV file"""
        try:
            df = pd.DataFrame(data)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Save to CSV
            df.to_csv(filename, index=False, encoding='utf-8')
            
            # Log the save operation
            self.log_operation(f"Saved {len(data)} records to {filename}")
            
        except Exception as e:
            print(f"❌ Failed to save CSV: {e}")
            raise
    
    def load_from_csv(self, filename: str) -> pd.DataFrame:
        """Load data from CSV file"""
        try:
            if os.path.exists(filename):
                return pd.read_csv(filename)
            else:
                print(f"⚠️  File not found: {filename}")
                return pd.DataFrame()
        except Exception as e:
            print(f"❌ Failed to load CSV: {e}")
            return pd.DataFrame()
    
    def log_operation(self, message: str):
        """Log operations to file"""
        try:
            log_file = 'data/output/logs/screening_log.txt'
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
                
        except Exception as e:
            print(f"⚠️  Failed to write log: {e}")