"""
Analytics Service for SneakerCanvasBD
Aggregates data from all services for dashboard displays
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd

from .base_service import BaseService


class AnalyticsService(BaseService):
    """Service for business analytics and dashboard data"""
    
    def __init__(self, data_dir: str):
        super().__init__(data_dir)
        self.invoice_file = os.path.join(data_dir, 'invoices.csv')
        self.inventory_file = os.path.join(data_dir, 'inventory.csv')
        self.expense_file = os.path.join(data_dir, 'expenses.csv')
    
    # ===== Revenue & Profit =====
    
    def get_monthly_revenue_expense(self, months: int = 6) -> List[Dict[str, Any]]:
        """Get monthly revenue vs expense data for bar chart"""
        try:
            # Load data
            invoices = pd.read_csv(self.invoice_file) if os.path.exists(self.invoice_file) else pd.DataFrame()
            expenses = pd.read_csv(self.expense_file) if os.path.exists(self.expense_file) else pd.DataFrame()
            
            # Parse dates
            if not invoices.empty:
                invoices['date_parsed'] = pd.to_datetime(invoices['date'], errors='coerce')
                invoices['month'] = invoices['date_parsed'].dt.to_period('M')
            
            if not expenses.empty:
                expenses['date_parsed'] = pd.to_datetime(expenses['date'], errors='coerce')
                expenses['month'] = expenses['date_parsed'].dt.to_period('M')
            
            # Generate month list
            now = datetime.now()
            month_list = []
            for i in range(months - 1, -1, -1):
                month_date = now - timedelta(days=i * 30)
                month_list.append(month_date.strftime('%Y-%m'))
            
            result = []
            for month_str in month_list:
                month_period = pd.Period(month_str)
                
                # Revenue for month
                if not invoices.empty and 'month' in invoices.columns:
                    month_invoices = invoices[invoices['month'] == month_period]
                    revenue = month_invoices['grand_total'].astype(float).sum()
                else:
                    revenue = 0
                
                # Expenses for month
                if not expenses.empty and 'month' in expenses.columns:
                    month_expenses = expenses[expenses['month'] == month_period]
                    expense = month_expenses['amount'].astype(float).sum()
                else:
                    expense = 0
                
                result.append({
                    'month': month_str,
                    'month_label': month_period.strftime('%b %Y'),
                    'revenue': revenue,
                    'expense': expense,
                    'profit': revenue - expense
                })
            
            return result
        except Exception as e:
            print(f"Error getting monthly data: {e}")
            return []
    
    def get_net_profit(self, period: str = 'month') -> Dict[str, Any]:
        """Get net profit for a period"""
        try:
            invoices = pd.read_csv(self.invoice_file) if os.path.exists(self.invoice_file) else pd.DataFrame()
            expenses = pd.read_csv(self.expense_file) if os.path.exists(self.expense_file) else pd.DataFrame()
            inventory = pd.read_csv(self.inventory_file) if os.path.exists(self.inventory_file) else pd.DataFrame()
            
            now = datetime.now()
            
            if period == 'month':
                start_date = now.replace(day=1)
            elif period == 'week':
                start_date = now - timedelta(days=7)
            elif period == 'year':
                start_date = now.replace(month=1, day=1)
            else:
                start_date = now.replace(day=1)
            
            # Calculate revenue
            revenue = 0
            if not invoices.empty:
                invoices['date_parsed'] = pd.to_datetime(invoices['date'], errors='coerce')
                period_invoices = invoices[invoices['date_parsed'] >= start_date]
                revenue = period_invoices['grand_total'].astype(float).sum()
            
            # Calculate expenses
            expense = 0
            if not expenses.empty:
                expenses['date_parsed'] = pd.to_datetime(expenses['date'], errors='coerce')
                period_expenses = expenses[expenses['date_parsed'] >= start_date]
                expense = period_expenses['amount'].astype(float).sum()
            
            # Calculate cost of goods sold (buying price of sold items)
            cogs = 0
            if not invoices.empty and not inventory.empty:
                # This is simplified - in reality would need to track actual COGS
                try:
                    period_invoices = invoices[invoices['date_parsed'] >= start_date]
                    for _, row in period_invoices.iterrows():
                        import ast
                        items = ast.literal_eval(str(row.get('items_json', '[]')))
                        for item in items:
                            name = item.get('name', '')
                            size = str(item.get('size', ''))
                            qty = int(item.get('qty', 1))
                            
                            # Get buying price from inventory
                            mask = (inventory['name'] == name) & (inventory['size'].astype(str) == size)
                            if mask.any():
                                buying_price = float(inventory.loc[mask, 'buying_price'].iloc[0] or 0)
                                cogs += buying_price * qty
                except:
                    pass
            
            net_profit = revenue - expense - cogs
            gross_profit = revenue - cogs
            margin_pct = (gross_profit / revenue * 100) if revenue > 0 else 0
            
            return {
                'revenue': revenue,
                'expenses': expense,
                'cogs': cogs,
                'gross_profit': gross_profit,
                'net_profit': net_profit,
                'margin_pct': margin_pct,
                'period': period
            }
        except Exception as e:
            print(f"Error calculating net profit: {e}")
            return {
                'revenue': 0,
                'expenses': 0,
                'cogs': 0,
                'gross_profit': 0,
                'net_profit': 0,
                'margin_pct': 0,
                'period': period
            }
    
    # ===== Sales Analysis =====
    
    def get_best_selling_sizes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get best-selling sizes from sales data"""
        try:
            invoices = pd.read_csv(self.invoice_file)
            
            size_counts = {}
            size_revenue = {}
            
            for _, row in invoices.iterrows():
                try:
                    import ast
                    items = ast.literal_eval(str(row.get('items_json', '[]')))
                    for item in items:
                        size = str(item.get('size', 'Unknown'))
                        qty = int(item.get('qty', 1))
                        price = float(item.get('price', 0))
                        
                        size_counts[size] = size_counts.get(size, 0) + qty
                        size_revenue[size] = size_revenue.get(size, 0) + (price * qty)
                except:
                    continue
            
            result = [
                {
                    'size': size,
                    'quantity': size_counts[size],
                    'revenue': size_revenue.get(size, 0)
                }
                for size in size_counts
            ]
            
            return sorted(result, key=lambda x: x['quantity'], reverse=True)[:limit]
        except:
            return []
    
    def get_daily_sales_trends(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily sales trends for chart"""
        try:
            invoices = pd.read_csv(self.invoice_file)
            invoices['date_parsed'] = pd.to_datetime(invoices['date'], errors='coerce')
            
            cutoff = datetime.now() - timedelta(days=days)
            recent = invoices[invoices['date_parsed'] >= cutoff]
            
            # Generate all dates in range
            date_range = pd.date_range(start=cutoff, periods=days + 1, freq='D')
            
            result = []
            for date in date_range:
                date_str = date.strftime('%Y-%m-%d')
                day_invoices = recent[recent['date_parsed'].dt.date == date.date()]
                
                revenue = day_invoices['grand_total'].astype(float).sum()
                count = len(day_invoices)
                
                result.append({
                    'date': date_str,
                    'day_label': date.strftime('%a'),
                    'revenue': revenue,
                    'invoice_count': count
                })
            
            return result
        except Exception as e:
            print(f"Error getting sales trends: {e}")
            return []
    
    def get_top_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top customers by total spend"""
        try:
            invoices = pd.read_csv(self.invoice_file)
            
            customer_data = invoices.groupby('customer_name').agg({
                'grand_total': 'sum',
                'invoice_number': 'count'
            }).reset_index()
            
            customer_data.columns = ['customer_name', 'total_spend', 'order_count']
            customer_data = customer_data.sort_values('total_spend', ascending=False)
            
            return customer_data.head(limit).to_dict('records')
        except:
            return []
    
    def get_top_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top-selling products"""
        try:
            invoices = pd.read_csv(self.invoice_file)
            
            product_sales = {}
            product_revenue = {}
            
            for _, row in invoices.iterrows():
                try:
                    import ast
                    items = ast.literal_eval(str(row.get('items_json', '[]')))
                    for item in items:
                        name = item.get('name', 'Unknown')
                        qty = int(item.get('qty', 1))
                        price = float(item.get('price', 0))
                        
                        product_sales[name] = product_sales.get(name, 0) + qty
                        product_revenue[name] = product_revenue.get(name, 0) + (price * qty)
                except:
                    continue
            
            result = [
                {
                    'name': name,
                    'quantity_sold': product_sales[name],
                    'revenue': product_revenue.get(name, 0)
                }
                for name in product_sales
            ]
            
            return sorted(result, key=lambda x: x['quantity_sold'], reverse=True)[:limit]
        except:
            return []
    
    # ===== Dashboard Summary =====
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get all key metrics for dashboard"""
        try:
            # Inventory metrics
            inventory = pd.read_csv(self.inventory_file) if os.path.exists(self.inventory_file) else pd.DataFrame()
            total_stock = int(inventory['stock'].astype(int).sum()) if not inventory.empty else 0
            inventory_value = float((inventory['stock'].astype(int) * inventory['price'].astype(float)).sum()) if not inventory.empty else 0
            low_stock_count = len(inventory[inventory['stock'].astype(int) <= 5]) if not inventory.empty else 0
            
            # Monthly profit
            profit_data = self.get_net_profit('month')
            
            # Daily trends
            daily_trends = self.get_daily_sales_trends(7)
            
            # Today's sales
            today = datetime.now().date()
            invoices = pd.read_csv(self.invoice_file) if os.path.exists(self.invoice_file) else pd.DataFrame()
            today_sales = 0
            if not invoices.empty:
                invoices['date_parsed'] = pd.to_datetime(invoices['date'], errors='coerce')
                today_invoices = invoices[invoices['date_parsed'].dt.date == today]
                today_sales = float(today_invoices['grand_total'].astype(float).sum())
            
            return {
                'total_stock': total_stock,
                'inventory_value': inventory_value,
                'low_stock_count': low_stock_count,
                'monthly_revenue': profit_data['revenue'],
                'monthly_expense': profit_data['expenses'],
                'monthly_profit': profit_data['net_profit'],
                'profit_margin': profit_data['margin_pct'],
                'today_sales': today_sales,
                'daily_trends': daily_trends
            }
        except Exception as e:
            print(f"Error getting dashboard summary: {e}")
            return {
                'total_stock': 0,
                'inventory_value': 0,
                'low_stock_count': 0,
                'monthly_revenue': 0,
                'monthly_expense': 0,
                'monthly_profit': 0,
                'profit_margin': 0,
                'today_sales': 0,
                'daily_trends': []
            }
