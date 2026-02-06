# Invoice History Tab Implementation

import tkinter as tk
from tkinter import ttk, messagebox
import os
from invoice_generator import InvoiceGenerator

# Get script directory for PDF path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class InvoiceHistoryTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.c = app.c
        
        # Main container
        main = ttk.Frame(parent, style="Main.TFrame")
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
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
            bg=self.c['danger'], fg='white', relief='flat', padx=15, font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 10))
        
        tk.Button(
            btn_frame, text="🔄 Regenerate PDF", 
            command=self._regenerate_pdf,
            bg=self.c['warning'], fg='white', relief='flat', padx=15, font=("Segoe UI", 10, "bold")
        ).pack(side="left")
        
        # Load invoices
        self._refresh()
    
    def _refresh(self):
        """Refresh invoice list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load all invoices
        invoices = self.app.dm.get_all_invoices()
        
        for inv in invoices:
            self.tree.insert("", "end", values=(
                inv.get('invoice_number', ''),
                inv.get('date', ''),
                inv.get('customer_name', ''),
                inv.get('customer_phone', ''),
                f"{float(inv.get('grand_total', 0)):,.0f}",
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
            self.tree.insert("", "end", values=(
                inv.get('invoice_number', ''),
                inv.get('date', ''),
                inv.get('customer_name', ''),
                inv.get('customer_phone', ''),
                f"{float(inv.get('grand_total', 0)):,.0f}",
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
            prod_text = f"• {prod.get('name', '')} (Size {prod.get('size', '')}) x{prod.get('qty', 0)} = {float(prod.get('price', 0)) * int(prod.get('qty', 0)):,.0f} BDT"
            ttk.Label(content, text=prod_text, style="Label.TLabel").pack(anchor="w", padx=(10, 0))
        
        # Totals
        ttk.Label(content, text=f"\nSubtotal: {float(invoice_data.get('subtotal', 0)):,.0f} BDT", style="Label.TLabel").pack(anchor="w", pady=(15, 0))
        ttk.Label(content, text=f"Discount: {float(invoice_data.get('discount', 0)):,.0f} BDT", style="Label.TLabel").pack(anchor="w")
        ttk.Label(content, text=f"Delivery: {float(invoice_data.get('delivery', 0)):,.0f} BDT", style="Label.TLabel").pack(anchor="w")
        ttk.Label(content, text=f"Grand Total: {float(invoice_data.get('grand_total', 0)):,.0f} BDT", style="Header.TLabel").pack(anchor="w", pady=(5, 15))
        
        ttk.Label(content, text=f"Payment Method: {invoice_data.get('payment_method', '')}", style="Label.TLabel").pack(anchor="w")
        if invoice_data.get('transaction_id'):
            ttk.Label(content, text=f"Transaction ID: {invoice_data.get('transaction_id', '')}", style="Label.TLabel").pack(anchor="w")
    
    def _edit_invoice(self):
        """Edit selected invoice with a dialog"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an invoice to edit.")
            return
        
        invoice_number = self.tree.item(sel[0])['values'][0]
        invoice_data = self.app.dm.get_invoice(invoice_number)
        
        if not invoice_data:
            messagebox.showerror("Error", "Invoice data not found!")
            return
        
        # Create edit dialog
        edit_win = tk.Toplevel(self.parent)
        edit_win.title(f"Edit Invoice - {invoice_number}")
        edit_win.geometry("700x800")
        edit_win.configure(bg=self.c['bg'])
        edit_win.transient(self.parent)
        edit_win.grab_set()
        
        # Main scrollable frame
        canvas = tk.Canvas(edit_win, bg=self.c['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(edit_win, orient="vertical", command=canvas.yview)
        content = ttk.Frame(canvas, style="Main.TFrame")
        
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Header
        ttk.Label(content, text=f"✏️ EDIT INVOICE: {invoice_number}", style="Header.TLabel").pack(anchor="w", pady=(0, 20))
        
        # Customer Info Section
        cust_frame = tk.Frame(content, bg=self.c['card'], padx=15, pady=15)
        cust_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(cust_frame, text="CUSTOMER INFO", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Customer Name
        ttk.Label(cust_frame, text="Name:", style="Label.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        name_var = tk.StringVar(value=invoice_data.get('customer_name', ''))
        tk.Entry(cust_frame, textvariable=name_var, bg=self.c['input'], fg='white', insertbackground='white', font=("Segoe UI", 10), width=40).grid(row=1, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Phone
        ttk.Label(cust_frame, text="Phone:", style="Label.TLabel").grid(row=2, column=0, sticky="w", pady=5)
        phone_var = tk.StringVar(value=invoice_data.get('customer_phone', ''))
        tk.Entry(cust_frame, textvariable=phone_var, bg=self.c['input'], fg='white', insertbackground='white', font=("Segoe UI", 10), width=40).grid(row=2, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Address
        ttk.Label(cust_frame, text="Address:", style="Label.TLabel").grid(row=3, column=0, sticky="w", pady=5)
        addr_var = tk.StringVar(value=invoice_data.get('customer_address', ''))
        tk.Entry(cust_frame, textvariable=addr_var, bg=self.c['input'], fg='white', insertbackground='white', font=("Segoe UI", 10), width=40).grid(row=3, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Products Section
        prod_frame = tk.Frame(content, bg=self.c['card'], padx=15, pady=15)
        prod_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(prod_frame, text="PRODUCTS", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))
        
        # Product entries list
        product_entries = []
        products = invoice_data.get('products', [])
        
        for i, prod in enumerate(products):
            prod_row = tk.Frame(prod_frame, bg=self.c['card'])
            prod_row.pack(fill="x", pady=5)
            
            # Name
            ttk.Label(prod_row, text="Name:", style="Label.TLabel").pack(side="left")
            name_e = tk.Entry(prod_row, bg=self.c['input'], fg='white', insertbackground='white', font=("Segoe UI", 10), width=20)
            name_e.insert(0, prod.get('name', ''))
            name_e.pack(side="left", padx=(5, 10))
            
            # Size
            ttk.Label(prod_row, text="Size:", style="Label.TLabel").pack(side="left")
            size_e = tk.Entry(prod_row, bg=self.c['input'], fg='white', insertbackground='white', font=("Segoe UI", 10), width=6)
            size_e.insert(0, prod.get('size', ''))
            size_e.pack(side="left", padx=(5, 10))
            
            # Qty
            ttk.Label(prod_row, text="Qty:", style="Label.TLabel").pack(side="left")
            qty_e = tk.Entry(prod_row, bg=self.c['input'], fg='white', insertbackground='white', font=("Segoe UI", 10), width=5)
            qty_e.insert(0, str(prod.get('qty', 1)))
            qty_e.pack(side="left", padx=(5, 10))
            
            # Price
            ttk.Label(prod_row, text="Price:", style="Label.TLabel").pack(side="left")
            price_e = tk.Entry(prod_row, bg=self.c['input'], fg='white', insertbackground='white', font=("Segoe UI", 10), width=10)
            price_e.insert(0, str(prod.get('price', 0)))
            price_e.pack(side="left", padx=(5, 0))
            
            product_entries.append({'name': name_e, 'size': size_e, 'qty': qty_e, 'price': price_e})
        
        # Amounts Section
        amt_frame = tk.Frame(content, bg=self.c['card'], padx=15, pady=15)
        amt_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(amt_frame, text="AMOUNTS", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Discount
        ttk.Label(amt_frame, text="Discount:", style="Label.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        discount_var = tk.StringVar(value=str(invoice_data.get('discount', 0)))
        tk.Entry(amt_frame, textvariable=discount_var, bg=self.c['input'], fg='white', insertbackground='white', font=("Segoe UI", 10), width=15).grid(row=1, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Delivery
        ttk.Label(amt_frame, text="Delivery:", style="Label.TLabel").grid(row=2, column=0, sticky="w", pady=5)
        delivery_var = tk.StringVar(value=str(invoice_data.get('delivery', 0)))
        tk.Entry(amt_frame, textvariable=delivery_var, bg=self.c['input'], fg='white', insertbackground='white', font=("Segoe UI", 10), width=15).grid(row=2, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Payment Section
        pay_frame = tk.Frame(content, bg=self.c['card'], padx=15, pady=15)
        pay_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(pay_frame, text="PAYMENT", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Payment Method
        ttk.Label(pay_frame, text="Method:", style="Label.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        payment_var = tk.StringVar(value=invoice_data.get('payment_method', 'Cash'))
        payment_combo = ttk.Combobox(pay_frame, textvariable=payment_var, values=["Cash", "bKash", "Nagad", "Card"], state="readonly", width=15)
        payment_combo.grid(row=1, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Transaction ID
        ttk.Label(pay_frame, text="Transaction ID:", style="Label.TLabel").grid(row=2, column=0, sticky="w", pady=5)
        trans_var = tk.StringVar(value=invoice_data.get('transaction_id', ''))
        tk.Entry(pay_frame, textvariable=trans_var, bg=self.c['input'], fg='white', insertbackground='white', font=("Segoe UI", 10), width=25).grid(row=2, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Buttons
        btn_frame = tk.Frame(content, bg=self.c['bg'])
        btn_frame.pack(fill="x", pady=(20, 0))
        
        def save_changes():
            try:
                # Collect product data
                updated_products = []
                subtotal = 0
                for pe in product_entries:
                    name = pe['name'].get().strip()
                    if not name:
                        continue
                    size = pe['size'].get().strip()
                    qty = int(pe['qty'].get() or 1)
                    price = float(pe['price'].get() or 0)
                    updated_products.append({
                        'name': name,
                        'size': size,
                        'qty': qty,
                        'price': price
                    })
                    subtotal += qty * price
                
                discount = float(discount_var.get() or 0)
                delivery = float(delivery_var.get() or 0)
                grand_total = subtotal - discount + delivery
                
                # Update invoice data
                updated_data = {
                    'invoice_number': invoice_number,
                    'date': invoice_data.get('date', ''),
                    'customer_name': name_var.get(),
                    'customer_phone': phone_var.get(),
                    'customer_address': addr_var.get(),
                    'subtotal': subtotal,
                    'discount': discount,
                    'delivery': delivery,
                    'grand_total': grand_total,
                    'payment_method': payment_var.get(),
                    'transaction_id': trans_var.get(),
                    'products': updated_products
                }
                
                # Save to data manager
                success = self.app.dm.update_invoice(invoice_number, {
                    'customer_name': updated_data['customer_name'],
                    'customer_phone': updated_data['customer_phone'],
                    'customer_address': updated_data['customer_address'],
                    'subtotal': updated_data['subtotal'],
                    'discount': updated_data['discount'],
                    'delivery': updated_data['delivery'],
                    'grand_total': updated_data['grand_total'],
                    'payment_method': updated_data['payment_method'],
                    'transaction_id': updated_data['transaction_id'],
                    'items_json': str(updated_products)
                })
                
                if not success:
                    messagebox.showerror("Error", "Failed to save changes!")
                    return
                
                # Regenerate PDF
                folder = self.app.dm.get_config('output_folder', SCRIPT_DIR)
                path = os.path.join(folder, f"Invoice_{invoice_number.replace('#','').replace('-','_')}.pdf")
                
                gen = InvoiceGenerator(path)
                gen.generate(updated_data)
                
                edit_win.destroy()
                self._refresh()
                
                messagebox.showinfo("Success", f"Invoice updated and PDF regenerated!\n\nSaved to: {path}")
                os.startfile(path)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save changes: {str(e)}")
        
        tk.Button(btn_frame, text="💾 SAVE & REGENERATE PDF", command=save_changes, 
                 bg=self.c['accent'], fg='white', relief='flat', padx=20, pady=10,
                 font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0, 10))
        
        tk.Button(btn_frame, text="Cancel", command=edit_win.destroy,
                 bg=self.c['card'], fg='white', relief='flat', padx=20, pady=10,
                 font=("Segoe UI", 10)).pack(side="left")
    
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
