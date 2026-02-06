"""
Invoice Service for SneakerCanvasBD
Handles all invoice operations with status tracking, returns, and duplicate detection
"""

import hashlib
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import ast

from .base_service import BaseService


class InvoiceService(BaseService):
    """Service for invoice management with status and returns support"""
    
    # Schema definition
    COLUMNS = [
        'invoice_number', 'date', 'customer_name', 'customer_phone',
        'customer_address', 'subtotal', 'discount', 'delivery',
        'grand_total', 'payment_method', 'transaction_id', 'items_json',
        'status', 'original_invoice_no', 'hash'
    ]
    
    # New columns for migration
    NEW_COLUMNS = {
        'status': 'PAID',
        'original_invoice_no': '',
        'hash': ''
    }
    
    # Valid statuses
    STATUSES = ['PAID', 'PARTIAL', 'DUE']
    
    # Payment methods
    PAYMENT_METHODS = ['Cash', 'bKash', 'Nagad', 'Card']
    
    def __init__(self, data_dir: str):
        super().__init__(data_dir)
        self.invoice_file = os.path.join(data_dir, 'invoices.csv')
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Ensure invoice file has correct schema"""
        if not os.path.exists(self.invoice_file):
            df = pd.DataFrame(columns=self.COLUMNS)
            df.to_csv(self.invoice_file, index=False)
        else:
            valid, missing = self.validate_schema(self.invoice_file, self.COLUMNS)
            if not valid:
                self.migrate_schema(self.invoice_file, self.NEW_COLUMNS)
                self._generate_missing_hashes()
    
    def _generate_missing_hashes(self):
        """Generate hash for invoices without one"""
        try:
            df = pd.read_csv(self.invoice_file)
            if 'hash' not in df.columns:
                df['hash'] = ''
            
            for idx, row in df.iterrows():
                if pd.isna(row.get('hash', '')) or row.get('hash', '') == '':
                    invoice_hash = self._compute_hash(
                        row.get('customer_name', ''),
                        row.get('items_json', ''),
                        row.get('date', '')
                    )
                    df.at[idx, 'hash'] = invoice_hash
            
            df.to_csv(self.invoice_file, index=False)
        except Exception as e:
            print(f"Error generating hashes: {e}")
    
    def _compute_hash(self, customer: str, items: str, date: str) -> str:
        """Compute hash for duplicate detection"""
        content = f"{customer}|{items}|{date}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    # ===== CRUD Operations =====
    
    def get_next_invoice_number(self) -> str:
        """Generate the next invoice number"""
        try:
            df = pd.read_csv(self.invoice_file)
            df = df[df['invoice_number'].notna() & (df['invoice_number'] != '')]
            
            if df.empty:
                return f"#SC-{datetime.now().year}-001"
            
            last_inv = df['invoice_number'].iloc[-1]
            try:
                prefix, year, num = str(last_inv).split('-')
                new_num = int(num) + 1
                return f"{prefix}-{year}-{new_num:03d}"
            except:
                return f"#SC-{datetime.now().year}-001"
        except:
            return f"#SC-{datetime.now().year}-001"
    
    def save_invoice(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Save an invoice. Returns (success, warning_message)"""
        try:
            # Compute hash for duplicate detection
            items_str = str(data.get('products', []))
            invoice_hash = self._compute_hash(
                data.get('customer_name', ''),
                items_str,
                data.get('date', '')
            )
            
            # Check for duplicates
            warning = None
            existing = self.detect_duplicate(invoice_hash)
            if existing:
                warning = f"Possible duplicate of invoice {existing['invoice_number']}"
            
            row = [
                data.get('invoice_number', ''),
                data.get('date', ''),
                data.get('customer_name', ''),
                data.get('customer_phone', ''),
                data.get('customer_address', ''),
                data.get('subtotal', 0),
                data.get('discount', 0),
                data.get('delivery', 0),
                data.get('grand_total', 0),
                data.get('payment_method', 'Cash'),
                data.get('transaction_id', ''),
                items_str,
                data.get('status', 'PAID'),
                data.get('original_invoice_no', ''),
                invoice_hash
            ]
            
            with open(self.invoice_file, 'a', newline='', encoding='utf-8') as f:
                import csv
                writer = csv.writer(f)
                writer.writerow(row)
            
            return True, warning
        except Exception as e:
            print(f"Error saving invoice: {e}")
            return False, str(e)
    
    def get_invoice(self, invoice_number: str) -> Optional[Dict[str, Any]]:
        """Get an invoice by number"""
        try:
            df = pd.read_csv(self.invoice_file)
            invoice = df[df['invoice_number'] == invoice_number]
            if not invoice.empty:
                data = invoice.iloc[0].to_dict()
                try:
                    data['products'] = ast.literal_eval(data.get('items_json', '[]'))
                except:
                    data['products'] = []
                return data
            return None
        except:
            return None
    
    def get_all_invoices(self) -> List[Dict[str, Any]]:
        """Get all invoices"""
        try:
            df = pd.read_csv(self.invoice_file)
            invoices = []
            for _, row in df.iterrows():
                if pd.isna(row.get('invoice_number', '')):
                    continue
                
                invoice_data = row.to_dict()
                try:
                    invoice_data['products'] = ast.literal_eval(str(invoice_data.get('items_json', '[]')))
                except:
                    invoice_data['products'] = []
                invoices.append(invoice_data)
            return invoices
        except Exception as e:
            print(f"Error loading invoices: {e}")
            return []
    
    def update_invoice(self, invoice_number: str, updates: Dict[str, Any]) -> bool:
        """Update an existing invoice"""
        try:
            df = pd.read_csv(self.invoice_file)
            mask = df['invoice_number'] == invoice_number
            if mask.any():
                for key, value in updates.items():
                    if key in df.columns and key != 'invoice_number':
                        df.loc[mask, key] = value
                df.to_csv(self.invoice_file, index=False)
                return True
            return False
        except Exception as e:
            print(f"Error updating invoice: {e}")
            return False
    
    def delete_invoice(self, invoice_number: str) -> Optional[Dict[str, Any]]:
        """Delete an invoice and return its data"""
        try:
            df = pd.read_csv(self.invoice_file)
            mask = df['invoice_number'] == invoice_number
            if mask.any():
                invoice_data = df[mask].iloc[0].to_dict()
                df = df[~mask]
                df.to_csv(self.invoice_file, index=False)
                return invoice_data
            return None
        except Exception as e:
            print(f"Error deleting invoice: {e}")
            return None
    
    def search_invoices(self, query: str, field: str = 'all') -> List[Dict[str, Any]]:
        """Search invoices by various fields"""
        try:
            df = pd.read_csv(self.invoice_file)
            query = str(query).lower()
            
            if field == 'all':
                mask = (
                    df['invoice_number'].astype(str).str.lower().str.contains(query, na=False) |
                    df['customer_name'].astype(str).str.lower().str.contains(query, na=False) |
                    df['customer_phone'].astype(str).str.lower().str.contains(query, na=False)
                )
            elif field in df.columns:
                mask = df[field].astype(str).str.lower().str.contains(query, na=False)
            else:
                return []
            
            result_df = df[mask]
            invoices = []
            for _, row in result_df.iterrows():
                invoice_data = row.to_dict()
                try:
                    invoice_data['products'] = ast.literal_eval(str(invoice_data.get('items_json', '[]')))
                except:
                    invoice_data['products'] = []
                invoices.append(invoice_data)
            return invoices
        except Exception as e:
            print(f"Error searching invoices: {e}")
            return []
    
    # ===== Status Operations =====
    
    def update_invoice_status(self, invoice_number: str, status: str) -> bool:
        """Update invoice status (PAID, PARTIAL, DUE)"""
        if status not in self.STATUSES:
            return False
        return self.update_invoice(invoice_number, {'status': status})
    
    def get_invoices_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all invoices with a specific status"""
        try:
            df = pd.read_csv(self.invoice_file)
            if 'status' not in df.columns:
                return []
            
            filtered = df[df['status'] == status]
            invoices = []
            for _, row in filtered.iterrows():
                invoice_data = row.to_dict()
                try:
                    invoice_data['products'] = ast.literal_eval(str(invoice_data.get('items_json', '[]')))
                except:
                    invoice_data['products'] = []
                invoices.append(invoice_data)
            return invoices
        except:
            return []
    
    # ===== Returns & Refunds =====
    
    def create_return_invoice(self, original_invoice_no: str, return_items: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Create a return/refund invoice linked to original"""
        original = self.get_invoice(original_invoice_no)
        if not original:
            return False, "Original invoice not found"
        
        # Generate return invoice number
        return_number = f"RET-{original_invoice_no.replace('#', '').replace('-', '_')}"
        
        # Calculate negative amounts
        subtotal = sum(-abs(item.get('price', 0) * item.get('qty', 1)) for item in return_items)
        
        return_data = {
            'invoice_number': return_number,
            'date': datetime.now().strftime('%m/%d/%Y'),
            'customer_name': original.get('customer_name', ''),
            'customer_phone': original.get('customer_phone', ''),
            'customer_address': original.get('customer_address', ''),
            'subtotal': subtotal,
            'discount': 0,
            'delivery': 0,
            'grand_total': subtotal,
            'payment_method': 'Refund',
            'transaction_id': '',
            'products': return_items,
            'status': 'PAID',
            'original_invoice_no': original_invoice_no
        }
        
        success, warning = self.save_invoice(return_data)
        return success, return_number if success else warning
    
    def get_returns_for_invoice(self, invoice_number: str) -> List[Dict[str, Any]]:
        """Get all returns/refunds for an invoice"""
        try:
            df = pd.read_csv(self.invoice_file)
            if 'original_invoice_no' not in df.columns:
                return []
            
            returns = df[df['original_invoice_no'] == invoice_number]
            result = []
            for _, row in returns.iterrows():
                data = row.to_dict()
                try:
                    data['products'] = ast.literal_eval(str(data.get('items_json', '[]')))
                except:
                    data['products'] = []
                result.append(data)
            return result
        except:
            return []
    
    # ===== Duplicate Detection =====
    
    def detect_duplicate(self, invoice_hash: str) -> Optional[Dict[str, Any]]:
        """Check if an invoice with this hash exists"""
        try:
            df = pd.read_csv(self.invoice_file)
            if 'hash' not in df.columns:
                return None
            
            matching = df[df['hash'] == invoice_hash]
            if not matching.empty:
                return matching.iloc[0].to_dict()
            return None
        except:
            return None
    
    def check_potential_duplicate(self, customer: str, items: str, date: str) -> Optional[Dict[str, Any]]:
        """Check for potential duplicate before saving"""
        invoice_hash = self._compute_hash(customer, items, date)
        return self.detect_duplicate(invoice_hash)
    
    # ===== Analytics =====
    
    def get_daily_sales(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily sales data for the last N days"""
        try:
            df = pd.read_csv(self.invoice_file)
            
            # Convert date and filter
            df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
            cutoff = datetime.now() - timedelta(days=days)
            
            recent = df[df['date_parsed'] >= cutoff]
            
            # Group by date
            recent['date_str'] = recent['date_parsed'].dt.strftime('%Y-%m-%d')
            daily = recent.groupby('date_str').agg({
                'grand_total': 'sum',
                'invoice_number': 'count'
            }).reset_index()
            
            daily.columns = ['date', 'revenue', 'invoice_count']
            return daily.to_dict('records')
        except Exception as e:
            print(f"Error getting daily sales: {e}")
            return []
    
    def get_monthly_revenue(self) -> Dict[str, float]:
        """Get revenue for current and previous month"""
        try:
            df = pd.read_csv(self.invoice_file)
            df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
            
            now = datetime.now()
            current_month_start = now.replace(day=1)
            prev_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            
            current = df[(df['date_parsed'] >= current_month_start)]['grand_total'].astype(float).sum()
            previous = df[(df['date_parsed'] >= prev_month_start) & 
                         (df['date_parsed'] < current_month_start)]['grand_total'].astype(float).sum()
            
            return {
                'current_month': current,
                'previous_month': previous,
                'change_pct': ((current - previous) / previous * 100) if previous > 0 else 0
            }
        except Exception as e:
            print(f"Error getting monthly revenue: {e}")
            return {'current_month': 0, 'previous_month': 0, 'change_pct': 0}
    
    def get_best_selling_sizes(self) -> List[Dict[str, Any]]:
        """Get breakdown of sales by shoe size"""
        try:
            df = pd.read_csv(self.invoice_file)
            
            size_counts = {}
            for _, row in df.iterrows():
                try:
                    items = ast.literal_eval(str(row.get('items_json', '[]')))
                    for item in items:
                        size = str(item.get('size', 'Unknown'))
                        qty = int(item.get('qty', 1))
                        size_counts[size] = size_counts.get(size, 0) + qty
                except:
                    continue
            
            result = [{'size': k, 'quantity': v} for k, v in size_counts.items()]
            return sorted(result, key=lambda x: x['quantity'], reverse=True)
        except:
            return []
    
    def get_invoice_summary(self) -> Dict[str, Any]:
        """Get summary stats for dashboard"""
        try:
            df = pd.read_csv(self.invoice_file)
            df = df[df['invoice_number'].notna() & (df['invoice_number'] != '')]
            
            total_invoices = len(df)
            total_revenue = df['grand_total'].astype(float).sum()
            
            # Status breakdown
            status_counts = {}
            if 'status' in df.columns:
                status_counts = df['status'].value_counts().to_dict()
            
            # Today's sales
            today = datetime.now().strftime('%m/%d/%Y')
            today_sales = df[df['date'] == today]['grand_total'].astype(float).sum()
            
            return {
                'total_invoices': total_invoices,
                'total_revenue': total_revenue,
                'status_counts': status_counts,
                'today_sales': today_sales
            }
        except Exception as e:
            print(f"Error getting invoice summary: {e}")
            return {
                'total_invoices': 0,
                'total_revenue': 0,
                'status_counts': {},
                'today_sales': 0
            }
