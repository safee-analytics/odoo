# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""
Accounting Business Logic API
All accounting operations, reports, reconciliation, payments
"""

import json
import logging
import jwt
from datetime import datetime, timedelta
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError, UserError

_logger = logging.getLogger(__name__)

JWT_SECRET = 'your-secret-key-change-this-in-production'
JWT_ALGORITHM = 'HS256'


def verify_token(func):
    """Decorator to verify JWT token"""
    def wrapper(self, *args, **kwargs):
        try:
            auth_header = request.httprequest.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return {'error': 'Missing or invalid authorization header', 'status': 401}

            token = auth_header[7:]
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

            db = payload.get('db')
            uid = payload.get('uid')

            request.session.db = db
            request.env.uid = uid
            request.uid = uid

            return func(self, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            return {'error': 'Token expired', 'status': 401}
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token', 'status': 401}
        except Exception as e:
            _logger.exception("Token verification error")
            return {'error': str(e), 'status': 500}

    return wrapper


class AccountingAPI(http.Controller):
    """Complete Accounting Business Logic"""

    # ============= INVOICES =============

    @http.route('/api/accounting/invoices/list', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def list_invoices(self, **kwargs):
        """List invoices with filters"""
        try:
            domain = kwargs.get('domain', [])
            invoice_type = kwargs.get('type', 'out_invoice')  # out_invoice, in_invoice, out_refund, in_refund
            state = kwargs.get('state')  # draft, posted, cancel
            payment_state = kwargs.get('payment_state')  # not_paid, in_payment, paid, partial, reversed
            limit = kwargs.get('limit', 80)
            offset = kwargs.get('offset', 0)

            domain.append(('move_type', '=', invoice_type))
            if state:
                domain.append(('state', '=', state))
            if payment_state:
                domain.append(('payment_state', '=', payment_state))

            invoices = request.env['account.move'].search(domain, limit=limit, offset=offset)

            return {
                'success': True,
                'data': [{
                    'id': inv.id,
                    'name': inv.name,
                    'partner_id': inv.partner_id.id,
                    'partner_name': inv.partner_id.name,
                    'invoice_date': inv.invoice_date.isoformat() if inv.invoice_date else None,
                    'invoice_date_due': inv.invoice_date_due.isoformat() if inv.invoice_date_due else None,
                    'amount_untaxed': inv.amount_untaxed,
                    'amount_tax': inv.amount_tax,
                    'amount_total': inv.amount_total,
                    'amount_residual': inv.amount_residual,
                    'state': inv.state,
                    'payment_state': inv.payment_state,
                    'currency': inv.currency_id.name,
                } for inv in invoices]
            }

        except Exception as e:
            _logger.exception("Error listing invoices")
            return {'error': str(e), 'status': 500}

    @http.route('/api/accounting/invoice/<int:invoice_id>/post', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def post_invoice(self, invoice_id, **kwargs):
        """Post invoice - creates journal entries"""
        try:
            invoice = request.env['account.move'].browse(invoice_id)
            if not invoice.exists():
                return {'error': 'Invoice not found', 'status': 404}

            invoice.action_post()

            return {
                'success': True,
                'data': {
                    'id': invoice.id,
                    'name': invoice.name,
                    'state': invoice.state,
                    'amount_total': invoice.amount_total
                }
            }

        except Exception as e:
            _logger.exception(f"Error posting invoice {invoice_id}")
            return {'error': str(e), 'status': 500}

    @http.route('/api/accounting/invoice/<int:invoice_id>/register_payment', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def register_payment(self, invoice_id, **kwargs):
        """Register payment for invoice"""
        try:
            invoice = request.env['account.move'].browse(invoice_id)
            if not invoice.exists():
                return {'error': 'Invoice not found', 'status': 404}

            amount = kwargs.get('amount', invoice.amount_residual)
            payment_date = kwargs.get('payment_date', datetime.now().date())
            journal_id = kwargs.get('journal_id')
            payment_method_id = kwargs.get('payment_method_id')

            # Create payment
            payment_vals = {
                'payment_type': 'inbound' if invoice.move_type == 'out_invoice' else 'outbound',
                'partner_type': 'customer' if invoice.move_type == 'out_invoice' else 'supplier',
                'partner_id': invoice.partner_id.id,
                'amount': amount,
                'date': payment_date,
                'ref': invoice.name,
                'journal_id': journal_id,
                'payment_method_line_id': payment_method_id,
            }

            payment = request.env['account.payment'].create(payment_vals)
            payment.action_post()

            # Reconcile
            invoice.js_assign_outstanding_line(payment.move_id.line_ids.filtered(lambda l: not l.reconciled).id)

            return {
                'success': True,
                'data': {
                    'payment_id': payment.id,
                    'payment_name': payment.name,
                    'amount': payment.amount,
                    'invoice_payment_state': invoice.payment_state
                }
            }

        except Exception as e:
            _logger.exception(f"Error registering payment for invoice {invoice_id}")
            return {'error': str(e), 'status': 500}

    @http.route('/api/accounting/invoice/<int:invoice_id>/send_email', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def send_invoice_email(self, invoice_id, **kwargs):
        """Send invoice by email"""
        try:
            invoice = request.env['account.move'].browse(invoice_id)
            if not invoice.exists():
                return {'error': 'Invoice not found', 'status': 404}

            template = request.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
            if template:
                invoice.message_post_with_source(
                    template,
                    email_layout_xmlid='mail.mail_notification_layout_with_responsible_signature',
                    subtype_xmlid='mail.mt_comment',
                )

            return {
                'success': True,
                'message': f'Invoice {invoice.name} sent to {invoice.partner_id.email}'
            }

        except Exception as e:
            _logger.exception(f"Error sending invoice {invoice_id}")
            return {'error': str(e), 'status': 500}

    # ============= PAYMENTS =============

    @http.route('/api/accounting/payments/list', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def list_payments(self, **kwargs):
        """List payments"""
        try:
            domain = kwargs.get('domain', [])
            payment_type = kwargs.get('payment_type')  # inbound, outbound
            state = kwargs.get('state')  # draft, posted, cancel
            limit = kwargs.get('limit', 80)

            if payment_type:
                domain.append(('payment_type', '=', payment_type))
            if state:
                domain.append(('state', '=', state))

            payments = request.env['account.payment'].search(domain, limit=limit)

            return {
                'success': True,
                'data': [{
                    'id': p.id,
                    'name': p.name,
                    'partner_name': p.partner_id.name,
                    'amount': p.amount,
                    'payment_date': p.date.isoformat() if p.date else None,
                    'payment_type': p.payment_type,
                    'state': p.state,
                    'ref': p.ref,
                } for p in payments]
            }

        except Exception as e:
            _logger.exception("Error listing payments")
            return {'error': str(e), 'status': 500}

    # ============= BANK RECONCILIATION =============

    @http.route('/api/accounting/reconciliation/bank_statements', type='jsonrpc', auth='none', methods=['GET'], csrf=False, cors='*')
    @verify_token
    def bank_statements(self, **kwargs):
        """Get bank statements for reconciliation"""
        try:
            statements = request.env['account.bank.statement'].search([
                ('state', '=', 'open')
            ])

            return {
                'success': True,
                'data': [{
                    'id': s.id,
                    'name': s.name,
                    'journal_id': s.journal_id.id,
                    'journal_name': s.journal_id.name,
                    'balance_start': s.balance_start,
                    'balance_end_real': s.balance_end_real,
                    'date': s.date.isoformat() if s.date else None,
                    'line_count': len(s.line_ids),
                } for s in statements]
            }

        except Exception as e:
            _logger.exception("Error getting bank statements")
            return {'error': str(e), 'status': 500}

    @http.route('/api/accounting/reconciliation/suggestions/<int:line_id>', type='jsonrpc', auth='none', methods=['GET'], csrf=False, cors='*')
    @verify_token
    def reconciliation_suggestions(self, line_id, **kwargs):
        """Get reconciliation suggestions for bank statement line"""
        try:
            line = request.env['account.bank.statement.line'].browse(line_id)
            if not line.exists():
                return {'error': 'Line not found', 'status': 404}

            # Get matching moves
            suggestions = line._get_reconciliation_proposition()

            return {
                'success': True,
                'data': [{
                    'id': m.id,
                    'name': m.name,
                    'partner_name': m.partner_id.name if m.partner_id else None,
                    'amount': m.amount_residual,
                    'date': m.date.isoformat() if m.date else None,
                } for m in suggestions]
            }

        except Exception as e:
            _logger.exception(f"Error getting reconciliation suggestions for line {line_id}")
            return {'error': str(e), 'status': 500}

    # ============= REPORTS =============

    @http.route('/api/accounting/reports/balance_sheet', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def balance_sheet(self, **kwargs):
        """Balance Sheet report"""
        try:
            date = kwargs.get('date', datetime.now().date())
            company_id = kwargs.get('company_id', request.env.company.id)

            AccountLine = request.env['account.move.line']

            # Assets
            assets = AccountLine.read_group(
                domain=[
                    ('date', '<=', date),
                    ('account_id.account_type', 'in', ['asset_receivable', 'asset_cash', 'asset_current', 'asset_non_current', 'asset_prepayments', 'asset_fixed']),
                    ('company_id', '=', company_id)
                ],
                fields=['account_id', 'debit', 'credit'],
                groupby=['account_id']
            )

            # Liabilities
            liabilities = AccountLine.read_group(
                domain=[
                    ('date', '<=', date),
                    ('account_id.account_type', 'in', ['liability_payable', 'liability_credit_card', 'liability_current', 'liability_non_current']),
                    ('company_id', '=', company_id)
                ],
                fields=['account_id', 'debit', 'credit'],
                groupby=['account_id']
            )

            # Equity
            equity = AccountLine.read_group(
                domain=[
                    ('date', '<=', date),
                    ('account_id.account_type', '=', 'equity'),
                    ('company_id', '=', company_id)
                ],
                fields=['account_id', 'debit', 'credit'],
                groupby=['account_id']
            )

            total_assets = sum(a['debit'] - a['credit'] for a in assets)
            total_liabilities = sum(l['credit'] - l['debit'] for l in liabilities)
            total_equity = sum(e['credit'] - e['debit'] for e in equity)

            return {
                'success': True,
                'data': {
                    'date': date.isoformat() if isinstance(date, datetime) else date,
                    'assets': {
                        'accounts': assets,
                        'total': total_assets
                    },
                    'liabilities': {
                        'accounts': liabilities,
                        'total': total_liabilities
                    },
                    'equity': {
                        'accounts': equity,
                        'total': total_equity
                    },
                    'balance_check': total_assets - (total_liabilities + total_equity)
                }
            }

        except Exception as e:
            _logger.exception("Error generating balance sheet")
            return {'error': str(e), 'status': 500}

    @http.route('/api/accounting/reports/profit_loss', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def profit_loss(self, **kwargs):
        """Profit & Loss report"""
        try:
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to', datetime.now().date())
            company_id = kwargs.get('company_id', request.env.company.id)

            domain = [('company_id', '=', company_id)]
            if date_from:
                domain.append(('date', '>=', date_from))
            if date_to:
                domain.append(('date', '<=', date_to))

            AccountLine = request.env['account.move.line']

            # Revenue
            revenue = AccountLine.read_group(
                domain=domain + [('account_id.account_type', '=', 'income')],
                fields=['account_id', 'debit', 'credit'],
                groupby=['account_id']
            )

            # Expenses
            expenses = AccountLine.read_group(
                domain=domain + [('account_id.account_type', '=', 'expense')],
                fields=['account_id', 'debit', 'credit'],
                groupby=['account_id']
            )

            # COGS
            cogs = AccountLine.read_group(
                domain=domain + [('account_id.account_type', '=', 'expense_direct_cost')],
                fields=['account_id', 'debit', 'credit'],
                groupby=['account_id']
            )

            total_revenue = sum(r['credit'] - r['debit'] for r in revenue)
            total_expenses = sum(e['debit'] - e['credit'] for e in expenses)
            total_cogs = sum(c['debit'] - c['credit'] for c in cogs)

            gross_profit = total_revenue - total_cogs
            net_profit = gross_profit - total_expenses

            return {
                'success': True,
                'data': {
                    'period': {
                        'from': date_from,
                        'to': date_to
                    },
                    'revenue': {
                        'accounts': revenue,
                        'total': total_revenue
                    },
                    'cost_of_goods_sold': {
                        'accounts': cogs,
                        'total': total_cogs
                    },
                    'gross_profit': gross_profit,
                    'expenses': {
                        'accounts': expenses,
                        'total': total_expenses
                    },
                    'net_profit': net_profit,
                    'margin_percent': (net_profit / total_revenue * 100) if total_revenue else 0
                }
            }

        except Exception as e:
            _logger.exception("Error generating P&L")
            return {'error': str(e), 'status': 500}

    @http.route('/api/accounting/reports/aged_receivables', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def aged_receivables(self, **kwargs):
        """Aged Receivables (AR Aging) report"""
        try:
            date = kwargs.get('date', datetime.now().date())

            Invoice = request.env['account.move']
            unpaid = Invoice.search([
                ('move_type', '=', 'out_invoice'),
                ('payment_state', 'in', ['not_paid', 'partial']),
                ('invoice_date', '<=', date)
            ])

            aging_buckets = {
                'current': [],
                '1-30': [],
                '31-60': [],
                '61-90': [],
                '90+': []
            }

            for inv in unpaid:
                days_overdue = (date - inv.invoice_date_due).days if inv.invoice_date_due else 0

                bucket_data = {
                    'invoice_id': inv.id,
                    'invoice_name': inv.name,
                    'partner_name': inv.partner_id.name,
                    'amount': inv.amount_residual,
                    'days_overdue': days_overdue
                }

                if days_overdue <= 0:
                    aging_buckets['current'].append(bucket_data)
                elif days_overdue <= 30:
                    aging_buckets['1-30'].append(bucket_data)
                elif days_overdue <= 60:
                    aging_buckets['31-60'].append(bucket_data)
                elif days_overdue <= 90:
                    aging_buckets['61-90'].append(bucket_data)
                else:
                    aging_buckets['90+'].append(bucket_data)

            return {
                'success': True,
                'data': {
                    'date': date.isoformat() if isinstance(date, datetime) else date,
                    'aging': {
                        'current': {
                            'invoices': aging_buckets['current'],
                            'total': sum(i['amount'] for i in aging_buckets['current'])
                        },
                        '1-30_days': {
                            'invoices': aging_buckets['1-30'],
                            'total': sum(i['amount'] for i in aging_buckets['1-30'])
                        },
                        '31-60_days': {
                            'invoices': aging_buckets['31-60'],
                            'total': sum(i['amount'] for i in aging_buckets['31-60'])
                        },
                        '61-90_days': {
                            'invoices': aging_buckets['61-90'],
                            'total': sum(i['amount'] for i in aging_buckets['61-90'])
                        },
                        '90+_days': {
                            'invoices': aging_buckets['90+'],
                            'total': sum(i['amount'] for i in aging_buckets['90+'])
                        }
                    },
                    'total_outstanding': sum(inv.amount_residual for inv in unpaid)
                }
            }

        except Exception as e:
            _logger.exception("Error generating aged receivables")
            return {'error': str(e), 'status': 500}

    @http.route('/api/accounting/reports/cash_flow', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def cash_flow(self, **kwargs):
        """Cash Flow statement"""
        try:
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to', datetime.now().date())

            AccountLine = request.env['account.move.line']

            domain = []
            if date_from:
                domain.append(('date', '>=', date_from))
            if date_to:
                domain.append(('date', '<=', date_to))

            # Operating Activities
            operating = AccountLine.read_group(
                domain=domain + [('account_id.account_type', 'in', ['income', 'expense', 'expense_direct_cost'])],
                fields=['debit', 'credit'],
                groupby=[]
            )

            # Investing Activities
            investing = AccountLine.read_group(
                domain=domain + [('account_id.account_type', 'in', ['asset_fixed', 'asset_non_current'])],
                fields=['debit', 'credit'],
                groupby=[]
            )

            # Financing Activities
            financing = AccountLine.read_group(
                domain=domain + [('account_id.account_type', 'in', ['liability_non_current', 'equity'])],
                fields=['debit', 'credit'],
                groupby=[]
            )

            operating_cash = operating[0]['credit'] - operating[0]['debit'] if operating else 0
            investing_cash = investing[0]['debit'] - investing[0]['credit'] if investing else 0
            financing_cash = financing[0]['credit'] - financing[0]['debit'] if financing else 0

            return {
                'success': True,
                'data': {
                    'period': {'from': date_from, 'to': date_to},
                    'operating_activities': operating_cash,
                    'investing_activities': investing_cash,
                    'financing_activities': financing_cash,
                    'net_cash_flow': operating_cash + investing_cash + financing_cash
                }
            }

        except Exception as e:
            _logger.exception("Error generating cash flow")
            return {'error': str(e), 'status': 500}

    # ============= TAX REPORTS =============

    @http.route('/api/accounting/reports/tax_report', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def tax_report(self, **kwargs):
        """Tax report"""
        try:
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to', datetime.now().date())

            domain = [('move_id.state', '=', 'posted')]
            if date_from:
                domain.append(('move_id.date', '>=', date_from))
            if date_to:
                domain.append(('move_id.date', '<=', date_to))

            TaxLine = request.env['account.move.line']

            # Group by tax
            tax_lines = TaxLine.read_group(
                domain=domain + [('tax_ids', '!=', False)],
                fields=['tax_ids', 'price_subtotal', 'price_total'],
                groupby=['tax_ids']
            )

            return {
                'success': True,
                'data': {
                    'period': {'from': date_from, 'to': date_to},
                    'taxes': tax_lines
                }
            }

        except Exception as e:
            _logger.exception("Error generating tax report")
            return {'error': str(e), 'status': 500}
