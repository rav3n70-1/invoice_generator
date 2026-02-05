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
        """Delete an invoice and return its data (for potential inventory restoration)"""
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
                    invoice_data['products'] = ast.literal_eval(invoice_data['items_json'])
                except:
                    invoice_data['products'] = []
                invoices.append(invoice_data)
            return invoices
        except Exception as e:
            print(f"Error searching invoices: {e}")
            return []
