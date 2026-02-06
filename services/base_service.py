"""
Base Service for SneakerCanvasBD
Provides common utilities: file locking, backups, schema validation
"""

import csv
import os
import shutil
import json
from datetime import datetime
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

# Platform-specific locking imports
if os.name == 'nt':
    import msvcrt
else:
    import fcntl


class FileLock:
    """Cross-platform file locking context manager"""
    
    def __init__(self, file_path: str, mode: str = 'r+'):
        self.file_path = file_path
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        self.file = open(self.file_path, self.mode, newline='', encoding='utf-8')
        if os.name == 'nt':
            # Windows locking
            import msvcrt
            msvcrt.locking(self.file.fileno(), msvcrt.LK_LOCK, 1)
        else:
            # Unix locking
            import fcntl
            fcntl.flock(self.file.fileno(), fcntl.LOCK_EX)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            if os.name == 'nt':
                import msvcrt
                try:
                    msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, 1)
                except:
                    pass
            else:
                import fcntl
                fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)
            self.file.close()
        return False


class BaseService:
    """Base class for all services with common utilities"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.backup_dir = os.path.join(data_dir, 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, file_path: str) -> Optional[str]:
        """Create a dated backup of a file"""
        if not os.path.exists(file_path):
            return None
        
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        date_str = datetime.now().strftime('%Y-%m-%d')
        backup_name = f"{name}_{date_str}{ext}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        # Only create one backup per day
        if not os.path.exists(backup_path):
            shutil.copy2(file_path, backup_path)
            return backup_path
        return backup_path
    
    def create_daily_backup(self, file_paths: List[str]) -> Dict[str, str]:
        """Create daily backups for multiple files"""
        backups = {}
        for path in file_paths:
            backup = self.create_backup(path)
            if backup:
                backups[path] = backup
        return backups
    
    def validate_schema(self, file_path: str, required_columns: List[str]) -> Tuple[bool, List[str]]:
        """Validate CSV file has required columns. Returns (valid, missing_columns)"""
        if not os.path.exists(file_path):
            return False, required_columns
        
        try:
            df = pd.read_csv(file_path, nrows=0)
            existing_cols = set(df.columns)
            missing = [col for col in required_columns if col not in existing_cols]
            return len(missing) == 0, missing
        except Exception as e:
            return False, required_columns
    
    def migrate_schema(self, file_path: str, new_columns: Dict[str, Any]) -> bool:
        """Add new columns to CSV with default values"""
        if not os.path.exists(file_path):
            return False
        
        try:
            # Backup first
            self.create_backup(file_path)
            
            df = pd.read_csv(file_path)
            for col, default in new_columns.items():
                if col not in df.columns:
                    df[col] = default
            df.to_csv(file_path, index=False)
            return True
        except Exception as e:
            print(f"Schema migration error: {e}")
            return False
    
    def read_csv_safe(self, file_path: str) -> List[Dict[str, Any]]:
        """Read CSV with error handling"""
        if not os.path.exists(file_path):
            return []
        try:
            df = pd.read_csv(file_path)
            return df.to_dict('records')
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
    
    def write_csv_safe(self, file_path: str, data: List[Dict[str, Any]], columns: List[str]) -> bool:
        """Write CSV with error handling"""
        try:
            df = pd.DataFrame(data, columns=columns)
            df.to_csv(file_path, index=False)
            return True
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return False
    
    def append_row(self, file_path: str, row: List[Any]) -> bool:
        """Append a single row to CSV"""
        try:
            with open(file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            return True
        except Exception as e:
            print(f"Error appending to {file_path}: {e}")
            return False
