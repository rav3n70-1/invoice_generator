"""
Inventory Service for SneakerCanvasBD
Handles all inventory operations with product IDs, stock alerts, aging, and profitability analysis
"""

import uuid
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

from .base_service import BaseService


class InventoryService(BaseService):
    """Service for inventory management with intelligence features"""
    
    # Schema definition
    COLUMNS = [
        'product_id', 'name', 'description', 'size', 'price', 
        'buying_price', 'stock', 'added_date', 'sold_quantity'
    ]
    
    # Default columns for migration
    NEW_COLUMNS = {
        'product_id': '',
        'added_date': datetime.now().strftime('%Y-%m-%d'),
        'sold_quantity': 0
    }
    
    def __init__(self, data_dir: str):
        super().__init__(data_dir)
        self.inventory_file = os.path.join(data_dir, 'inventory.csv')
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Ensure inventory file has correct schema"""
        if not os.path.exists(self.inventory_file):
            # Create with new schema
            df = pd.DataFrame(columns=self.COLUMNS)
            df.to_csv(self.inventory_file, index=False)
        else:
            # Migrate existing schema
            valid, missing = self.validate_schema(self.inventory_file, self.COLUMNS)
            if not valid:
                self.migrate_schema(self.inventory_file, self.NEW_COLUMNS)
                # Generate product IDs for existing items
                self._generate_missing_product_ids()
    
    def _generate_missing_product_ids(self):
        """Generate product_id for items that don't have one"""
        try:
            df = pd.read_csv(self.inventory_file)
            if 'product_id' not in df.columns:
                df['product_id'] = ''
            
            # Generate IDs for rows without one
            for idx, row in df.iterrows():
                if pd.isna(row['product_id']) or row['product_id'] == '':
                    df.at[idx, 'product_id'] = self.generate_product_id()
            
            df.to_csv(self.inventory_file, index=False)
        except Exception as e:
            print(f"Error generating product IDs: {e}")
    
    def generate_product_id(self) -> str:
        """Generate a unique product ID in format SC-SKU-XXXXX"""
        # Get existing IDs to ensure uniqueness
        try:
            df = pd.read_csv(self.inventory_file)
            existing_ids = set(df['product_id'].dropna().tolist()) if 'product_id' in df.columns else set()
        except:
            existing_ids = set()
        
        # Generate sequential ID
        counter = 1
        while True:
            new_id = f"SC-SKU-{counter:05d}"
            if new_id not in existing_ids:
                return new_id
            counter += 1
    
    # ===== CRUD Operations =====
    
    def get_inventory(self) -> List[Dict[str, Any]]:
        """Get all inventory items"""
        return self.read_csv_safe(self.inventory_file)
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get a product by its ID"""
        try:
            df = pd.read_csv(self.inventory_file)
            product = df[df['product_id'] == product_id]
            if not product.empty:
                return product.iloc[0].to_dict()
            return None
        except:
            return None
    
    def get_product_by_name_size(self, name: str, size: str) -> Optional[Dict[str, Any]]:
        """Get a product by name and size (legacy support)"""
        try:
            df = pd.read_csv(self.inventory_file)
            df['size'] = df['size'].astype(str)
            mask = (df['name'] == name) & (df['size'] == str(size))
            if mask.any():
                return df[mask].iloc[0].to_dict()
            return None
        except:
            return None
    
    def add_product(self, product: Dict[str, Any]) -> Tuple[bool, str]:
        """Add a new product or update existing one. Returns (success, product_id)"""
        try:
            df = pd.read_csv(self.inventory_file)
            
            # Ensure all columns exist
            for col in self.COLUMNS:
                if col not in df.columns:
                    df[col] = self.NEW_COLUMNS.get(col, '')
            
            df['size'] = df['size'].astype(str)
            target_size = str(product.get('size', ''))
            
            # Check if exists by name + size
            mask = (df['name'] == product['name']) & (df['size'] == target_size)
            
            if mask.any():
                # Update existing
                product_id = df.loc[mask, 'product_id'].iloc[0]
                if pd.isna(product_id) or product_id == '':
                    product_id = self.generate_product_id()
                    df.loc[mask, 'product_id'] = product_id
                
                df.loc[mask, 'stock'] = product.get('stock', 0)
                df.loc[mask, 'price'] = product.get('price', 0)
                df.loc[mask, 'buying_price'] = product.get('buying_price', 0)
                df.loc[mask, 'description'] = product.get('description', '')
                df.to_csv(self.inventory_file, index=False)
                return True, product_id
            else:
                # Create new
                product_id = product.get('product_id') or self.generate_product_id()
                new_row = {
                    'product_id': product_id,
                    'name': product['name'],
                    'description': product.get('description', ''),
                    'size': target_size,
                    'price': product.get('price', 0),
                    'buying_price': product.get('buying_price', 0),
                    'stock': product.get('stock', 0),
                    'added_date': product.get('added_date', datetime.now().strftime('%Y-%m-%d')),
                    'sold_quantity': product.get('sold_quantity', 0)
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(self.inventory_file, index=False)
                return True, product_id
        except Exception as e:
            print(f"Error adding product: {e}")
            return False, ''
    
    def update_product(self, product_id: str, updates: Dict[str, Any]) -> bool:
        """Update a product by its ID"""
        try:
            df = pd.read_csv(self.inventory_file)
            mask = df['product_id'] == product_id
            if mask.any():
                for key, value in updates.items():
                    if key in df.columns and key != 'product_id':
                        df.loc[mask, key] = value
                df.to_csv(self.inventory_file, index=False)
                return True
            return False
        except Exception as e:
            print(f"Error updating product: {e}")
            return False
    
    def update_product_by_name_size(self, name: str, size: str, updates: Dict[str, Any]) -> bool:
        """Update a product by name and size (legacy support)"""
        try:
            df = pd.read_csv(self.inventory_file)
            df['size'] = df['size'].astype(str)
            mask = (df['name'] == name) & (df['size'] == str(size))
            if mask.any():
                for key, value in updates.items():
                    if key in df.columns:
                        df.loc[mask, key] = value
                df.to_csv(self.inventory_file, index=False)
                return True
            return False
        except Exception as e:
            print(f"Error updating product: {e}")
            return False
    
    def delete_product(self, product_id: str) -> bool:
        """Delete a product by its ID"""
        try:
            df = pd.read_csv(self.inventory_file)
            df = df[df['product_id'] != product_id]
            df.to_csv(self.inventory_file, index=False)
            return True
        except:
            return False
    
    def delete_product_by_name_size(self, name: str, size: str) -> bool:
        """Delete a product by name and size (legacy support)"""
        try:
            df = pd.read_csv(self.inventory_file)
            df['size'] = df['size'].astype(str)
            df = df[~((df['name'] == name) & (df['size'] == str(size)))]
            df.to_csv(self.inventory_file, index=False)
            return True
        except:
            return False
    
    # ===== Stock Operations =====
    
    def check_stock_availability(self, name: str, size: str, required_qty: int) -> Tuple[bool, int]:
        """Check if sufficient stock is available"""
        try:
            df = pd.read_csv(self.inventory_file)
            df['size'] = df['size'].astype(str)
            mask = (df['name'] == name) & (df['size'] == str(size))
            if mask.any():
                current_stock = int(df.loc[mask, 'stock'].iloc[0])
                return current_stock >= required_qty, current_stock
            return False, 0
        except Exception as e:
            print(f"Stock check error: {e}")
            return False, 0
    
    def reduce_stock(self, name: str, size: str, quantity: int) -> Tuple[bool, int]:
        """Reduce stock after a sale"""
        try:
            df = pd.read_csv(self.inventory_file)
            df['size'] = df['size'].astype(str)
            mask = (df['name'] == name) & (df['size'] == str(size))
            if mask.any():
                current_stock = int(df.loc[mask, 'stock'].iloc[0])
                new_stock = max(0, current_stock - quantity)
                df.loc[mask, 'stock'] = new_stock
                
                # Update sold_quantity
                if 'sold_quantity' in df.columns:
                    current_sold = int(df.loc[mask, 'sold_quantity'].iloc[0] or 0)
                    df.loc[mask, 'sold_quantity'] = current_sold + quantity
                
                df.to_csv(self.inventory_file, index=False)
                return True, new_stock
            return False, 0
        except Exception as e:
            print(f"Stock reduction error: {e}")
            return False, 0
    
    def restore_stock(self, name: str, size: str, quantity: int) -> Tuple[bool, int]:
        """Restore stock (for returns)"""
        try:
            df = pd.read_csv(self.inventory_file)
            df['size'] = df['size'].astype(str)
            mask = (df['name'] == name) & (df['size'] == str(size))
            if mask.any():
                current_stock = int(df.loc[mask, 'stock'].iloc[0])
                new_stock = current_stock + quantity
                df.loc[mask, 'stock'] = new_stock
                
                # Update sold_quantity (reduce)
                if 'sold_quantity' in df.columns:
                    current_sold = int(df.loc[mask, 'sold_quantity'].iloc[0] or 0)
                    df.loc[mask, 'sold_quantity'] = max(0, current_sold - quantity)
                
                df.to_csv(self.inventory_file, index=False)
                return True, new_stock
            return False, 0
        except Exception as e:
            print(f"Stock restore error: {e}")
            return False, 0
    
    # ===== Intelligence Features =====
    
    def get_low_stock_items(self, threshold: int = 5) -> List[Dict[str, Any]]:
        """Get items with stock at or below threshold"""
        try:
            df = pd.read_csv(self.inventory_file)
            low_stock = df[df['stock'].astype(int) <= threshold]
            return low_stock.to_dict('records')
        except:
            return []
    
    def get_aging_products(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get products unsold for more than X days"""
        try:
            df = pd.read_csv(self.inventory_file)
            if 'added_date' not in df.columns:
                return []
            
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.strftime('%Y-%m-%d')
            
            # Filter items added before cutoff that still have stock
            df['added_date'] = pd.to_datetime(df['added_date'], errors='coerce')
            aging = df[(df['added_date'] < cutoff_date) & (df['stock'].astype(int) > 0)]
            
            result = aging.to_dict('records')
            for item in result:
                if pd.notna(item.get('added_date')):
                    added = item['added_date']
                    if hasattr(added, 'strftime'):
                        item['days_in_stock'] = (datetime.now() - added).days
                        item['added_date'] = added.strftime('%Y-%m-%d')
                    else:
                        item['days_in_stock'] = 0
            return result
        except Exception as e:
            print(f"Error getting aging products: {e}")
            return []
    
    def get_profit_by_sku(self) -> List[Dict[str, Any]]:
        """Calculate profit per SKU: (selling_price - buying_price) * sold_quantity"""
        try:
            df = pd.read_csv(self.inventory_file)
            
            # Ensure required columns exist
            if 'buying_price' not in df.columns:
                df['buying_price'] = 0
            if 'sold_quantity' not in df.columns:
                df['sold_quantity'] = 0
            
            df['unit_profit'] = df['price'].astype(float) - df['buying_price'].astype(float)
            df['total_profit'] = df['unit_profit'] * df['sold_quantity'].astype(int)
            df['margin_pct'] = (df['unit_profit'] / df['price'].astype(float) * 100).fillna(0)
            
            result = df[['product_id', 'name', 'size', 'price', 'buying_price', 
                        'sold_quantity', 'unit_profit', 'total_profit', 'margin_pct']].to_dict('records')
            return result
        except Exception as e:
            print(f"Error calculating profit: {e}")
            return []
    
    def get_top_profitable(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top N profitable products by total profit"""
        profits = self.get_profit_by_sku()
        sorted_profits = sorted(profits, key=lambda x: x.get('total_profit', 0), reverse=True)
        return sorted_profits[:limit]
    
    def get_stock_summary(self) -> Dict[str, Any]:
        """Get summary statistics for dashboard"""
        try:
            df = pd.read_csv(self.inventory_file)
            
            total_items = len(df)
            total_stock = df['stock'].astype(int).sum()
            
            # Inventory value at selling price
            df['value'] = df['stock'].astype(int) * df['price'].astype(float)
            inventory_value = df['value'].sum()
            
            # Inventory cost at buying price
            if 'buying_price' in df.columns:
                df['cost'] = df['stock'].astype(int) * df['buying_price'].astype(float)
                inventory_cost = df['cost'].sum()
            else:
                inventory_cost = 0
            
            # Potential profit
            potential_profit = inventory_value - inventory_cost
            
            # Low stock count (threshold 5)
            low_stock_count = len(df[df['stock'].astype(int) <= 5])
            
            return {
                'total_items': total_items,
                'total_stock': total_stock,
                'inventory_value': inventory_value,
                'inventory_cost': inventory_cost,
                'potential_profit': potential_profit,
                'low_stock_count': low_stock_count
            }
        except Exception as e:
            print(f"Error getting stock summary: {e}")
            return {
                'total_items': 0,
                'total_stock': 0,
                'inventory_value': 0,
                'inventory_cost': 0,
                'potential_profit': 0,
                'low_stock_count': 0
            }
    
    def get_unique_product_names(self) -> List[str]:
        """Get list of unique product names for dropdowns"""
        try:
            df = pd.read_csv(self.inventory_file)
            return sorted(df['name'].unique().tolist())
        except:
            return []
    
    def get_sizes_for_product(self, name: str) -> List[str]:
        """Get available sizes for a product"""
        try:
            df = pd.read_csv(self.inventory_file)
            sizes = df[df['name'] == name]['size'].astype(str).unique().tolist()
            return sorted(sizes, key=lambda x: int(x) if x.isdigit() else x)
        except:
            return []
