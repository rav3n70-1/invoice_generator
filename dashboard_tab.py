"""
Dashboard Tab for SneakerCanvasBD
Analytics dashboard with KPI cards, charts, and key business metrics
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import math


class DashboardTab(ttk.Frame):
    """Analytics dashboard with charts and KPI cards"""
    
    def __init__(self, parent, app):
        super().__init__(parent, style="Main.TFrame")
        self.app = app
        self.c = app.c
        
        # Services
        self.analytics = None
        self.inventory_svc = None
        self.invoice_svc = None
        
        self._init_services()
        self._create_ui()
        self._refresh()
    
    def _init_services(self):
        """Initialize services"""
        try:
            from services import AnalyticsService, InventoryService, InvoiceService
            self.analytics = AnalyticsService(self.app.dm.data_dir)
            self.inventory_svc = InventoryService(self.app.dm.data_dir)
            self.invoice_svc = InvoiceService(self.app.dm.data_dir)
        except Exception as e:
            print(f"Error initializing services: {e}")
    
    def _create_ui(self):
        """Create dashboard UI"""
        # Main scrollable container
        canvas = tk.Canvas(self, bg=self.c['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = ttk.Frame(canvas, style="Main.TFrame")
        
        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Header
        header = ttk.Frame(self.scroll_frame, style="Main.TFrame")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        ttk.Label(header, text="📊 DASHBOARD", style="Header.TLabel", 
                 font=("Segoe UI", 20, "bold")).pack(side="left")
        
        tk.Button(header, text="🔄 Refresh", command=self._refresh,
                 bg=self.c['card'], fg='white', relief='flat', 
                 font=("Segoe UI", 10)).pack(side="right")
        
        # KPI Cards Row
        self.kpi_frame = ttk.Frame(self.scroll_frame, style="Main.TFrame")
        self.kpi_frame.pack(fill="x", padx=20, pady=10)
        
        self._create_kpi_cards()
        
        # Charts Row
        charts_row = ttk.Frame(self.scroll_frame, style="Main.TFrame")
        charts_row.pack(fill="x", padx=20, pady=10)
        
        # Revenue Chart (Left)
        self.revenue_chart_frame = tk.Frame(charts_row, bg=self.c['card'], padx=20, pady=15)
        self.revenue_chart_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(self.revenue_chart_frame, text="MONTHLY REVENUE vs EXPENSES", 
                bg=self.c['card'], fg='white', font=("Segoe UI", 11, "bold")).pack(anchor="w")
        
        self.revenue_canvas = tk.Canvas(self.revenue_chart_frame, bg=self.c['card'], 
                                        highlightthickness=0, height=200)
        self.revenue_canvas.pack(fill="both", expand=True, pady=10)
        
        # Best Sizes Chart (Right)
        self.sizes_chart_frame = tk.Frame(charts_row, bg=self.c['card'], padx=20, pady=15)
        self.sizes_chart_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        tk.Label(self.sizes_chart_frame, text="BEST SELLING SIZES", 
                bg=self.c['card'], fg='white', font=("Segoe UI", 11, "bold")).pack(anchor="w")
        
        self.sizes_canvas = tk.Canvas(self.sizes_chart_frame, bg=self.c['card'], 
                                       highlightthickness=0, height=200)
        self.sizes_canvas.pack(fill="both", expand=True, pady=10)
        
        # Daily Trends Chart
        trends_frame = tk.Frame(self.scroll_frame, bg=self.c['card'], padx=20, pady=15)
        trends_frame.pack(fill="x", padx=20, pady=10)
        
        trends_header = tk.Frame(trends_frame, bg=self.c['card'])
        trends_header.pack(fill="x")
        
        tk.Label(trends_header, text="DAILY SALES TRENDS", 
                bg=self.c['card'], fg='white', font=("Segoe UI", 11, "bold")).pack(side="left")
        
        # Period selector
        self.trends_period = tk.StringVar(value="7")
        period_frame = tk.Frame(trends_header, bg=self.c['card'])
        period_frame.pack(side="right")
        
        for text, value in [("7 Days", "7"), ("30 Days", "30")]:
            tk.Radiobutton(period_frame, text=text, variable=self.trends_period, 
                          value=value, bg=self.c['card'], fg='white',
                          selectcolor=self.c['accent'], activebackground=self.c['card'],
                          command=self._update_trends_chart).pack(side="left", padx=5)
        
        self.trends_canvas = tk.Canvas(trends_frame, bg=self.c['card'], 
                                        highlightthickness=0, height=180)
        self.trends_canvas.pack(fill="both", expand=True, pady=10)
        
        # Top Products & Low Stock Row
        bottom_row = ttk.Frame(self.scroll_frame, style="Main.TFrame")
        bottom_row.pack(fill="x", padx=20, pady=(10, 20))
        
        # Top Products (Left)
        top_prods_frame = tk.Frame(bottom_row, bg=self.c['card'], padx=15, pady=15)
        top_prods_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(top_prods_frame, text="🏆 TOP SELLING PRODUCTS", 
                bg=self.c['card'], fg='white', font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        self.top_products_list = ttk.Treeview(top_prods_frame, columns=("Product", "Sold", "Revenue"),
                                              show="headings", height=5)
        self.top_products_list.heading("Product", text="Product")
        self.top_products_list.heading("Sold", text="Sold")
        self.top_products_list.heading("Revenue", text="Revenue")
        self.top_products_list.column("Product", width=150)
        self.top_products_list.column("Sold", width=60, anchor="center")
        self.top_products_list.column("Revenue", width=80, anchor="e")
        self.top_products_list.pack(fill="both", expand=True)
        
        # Low Stock Alerts (Right)
        low_stock_frame = tk.Frame(bottom_row, bg=self.c['card'], padx=15, pady=15)
        low_stock_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        tk.Label(low_stock_frame, text="⚠️ LOW STOCK ALERTS", 
                bg=self.c['card'], fg=self.c['warning'], font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        self.low_stock_list = ttk.Treeview(low_stock_frame, columns=("Product", "Size", "Stock"),
                                           show="headings", height=5)
        self.low_stock_list.heading("Product", text="Product")
        self.low_stock_list.heading("Size", text="Size")
        self.low_stock_list.heading("Stock", text="Stock")
        self.low_stock_list.column("Product", width=150)
        self.low_stock_list.column("Size", width=60, anchor="center")
        self.low_stock_list.column("Stock", width=60, anchor="center")
        self.low_stock_list.pack(fill="both", expand=True)
        
        # Configure Treeview tags for low stock
        self.low_stock_list.tag_configure('critical', foreground=self.c['error'])
        self.low_stock_list.tag_configure('warning', foreground=self.c['warning'])
    
    def _create_kpi_cards(self):
        """Create KPI cards"""
        # Clear existing
        for widget in self.kpi_frame.winfo_children():
            widget.destroy()
        
        # Card container with grid
        cards = [
            ("Total Stock", "0", "📦", "units in inventory"),
            ("Inventory Value", "৳0", "💰", "at selling price"),
            ("Monthly Revenue", "৳0", "📈", "this month"),
            ("Net Profit", "৳0", "💵", "this month")
        ]
        
        self.kpi_labels = {}
        
        for i, (title, value, icon, subtitle) in enumerate(cards):
            card = tk.Frame(self.kpi_frame, bg=self.c['card'], padx=20, pady=15)
            card.pack(side="left", fill="both", expand=True, padx=5)
            
            # Icon
            tk.Label(card, text=icon, bg=self.c['card'], 
                    font=("Segoe UI", 24)).pack(anchor="w")
            
            # Title
            tk.Label(card, text=title, bg=self.c['card'], fg='#94a3b8',
                    font=("Segoe UI", 10)).pack(anchor="w", pady=(5, 0))
            
            # Value
            value_label = tk.Label(card, text=value, bg=self.c['card'], fg='white',
                                  font=("Segoe UI", 22, "bold"))
            value_label.pack(anchor="w")
            self.kpi_labels[title] = value_label
            
            # Subtitle
            tk.Label(card, text=subtitle, bg=self.c['card'], fg='#64748b',
                    font=("Segoe UI", 9)).pack(anchor="w")
    
    def _refresh(self):
        """Refresh all dashboard data"""
        self._update_kpis()
        self._update_revenue_chart()
        self._update_sizes_chart()
        self._update_trends_chart()
        self._update_top_products()
        self._update_low_stock()
    
    def _update_kpis(self):
        """Update KPI card values"""
        try:
            if self.analytics:
                summary = self.analytics.get_dashboard_summary()
            else:
                summary = {'total_stock': 0, 'inventory_value': 0, 'monthly_revenue': 0, 'monthly_profit': 0}
            
            self.kpi_labels["Total Stock"].config(text=f"{summary.get('total_stock', 0):,}")
            self.kpi_labels["Inventory Value"].config(text=f"৳{summary.get('inventory_value', 0):,.0f}")
            self.kpi_labels["Monthly Revenue"].config(text=f"৳{summary.get('monthly_revenue', 0):,.0f}")
            self.kpi_labels["Net Profit"].config(text=f"৳{summary.get('monthly_profit', 0):,.0f}")
        except Exception as e:
            print(f"Error updating KPIs: {e}")
    
    def _update_revenue_chart(self):
        """Draw revenue vs expense bar chart"""
        self.revenue_canvas.delete("all")
        
        try:
            if self.analytics:
                data = self.analytics.get_monthly_revenue_expense(6)
            else:
                data = []
            
            if not data:
                self.revenue_canvas.create_text(150, 100, text="No data available", 
                                               fill='#64748b', font=("Segoe UI", 11))
                return
            
            # Dimensions
            self.revenue_canvas.update_idletasks()
            w = self.revenue_canvas.winfo_width() or 400
            h = self.revenue_canvas.winfo_height() or 180
            
            padding = 40
            chart_w = w - (padding * 2)
            chart_h = h - (padding * 2)
            
            # Find max value for scaling
            max_val = max([max(d['revenue'], d['expense']) for d in data] + [1])
            
            # Draw bars
            bar_group_width = chart_w / len(data)
            bar_width = bar_group_width * 0.3
            
            for i, d in enumerate(data):
                x_center = padding + (i * bar_group_width) + (bar_group_width / 2)
                
                # Revenue bar (left)
                rev_height = (d['revenue'] / max_val) * chart_h
                x1 = x_center - bar_width - 2
                y1 = h - padding - rev_height
                x2 = x_center - 2
                y2 = h - padding
                self.revenue_canvas.create_rectangle(x1, y1, x2, y2, fill='#22c55e', outline='')
                
                # Expense bar (right)
                exp_height = (d['expense'] / max_val) * chart_h
                x1 = x_center + 2
                y1 = h - padding - exp_height
                x2 = x_center + bar_width + 2
                y2 = h - padding
                self.revenue_canvas.create_rectangle(x1, y1, x2, y2, fill='#ef4444', outline='')
                
                # Label
                self.revenue_canvas.create_text(x_center, h - 15, text=d['month_label'],
                                               fill='#94a3b8', font=("Segoe UI", 8))
            
            # Legend
            self.revenue_canvas.create_rectangle(padding, 5, padding + 12, 17, fill='#22c55e', outline='')
            self.revenue_canvas.create_text(padding + 18, 11, text="Revenue", anchor="w",
                                           fill='#94a3b8', font=("Segoe UI", 9))
            
            self.revenue_canvas.create_rectangle(padding + 80, 5, padding + 92, 17, fill='#ef4444', outline='')
            self.revenue_canvas.create_text(padding + 98, 11, text="Expenses", anchor="w",
                                           fill='#94a3b8', font=("Segoe UI", 9))
            
        except Exception as e:
            print(f"Error drawing revenue chart: {e}")
    
    def _update_sizes_chart(self):
        """Draw best selling sizes bar chart"""
        self.sizes_canvas.delete("all")
        
        try:
            if self.analytics:
                data = self.analytics.get_best_selling_sizes(8)
            else:
                data = []
            
            if not data:
                self.sizes_canvas.create_text(150, 100, text="No data available",
                                             fill='#64748b', font=("Segoe UI", 11))
                return
            
            # Dimensions
            self.sizes_canvas.update_idletasks()
            w = self.sizes_canvas.winfo_width() or 400
            h = self.sizes_canvas.winfo_height() or 180
            
            padding = 40
            chart_h = h - (padding * 2)
            
            # Find max value
            max_val = max([d['quantity'] for d in data] + [1])
            
            # Draw horizontal bars
            bar_height = min(20, (chart_h - 10) / len(data))
            
            for i, d in enumerate(data):
                y_center = padding + (i * (bar_height + 5))
                
                # Size label
                self.sizes_canvas.create_text(padding - 5, y_center + bar_height/2,
                                             text=d['size'], anchor="e",
                                             fill='white', font=("Segoe UI", 9))
                
                # Bar
                bar_width = (d['quantity'] / max_val) * (w - padding * 2 - 40)
                self.sizes_canvas.create_rectangle(padding, y_center,
                                                  padding + bar_width, y_center + bar_height,
                                                  fill='#3b82f6', outline='')
                
                # Quantity label
                self.sizes_canvas.create_text(padding + bar_width + 5, y_center + bar_height/2,
                                             text=str(d['quantity']), anchor="w",
                                             fill='#94a3b8', font=("Segoe UI", 9))
            
        except Exception as e:
            print(f"Error drawing sizes chart: {e}")
    
    def _update_trends_chart(self):
        """Draw daily sales trend line chart"""
        self.trends_canvas.delete("all")
        
        try:
            days = int(self.trends_period.get())
            if self.analytics:
                data = self.analytics.get_daily_sales_trends(days)
            else:
                data = []
            
            if not data:
                self.trends_canvas.create_text(200, 80, text="No data available",
                                              fill='#64748b', font=("Segoe UI", 11))
                return
            
            # Dimensions
            self.trends_canvas.update_idletasks()
            w = self.trends_canvas.winfo_width() or 800
            h = self.trends_canvas.winfo_height() or 160
            
            padding = 50
            chart_w = w - (padding * 2)
            chart_h = h - (padding * 2)
            
            # Find max value
            max_val = max([d['revenue'] for d in data] + [1])
            
            # Calculate points
            points = []
            step = chart_w / (len(data) - 1) if len(data) > 1 else chart_w
            
            for i, d in enumerate(data):
                x = padding + (i * step)
                y = h - padding - ((d['revenue'] / max_val) * chart_h)
                points.append((x, y))
            
            # Draw grid lines
            for i in range(5):
                y = padding + (i * (chart_h / 4))
                self.trends_canvas.create_line(padding, y, w - padding, y, 
                                              fill='#374151', dash=(2, 4))
            
            # Draw line
            if len(points) >= 2:
                flat_points = [coord for point in points for coord in point]
                self.trends_canvas.create_line(flat_points, fill='#ef4444', width=2, smooth=True)
            
            # Draw points and labels
            for i, (x, y) in enumerate(points):
                self.trends_canvas.create_oval(x-4, y-4, x+4, y+4, fill='#ef4444', outline='white')
                
                # Show every Nth label based on data count
                label_interval = max(1, len(data) // 7)
                if i % label_interval == 0 or i == len(data) - 1:
                    self.trends_canvas.create_text(x, h - 15, text=data[i]['day_label'],
                                                  fill='#94a3b8', font=("Segoe UI", 8))
            
        except Exception as e:
            print(f"Error drawing trends chart: {e}")
    
    def _update_top_products(self):
        """Update top products list"""
        for item in self.top_products_list.get_children():
            self.top_products_list.delete(item)
        
        try:
            if self.analytics:
                products = self.analytics.get_top_products(5)
            else:
                products = []
            
            for p in products:
                self.top_products_list.insert("", "end", values=(
                    p.get('name', '')[:25],
                    p.get('quantity_sold', 0),
                    f"৳{p.get('revenue', 0):,.0f}"
                ))
        except Exception as e:
            print(f"Error updating top products: {e}")
    
    def _update_low_stock(self):
        """Update low stock alerts list"""
        for item in self.low_stock_list.get_children():
            self.low_stock_list.delete(item)
        
        try:
            if self.inventory_svc:
                items = self.inventory_svc.get_low_stock_items(5)
            else:
                items = []
            
            for item in items[:10]:
                stock = int(item.get('stock', 0))
                tag = 'critical' if stock <= 2 else 'warning'
                
                self.low_stock_list.insert("", "end", values=(
                    item.get('name', '')[:20],
                    item.get('size', ''),
                    stock
                ), tags=(tag,))
        except Exception as e:
            print(f"Error updating low stock: {e}")
