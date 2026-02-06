"""
Expense Service for SneakerCanvasBD
Handles expense tracking with cost allocation to inventory
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

from .base_service import BaseService


class ExpenseService(BaseService):
    """Service for expense management with inventory cost allocation"""
    
    # Schema definition
    COLUMNS = [
        'expense_id', 'date', 'category', 'amount', 'description', 
        'related_product', 'allocated'
    ]
    
    NEW_COLUMNS = {
        'expense_id': '',
        'allocated': False
    }
    
    DEFAULT_CATEGORIES = ["Packaging", "Courier", "Product Purchase", "Marketing", "Customs", "Logistics", "Other"]
    
    def __init__(self, data_dir: str, config_file: str = None):
        super().__init__(data_dir)
        self.expense_file = os.path.join(data_dir, 'expenses.csv')
        self.config_file = config_file
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Ensure expense file has correct schema"""
        if not os.path.exists(self.expense_file):
            df = pd.DataFrame(columns=self.COLUMNS)
            df.to_csv(self.expense_file, index=False)
        else:
            valid, missing = self.validate_schema(self.expense_file, self.COLUMNS)
            if not valid:
                self.migrate_schema(self.expense_file, self.NEW_COLUMNS)
                self._generate_missing_ids()
    
    def _generate_missing_ids(self):
        """Generate expense IDs for entries without one"""
        try:
            df = pd.read_csv(self.expense_file)
            if 'expense_id' not in df.columns:
                df['expense_id'] = ''
            
            counter = 1
            for idx, row in df.iterrows():
                if pd.isna(row.get('expense_id', '')) or row.get('expense_id', '') == '':
                    df.at[idx, 'expense_id'] = f"EXP-{counter:05d}"
                    counter += 1
            
            df.to_csv(self.expense_file, index=False)
        except Exception as e:
            print(f"Error generating expense IDs: {e}")
    
    def _generate_expense_id(self) -> str:
        """Generate unique expense ID"""
        try:
            df = pd.read_csv(self.expense_file)
            existing = set(df['expense_id'].dropna().tolist()) if 'expense_id' in df.columns else set()
        except:
            existing = set()
        
        counter = 1
        while True:
            new_id = f"EXP-{counter:05d}"
            if new_id not in existing:
                return new_id
            counter += 1
    
    # ===== CRUD Operations =====
    
    def get_expenses(self) -> List[Dict[str, Any]]:
        """Get all expenses"""
        return self.read_csv_safe(self.expense_file)
    
    def get_expense_by_id(self, expense_id: str) -> Optional[Dict[str, Any]]:
        """Get expense by ID"""
        try:
            df = pd.read_csv(self.expense_file)
            expense = df[df['expense_id'] == expense_id]
            if not expense.empty:
                return expense.iloc[0].to_dict()
            return None
        except:
            return None
    
    def add_expense(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Add a new expense. Returns (success, expense_id)"""
        try:
            expense_id = data.get('expense_id') or self._generate_expense_id()
            
            row = [
                expense_id,
                data.get('date', datetime.now().strftime('%m/%d/%Y')),
                data.get('category', ''),
                data.get('amount', 0),
                data.get('description', ''),
                data.get('related_product', ''),
                data.get('allocated', False)
            ]
            
            with open(self.expense_file, 'a', newline='', encoding='utf-8') as f:
                import csv
                writer = csv.writer(f)
                writer.writerow(row)
            
            return True, expense_id
        except Exception as e:
            print(f"Error adding expense: {e}")
            return False, str(e)
    
    def update_expense(self, expense_id: str, updates: Dict[str, Any]) -> bool:
        """Update an expense by ID"""
        try:
            df = pd.read_csv(self.expense_file)
            mask = df['expense_id'] == expense_id
            if mask.any():
                for key, value in updates.items():
                    if key in df.columns:
                        df.loc[mask, key] = value
                df.to_csv(self.expense_file, index=False)
                return True
            return False
        except Exception as e:
            print(f"Error updating expense: {e}")
            return False
    
    def delete_expense(self, expense_id: str) -> bool:
        """Delete expense by ID"""
        try:
            df = pd.read_csv(self.expense_file)
            df = df[df['expense_id'] != expense_id]
            df.to_csv(self.expense_file, index=False)
            return True
        except:
            return False
    
    def delete_expense_by_fields(self, row_data: Dict[str, Any]) -> bool:
        """Delete expense by matching fields (legacy support)"""
        try:
            df = pd.read_csv(self.expense_file)
            mask = (
                (df['date'] == row_data.get('date', '')) &
                (df['category'] == row_data.get('category', '')) &
                (df['amount'].astype(str) == str(row_data.get('amount', 0))) &
                (df['description'] == row_data.get('description', ''))
            )
            df = df[~mask]
            df.to_csv(self.expense_file, index=False)
            return True
        except Exception as e:
            print(f"Error deleting expense: {e}")
            return False
    
    # ===== Cost Allocation =====
    
    def allocate_to_inventory(self, expense_id: str, product_id: str) -> bool:
        """Allocate an expense to a specific product"""
        return self.update_expense(expense_id, {
            'related_product': product_id,
            'allocated': True
        })
    
    def get_allocated_costs(self, product_id: str) -> float:
        """Get total allocated costs for a product"""
        try:
            df = pd.read_csv(self.expense_file)
            if 'related_product' not in df.columns:
                return 0
            
            allocated = df[df['related_product'] == product_id]
            return allocated['amount'].astype(float).sum()
        except:
            return 0
    
    def get_allocated_costs_by_name(self, product_name: str) -> float:
        """Get allocated costs by product name (partial match)"""
        try:
            df = pd.read_csv(self.expense_file)
            if 'related_product' not in df.columns:
                return 0
            
            allocated = df[df['related_product'].astype(str).str.contains(product_name, case=False, na=False)]
            return allocated['amount'].astype(float).sum()
        except:
            return 0
    
    def get_unallocated_expenses(self) -> List[Dict[str, Any]]:
        """Get expenses not allocated to any product"""
        try:
            df = pd.read_csv(self.expense_file)
            if 'allocated' not in df.columns:
                # All expenses without related_product are unallocated
                unallocated = df[df['related_product'].isna() | (df['related_product'] == '')]
            else:
                unallocated = df[(df['allocated'] != True) | pd.isna(df['allocated'])]
            
            return unallocated.to_dict('records')
        except:
            return []
    
    # ===== Categories =====
    
    def get_categories(self, config_manager=None) -> List[str]:
        """Get expense categories"""
        if config_manager:
            return config_manager.get('expense_categories', self.DEFAULT_CATEGORIES)
        return self.DEFAULT_CATEGORIES
    
    def add_category(self, category: str, config_manager=None) -> bool:
        """Add a new expense category"""
        if config_manager:
            cats = self.get_categories(config_manager)
            if category not in cats:
                cats.append(category)
                config_manager.save('expense_categories', cats)
                return True
        return False
    
    def delete_category(self, category: str, config_manager=None) -> bool:
        """Delete an expense category"""
        if config_manager:
            cats = self.get_categories(config_manager)
            if category in cats:
                cats.remove(category)
                config_manager.save('expense_categories', cats)
                return True
        return False
    
    # ===== Analytics =====
    
    def get_monthly_expenses(self) -> Dict[str, float]:
        """Get expenses for current and previous month"""
        try:
            df = pd.read_csv(self.expense_file)
            df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
            
            now = datetime.now()
            current_month_start = now.replace(day=1)
            prev_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            
            current = df[(df['date_parsed'] >= current_month_start)]['amount'].astype(float).sum()
            previous = df[(df['date_parsed'] >= prev_month_start) & 
                         (df['date_parsed'] < current_month_start)]['amount'].astype(float).sum()
            
            return {
                'current_month': current,
                'previous_month': previous,
                'change_pct': ((current - previous) / previous * 100) if previous > 0 else 0
            }
        except Exception as e:
            print(f"Error getting monthly expenses: {e}")
            return {'current_month': 0, 'previous_month': 0, 'change_pct': 0}
    
    def get_expenses_by_category(self) -> Dict[str, float]:
        """Get breakdown of expenses by category"""
        try:
            df = pd.read_csv(self.expense_file)
            grouped = df.groupby('category')['amount'].sum().to_dict()
            return grouped
        except:
            return {}
    
    def get_expense_summary(self) -> Dict[str, Any]:
        """Get expense summary for dashboard"""
        try:
            df = pd.read_csv(self.expense_file)
            
            total_expenses = df['amount'].astype(float).sum()
            expense_count = len(df)
            
            # Category breakdown
            by_category = df.groupby('category')['amount'].sum().to_dict()
            
            # Monthly data
            monthly = self.get_monthly_expenses()
            
            return {
                'total_expenses': total_expenses,
                'expense_count': expense_count,
                'by_category': by_category,
                'current_month': monthly['current_month'],
                'previous_month': monthly['previous_month']
            }
        except Exception as e:
            print(f"Error getting expense summary: {e}")
            return {
                'total_expenses': 0,
                'expense_count': 0,
                'by_category': {},
                'current_month': 0,
                'previous_month': 0
            }
