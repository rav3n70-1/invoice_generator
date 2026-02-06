import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta

class ExpenseTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="Main.TFrame")
        self.app = app
        self.c = app.c
        self._create_ui()
        
    def _create_ui(self):
        # Layout: Left (Form), Right (Dashboard - Stats + Chart + List)
        self.paned = tk.PanedWindow(self, orient="horizontal", bg=self.c['bg'], sashwidth=4, sashrelief="flat")
        self.paned.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- LEFT PANEL: Add Expense ---
        left = ttk.Frame(self.paned, style="Card.TFrame", padding=20)
        self.paned.add(left, minsize=320, stretch="never")
        
        ttk.Label(left, text="ADD EXPENSE", style="CardTitle.TLabel").pack(pady=(0, 20), anchor="w")
        
        # Date
        ttk.Label(left, text="Date", style="Dim.TLabel").pack(anchor="w")
        self.date_ent = DateEntry(left, width=12, background=self.c['accent'], foreground='white', borderwidth=0, date_pattern='dd/mm/yyyy')
        self.date_ent.pack(fill="x", pady=(5, 15))
        
        # Category
        ttk.Label(left, text="Category", style="Dim.TLabel").pack(anchor="w")
        cat_frame = ttk.Frame(left, style="Card.TFrame")
        cat_frame.pack(fill="x", pady=(5, 15))
        
        self.cat_var = tk.StringVar()
        self.cb_cat = ttk.Combobox(cat_frame, textvariable=self.cat_var, state="readonly", font=("Segoe UI", 10))
        self.cb_cat.pack(side="left", fill="x", expand=True)
        
        tk.Button(cat_frame, text="⚙", command=self._manage_cats, bg=self.c['input'], fg='white', relief='flat', width=3).pack(side="right", padx=(5, 0))
        
        # Amount
        ttk.Label(left, text="Amount (BDT)", style="Dim.TLabel").pack(anchor="w")
        self.amount_var = tk.DoubleVar()
        tk.Entry(left, textvariable=self.amount_var, bg=self.c['input'], fg='white', relief='flat', font=("Segoe UI", 11)).pack(fill="x", pady=(5, 15))
        
        # Description
        ttk.Label(left, text="Description", style="Dim.TLabel").pack(anchor="w")
        self.desc_var = tk.StringVar()
        tk.Entry(left, textvariable=self.desc_var, bg=self.c['input'], fg='white', relief='flat', font=("Segoe UI", 10)).pack(fill="x", pady=(5, 15))
        
        # Related Product
        ttk.Label(left, text="Related Product (Optional)", style="Dim.TLabel").pack(anchor="w")
        self.prod_var = tk.StringVar()
        self.cb_prod = ttk.Combobox(left, textvariable=self.prod_var, width=30, font=("Segoe UI", 10))
        self.cb_prod.pack(fill="x", pady=(5, 25))
        
        tk.Button(left, text="SAVE EXPENSE", command=self._save_expense, 
                 bg=self.c['accent'], fg=self.c['sidebar'], font=("Segoe UI", 10, "bold"), relief="flat", pady=12, cursor="hand2").pack(fill="x")
        
        # --- RIGHT PANEL: Dashboard ---
        right_container = ttk.Frame(self.paned, style="Main.TFrame")
        self.paned.add(right_container, minsize=600, stretch="always")
        
        # 1. Stats Row
        stats_frame = ttk.Frame(right_container, style="Main.TFrame")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        self.card_total = self._create_card(stats_frame, "TOTAL EXPENSES", "0 BDT", "All Time")
        self.card_month = self._create_card(stats_frame, "THIS MONTH", "0 BDT", datetime.now().strftime("%B"))
        self.card_week = self._create_card(stats_frame, "THIS WEEK", "0 BDT", "Last 7 Days")
        
        self.card_total.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.card_month.pack(side="left", fill="x", expand=True, padx=5)
        self.card_week.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # 2. Charts & List Split
        split_frame = tk.PanedWindow(right_container, orient="vertical", bg=self.c['bg'], sashwidth=4, sashrelief="flat")
        split_frame.pack(fill="both", expand=True)

        # Chart Area
        chart_frame = ttk.Frame(split_frame, style="Card.TFrame", padding=15)
        split_frame.add(chart_frame, minsize=200, stretch="always")
        
        ttk.Label(chart_frame, text="EXPENSES BY CATEGORY (This Month)", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.chart_canvas = tk.Canvas(chart_frame, bg=self.c['card'], highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True)
        self.chart_canvas.bind("<Configure>", self._redraw_chart) # Redraw on resize

        # List Area
        list_frame = ttk.Frame(split_frame, style="Main.TFrame")
        split_frame.add(list_frame, minsize=250, stretch="always")
        
        header = ttk.Frame(list_frame, style="Main.TFrame")
        header.pack(fill="x", pady=(15, 10))
        
        ttk.Label(header, text="RECENT TRANSACTIONS", style="Header.TLabel").pack(side="left")
        
        btn_frame = ttk.Frame(header, style="Main.TFrame")
        btn_frame.pack(side="right")
        tk.Button(btn_frame, text="🔄 Refresh", command=self._refresh, bg=self.c['card'], fg='white', relief='flat').pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑 Delete", command=self._delete_expense, bg=self.c['error'], fg='white', relief='flat').pack(side="left")
        
        # Treeview
        cols = ("Date", "Category", "Amount", "Description", "Product")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", selectmode="browse", style="Treeview")
        
        self.tree.heading("Date", text="Date")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Product", text="Product")
        
        self.tree.column("Date", width=100)
        self.tree.column("Category", width=120)
        self.tree.column("Amount", width=100)
        self.tree.column("Description", width=250)
        self.tree.column("Product", width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.monthly_category_data = {} # Store for chart
        
        # Setup data
        self._refresh()

    def _create_card(self, parent, title, value, subtext):
        f = ttk.Frame(parent, style="Card.TFrame", padding=15)
        ttk.Label(f, text=title, style="Dim.TLabel", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        lbl = ttk.Label(f, text=value, font=("Segoe UI", 20, "bold"), foreground=self.c['accent'], background=self.c['card'])
        lbl.pack(anchor="w", pady=(5, 0))
        ttk.Label(f, text=subtext, style="Dim.TLabel", font=("Segoe UI", 8)).pack(anchor="w")
        f.lbl_value = lbl # Store reference
        return f

    def _redraw_chart(self, event=None):
        self._draw_chart(self.monthly_category_data)

    def _draw_chart(self, data):
        self.chart_canvas.delete("all")
        if not data:
            self.chart_canvas.create_text(self.chart_canvas.winfo_width()/2, self.chart_canvas.winfo_height()/2, 
                                        text="No Data for this Month", fill="gray", font=("Segoe UI", 12))
            return
            
        w = self.chart_canvas.winfo_width()
        h = self.chart_canvas.winfo_height()
        if w < 50 or h < 50: return # Too small
        
        # Margin
        pad_x = 40
        pad_y = 30
        graph_w = w - 2*pad_x
        graph_h = h - 2*pad_y
        
        max_val = max(data.values()) if data.values() else 1
        
        bar_width = graph_w / len(data) * 0.6
        spacing = graph_w / len(data)
        
        colors = ["#4cc9f0", "#4361ee", "#3a0ca3", "#7209b7", "#f72585"]
        
        for i, (cat, val) in enumerate(data.items()):
            x = pad_x + (i * spacing) + (spacing - bar_width)/2
            bar_h = (val / max_val) * graph_h
            y = h - pad_y - bar_h
            
            # Draw bar
            color = colors[i % len(colors)]
            self.chart_canvas.create_rectangle(x, y, x + bar_width, h - pad_y, fill=color, outline="")
            
            # Label val
            self.chart_canvas.create_text(x + bar_width/2, y - 10, text=f"{val:.0f}", fill="white", font=("Segoe UI", 8, "bold"))
            
            # Label cat (truncate if long)
            cat_lbl = cat if len(cat) < 10 else cat[:8]+".."
            self.chart_canvas.create_text(x + bar_width/2, h - pad_y + 15, text=cat_lbl, fill="#a0a0a0", font=("Segoe UI", 8))

    def _refresh(self):
        # Refresh categories
        cats = self.app.dm.get_expense_categories()
        self.cb_cat['values'] = cats
        if cats and not self.cat_var.get(): self.cb_cat.current(0)
        
        # Refresh products
        inv = self.app.dm.get_inventory()
        prod_names = sorted(list(set(i['name'] for i in inv)))
        self.cb_prod['values'] = prod_names
        
        # Clear tree
        for i in self.tree.get_children(): self.tree.delete(i)
        
        # Load expenses
        expenses = self.app.dm.get_expenses()
        total_all = 0
        total_month = 0
        total_week = 0
        
        self.monthly_category_data = {} # Reset
        
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        start_week = now - timedelta(days=now.weekday())
        start_week = start_week.replace(hour=0, minute=0, second=0, microsecond=0)
        
        for ex in reversed(expenses): # Show newest first
            try:
                amt = float(ex['amount'])
                cat = ex['category']
                total_all += amt
                
                # Parse date
                d_str = ex['date']
                try:
                    d_obj = datetime.strptime(d_str, "%d/%m/%Y")
                    if d_obj.month == current_month and d_obj.year == current_year:
                        total_month += amt
                        # Add to category breakdown
                        self.monthly_category_data[cat] = self.monthly_category_data.get(cat, 0) + amt
                        
                    if d_obj >= start_week:
                        total_week += amt
                except: pass
                
                self.tree.insert("", "end", values=(
                    ex['date'], ex['category'], f"{amt:,.2f}", ex.get('description',''), ex.get('related_product','')
                ))
            except: pass
            
        # Update Cards
        self.card_total.lbl_value.config(text=f"{total_all:,.0f} BDT")
        self.card_month.lbl_value.config(text=f"{total_month:,.0f} BDT")
        self.card_week.lbl_value.config(text=f"{total_week:,.0f} BDT")
        
        # Draw Chart
        self._draw_chart(self.monthly_category_data)

    def _save_expense(self):
        amt = self.amount_var.get()
        if amt <= 0:
            messagebox.showwarning("Error", "Amount must be positive.")
            return
            
        data = {
            'date': self.date_ent.get(),
            'category': self.cat_var.get(),
            'amount': amt,
            'description': self.desc_var.get(),
            'related_product': self.prod_var.get()
        }
        
        if self.app.dm.add_expense(data):
            self._refresh()
            self.amount_var.set(0)
            self.desc_var.set("")
            self.prod_var.set("")
            messagebox.showinfo("Success", "Expense added!")
        else:
            messagebox.showerror("Error", "Failed to save expense.")

    def _delete_expense(self):
        sel = self.tree.selection()
        if not sel: return
        
        if messagebox.askyesno("Confirm", "Delete selected expense?"):
            item = self.tree.item(sel[0])['values']
            data = {
                'date': item[0],
                'category': item[1],
                'amount': float(str(item[2]).replace(",","")),
                'description': item[3]
            }
            if self.app.dm.delete_expense(data):
                self._refresh()
            else:
                messagebox.showerror("Error", "Could not delete expense.")

    def _manage_cats(self):
        top = tk.Toplevel(self)
        top.title("Manage Categories")
        top.geometry("300x400")
        top.configure(bg=self.c['bg'])
        
        listbox = tk.Listbox(top, bg=self.c['input'], fg='white', relief='flat')
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        for c in self.cb_cat['values']: listbox.insert("end", c)
        
        def add_c():
            new_c = tk.simpledialog.askstring("New Category", "Enter category name:")
            if new_c:
                if self.app.dm.add_expense_category(new_c):
                    listbox.insert("end", new_c)
                    self._refresh()
        
        def del_c():
            sel = listbox.curselection()
            if sel:
                c = listbox.get(sel[0])
                if self.app.dm.delete_expense_category(c):
                    listbox.delete(sel[0])
                    self._refresh()
        
        btn_frame = ttk.Frame(top, style="Main.TFrame")
        btn_frame.pack(fill="x", pady=10)
        tk.Button(btn_frame, text="+ Add", command=add_c, bg=self.c['success'], fg='black').pack(side="left", padx=10, fill="x", expand=True)
        tk.Button(btn_frame, text="- Delete", command=del_c, bg=self.c['error'], fg='white').pack(side="right", padx=10, fill="x", expand=True)
