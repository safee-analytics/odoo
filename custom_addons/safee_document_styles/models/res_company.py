# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Color Settings
    safee_primary_color = fields.Char(
        string='Primary Color',
        default='#3B82F6',
        help='Primary brand color used in document headers and accents',
    )
    safee_secondary_color = fields.Char(
        string='Secondary Color',
        default='#8B5CF6',
        help='Secondary/accent color for highlights',
    )
    safee_accent_color = fields.Char(
        string='Accent Color',
        default='#8B5CF6',
        help='Accent color for table headers and buttons',
    )
    safee_text_color = fields.Char(
        string='Text Color',
        default='#1F2937',
        help='Main text color for document body',
    )
    safee_background_color = fields.Char(
        string='Background Color',
        default='#FFFFFF',
        help='Document background color',
    )

    # Font Settings
    safee_heading_font = fields.Selection([
        ('Inter', 'Inter'),
        ('Roboto', 'Roboto'),
        ('Open Sans', 'Open Sans'),
        ('Lato', 'Lato'),
        ('Montserrat', 'Montserrat'),
        ('Poppins', 'Poppins'),
        ('Arial', 'Arial'),
        ('Times New Roman', 'Times New Roman'),
    ], string='Heading Font', default='Inter')

    safee_body_font = fields.Selection([
        ('Inter', 'Inter'),
        ('Roboto', 'Roboto'),
        ('Open Sans', 'Open Sans'),
        ('Lato', 'Lato'),
        ('Montserrat', 'Montserrat'),
        ('Poppins', 'Poppins'),
        ('Arial', 'Arial'),
        ('Times New Roman', 'Times New Roman'),
    ], string='Body Font', default='Inter')

    safee_font_size = fields.Selection([
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ], string='Font Size', default='medium')

    # Logo Settings
    safee_logo_position = fields.Selection([
        ('left', 'Left'),
        ('center', 'Center'),
        ('right', 'Right'),
    ], string='Logo Position', default='left')

    # Display Options - General
    safee_show_logo = fields.Boolean(
        string='Show Company Logo',
        default=True,
    )
    safee_show_company_address = fields.Boolean(
        string='Show Company Address',
        default=True,
    )
    safee_show_footer = fields.Boolean(
        string='Show Footer',
        default=True,
    )
    safee_show_page_numbers = fields.Boolean(
        string='Show Page Numbers',
        default=True,
    )

    # Display Options - Invoice Specific
    safee_show_payment_terms = fields.Boolean(
        string='Show Payment Terms',
        default=True,
    )
    safee_show_bank_details = fields.Boolean(
        string='Show Bank Details',
        default=True,
    )
    safee_show_qr_code = fields.Boolean(
        string='Show Payment QR Code',
        default=False,
    )
    safee_show_tax_details = fields.Boolean(
        string='Show Tax Breakdown',
        default=True,
    )

    # Display Options - HR Specific
    safee_show_employee_photo = fields.Boolean(
        string='Show Employee Photo (Payslips)',
        default=False,
    )
    safee_show_signature_line = fields.Boolean(
        string='Show Signature Line',
        default=True,
    )

    # Custom Text
    safee_custom_header_text = fields.Text(
        string='Custom Header Text',
        help='Optional text displayed in document header',
    )
    safee_custom_footer_text = fields.Text(
        string='Custom Footer Text',
        default='Thank you for your business!',
        help='Text displayed in document footer',
    )

    # Label Customization (for invoices)
    safee_invoice_label = fields.Char(
        string='Invoice Label',
        default='INVOICE',
    )
    safee_quote_label = fields.Char(
        string='Quote Label',
        default='QUOTATION',
    )
    safee_bill_to_label = fields.Char(
        string='Bill To Label',
        default='BILL TO',
    )
    safee_date_label = fields.Char(
        string='Date Label',
        default='DATE',
    )
    safee_due_date_label = fields.Char(
        string='Due Date Label',
        default='DUE DATE',
    )
    safee_total_label = fields.Char(
        string='Total Label',
        default='TOTAL',
    )

    def get_font_size_px(self):
        """Return font size in pixels based on selection"""
        sizes = {
            'small': 10,
            'medium': 12,
            'large': 14,
        }
        return sizes.get(self.safee_font_size, 12)
