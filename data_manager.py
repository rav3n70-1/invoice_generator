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
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
INTERNAL_DATA_DIR = os.path.join(DATA_DIR, 'data')
INVOICE_FILE = os.path.join(INTERNAL_DATA_DIR, 'invoices.csv')
INVENTORY_FILE = os.path.join(INTERNAL_DATA_DIR, 'inventory.csv')
CONFIG_FILE = os.path.join(INTERNAL_DATA_DIR, 'config.json')

# Ensure data directory exists
os.makedirs(INTERNAL_DATA_DIR, exist_ok=True)

class DataManager:
    def __init__(self):
        self._init_files()
        self.config = self.load_config()
    
    def _init_files(self):
        """Initialize CSV files with headers if they don't exist"""
        if not os.path.exists(INVOICE_FILE):
             with open(INVOICE_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'invoice_number', 'date', 'customer_name', 'customer_phone', 
                    'customer_address', 'subtotal', 'discount', 'delivery', 
                    'grand_total', 'payment_method', 'transaction_id', 'items_json'
                ])
        
        if not os.path.exists(INVENTORY_FILE):
            with open(INVENTORY_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'description', 'size', 'price', 'stock'])
    
    # ===== CONFIGURATION =====
    
    def load_config(self):
        """Load configuration from JSON"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except: pass
        return {'output_folder': ''}
        
    def save_config(self, key, value):
        """Save a config value"""
        self.config[key] = value
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f)
            return True
        except: return False

    def check_connection(self):
        """Check if data files are accessible"""
        return os.path.exists(INVOICE_FILE) and os.path.exists(INVENTORY_FILE)

    # ===== IMPORT / EXPORT =====

    def export_data(self, target_folder):
        """Export CSVs to a target folder"""
        try:
            shutil.copy2(INVENTORY_FILE, os.path.join(target_folder, 'inventory_backup.csv'))
            shutil.copy2(INVOICE_FILE, os.path.join(target_folder, 'invoices_backup.csv'))
            return True, "Export successful!"
        except Exception as e:
            return False, str(e)

    def import_data(self, source_file, type='inventory'):
        """Import CSV data (overwrite for now)"""
        try:
            target = INVENTORY_FILE if type == 'inventory' else INVOICE_FILE
            
            # Verify columns
            df = pd.read_csv(source_file)
            required_inv = ['name', 'price', 'stock'] # Minimal requirements
            required_invoices = ['invoice_number', 'grand_total']
            
            if type == 'inventory':
                if not all(col in df.columns for col in required_inv):
                    return False, "Invalid Inventory CSV format"
                # If 'size' missing, default to 'One Size'
                if 'size' not in df.columns: df['size'] = 'One Size'
                if 'description' not in df.columns: df['description'] = ''
            
            # Save
            df.to_csv(target, index=False)
            return True, "Import successful!"
        except Exception as e:
            return False, str(e)
            
    # ===== INVOICE OPERATIONS =====
    
    def get_next_invoice_number(self):
        """Generate the next invoice number based on the last entry"""
        try:
            df = pd.read_csv(INVOICE_FILE)
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
            
            with open(INVOICE_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            return True
        except Exception as e:
            print(f"Error save: {e}")
            return False

    def get_invoice(self, invoice_number):
        """Retrieve an invoice by number"""
        try:
            df = pd.read_csv(INVOICE_FILE)
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
            if os.path.exists(INVENTORY_FILE):
                df = pd.read_csv(INVENTORY_FILE)
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
            df = pd.read_csv(INVENTORY_FILE)
            mask = (df['name'] == product['name']) & (df['size'] == str(product.get('size','')))
            
            if mask.any():
                # Update existing
                df.loc[mask, 'stock'] = product.get('stock', 0)
                df.loc[mask, 'price'] = product.get('price', 0)
                df.loc[mask, 'description'] = product.get('description', '')
                df.to_csv(INVENTORY_FILE, index=False)
            else:
                # Append
                with open(INVENTORY_FILE, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        product['name'],
                        product.get('description', ''),
                        product.get('size', ''),
                        product['price'],
                        product.get('stock', 0)
                    ])
            return True
        except Exception as e:
            print(f"Error adding: {e}")
            return False

    def update_product_row(self, name, size, new_data):
        """Update a specific product row completely"""
        try:
            df = pd.read_csv(INVENTORY_FILE)
            # Convert both size column and input to string for comparison
            mask = (df['name'] == name) & (df['size'].astype(str) == str(size))
            if mask.any():
                # Update fields
                for key, val in new_data.items():
                    if key in df.columns:
                        df.loc[mask, key] = val
                df.to_csv(INVENTORY_FILE, index=False)
                return True
            return False
        except Exception as e:
            print(f"Update error: {e}")
            return False

    def delete_product(self, name, size):
        """Delete a product by name and size"""
        try:
            df = pd.read_csv(INVENTORY_FILE)
            # Convert both size column and input to string for comparison
            df = df[~((df['name'] == name) & (df['size'].astype(str) == str(size)))]
            df.to_csv(INVENTORY_FILE, index=False)
            return True
        except: return False

    def check_stock_availability(self, name, size, required_qty):
        """Check if sufficient stock is available for a product"""
        try:
            df = pd.read_csv(INVENTORY_FILE)
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
            df = pd.read_csv(INVENTORY_FILE)
            # Convert both size column and input to string for comparison
            mask = (df['name'] == name) & (df['size'].astype(str) == str(size))
            if mask.any():
                current_stock = int(df.loc[mask, 'stock'].iloc[0])
                new_stock = max(0, current_stock - quantity)
                df.loc[mask, 'stock'] = new_stock
                df.to_csv(INVENTORY_FILE, index=False)
                return True, new_stock
            return False, 0
        except Exception as e:
            print(f"Stock reduction error: {e}")
            return False, 0
    
    def get_all_invoices(self):
        """Get all invoices as list of dictionaries"""
        try:
            df = pd.read_csv(INVOICE_FILE)
            invoices = []
            for _, row in df.iterrows():
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
        try:
            df = pd.read_csv(INVOICE_FILE)
            mask = df['invoice_number'] == invoice_number
            if mask.any():
                # Update all fields from updated_data
                for key, value in updated_data.items():
                    if key in df.columns and key != 'invoice_number':
                        df.loc[mask, key] = value
                df.to_csv(INVOICE_FILE, index=False)
                return True
            return False
        except Exception as e:
            print(f"Error updating invoice: {e}")
            return False
    
    def delete_invoice(self, invoice_number):
        """Delete an invoice and return its data"""
        try:
            df = pd.read_csv(INVOICE_FILE)
            # Get the invoice data before deleting
            invoice_data = None
            mask = df['invoice_number'] == invoice_number
            if mask.any():
                invoice_data = df[mask].iloc[0].to_dict()
                # Remove the invoice
                df = df[~mask]
                df.to_csv(INVOICE_FILE, index=False)
            return invoice_data
        except Exception as e:
            print(f"Error deleting invoice: {e}")
            return None
    
    def search_invoices(self, query, field='all'):
        """Search invoices by invoice number, customer name, or phone"""
        try:
            df = pd.read_csv(INVOICE_FILE)
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
