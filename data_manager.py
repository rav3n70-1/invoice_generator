"""
Data Manager for Sneaker Canvas BD Invoice App
Handles storage and retrieval of invoices and inventory using CSV files.
Features: Config Persistence, Import/Export, Connection Check.
"""

import csv
import json
import os
import shutil
from datetime import datetime
import pandas as pd

# File paths
# File paths
APP_NAME = "SneakerCanvasBD"
APPDATA = os.getenv('APPDATA')
APP_CONFIG_DIR = os.path.join(APPDATA, APP_NAME)
CONFIG_FILE = os.path.join(APP_CONFIG_DIR, 'config.json')

# Ensure config directory exists
os.makedirs(APP_CONFIG_DIR, exist_ok=True)

class DataManager:
    def __init__(self):
        self.config = self.load_config()
        self.data_dir = self.config.get('data_folder', self._get_default_data_dir())
        self._init_files()
        
    def _get_default_data_dir(self):
        """Get default data directory in My Documents"""
        docs = os.path.expanduser("~/Documents")
        return os.path.join(docs, APP_NAME)
        
    def _init_files(self):
        """Initialize CSV files with headers if they don't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
            
        self.invoice_file = os.path.join(self.data_dir, 'invoices.csv')
        self.inventory_file = os.path.join(self.data_dir, 'inventory.csv')
        self.expense_file = os.path.join(self.data_dir, 'expenses.csv')
        
        if not os.path.exists(self.invoice_file):
             with open(self.invoice_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'invoice_number', 'date', 'customer_name', 'customer_phone', 
                    'customer_address', 'subtotal', 'discount', 'delivery', 
                    'grand_total', 'payment_method', 'transaction_id', 'items_json'
                ])
        
        if not os.path.exists(self.inventory_file):
            with open(self.inventory_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'description', 'size', 'price', 'buying_price', 'stock'])
                
        if not os.path.exists(self.expense_file):
            with open(self.expense_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['date', 'category', 'amount', 'description', 'related_product'])
    
    # ===== CONFIGURATION =====
    
    def load_config(self):
        """Load configuration from JSON in AppData"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except: pass
        return {}
        
    def save_config(self, key, value):
        """Save a config value"""
        self.config[key] = value
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f)
            return True
        except: return False
        
    def set_data_folder(self, new_path):
        """Update data folder path and move files if requested (logic handled by caller usually, but we update config here)"""
        self.config['data_folder'] = new_path
        self.data_dir = new_path
        self.save_config('data_folder', new_path)
        self._init_files() # Re-init to ensure files exist at new location
        return True

    def check_connection(self):
        """Check if data files are accessible"""
        return os.path.exists(self.invoice_file) and os.path.exists(self.inventory_file)

    # ===== IMPORT / EXPORT =====

    def export_data(self, target_folder):
        """Export CSVs to a target folder"""
        try:
            shutil.copy2(self.inventory_file, os.path.join(target_folder, 'inventory_backup.csv'))
            shutil.copy2(self.invoice_file, os.path.join(target_folder, 'invoices_backup.csv'))
            return True, "Export successful!"
        except Exception as e:
            return False, str(e)

    def import_data(self, source_file, type='inventory'):
        """Import CSV data (overwrite for now)"""
        try:
            target = self.inventory_file if type == 'inventory' else self.invoice_file
            
            # Verify columns
            df = pd.read_csv(source_file)
            required_inv = ['name', 'price', 'stock'] # Minimal requirements
            required_invoices = ['invoice_number', 'grand_total']
            
            if type == 'inventory':
                if not all(col in df.columns for col in required_inv):
                    return False, "Invalid Inventory CSV format"
                # Defaults
                if 'size' not in df.columns: df['size'] = 'One Size'
                if 'description' not in df.columns: df['description'] = ''
                if 'buying_price' not in df.columns: df['buying_price'] = 0
            
            # Save
            df.to_csv(target, index=False)
            return True, "Import successful!"
        except Exception as e:
            return False, str(e)

    # ===== INVOICE OPERATIONS =====
    
    def get_next_invoice_number(self):
        """Generate the next invoice number based on the last entry"""
        try:
            df = pd.read_csv(self.invoice_file)
            if df.empty:
                return f"#SC-{datetime.now().year}-001"
            
            last_inv = df['invoice_number'].iloc[-1]
            try:
                # Expecting format #SC-YYYY-XXX
                prefix, year, num = last_inv.split('-')
                new_num = int(num) + 1
                return f"{prefix}-{year}-{new_num:03d}"
            except:
                return f"#SC-{datetime.now().year}-001"
        except:
            return f"#SC-{datetime.now().year}-001"
    
    def save_invoice(self, data):
        """Save an invoice to the CSV"""
        try:
            items_str = str(data['products']) 
            row = [
                data['invoice_number'],
                data['date'],
                data['customer_name'],
                data['customer_phone'],
                data['customer_address'],
                data['subtotal'],
                data['discount'],
                data['delivery'],
                data['grand_total'],
                data['payment_method'],
                data.get('transaction_id', ''),
                items_str
            ]
            
            with open(self.invoice_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            return True
        except Exception as e:
            print(f"Error save: {e}")
            return False

    def get_invoice(self, invoice_number):
        """Retrieve an invoice by number"""
        try:
            df = pd.read_csv(self.invoice_file)
            invoice = df[df['invoice_number'] == invoice_number]
            if not invoice.empty:
                data = invoice.iloc[0].to_dict()
                try:
                    import ast
                    data['products'] = ast.literal_eval(data['items_json'])
                except:
                    data['products'] = []
                return data
            return None
        except: return None

    # ===== INVENTORY OPERATIONS =====
    
    def get_inventory(self):
        """Get all inventory items"""
        try:
            if os.path.exists(self.inventory_file):
                df = pd.read_csv(self.inventory_file)
                # Ensure description exists
                if 'description' not in df.columns:
                    df['description'] = ''
                return df.to_dict('records')
            return []
        except:
            return []

    def add_product(self, product):
        """Add a new product to inventory"""
        try:
            # Check if exists (Name + Size matches)
            df = pd.read_csv(self.inventory_file)
            
            # Ensure buying_price column exists
            if 'buying_price' not in df.columns: df['buying_price'] = 0
            
            # Normalize types for comparison
            # convert df size to string for robust comparison (handling explicit string vs int issues)
            df['size'] = df['size'].astype(str)
            target_size = str(product.get('size',''))
            
            mask = (df['name'] == product['name']) & (df['size'] == target_size)
            
            if mask.any():
                # Update existing
                df.loc[mask, 'stock'] = product.get('stock', 0)
                df.loc[mask, 'price'] = product.get('price', 0)
                df.loc[mask, 'buying_price'] = product.get('buying_price', 0)
                df.loc[mask, 'description'] = product.get('description', '')
                df.to_csv(self.inventory_file, index=False)
            else:
                # Append
                with open(self.inventory_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        product['name'],
                        product.get('description', ''),
                        product.get('size', ''),
                        product['price'],
                        product.get('buying_price', 0),
                        product.get('stock', 0)
                    ])
            return True
        except Exception as e:
            print(f"Error adding: {e}")
            return False

    def update_product_row(self, name, size, new_data):
        """Update a specific product row completely"""
        try:
            df = pd.read_csv(self.inventory_file)
            # Convert both size column and input to string for comparison
            mask = (df['name'] == name) & (df['size'].astype(str) == str(size))
            if mask.any():
                # Update fields
                for key, val in new_data.items():
                    if key in df.columns:
                        df.loc[mask, key] = val
                df.to_csv(self.inventory_file, index=False)
                return True
            return False
        except Exception as e:
            print(f"Update error: {e}")
            return False

    def delete_product(self, name, size):
        """Delete a product by name and size"""
        try:
            df = pd.read_csv(self.inventory_file)
            # Convert both size column and input to string for comparison
            df = df[~((df['name'] == name) & (df['size'].astype(str) == str(size)))]
            df.to_csv(self.inventory_file, index=False)
            return True
        except: return False

    def check_stock_availability(self, name, size, required_qty):
        """Check if sufficient stock is available for a product"""
        try:
            df = pd.read_csv(self.inventory_file)
            # Convert both size column and input to string for comparison
            mask = (df['name'] == name) & (df['size'].astype(str) == str(size))
            if mask.any():
                current_stock = int(df.loc[mask, 'stock'].iloc[0])
                return current_stock >= required_qty, current_stock
            return False, 0
        except Exception as e:
            print(f"Stock check error: {e}")
            return False, 0

    def reduce_stock(self, name, size, quantity):
        """Reduce stock after an invoice is created"""
        try:
            df = pd.read_csv(self.inventory_file)
            # Convert both size column and input to string for comparison
            mask = (df['name'] == name) & (df['size'].astype(str) == str(size))
            if mask.any():
                current_stock = int(df.loc[mask, 'stock'].iloc[0])
                new_stock = max(0, current_stock - quantity)
                df.loc[mask, 'stock'] = new_stock
                df.to_csv(self.inventory_file, index=False)
                return True, new_stock
            return False, 0
        except Exception as e:
            print(f"Stock reduction error: {e}")
            return False, 0
    
    def get_config(self, key, default=None):
        """Get a configuration value safely"""
        cfg = self.load_config()
        return cfg.get(key, default)

    def get_all_invoices(self):
        """Get all invoices as list of dictionaries"""
        try:
            df = pd.read_csv(self.invoice_file)
            invoices = []
            for _, row in df.iterrows():
                # Skip invalid rows (NaN invoice number)
                if pd.isna(row['invoice_number']):
                    continue
                    
                invoice_data = row.to_dict()
                # Parse items_json back to list
                try:
                    import ast
                    invoice_data['products'] = ast.literal_eval(invoice_data['items_json'])
                except:
                    invoice_data['products'] = []
                invoices.append(invoice_data)
            return invoices
        except Exception as e:
            print(f"Error loading invoices: {e}")
            return []
    
    def update_invoice(self, invoice_number, updated_data):
        """Update an existing invoice"""
        import time
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                df = pd.read_csv(self.invoice_file, dtype=str)  # Read all as strings
                mask = df['invoice_number'] == invoice_number
                if mask.any():
                    # Update all fields from updated_data
                    for key, value in updated_data.items():
                        if key in df.columns and key != 'invoice_number':
                            df.loc[mask, key] = str(value) if value is not None else ''
                    df.to_csv(self.invoice_file, index=False)
                    return True
                return False
            except PermissionError as e:
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Wait before retry
                    continue
                print(f"Error updating invoice: File may be open in another program. Please close it and try again.")
                return False
            except Exception as e:
                print(f"Error updating invoice: {e}")
                return False
        return False
    
    def delete_invoice(self, invoice_number):
        """Delete an invoice and return its data"""
        try:
            df = pd.read_csv(self.invoice_file)
            # Get the invoice data before deleting
            invoice_data = None
            mask = df['invoice_number'] == invoice_number
            if mask.any():
                invoice_data = df[mask].iloc[0].to_dict()
                # Remove the invoice
                df = df[~mask]
                df.to_csv(self.invoice_file, index=False)
            return invoice_data
        except Exception as e:
            print(f"Error deleting invoice: {e}")
            return None
    
    def search_invoices(self, query, field='all'):
        """Search invoices by invoice number, customer name, or phone"""
        try:
            df = pd.read_csv(self.invoice_file)
            query = str(query).lower()
            
            if field == 'all':
                # Search in all text fields
                mask = (
                    df['invoice_number'].str.lower().str.contains(query, na=False) |
                    df['customer_name'].str.lower().str.contains(query, na=False) |
                    df['customer_phone'].str.lower().str.contains(query, na=False)
                )
            elif field in df.columns:
                mask = df[field].str.lower().str.contains(query, na=False)
            else:
                return []
            
            result_df = df[mask]
            invoices = []
            for _, row in result_df.iterrows():
                invoice_data = row.to_dict()
                try:
                    import ast
                    invoice_data['products'] = ast.literal_eval(invoice_data['products'])
                except:
                    invoice_data['products'] = []
                invoices.append(invoice_data)
            return invoices
        except Exception as e:
            print(f"Error searching invoices: {e}")
            return []

    # ===== EXPENSE OPERATIONS =====

    def get_expenses(self):
        """Get all expenses"""
        try:
            if os.path.exists(self.expense_file):
                df = pd.read_csv(self.expense_file)
                return df.to_dict('records')
            return []
        except: return []

    def add_expense(self, data):
        """Add a new expense"""
        try:
            # data: date, category, amount, description, related_product
            with open(self.expense_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    data['date'],
                    data['category'],
                    data['amount'],
                    data.get('description', ''),
                    data.get('related_product', '')
                ])
            return True
        except Exception as e:
            print(f"Error adding expense: {e}")
            return False

    def delete_expense(self, row_data):
        """Delete an expense (match by all fields for now as we don't have IDs)"""
        try:
            df = pd.read_csv(self.expense_file)
            # Create mask matching all fields
            mask = (df['date'] == row_data['date']) & \
                   (df['category'] == row_data['category']) & \
                   (df['amount'].astype(str) == str(row_data['amount'])) & \
                   (df['description'] == row_data.get('description', ''))
            
            df = df[~mask]
            df.to_csv(self.expense_file, index=False)
            return True
        except Exception as e:
            print(f"Error deleting expense: {e}")
            return False

    def get_expense_categories(self):
        """Get expense categories from config"""
        defaults = ["Packaging", "Courier", "Product Purchase", "Marketing", "Other"]
        return self.get_config('expense_categories', defaults)

    def add_expense_category(self, category):
        """Add a new expense category"""
        cats = self.get_expense_categories()
        if category not in cats:
            cats.append(category)
            self.save_config('expense_categories', cats)
            return True
        return False

    def delete_expense_category(self, category):
        """Delete an expense category"""
        cats = self.get_expense_categories()
        if category in cats:
            cats.remove(category)
            self.save_config('expense_categories', cats)
            return True
        return False
