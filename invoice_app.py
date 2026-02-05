"""
Invoice Generator & Inventory Manager v3.1
Features: Header Bar, Status Light, Import/Export, Inventory CRUD + Description.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import os
import time
from datetime import datetime
from invoice_generator import InvoiceGenerator
from data_manager import DataManager
from loading_screen import LoadingScreen

# Fix Windows taskbar icon
try:
    import ctypes
    myappid = 'sneakercanvasbd.invoicemanager.v3.1'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass


# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LOGO = os.path.join(SCRIPT_DIR, "assets", "logo.jpg")
DEFAULT_SIGN = os.path.join(SCRIPT_DIR, "assets", "SIGN JOY.png")

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sneaker Canvas BD - Management System v3.1")
        self.root.geometry("1300x850")
        self.root.minsize(1000, 700)
        
        # Set program icon (both window and taskbar)
        try:
            icon_path = os.path.join(SCRIPT_DIR, "assets", "logo.ico")
            if os.path.exists(icon_path):
                # Set icon for both window title bar and taskbar
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not set icon: {e}")
        
        # Colors
        self.c = {
            'bg': '#1e1e2e',
            'sidebar': '#181825',
            'card': '#313244',
            'accent': '#f38ba8',       # Red/Pinkish
            'accent_hover': '#d27b91',
            'text': '#cdd6f4',
            'text_dim': '#a6adc8',
            'input': '#45475a',
            'success': '#a6e3a1',
            'warning': '#f9e2af',
            'error': '#f38ba8'
        }
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._setup_styles()
        
        self.dm = DataManager()
        
        # === TOP BAR (Connection & Data) ===
        self._create_top_bar()
        
        # Main Layout
        self.main_container = ttk.Frame(self.root, style="Main.TFrame")
        self.main_container.pack(fill='both', expand=True)
        
        # Notebook
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.invoice_tab = InvoiceTab(self.notebook, self)
        self.inventory_tab = InventoryTab(self.notebook, self)
        self.history_tab = InvoiceHistoryTab(self.notebook, self)
        self.notebook.add(self.invoice_tab, text="   🧾 INVOICE GENERATOR   ")
        self.notebook.add(self.inventory_tab, text="   👟 INVENTORY & STOCK   ")
        self.notebook.add(self.history_tab, text="   📋 INVOICE HISTORY   ")
        
        # Load config
        self._load_config()

    def _setup_styles(self):
        self.root.configure(bg=self.c['bg'])
        self.style.configure("Main.TFrame", background=self.c['bg'])
        self.style.configure("Card.TFrame", background=self.c['card'])
        self.style.configure("Sidebar.TFrame", background=self.c['sidebar'])
        self.style.configure("Top.TFrame", background=self.c['sidebar'])
        
        self.style.configure("TLabel", background=self.c['card'], foreground=self.c['text'], font=("Segoe UI", 10))
        self.style.configure("Status.TLabel", background=self.c['sidebar'], foreground=self.c['text'], font=("Segoe UI", 9, "bold"))
        self.style.configure("Header.TLabel", background=self.c['bg'], foreground=self.c['accent'], font=("Segoe UI", 18, "bold"))
        self.style.configure("CardTitle.TLabel", background=self.c['card'], foreground=self.c['accent'], font=("Segoe UI", 12, "bold"))
        
        # Notebook
        self.style.configure("TNotebook", background=self.c['bg'], borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.c['card'], foreground=self.c['text'], padding=[20, 10], font=("Segoe UI", 10, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", self.c['accent'])], foreground=[("selected", self.c['bg'])])
        
        # Treeview
        self.style.configure("Treeview", background="#1e1e2e", foreground="#cdd6f4", fieldbackground="#1e1e2e", rowheight=30)
        self.style.configure("Treeview.Heading", background="#313244", foreground="#cdd6f4", font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview", background=[('selected', self.c['accent'])], foreground=[('selected', self.c['bg'])])

    def _create_top_bar(self):
        bar = ttk.Frame(self.root, style="Top.TFrame", padding=(10, 5))
        bar.pack(fill="x")
        
        # App Title
        ttk.Label(bar, text="Sneaker Canvas BD", background=self.c['sidebar'], foreground="white", font=("Segoe UI", 11, "bold")).pack(side="left")
        
        # Right Side Controls
        
        # Import/Export
        tk.Button(bar, text="⬇ Import Data", command=self._import_data, bg=self.c['input'], fg='white', relief='flat').pack(side="right", padx=5)
        tk.Button(bar, text="⬆ Export Data", command=self._export_data, bg=self.c['input'], fg='white', relief='flat').pack(side="right", padx=5)
        
        # Connection Status
        self.status_canvas = tk.Canvas(bar, width=20, height=20, bg=self.c['sidebar'], highlightthickness=0)
        self.status_canvas.pack(side="right", padx=(15, 5))
        self.status_light = self.status_canvas.create_oval(2, 2, 18, 18, fill=self.c['success']) # Default Green
        ttk.Label(bar, text="Database", style="Status.TLabel").pack(side="right")
        
        # Check connection initially
        self.check_connection()

    def check_connection(self):
        connected = self.dm.check_connection()
        color = self.c['success'] if connected else self.c['error']
        self.status_canvas.itemconfig(self.status_light, fill=color)
        
    def _import_data(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            # Ask type
            resp = messagebox.askyesno("Data Type", "Is this an INVENTORY file?\n(Yes=Inventory, No=Invoices)")
            dtype = 'inventory' if resp else 'invoice'
            success, msg = self.dm.import_data(path, dtype)
            if success:
                messagebox.showinfo("Success", msg)
                # Refresh tabs
                self.inventory_tab._refresh()
            else:
                messagebox.showerror("Error", msg)

    def _export_data(self):
        folder = filedialog.askdirectory(title="Select Folder for Backup")
        if folder:
            success, msg = self.dm.export_data(folder)
            if success:
                messagebox.showinfo("Success", f"{msg}\nFiles saved to: {folder}")
            else:
                messagebox.showerror("Error", msg)

    def _load_config(self):
        cfg = self.dm.load_config()
        if cfg.get('output_folder'):
            self.invoice_tab.output_folder = cfg['output_folder']


class InvoiceTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="Main.TFrame")
        self.app = app
        self.c = app.c
        self.products = []
        self.output_folder = ""
        
        self.store_info = {
            'name': 'SNEAKER CANVAS BD',
            'tagline': 'Premium Footwear & Streetwear',
            'address': '80/7, South Saidabad, Dhaka',
            'phone': '01957124591',
            'email': 'sneakercanvasbd@gmail.com'
        }
        self._create_ui()

    # Reuse previous logic with minor updates for config handling
    def _create_ui(self):
        self.paned = tk.PanedWindow(self, orient="horizontal", bg=self.c['bg'], sashwidth=2)
        self.paned.pack(fill="both", expand=True)
        self.left = ttk.Frame(self.paned, style="Main.TFrame")
        self.paned.add(self.left, minsize=600)
        self._create_header_section(self.left)
        self._create_product_section(self.left)
        self.right = ttk.Frame(self.paned, style="Card.TFrame")
        self.paned.add(self.right, minsize=450)
        self._create_preview_section(self.right)

    def _create_header_section(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        card.pack(fill="x", padx=10, pady=10)
        row1 = ttk.Frame(card, style="Card.TFrame"); row1.pack(fill="x", pady=(0, 10))
        ttk.Label(row1, text="INVOICE #", style="Dim.TLabel").pack(side="left")
        self.inv_num = tk.StringVar(); self._generate_next_inv()
        e_inv = tk.Entry(row1, textvariable=self.inv_num, bg=self.c['input'], fg='white', relief='flat', width=18)
        e_inv.pack(side="left", padx=10); e_inv.bind("<Return>", self._load_from_db)
        self.date_entry = DateEntry(row1, width=12, background=self.c['accent'], foreground='white', borderwidth=0, date_pattern='dd/mm/yyyy')
        self.date_entry.pack(side="left", padx=10)
        tk.Button(row1, text="🔄 Reset", command=self._reset_form, bg=self.c['input'], fg='white', relief='flat').pack(side="right")
        ttk.Separator(card, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(card, text="CUSTOMER DETAILS", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))
        row2 = ttk.Frame(card, style="Card.TFrame"); row2.pack(fill="x")
        col1 = ttk.Frame(row2, style="Card.TFrame"); col1.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Label(col1, text="Name", style="Dim.TLabel").pack(anchor="w")
        self.cust_name = tk.StringVar()
        tk.Entry(col1, textvariable=self.cust_name, bg=self.c['input'], fg='white', relief='flat').pack(fill="x", pady=2)
        col2 = ttk.Frame(row2, style="Card.TFrame"); col2.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Label(col2, text="Phone", style="Dim.TLabel").pack(anchor="w")
        self.cust_phone = tk.StringVar()
        tk.Entry(col2, textvariable=self.cust_phone, bg=self.c['input'], fg='white', relief='flat').pack(fill="x", pady=2)
        col3 = ttk.Frame(row2, style="Card.TFrame"); col3.pack(side="left", fill="x", expand=True)
        ttk.Label(col3, text="Address", style="Dim.TLabel").pack(anchor="w")
        self.cust_addr = tk.StringVar()
        tk.Entry(col3, textvariable=self.cust_addr, bg=self.c['input'], fg='white', relief='flat').pack(fill="x", pady=2)
        for v in [self.inv_num, self.cust_name, self.cust_phone, self.cust_addr]: v.trace_add("write", lambda *a: self._calc_totals())
        self.date_entry.bind("<<DateEntrySelected>>", lambda e: self._calc_totals())

    def _create_product_section(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        card.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        head = ttk.Frame(card, style="Card.TFrame"); head.pack(fill="x", pady=(0, 10))
        ttk.Label(head, text="PRODUCTS", style="CardTitle.TLabel").pack(side="left")
        ttk.Button(head, text="+ Add Item", style="Accent.TButton", command=self._add_row).pack(side="right")
        canvas = tk.Canvas(card, bg=self.c['card'], highlightthickness=0)
        scroll = ttk.Scrollbar(card, orient="vertical", command=canvas.yview)
        self.prod_frame = ttk.Frame(canvas, style="Card.TFrame")
        self.prod_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.prod_frame, anchor="nw", width=550)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True); scroll.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self._add_row()

    def _add_row(self, data=None):
        row = ttk.Frame(self.prod_frame, style="Card.TFrame")
        row.pack(fill="x", pady=5)
        v_name = tk.StringVar(value=data['name'] if data else "")
        v_size = tk.StringVar(value=data['size'] if data else "")
        v_price = tk.StringVar(value=str(data['price']) if data else "0")
        v_qty = tk.StringVar(value=str(data['qty']) if data else "1")
        inventory = self.app.dm.get_inventory()
        unique_names = sorted(list(set(i['name'] for i in inventory)))
        cb_name = ttk.Combobox(row, textvariable=v_name, values=unique_names, width=25)
        cb_name.pack(side="left", padx=2)
        cb_size = ttk.Combobox(row, textvariable=v_size, width=8)
        cb_size.pack(side="left", padx=2)
        def on_name_change(e):
            sel = cb_name.get()
            avail = [i for i in inventory if i['name'] == sel]
            sizes = sorted([str(i['size']) for i in avail]) # Fix for int sizes
            cb_size['values'] = sizes
            if sizes: cb_size.set(sizes[0]); on_size_change(None)
        def on_size_change(e):
            n = cb_name.get(); s = cb_size.get()
            item = next((i for i in inventory if i['name'] == n and str(i['size']) == s), None)
            if item: v_price.set(item['price'])
        cb_name.bind("<<ComboboxSelected>>", on_name_change)
        cb_size.bind("<<ComboboxSelected>>", on_size_change)
        tk.Entry(row, textvariable=v_price, width=10, bg=self.c['input'], fg='white', relief='flat').pack(side="left", padx=2)
        tk.Entry(row, textvariable=v_qty, width=5, bg=self.c['input'], fg='white', relief='flat').pack(side="left", padx=2)
        tk.Button(row, text="×", bg=self.c['card'], fg=self.c['accent'], relief="flat", font=("Arial", 12), command=lambda: self._del_row(row)).pack(side="left", padx=5)
        self.products.append({'frame': row, 'name': v_name, 'size': v_size, 'price': v_price, 'qty': v_qty})
        for v in [v_name, v_size, v_price, v_qty]: v.trace_add("write", lambda *a: self._calc_totals())

    def _del_row(self, row):
        if len(self.products) > 1:
            row.destroy()
            self.products = [p for p in self.products if p['frame'] != row]
            self._calc_totals()

    def _create_preview_section(self, parent):
        ttk.Label(parent, text="LIVE PREVIEW", style="CardTitle.TLabel").pack(pady=15)
        
        # Add scrollable canvas for preview
        canvas = tk.Canvas(parent, bg=self.c['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        content = ttk.Frame(canvas, style="Card.TFrame")
        
        content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=content, anchor="nw", width=440)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(15, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 15))
        
        # Make mousewheel work
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Company header
        ttk.Label(content, text=self.store_info['name'], font=("Segoe UI", 14, "bold"), 
                 foreground=self.c['accent']).pack(pady=(10, 2))
        ttk.Label(content, text=self.store_info['tagline'], style="Dim.TLabel", 
                 font=("Segoe UI", 9, "italic")).pack()
        ttk.Label(content, text=self.store_info['address'], style="Dim.TLabel").pack()
        ttk.Label(content, text=f"📞 {self.store_info['phone']}", style="Dim.TLabel").pack()
        ttk.Label(content, text=f"✉ {self.store_info['email']}", style="Dim.TLabel").pack(pady=(0, 10))
        
        ttk.Separator(content, orient="horizontal").pack(fill="x", pady=10, padx=20)
        
        # Invoice info
        self.lbl_inv = ttk.Label(content, text="#SC-...", font=("Consolas", 11, "bold"), 
                                foreground=self.c['accent'])
        self.lbl_inv.pack()
        self.lbl_cust = ttk.Label(content, text="Customer: ...", style="Dim.TLabel", justify="center")
        self.lbl_cust.pack(pady=5)
        
        ttk.Separator(content, orient="horizontal").pack(fill="x", pady=10, padx=20)
        
        # Products section with warning indicator
        prod_header = ttk.Frame(content, style="Card.TFrame")
        prod_header.pack(fill="x", padx=20)
        ttk.Label(prod_header, text="ITEMS:", style="Dim.TLabel", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.stock_warning = ttk.Label(prod_header, text="", foreground=self.c['warning'], font=("Segoe UI", 8))
        self.stock_warning.pack(side="right")
        
        self.lbl_prods = ttk.Label(content, text="...", justify="left", font=("Consolas", 9))
        self.lbl_prods.pack(anchor="w", padx=20, pady=5)
        
        ttk.Separator(content, orient="horizontal").pack(fill="x", pady=10, padx=20)
        
        # Totals section
        total_grid = ttk.Frame(content, style="Card.TFrame")
        total_grid.pack(fill="x", padx=20)
        
        ttk.Label(total_grid, text="Subtotal:", style="Dim.TLabel").grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_sub = ttk.Label(total_grid, text="0 BDT", style="TLabel", font=("Consolas", 10))
        self.lbl_sub.grid(row=0, column=1, sticky="e", pady=2)
        
        ttk.Label(total_grid, text="Discount:", style="Dim.TLabel").grid(row=1, column=0, sticky="w", pady=2)
        self.v_disc = tk.StringVar(value="0")
        tk.Entry(total_grid, textvariable=self.v_disc, width=10, bg=self.c['input'], 
                fg='white', relief='flat', font=("Consolas", 9)).grid(row=1, column=1, sticky="e", pady=2)
        
        ttk.Label(total_grid, text="Delivery:", style="Dim.TLabel").grid(row=2, column=0, sticky="w", pady=2)
        self.v_del = tk.StringVar(value="150")
        tk.Entry(total_grid, textvariable=self.v_del, width=10, bg=self.c['input'], 
                fg='white', relief='flat', font=("Consolas", 9)).grid(row=2, column=1, sticky="e", pady=2)
        
        total_grid.columnconfigure(0, weight=1)
        
        ttk.Separator(content, orient="horizontal").pack(fill="x", pady=10, padx=20)
        
        # Grand total
        self.lbl_total = ttk.Label(content, text="0 BDT", foreground=self.c['accent'], 
                                  font=("Segoe UI", 16, "bold"))
        self.lbl_total.pack(pady=5)
        
        # Payment method
        pay_frame = ttk.Frame(content, style="Card.TFrame")
        pay_frame.pack(pady=10)
        self.v_pay = tk.StringVar(value="bKash")
        self.v_trx = tk.StringVar()
        ttk.Radiobutton(pay_frame, text="💳 bKash", variable=self.v_pay, value="bKash", 
                       command=self._toggle_trx).pack(side="left", padx=5)
        ttk.Radiobutton(pay_frame, text="💵 COD", variable=self.v_pay, value="Cash on Delivery", 
                       command=self._toggle_trx).pack(side="left", padx=5)
        
        self.e_trx = tk.Entry(content, textvariable=self.v_trx, bg=self.c['input'], fg='white', 
                             relief='flat', width=20)
        self.e_trx.pack(pady=5)
        
        self.v_disc.trace_add("write", lambda *a: self._calc_totals())
        self.v_del.trace_add("write", lambda *a: self._calc_totals())
        
        # Set Output Folder Button
        tk.Button(parent, text="📂 Set Output Folder", command=self._set_output, 
                 bg=self.c['input'], fg='white', relief='flat').pack(fill="x", padx=15, pady=5)
        
        tk.Button(parent, text="GENERATE PDF", command=self._generate, 
                 bg=self.c['accent'], fg=self.c['sidebar'], font=("Segoe UI", 12, "bold"), 
                 relief="flat", pady=10).pack(side="bottom", fill="x", padx=15, pady=15)

    def _toggle_trx(self):
        if self.v_pay.get() == "bKash": self.e_trx.pack(pady=5)
        else: self.e_trx.pack_forget()

    def _calc_totals(self):
        sub = 0; txt = ""; stock_warnings = []
        for p in self.products:
            try:
                n = p['name'].get(); s = p['size'].get(); q = int(p['qty'].get()); pr = float(p['price'].get())
                t = q * pr; sub += t
                if n:
                    # Check stock availability
                    available, current_stock = self.app.dm.check_stock_availability(n, s, q)
                    stock_icon = "⚠️ " if not available else ""
                    txt += f"{stock_icon}{n} (Size {s}) x{q}  →  {t:,.0f} BDT\n"
                    if not available:
                        stock_warnings.append(f"{n} Size {s}")
            except: pass
        
        # Update stock warning label
        if stock_warnings:
            self.stock_warning.config(text=f"⚠️ Low stock: {len(stock_warnings)} item(s)")
        else:
            self.stock_warning.config(text="✓ Stock OK")
        
        try: d = float(self.v_disc.get())
        except: d = 0
        try: l = float(self.v_del.get())
        except: l = 0
        gt = sub - d + l
        self.lbl_sub.config(text=f"{sub:,.0f} BDT")
        self.lbl_total.config(text=f"{gt:,.0f} BDT")
        self.lbl_prods.config(text=txt if txt else "No items added yet...")
        self.lbl_inv.config(text=f"{self.inv_num.get()}  |  📅 {self.date_entry.get()}")
        self.lbl_cust.config(text=f"{self.cust_name.get() or 'Customer Name'}\n{self.cust_phone.get() or 'Phone'}\n{self.cust_addr.get() or 'Address'}")

    def _generate_next_inv(self): self.inv_num.set(self.app.dm.get_next_invoice_number())
    def _reset_form(self):
        self._generate_next_inv()
        self.cust_name.set(""); self.cust_phone.set(""); self.cust_addr.set("")
        for p in self.products: p['frame'].destroy()
        self.products = []; self._add_row(); self._calc_totals()

    def _load_from_db(self, e=None):
        data = self.app.dm.get_invoice(self.inv_num.get())
        if data:
            self.cust_name.set(data['customer_name']); self.cust_phone.set(data['customer_phone']); self.cust_addr.set(data['customer_address'])
            self.date_entry.set_date(data['date'])
            self.v_disc.set(data['discount']); self.v_del.set(data['delivery'])
            for p in self.products: p['frame'].destroy()
            self.products = []
            for item in data['products']: self._add_row(item)
            if not data['products']: self._add_row()
            messagebox.showinfo("Loaded", "Invoice loaded!")

    def _set_output(self):
        f = filedialog.askdirectory()
        if f:
            self.output_folder = f
            self.app.dm.save_config("output_folder", f)
            messagebox.showinfo("Saved", f"Output folder set to: {f}")

    def _generate(self):
        prods = []
        for p in self.products:
            try: prods.append({'name': p['name'].get(), 'description': '', 'size': p['size'].get(), 'qty': int(p['qty'].get()), 'price': float(p['price'].get())})
            except: pass
        
        # Validate stock availability before generating invoice
        stock_issues = []
        for prod in prods:
            available, current_stock = self.app.dm.check_stock_availability(
                prod['name'], prod['size'], prod['qty']
            )
            if not available:
                stock_issues.append(
                    f"{prod['name']} (Size {prod['size']}): Need {prod['qty']}, Available: {current_stock}"
                )
        
        if stock_issues:
            msg = "Insufficient stock for the following items:\n\n" + "\n".join(stock_issues)
            msg += "\n\nDo you want to continue anyway?"
            if not messagebox.askyesno("Stock Warning", msg):
                return
        
        data = {
            'invoice_number': self.inv_num.get(), 'date': self.date_entry.get(),
            'customer_name': self.cust_name.get(), 'customer_phone': self.cust_phone.get(), 'customer_address': self.cust_addr.get(),
            'products': prods, 'subtotal': self.lbl_sub.cget("text"),
            'discount': float(self.v_disc.get() or 0), 'delivery': float(self.v_del.get() or 0),
            'grand_total': float(self.lbl_total.cget("text").replace(" BDT","").replace(",","")),
            'payment_method': self.v_pay.get(), 'transaction_id': self.v_trx.get() if self.v_pay.get() == 'bKash' else '',
            'company_name': self.store_info['name'], 'company_tagline': self.store_info['tagline'],
            'company_address': self.store_info['address'], 'company_phone': self.store_info['phone'], 'company_email': self.store_info['email'],
            'logo_path': DEFAULT_LOGO, 'signature_path': DEFAULT_SIGN
        }
        self.app.dm.save_invoice(data)
        folder = self.output_folder if self.output_folder else SCRIPT_DIR
        path = os.path.join(folder, f"Invoice_{data['invoice_number'].replace('#','').replace('-','_')}.pdf")
        try:
            gen = InvoiceGenerator(path)
            gen.generate(data)
            
            # Reduce inventory after successful generation
            print("\n=== Starting Inventory Reduction ===")
            for prod in prods:
                print(f"Reducing: {prod['name']} Size {prod['size']} Qty: {prod['qty']}")
                success, new_stock = self.app.dm.reduce_stock(
                    prod['name'], prod['size'], prod['qty']
                )
                if success:
                    print(f"  ✓ Success! New stock = {new_stock}")
                else:
                    print(f"  ✗ Failed to reduce stock!")
            print("=== Inventory Reduction Complete ===\n")
            
            # Refresh inventory tab if it exists
            if hasattr(self.app, 'inventory_tab'):
                print("Refreshing inventory tab...")
                self.app.inventory_tab._refresh()
                print("Inventory tab refreshed!")
            
            # Refresh history tab if it exists
            if hasattr(self.app, 'history_tab'):
                self.app.history_tab._refresh()
            
            os.startfile(path)
            messagebox.showinfo("Success", f"Invoice generated and inventory updated!\n\nSaved to: {path}")
        except Exception as e: 
            print(f"ERROR in _generate: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", str(e))



class InventoryTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="Main.TFrame")
        self.app = app
        self.c = app.c
        self.view_mode = tk.StringVar(value="grouped")  # "grouped" or "individual"
        self._create_ui()
        
    def _create_ui(self):
        row = ttk.Frame(self, style="Main.TFrame")
        row.pack(fill="both", expand=True, padx=20, pady=20)
        
        # --- LEFT (Form) ---
        left = ttk.Frame(row, style="Card.TFrame", padding=20)
        left.pack(side="left", fill="y", padx=(0, 20))
        
        ttk.Label(left, text="MANAGE ITEM", style="CardTitle.TLabel").pack(pady=(0, 20))
        
        # Name
        ttk.Label(left, text="Product Name", style="Dim.TLabel").pack(anchor="w")
        self.name = tk.StringVar()
        tk.Entry(left, textvariable=self.name, bg=self.c['input'], fg='white', relief='flat').pack(fill="x", pady=(5, 15))
        
        # Description
        ttk.Label(left, text="Description", style="Dim.TLabel").pack(anchor="w")
        self.desc = tk.StringVar()
        tk.Entry(left, textvariable=self.desc, bg=self.c['input'], fg='white', relief='flat').pack(fill="x", pady=(5, 15))
        
        # Price
        ttk.Label(left, text="Price", style="Dim.TLabel").pack(anchor="w")
        self.price = tk.StringVar()
        tk.Entry(left, textvariable=self.price, bg=self.c['input'], fg='white', relief='flat').pack(fill="x", pady=(5, 15))
        
        # Size Grid
        ttk.Label(left, text="Stock per Size:", style="Dim.TLabel").pack(anchor="w", pady=(5, 10))
        matrix_frame = ttk.Frame(left, style="Card.TFrame")
        matrix_frame.pack()
        self.size_vars = {}
        sizes = range(36, 46)
        r, c = 0, 0
        for s in sizes:
            f = ttk.Frame(matrix_frame, style="Card.TFrame")
            f.grid(row=r, column=c, padx=5, pady=5)
            ttk.Label(f, text=str(s), width=3, anchor="center").pack()
            v = tk.StringVar(value="0")
            self.size_vars[s] = v
            tk.Entry(f, textvariable=v, width=5, bg=self.c['input'], fg='white', justify='center', relief='flat').pack()
            c += 1
            if c > 2: c = 0; r += 1
            
        tk.Button(left, text="SAVE / UPDATE", command=self._save, bg=self.c['success'], fg=self.c['sidebar'], font=("Segoe UI", 10, "bold"), relief="flat", pady=10).pack(fill="x", pady=20)
        
        # --- RIGHT (Table) ---
        right = ttk.Frame(row, style="Main.TFrame")
        right.pack(side="right", fill="both", expand=True)
        
        # Header with view mode toggle
        header_frame = ttk.Frame(right, style="Main.TFrame")
        header_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(header_frame, text="CURRENT STOCK", style="Header.TLabel").pack(side="left")
        
        # View mode buttons
        view_toggle = ttk.Frame(header_frame, style="Main.TFrame")
        view_toggle.pack(side="right")
        tk.Button(view_toggle, text="👥 Grouped View", 
                 command=lambda: self._switch_view("grouped"),
                 bg=self.c['accent'], fg='white', relief='flat', padx=10).pack(side="left", padx=2)
        tk.Button(view_toggle, text="📋 Individual View", 
                 command=lambda: self._switch_view("individual"),
                 bg=self.c['card'], fg='white', relief='flat', padx=10).pack(side="left", padx=2)
        
        self.tree = ttk.Treeview(right, columns=("Name", "Desc", "Price", "Sizes", "Total Stock"), show="headings")
        self.tree.heading("Name", text="Product Name"); self.tree.heading("Desc", text="Description")
        self.tree.heading("Price", text="Price"); self.tree.heading("Sizes", text="Sizes Available"); 
        self.tree.heading("Total Stock", text="Total Stock")
        self.tree.column("Sizes", width=200); self.tree.column("Total Stock", width=80, anchor="center")
        self.tree.column("Price", width=80); self.tree.column("Desc", width=150)
        self.tree.pack(fill="both", expand=True)
        
        # Controls
        ctrl = ttk.Frame(right, style="Main.TFrame")
        ctrl.pack(fill="x", pady=10)
        tk.Button(ctrl, text="REFRESH", command=self._refresh, bg=self.c['card'], fg='white', relief='flat').pack(side="left", padx=5)
        self.btn_del = tk.Button(ctrl, text="DELETE SELECTED", command=self._delete, bg=self.c['error'], fg=self.c['sidebar'], relief='flat')
        self.btn_del.pack(side="right", padx=5)
        
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self._refresh()
        
    def _save(self):
        n = self.name.get(); p = self.price.get(); d = self.desc.get()
        if not n or not p: return
        try:
            updates = 0
            for s, v in self.size_vars.items():
                stock = int(v.get() or 0)
                if stock > 0: # Only save if stock > 0 or it's an update? Logic is simple for now: add if > 0
                    self.app.dm.add_product({'name': n, 'description': d, 'price': float(p), 'size': str(s), 'stock': stock})
                    updates += 1
            if updates:
                self._refresh()
                messagebox.showinfo("Success", f"Updated {updates} size variants.")
            else: messagebox.showwarning("Notice", "No stock quantities entered.")
        except Exception as e: messagebox.showerror("Error", str(e))


    def _switch_view(self, mode):
        """Switch between grouped and individual view modes"""
        self.view_mode.set(mode)
        self._refresh()
    
    def _refresh(self):
        """Refresh the inventory display based on current view mode"""
        for i in self.tree.get_children(): 
            self.tree.delete(i)
        
        inventory = self.app.dm.get_inventory()
        
        if self.view_mode.get() == "grouped":
            # Group products by name
            grouped = {}
            for item in inventory:
                name = item['name']
                if name not in grouped:
                    grouped[name] = {
                        'description': item['description'],
                        'price': item['price'],
                        'sizes': {},
                        'total_stock': 0
                    }
                grouped[name]['sizes'][str(item['size'])] = item['stock']
                grouped[name]['total_stock'] += item['stock']
            
            # Display grouped data
            for name, data in sorted(grouped.items()):
                # Format sizes as "36:2, 37:3, 38:4..."
                size_str = ", ".join([f"{s}:{q}" for s, q in sorted(data['sizes'].items(), key=lambda x: int(x[0]))])
                self.tree.insert("", "end", values=(
                    name, 
                    data['description'], 
                    f"{data['price']:.0f} BDT",
                    size_str,
                    data['total_stock']
                ))
        else:
            # Individual view - show each size separately
            for item in inventory:
                self.tree.insert("", "end", values=(
                    item['name'], 
                    item['description'], 
                    f"{item['price']:.0f} BDT",
                    f"Size {item['size']}",
                    item['stock']
                ))

    def _on_select(self, e):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])['values']
        
        if self.view_mode.get() == "grouped":
            # In grouped view, load all size data for this product
            self.name.set(item[0])
            self.desc.set(item[1])
            # Remove " BDT" from price
            price_str = str(item[2]).replace(" BDT", "")
            self.price.set(price_str)
            
            # Clear all sizes first
            for v in self.size_vars.values(): 
                v.set("0")
            
            # Load all sizes for this product from inventory
            inventory = self.app.dm.get_inventory()
            for inv_item in inventory:
                if inv_item['name'] == item[0]:
                    size = int(inv_item['size'])
                    if size in self.size_vars:
                        self.size_vars[size].set(str(inv_item['stock']))
        else:
            # Individual view - same as before
            self.name.set(item[0])
            self.desc.set(item[1])
            price_str = str(item[2]).replace(" BDT", "")
            self.price.set(price_str)
            
            # Clear sizes first
            for v in self.size_vars.values(): 
                v.set("0")
            
            # Extract size from "Size XX" format
            size_text = str(item[3])
            if "Size " in size_text:
                size = int(size_text.replace("Size ", ""))
                stock = item[4]
                if size in self.size_vars:
                    self.size_vars[size].set(str(stock))

    def _delete(self):
        sel = self.tree.selection()
        if not sel: 
            messagebox.showwarning("No Selection", "Please select an item to delete.")
            return
        
        try:
            if self.view_mode.get() == "grouped":
                # In grouped view, ask to delete all sizes of this product
                item = self.tree.item(sel[0])['values']
                product_name = item[0]
                if messagebox.askyesno("Confirm", f"Delete all sizes of '{product_name}'?"):
                    inventory = self.app.dm.get_inventory()
                    deleted_count = 0
                    for inv_item in inventory:
                        if inv_item['name'] == product_name:
                            if self.app.dm.delete_product(inv_item['name'], inv_item['size']):
                                deleted_count += 1
                    self._refresh()
                    messagebox.showinfo("Success", f"Deleted {deleted_count} size variants of '{product_name}'")
            else:
                # Individual view - delete specific size
                if messagebox.askyesno("Confirm", "Delete selected item?"):
                    item = self.tree.item(sel[0])['values']
                    product_name = item[0]
                    # Extract size from "Size XX" format
                    size_text = str(item[3])
                    if "Size " in size_text:
                        size = size_text.replace("Size ", "")
                        if self.app.dm.delete_product(product_name, size):
                            self._refresh()
                            messagebox.showinfo("Success", f"Deleted {product_name} Size {size}")
                        else:
                            messagebox.showerror("Error", "Failed to delete item")
                    else:
                        messagebox.showerror("Error", f"Invalid size format: {size_text}")
        except Exception as e:
            messagebox.showerror("Error", f"Delete operation failed: {str(e)}")

class InvoiceHistoryTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="Main.TFrame")
        self.parent = parent  # Store parent for Toplevel windows
        self.app = app
        self.c = app.c
        
        # Main container (self) is the container now
        # We can pack widgets directly into self
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Use self instead of creating a new main frame
        main = self
        
        # Header with search
        header = ttk.Frame(main, style="Main.TFrame")
        header.pack(fill="x", pady=(0, 15))
        
        ttk.Label(header, text="📋 INVOICE HISTORY", style="Header.TLabel").pack(side="left")
        
        # Search frame
        search_frame = ttk.Frame(header, style="Main.TFrame")
        search_frame.pack(side="right")
        
        ttk.Label(search_frame, text="Search:", style="Label.TLabel").pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._filter_invoices())
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg=self.c['card'],
            fg='white',
            insertbackground='white',
            bd=0,
            font=("Segoe UI", 10),
            width=30
        )
        search_entry.pack(side="left", ipady=5, padx=5)
        
        # Table frame
        table_frame = ttk.Frame(main, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        
        # Treeview
        self.tree = ttk.Treeview(
            table_frame,
            columns=("Invoice #", "Date", "Customer", "Phone", "Total", "Payment"),
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )
        
        # Configure scrollbars
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        # Column headings
        self.tree.heading("Invoice #", text="Invoice #")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Customer", text="Customer Name")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Total", text="Total (BDT)")
        self.tree.heading("Payment", text="Payment Method")
        
        # Column widths
        self.tree.column("Invoice #", width=150, anchor="w")
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Customer", width=200, anchor="w")
        self.tree.column("Phone", width=120, anchor="w")
        self.tree.column("Total", width=120, anchor="e")
        self.tree.column("Payment", width=120, anchor="center")
        
        # Pack tree and scrollbars
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        
        # Double-click to view details
        self.tree.bind("<Double-Button-1>", lambda e: self._view_details())
        
        # Action buttons
        btn_frame = ttk.Frame(main, style="Main.TFrame")
        btn_frame.pack(fill="x")
        
        tk.Button(
            btn_frame, text="👁 View Details", 
            command=self._view_details,
            bg=self.c['accent'], fg='white', relief='flat', padx=15, font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 10))
        
        tk.Button(
            btn_frame, text="✏ Edit", 
            command=self._edit_invoice,
            bg=self.c['success'], fg='white', relief='flat', padx=15, font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 10))
        
        tk.Button(
            btn_frame, text="🗑 Delete", 
            command=self._delete_invoice,
            bg=self.c['error'], fg='white', relief='flat', padx=15, font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 10))
        
        tk.Button(
            btn_frame, text="🔄 Regenerate PDF", 
            command=self._regenerate_pdf,
            bg=self.c['warning'], fg='white', relief='flat', padx=15, font=("Segoe UI", 10, "bold")
        ).pack(side="left")
        
        # Load invoices
        self._refresh()
    
    
    def _parse_val(self, val):
        """Parse currency string to float"""
        if isinstance(val, (int, float)):
            return float(val)
        if hasattr(val, 'replace'):
            return float(val.replace(',', '').replace(' BDT', '').strip() or 0)
        return 0.0

    def _refresh(self):
        """Refresh invoice list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load all invoices
        invoices = self.app.dm.get_all_invoices()
        print(f"DEBUG: Loaded {len(invoices)} invoices: {[i.get('invoice_number') for i in invoices]}")
        
        for inv in invoices:
            total = self._parse_val(inv.get('grand_total', 0))
            self.tree.insert("", "end", values=(
                inv.get('invoice_number', ''),
                inv.get('date', ''),
                inv.get('customer_name', ''),
                inv.get('customer_phone', ''),
                f"{total:,.0f}",
                inv.get('payment_method', '')
            ))
    
    def _filter_invoices(self):
        """Filter invoices based on search query"""
        query = self.search_var.get().strip()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not query:
            self._refresh()
            return
        
        # Search invoices
        invoices = self.app.dm.search_invoices(query)
        
        for inv in invoices:
            total = self._parse_val(inv.get('grand_total', 0))
            self.tree.insert("", "end", values=(
                inv.get('invoice_number', ''),
                inv.get('date', ''),
                inv.get('customer_name', ''),
                inv.get('customer_phone', ''),
                f"{total:,.0f}",
                inv.get('payment_method', '')
            ))
    
    def _view_details(self):
        """View invoice details in a popup"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an invoice to view.")
            return
        
        invoice_number = self.tree.item(sel[0])['values'][0]
        invoice_data = self.app.dm.get_invoice(invoice_number)
        
        if not invoice_data:
            messagebox.showerror("Error", "Invoice not found!")
            return
        
        # Create details window
        details_win = tk.Toplevel(self.parent)
        details_win.title(f"Invoice Details - {invoice_number}")
        details_win.geometry("600x700")
        details_win.configure(bg=self.c['bg'])
        
        # Main frame with scrollbar
        canvas = tk.Canvas(details_win, bg=self.c['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(details_win, orient="vertical", command=canvas.yview)
        content = ttk.Frame(canvas, style="Main.TFrame")
        
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Invoice details
        ttk.Label(content, text=f"Invoice: {invoice_number}", style="Header.TLabel").pack(anchor="w", pady=(0, 10))
        ttk.Label(content, text=f"Date: {invoice_data.get('date', '')}", style="Label.TLabel").pack(anchor="w")
        ttk.Label(content, text=f"Customer: {invoice_data.get('customer_name', '')}", style="Label.TLabel").pack(anchor="w")
        ttk.Label(content, text=f"Phone: {invoice_data.get('customer_phone', '')}", style="Label.TLabel").pack(anchor="w")
        ttk.Label(content, text=f"Address: {invoice_data.get('customer_address', '')}", style="Label.TLabel").pack(anchor="w", pady=(0, 15))
        
        # Products
        ttk.Label(content, text="Products:", style="Header.TLabel").pack(anchor="w", pady=(10, 5))
        for prod in invoice_data.get('products', []):
            try:
                price = self._parse_val(prod.get('price', 0))
                qty = int(prod.get('qty', 0))
                total_price = price * qty
                prod_text = f"• {prod.get('name', '')} (Size {prod.get('size', '')}) x{qty} = {total_price:,.0f} BDT"
            except:
                prod_text = f"• {prod.get('name', '')} (Size {prod.get('size', '')}) x{prod.get('qty', '')}"
            ttk.Label(content, text=prod_text, style="Label.TLabel").pack(anchor="w", padx=(10, 0))
        
        # Totals
        subtotal = self._parse_val(invoice_data.get('subtotal', 0))
        discount = self._parse_val(invoice_data.get('discount', 0))
        delivery = self._parse_val(invoice_data.get('delivery', 0))
        grand_total = self._parse_val(invoice_data.get('grand_total', 0))
        
        ttk.Label(content, text=f"\nSubtotal: {subtotal:,.0f} BDT", style="Label.TLabel").pack(anchor="w", pady=(15, 0))
        ttk.Label(content, text=f"Discount: {discount:,.0f} BDT", style="Label.TLabel").pack(anchor="w")
        ttk.Label(content, text=f"Delivery: {delivery:,.0f} BDT", style="Label.TLabel").pack(anchor="w")
        ttk.Label(content, text=f"Grand Total: {grand_total:,.0f} BDT", style="Header.TLabel").pack(anchor="w", pady=(5, 15))
        
        ttk.Label(content, text=f"Payment Method: {invoice_data.get('payment_method', '')}", style="Label.TLabel").pack(anchor="w")
        if invoice_data.get('transaction_id'):
            ttk.Label(content, text=f"Transaction ID: {invoice_data.get('transaction_id', '')}", style="Label.TLabel").pack(anchor="w")
    
    def _edit_invoice(self):
        """Edit selected invoice (to be implemented with edit dialog)"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an invoice to edit.")
            return
        
        messagebox.showinfo("Coming Soon", "Edit functionality will open a dialog to modify invoice details and auto-regenerate the PDF.")
    
    def _delete_invoice(self):
        """Delete selected invoice"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an invoice to delete.")
            return
        
        invoice_number = self.tree.item(sel[0])['values'][0]
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete invoice {invoice_number}?\\n\\nThis action cannot be undone."):
            return
        
        deleted_data = self.app.dm.delete_invoice(invoice_number)
        if deleted_data:
            self._refresh()
            messagebox.showinfo("Success", f"Invoice {invoice_number} has been deleted.")
        else:
            messagebox.showerror("Error", "Failed to delete invoice.")
    
    def _regenerate_pdf(self):
        """Regenerate PDF for selected invoice"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an invoice to regenerate.")
            return
        
        invoice_number = self.tree.item(sel[0])['values'][0]
        invoice_data = self.app.dm.get_invoice(invoice_number)
        
        if not invoice_data:
            messagebox.showerror("Error", "Invoice data not found!")
            return
        
        try:
            # Generate PDF
            folder = self.app.dm.get_config('output_folder', SCRIPT_DIR)
            path = os.path.join(folder, f"Invoice_{invoice_number.replace('#','').replace('-','_')}.pdf")
            
            gen = InvoiceGenerator(path)
            gen.generate(invoice_data)
            
            messagebox.showinfo("Success", f"PDF regenerated successfully!\\n\\nSaved to: {path}")
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to regenerate PDF: {str(e)}")


def main():
    root = tk.Tk()
    root.withdraw()  # Hide main window while loading
    
    # Show loading screen
    splash = LoadingScreen(root)
    splash.next_stage()  # "Initializing application..."
    time.sleep(0.3)
    
    splash.next_stage()  # "Loading invoice database..."
    time.sleep(0.3)
    
    splash.next_stage()  # "Loading inventory..."
    time.sleep(0.3)
    
    splash.next_stage()  # "Setting up interface..."
    app = MainApp(root)
    time.sleep(0.3)
    
    splash.next_stage()  # "Almost ready..."
    time.sleep(0.2)
    
    # Close splash and show main window
    splash.close()
    root.deiconify()
    root.mainloop()

if __name__ == "__main__":
    main()
