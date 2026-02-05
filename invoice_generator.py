"""
Invoice Generator for Sneaker Canvas BD
Generates professional A4 PDF invoices using ReportLab
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime

# Brand Colors
BRAND_RED = colors.HexColor("#EE1C25")
BRAND_BLACK = colors.HexColor("#111111")
BRAND_GRAY = colors.HexColor("#666666")
BRAND_LIGHT_GRAY = colors.HexColor("#f3f4f6")

# Page dimensions
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 12 * mm


class InvoiceGenerator:
    def __init__(self, output_path="invoice.pdf"):
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=BRAND_BLACK,
            spaceAfter=2*mm
        ))
        self.styles.add(ParagraphStyle(
            name='CompanyTagline',
            fontName='Helvetica',
            fontSize=10,
            textColor=BRAND_GRAY,
            spaceAfter=3*mm
        ))
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            fontName='Helvetica-Bold',
            fontSize=36,
            textColor=BRAND_RED,
            alignment=TA_RIGHT
        ))
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=BRAND_RED,
            spaceAfter=3*mm
        ))
        self.styles.add(ParagraphStyle(
            name='CustomerName',
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=BRAND_BLACK,
            spaceAfter=2*mm
        ))
        self.styles.add(ParagraphStyle(
            name='CustomerInfo',
            fontName='Helvetica',
            fontSize=10,
            textColor=BRAND_GRAY
        ))
        self.styles.add(ParagraphStyle(
            name='FooterText',
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.white
        ))
        self.styles.add(ParagraphStyle(
            name='FooterSmall',
            fontName='Helvetica',
            fontSize=8,
            textColor=colors.HexColor("#9ca3af")
        ))

    def generate(self, invoice_data):
        """Generate the invoice PDF"""
        c = canvas.Canvas(self.output_path, pagesize=A4)
        
        # Draw all sections
        self._draw_header_strip(c)
        y_pos = self._draw_header(c, invoice_data)
        y_pos = self._draw_customer(c, invoice_data, y_pos)
        y_pos = self._draw_table(c, invoice_data, y_pos)
        y_pos = self._draw_summary(c, invoice_data, y_pos)
        self._draw_footer(c)
        
        c.save()
        print(f"Invoice generated: {self.output_path}")
        return self.output_path

    def _draw_header_strip(self, c):
        """Draw the red header strip at the top"""
        c.setFillColor(BRAND_RED)
        c.rect(0, PAGE_HEIGHT - 4*mm, PAGE_WIDTH, 4*mm, fill=True, stroke=False)

    def _draw_header(self, c, data):
        """Draw company header and invoice info"""
        y = PAGE_HEIGHT - 15*mm
        
        # Left side - Company info
        left_x = MARGIN
        
        # Logo placeholder (or actual logo if exists)
        logo_path = data.get('logo_path', 'logo.jpg')
        if os.path.exists(logo_path):
            try:
                c.drawImage(logo_path, left_x, y - 28*mm, width=28*mm, height=28*mm, preserveAspectRatio=True)
            except:
                # Draw placeholder
                c.setFillColor(BRAND_LIGHT_GRAY)
                c.rect(left_x, y - 28*mm, 28*mm, 28*mm, fill=True, stroke=False)
                c.setFillColor(BRAND_RED)
                c.setFont("Helvetica-Bold", 12)
                c.drawCentredString(left_x + 14*mm, y - 16*mm, "SC BD")
        else:
            # Draw placeholder
            c.setFillColor(BRAND_LIGHT_GRAY)
            c.rect(left_x, y - 28*mm, 28*mm, 28*mm, fill=True, stroke=False)
            c.setFillColor(BRAND_RED)
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(left_x + 14*mm, y - 16*mm, "SC BD")
        
        # Company name and tagline
        text_x = left_x + 32*mm
        c.setFillColor(BRAND_BLACK)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(text_x, y - 5*mm, data.get('company_name', 'SNEAKER CANVAS BD'))
        
        c.setFillColor(BRAND_GRAY)
        c.setFont("Helvetica", 9)
        c.drawString(text_x, y - 11*mm, data.get('company_tagline', 'Premium Footwear & Streetwear'))
        
        # Company contact info
        contact_y = y - 18*mm
        c.setFont("Helvetica", 9)
        c.setFillColor(BRAND_GRAY)
        c.drawString(text_x, contact_y, f"Address: {data.get('company_address', 'Shop 42, Block C, Dhaka, BD')}")
        c.drawString(text_x, contact_y - 4*mm, f"Phone: {data.get('company_phone', '+880 1XXX-XXXXXX')}")
        c.drawString(text_x, contact_y - 8*mm, f"Email: {data.get('company_email', 'contact@sneakercanvasbd.com')}")
        
        # Right side - Invoice title and number
        right_x = PAGE_WIDTH - MARGIN
        c.setFillColor(BRAND_RED)
        c.setFont("Helvetica-Bold", 36)
        c.drawRightString(right_x, y - 8*mm, "INVOICE")
        
        # Invoice number and date
        c.setFillColor(BRAND_GRAY)
        c.setFont("Helvetica", 9)
        c.drawRightString(right_x - 50*mm, y - 18*mm, "Invoice No")
        c.drawRightString(right_x - 50*mm, y - 25*mm, "Date")
        
        c.setFillColor(BRAND_BLACK)
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(right_x, y - 18*mm, data.get('invoice_number', '#SC-2024-001'))
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(right_x, y - 25*mm, data.get('date', datetime.now().strftime('%b %d, %Y')))
        
        # Divider line
        divider_y = y - 35*mm
        c.setStrokeColor(colors.HexColor("#e5e7eb"))
        c.setLineWidth(0.5)
        c.line(MARGIN, divider_y, PAGE_WIDTH - MARGIN, divider_y)
        
        return divider_y - 5*mm

    def _draw_customer(self, c, data, y_pos):
        """Draw customer information section"""
        # Section title
        c.setFillColor(BRAND_RED)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(MARGIN, y_pos, "BILL TO")
        
        y_pos -= 8*mm
        
        # Customer box with left border
        box_height = 22*mm
        c.setFillColor(BRAND_LIGHT_GRAY)
        c.rect(MARGIN, y_pos - box_height, 120*mm, box_height, fill=True, stroke=False)
        c.setFillColor(BRAND_RED)
        c.rect(MARGIN, y_pos - box_height, 1.5*mm, box_height, fill=True, stroke=False)
        
        # Customer details
        text_x = MARGIN + 5*mm
        c.setFillColor(BRAND_BLACK)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(text_x, y_pos - 6*mm, data.get('customer_name', 'Customer Name'))
        
        c.setFillColor(BRAND_GRAY)
        c.setFont("Helvetica", 9)
        c.drawString(text_x, y_pos - 12*mm, f"Phone: {data.get('customer_phone', '+880 1700-000000')}")
        c.drawString(text_x, y_pos - 17*mm, f"Address: {data.get('customer_address', 'House 12, Road 5, Dhanmondi, Dhaka')}")
        
        return y_pos - box_height - 8*mm

    def _draw_table(self, c, data, y_pos):
        """Draw the product table"""
        products = data.get('products', [])
        
        # Table header
        header_height = 10*mm
        c.setFillColor(BRAND_BLACK)
        c.rect(MARGIN, y_pos - header_height, PAGE_WIDTH - 2*MARGIN, header_height, fill=True, stroke=False)
        
        # Header text
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 9)
        
        col_widths = [75*mm, 25*mm, 15*mm, 30*mm, 30*mm]  # Item, Size, Qty, Price, Total
        x = MARGIN + 3*mm
        headers = ["ITEM DESCRIPTION", "SIZE", "QTY", "UNIT PRICE", "TOTAL"]
        
        for i, (header, width) in enumerate(zip(headers, col_widths)):
            if i < 2:
                c.drawString(x, y_pos - 6.5*mm, header)
            elif i == 2:
                c.drawCentredString(x + width/2, y_pos - 6.5*mm, header)
            else:
                c.drawRightString(x + width - 3*mm, y_pos - 6.5*mm, header)
            x += width
        
        y_pos -= header_height
        
        # Table rows
        row_height = 12*mm
        for idx, product in enumerate(products):
            # Alternate row background
            if idx % 2 == 1:
                c.setFillColor(colors.HexColor("#fef2f2"))
                c.rect(MARGIN, y_pos - row_height, PAGE_WIDTH - 2*MARGIN, row_height, fill=True, stroke=False)
            
            x = MARGIN + 3*mm
            
            # Item description
            c.setFillColor(BRAND_BLACK)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(x, y_pos - 5*mm, product.get('name', 'Product'))
            c.setFillColor(BRAND_GRAY)
            c.setFont("Helvetica", 8)
            c.drawString(x, y_pos - 9*mm, product.get('description', ''))
            x += col_widths[0]
            
            # Size
            c.setFillColor(BRAND_BLACK)
            c.setFont("Helvetica", 10)
            c.drawString(x, y_pos - 7*mm, product.get('size', '-'))
            x += col_widths[1]
            
            # Qty
            c.drawCentredString(x + col_widths[2]/2, y_pos - 7*mm, str(product.get('qty', 1)))
            x += col_widths[2]
            
            # Price
            price = product.get('price', 0)
            c.drawRightString(x + col_widths[3] - 3*mm, y_pos - 7*mm, f"{price:,.0f} BDT")
            x += col_widths[3]
            
            # Total
            total = product.get('qty', 1) * price
            c.setFont("Helvetica-Bold", 10)
            c.drawRightString(x + col_widths[4] - 3*mm, y_pos - 7*mm, f"{total:,.0f} BDT")
            
            # Row border
            c.setStrokeColor(colors.HexColor("#f3f4f6"))
            c.setLineWidth(0.5)
            c.line(MARGIN, y_pos - row_height, PAGE_WIDTH - MARGIN, y_pos - row_height)
            
            y_pos -= row_height
        
        return y_pos - 5*mm

    def _draw_summary(self, c, data, y_pos):
        """Draw the summary section (subtotal, discount, delivery, grand total)"""
        products = data.get('products', [])
        
        # Calculate totals
        subtotal = sum(p.get('qty', 1) * p.get('price', 0) for p in products)
        discount = data.get('discount', 0)
        delivery = data.get('delivery', 150)
        grand_total = subtotal - discount + delivery
        
        # Position summary on right side
        summary_x = PAGE_WIDTH - MARGIN - 70*mm
        summary_width = 70*mm
        
        # Subtotal
        c.setFillColor(BRAND_GRAY)
        c.setFont("Helvetica", 10)
        c.drawString(summary_x, y_pos, "Subtotal")
        c.setFillColor(BRAND_BLACK)
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(PAGE_WIDTH - MARGIN, y_pos, f"{subtotal:,.0f} BDT")
        y_pos -= 6*mm
        
        # Discount
        c.setFillColor(BRAND_RED)
        c.setFont("Helvetica", 10)
        c.drawString(summary_x, y_pos, "Discount")
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(PAGE_WIDTH - MARGIN, y_pos, f"-{discount:,.0f} BDT")
        y_pos -= 6*mm
        
        # Delivery
        c.setFillColor(BRAND_GRAY)
        c.setFont("Helvetica", 10)
        c.drawString(summary_x, y_pos, "Delivery Charge")
        c.setFillColor(BRAND_BLACK)
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(PAGE_WIDTH - MARGIN, y_pos, f"{delivery:,.0f} BDT")
        y_pos -= 8*mm
        
        # Divider
        c.setStrokeColor(colors.HexColor("#d1d5db"))
        c.setLineWidth(0.5)
        c.line(summary_x, y_pos, PAGE_WIDTH - MARGIN, y_pos)
        y_pos -= 5*mm
        
        # Grand Total box
        total_box_height = 12*mm
        c.setFillColor(BRAND_RED)
        c.roundRect(summary_x, y_pos - total_box_height, summary_width, total_box_height, 2*mm, fill=True, stroke=False)
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(summary_x + 4*mm, y_pos - 8*mm, "TOTAL")
        c.setFont("Helvetica-Bold", 14)
        c.drawRightString(PAGE_WIDTH - MARGIN - 4*mm, y_pos - 8*mm, f"{grand_total:,.0f} BDT")
        
        y_pos -= total_box_height + 8*mm
        
        # Payment method
        c.setFillColor(BRAND_GRAY)
        c.setFont("Helvetica", 8)
        c.drawRightString(PAGE_WIDTH - MARGIN, y_pos, "PAYMENT METHOD")
        y_pos -= 4*mm
        c.setFillColor(BRAND_BLACK)
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(PAGE_WIDTH - MARGIN, y_pos, data.get('payment_method', 'bKash / Cash on Delivery'))
        
        # Transaction ID if exists
        trx_id = data.get('transaction_id')
        if trx_id:
            y_pos -= 4*mm
            c.setFont("Helvetica", 9)
            c.drawRightString(PAGE_WIDTH - MARGIN, y_pos, f"TrxID: {trx_id}")

        # Signature
        sign_path = data.get('signature_path', 'assets/SIGN JOY.png')
        if os.path.exists(sign_path):
            # Draw signature on the left side, aligned with the bottom of summary
            sign_y = y_pos - 10*mm
            c.drawImage(sign_path, MARGIN + 10*mm, sign_y, width=40*mm, height=20*mm, preserveAspectRatio=True, mask='auto')
            
            # Line and text
            c.setStrokeColor(BRAND_BLACK)
            c.setLineWidth(0.5)
            c.line(MARGIN + 10*mm, sign_y, MARGIN + 50*mm, sign_y)
            
            c.setFont("Helvetica", 8)
            c.setFillColor(BRAND_BLACK)
            c.drawCentredString(MARGIN + 30*mm, sign_y - 4*mm, "Authorized Signature")
        
        return y_pos

    def _draw_footer(self, c):
        """Draw the footer section"""
        footer_height = 18*mm
        footer_y = 2*mm
        
        # Dark background
        c.setFillColor(colors.HexColor("#111827"))
        c.rect(0, footer_y, PAGE_WIDTH, footer_height, fill=True, stroke=False)
        
        # Red diagonal slice
        c.setFillColor(BRAND_RED)
        path = c.beginPath()
        path.moveTo(0, footer_y)
        path.lineTo(0, footer_y + footer_height)
        path.lineTo(25*mm, footer_y + footer_height)
        path.lineTo(35*mm, footer_y)
        path.close()
        c.drawPath(path, fill=True, stroke=False)
        
        # Thank you text
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40*mm, footer_y + 11*mm, "THANK YOU FOR YOUR SUPPORT")
        c.setFillColor(colors.HexColor("#9ca3af"))
        c.setFont("Helvetica", 8)
        c.drawString(40*mm, footer_y + 5*mm, "Keep walking fresh. Tag us on socials!")
        
        # Return policy
        c.drawRightString(PAGE_WIDTH - MARGIN, footer_y + 11*mm, "No returns after 3 days.")
        c.drawRightString(PAGE_WIDTH - MARGIN, footer_y + 5*mm, "Original box required for exchanges.")
        
        # Bottom red strip
        c.setFillColor(BRAND_RED)
        c.rect(0, 0, PAGE_WIDTH, 2*mm, fill=True, stroke=False)


def create_sample_invoice():
    """Create a sample invoice with demo data"""
    invoice_data = {
        # Company info
        'company_name': 'SNEAKER CANVAS BD',
        'company_tagline': 'Premium Footwear & Streetwear',
        'company_address': '80/7, South Saidabad, Dhaka',
        'company_phone': '01957124591',
        'company_email': 'sneakercanvasbd@gmail.com',
        'logo_path': 'assets/logo.jpg',
        
        # Invoice info
        'invoice_number': '#SC-2024-001',
        'date': 'Oct 24, 2024',
        
        # Customer info
        'customer_name': 'Customer Name',
        'customer_phone': '+880 1700-000000',
        'customer_address': 'House 12, Road 5, Dhanmondi, Dhaka',
        
        # Products
        'products': [
            {
                'name': 'Air Jordan 1 High OG "Lost & Found"',
                'description': 'Chicago colorway',
                'size': 'US 10',
                'qty': 1,
                'price': 25000
            },
            {
                'name': 'Yeezy Slide "Pure"',
                'description': 'Resin',
                'size': 'US 9',
                'qty': 1,
                'price': 8500
            }
        ],
        
        # Totals
        'discount': 0,
        'delivery': 150,
        'payment_method': 'bKash / Cash on Delivery'
    }
    
    generator = InvoiceGenerator("sneaker_invoice.pdf")
    return generator.generate(invoice_data)


if __name__ == "__main__":
    output_file = create_sample_invoice()
    print(f"\n✅ Invoice saved to: {output_file}")
    print("Open the PDF to view your invoice!")
