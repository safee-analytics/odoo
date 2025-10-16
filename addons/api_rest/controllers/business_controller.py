# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
import jwt
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


class BusinessController(http.Controller):
    """Business logic endpoints - the REAL useful stuff!"""

    # ============= SALES ORDERS =============

    @http.route('/api/sales/dashboard', type='jsonrpc', auth='none', methods=['GET'], csrf=False, cors='*')
    @verify_token
    def sales_dashboard(self, **kwargs):
        """
        Get sales dashboard with aggregations
        Returns: revenue by state, top customers, monthly trends
        """
        try:
            SaleOrder = request.env['sale.order']

            # Revenue by state
            revenue_by_state = SaleOrder.read_group(
                domain=[],
                fields=['state', 'amount_total'],
                groupby=['state']
            )

            # Top 10 customers by revenue
            top_customers = SaleOrder.read_group(
                domain=[('state', 'in', ['sale', 'done'])],
                fields=['partner_id', 'amount_total'],
                groupby=['partner_id'],
                limit=10,
                orderby='amount_total desc'
            )

            # Monthly revenue (last 6 months)
            monthly_revenue = SaleOrder.read_group(
                domain=[('state', 'in', ['sale', 'done'])],
                fields=['date_order:month', 'amount_total'],
                groupby=['date_order:month'],
                limit=6,
                orderby='date_order:month desc'
            )

            # Count by salesperson
            by_salesperson = SaleOrder.read_group(
                domain=[('state', 'in', ['sale', 'done'])],
                fields=['user_id', 'amount_total'],
                groupby=['user_id']
            )

            return {
                'success': True,
                'data': {
                    'revenue_by_state': revenue_by_state,
                    'top_customers': top_customers,
                    'monthly_revenue': monthly_revenue,
                    'by_salesperson': by_salesperson
                }
            }

        except Exception as e:
            _logger.exception("Error in sales dashboard")
            return {'error': str(e), 'status': 500}

    @http.route('/api/sales/confirm/<int:order_id>', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def confirm_sale_order(self, order_id, **kwargs):
        """
        Confirm a sales order - triggers business logic:
        - Creates delivery orders
        - Reserves stock
        - Updates invoice status
        - Sends confirmation email
        """
        try:
            order = request.env['sale.order'].browse(order_id)
            if not order.exists():
                return {'error': 'Order not found', 'status': 404}

            # This triggers ALL the business logic
            order.action_confirm()

            return {
                'success': True,
                'message': 'Order confirmed',
                'data': {
                    'order_id': order.id,
                    'name': order.name,
                    'state': order.state,
                    'delivery_count': order.delivery_count,
                    'invoice_status': order.invoice_status
                }
            }

        except Exception as e:
            _logger.exception(f"Error confirming order {order_id}")
            return {'error': str(e), 'status': 500}

    @http.route('/api/sales/<int:order_id>/create_invoice', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def create_invoice(self, order_id, **kwargs):
        """Create invoice from sales order"""
        try:
            order = request.env['sale.order'].browse(order_id)
            if not order.exists():
                return {'error': 'Order not found', 'status': 404}

            # Create invoice - triggers invoicing logic
            invoice = order._create_invoices()

            return {
                'success': True,
                'data': {
                    'invoice_id': invoice.id,
                    'invoice_name': invoice.name,
                    'amount_total': invoice.amount_total,
                    'state': invoice.state
                }
            }

        except Exception as e:
            _logger.exception(f"Error creating invoice for order {order_id}")
            return {'error': str(e), 'status': 500}

    # ============= INVENTORY =============

    @http.route('/api/inventory/stock_levels', type='jsonrpc', auth='none', methods=['GET'], csrf=False, cors='*')
    @verify_token
    def stock_levels(self, **kwargs):
        """
        Get current stock levels with alerts
        """
        try:
            Product = request.env['product.product']

            # Products with low stock
            low_stock = Product.search([
                ('type', '=', 'product'),
                ('qty_available', '<', 10)
            ])

            # Aggregated stock by category
            stock_by_category = Product.read_group(
                domain=[('type', '=', 'product')],
                fields=['categ_id', 'qty_available', 'virtual_available'],
                groupby=['categ_id']
            )

            return {
                'success': True,
                'data': {
                    'low_stock_products': [
                        {
                            'id': p.id,
                            'name': p.name,
                            'qty_available': p.qty_available,
                            'virtual_available': p.virtual_available,
                            'incoming_qty': p.incoming_qty,
                            'outgoing_qty': p.outgoing_qty
                        }
                        for p in low_stock
                    ],
                    'stock_by_category': stock_by_category
                }
            }

        except Exception as e:
            _logger.exception("Error getting stock levels")
            return {'error': str(e), 'status': 500}

    @http.route('/api/inventory/validate_delivery/<int:picking_id>', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def validate_delivery(self, picking_id, **kwargs):
        """
        Validate delivery - triggers:
        - Stock movement
        - Update quantities
        - Invoice creation (if needed)
        """
        try:
            picking = request.env['stock.picking'].browse(picking_id)
            if not picking.exists():
                return {'error': 'Delivery not found', 'status': 404}

            # Validate delivery - triggers stock moves
            picking.button_validate()

            return {
                'success': True,
                'data': {
                    'picking_id': picking.id,
                    'name': picking.name,
                    'state': picking.state,
                    'products_moved': len(picking.move_ids)
                }
            }

        except Exception as e:
            _logger.exception(f"Error validating delivery {picking_id}")
            return {'error': str(e), 'status': 500}

    # ============= ACCOUNTING =============

    @http.route('/api/accounting/receivables', type='jsonrpc', auth='none', methods=['GET'], csrf=False, cors='*')
    @verify_token
    def receivables(self, **kwargs):
        """Get accounts receivable - who owes you money"""
        try:
            Invoice = request.env['account.move']

            # Unpaid invoices
            unpaid = Invoice.search([
                ('move_type', '=', 'out_invoice'),
                ('payment_state', 'in', ['not_paid', 'partial'])
            ])

            # Aging: 0-30, 30-60, 60-90, 90+ days
            from datetime import datetime, timedelta
            today = datetime.now()

            aging = {
                '0-30': 0,
                '30-60': 0,
                '60-90': 0,
                '90+': 0
            }

            for inv in unpaid:
                days_due = (today - inv.invoice_date).days
                amount = inv.amount_residual

                if days_due <= 30:
                    aging['0-30'] += amount
                elif days_due <= 60:
                    aging['30-60'] += amount
                elif days_due <= 90:
                    aging['60-90'] += amount
                else:
                    aging['90+'] += amount

            # Top debtors
            by_partner = Invoice.read_group(
                domain=[
                    ('move_type', '=', 'out_invoice'),
                    ('payment_state', 'in', ['not_paid', 'partial'])
                ],
                fields=['partner_id', 'amount_residual'],
                groupby=['partner_id'],
                orderby='amount_residual desc',
                limit=10
            )

            return {
                'success': True,
                'data': {
                    'total_unpaid': sum(inv.amount_residual for inv in unpaid),
                    'invoice_count': len(unpaid),
                    'aging_analysis': aging,
                    'top_debtors': by_partner
                }
            }

        except Exception as e:
            _logger.exception("Error getting receivables")
            return {'error': str(e), 'status': 500}

    @http.route('/api/accounting/post_invoice/<int:invoice_id>', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def post_invoice(self, invoice_id, **kwargs):
        """
        Post invoice - triggers:
        - Journal entries
        - Account moves
        - Tax calculations
        - Partner balance updates
        """
        try:
            invoice = request.env['account.move'].browse(invoice_id)
            if not invoice.exists():
                return {'error': 'Invoice not found', 'status': 404}

            # Post invoice - creates journal entries
            invoice.action_post()

            return {
                'success': True,
                'data': {
                    'invoice_id': invoice.id,
                    'name': invoice.name,
                    'state': invoice.state,
                    'amount_total': invoice.amount_total,
                    'payment_state': invoice.payment_state
                }
            }

        except Exception as e:
            _logger.exception(f"Error posting invoice {invoice_id}")
            return {'error': str(e), 'status': 500}

    # ============= REPORTS =============

    @http.route('/api/reports/profit_loss', type='jsonrpc', auth='none', methods=['GET'], csrf=False, cors='*')
    @verify_token
    def profit_loss(self, **kwargs):
        """Profit & Loss report"""
        try:
            # Get date range from params
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')

            domain = []
            if date_from:
                domain.append(('date', '>=', date_from))
            if date_to:
                domain.append(('date', '<=', date_to))

            AccountLine = request.env['account.move.line']

            # Revenue
            revenue = AccountLine.read_group(
                domain=domain + [('account_id.account_type', '=', 'income')],
                fields=['debit', 'credit'],
                groupby=[]
            )

            # Expenses
            expenses = AccountLine.read_group(
                domain=domain + [('account_id.account_type', '=', 'expense')],
                fields=['debit', 'credit'],
                groupby=[]
            )

            revenue_amount = revenue[0]['credit'] - revenue[0]['debit'] if revenue else 0
            expense_amount = expenses[0]['debit'] - expenses[0]['credit'] if expenses else 0
            profit = revenue_amount - expense_amount

            return {
                'success': True,
                'data': {
                    'revenue': revenue_amount,
                    'expenses': expense_amount,
                    'profit': profit,
                    'margin': (profit / revenue_amount * 100) if revenue_amount else 0
                }
            }

        except Exception as e:
            _logger.exception("Error generating P&L")
            return {'error': str(e), 'status': 500}

    # ============= CUSTOMERS =============

    @http.route('/api/customers/top', type='jsonrpc', auth='none', methods=['GET'], csrf=False, cors='*')
    @verify_token
    def top_customers(self, **kwargs):
        """Get top customers with analytics"""
        try:
            limit = kwargs.get('limit', 20)

            Partner = request.env['res.partner']
            SaleOrder = request.env['sale.order']

            # Top customers by revenue
            top = SaleOrder.read_group(
                domain=[('state', 'in', ['sale', 'done'])],
                fields=['partner_id', 'amount_total'],
                groupby=['partner_id'],
                orderby='amount_total desc',
                limit=limit
            )

            # Enrich with customer data
            result = []
            for item in top:
                partner = Partner.browse(item['partner_id'][0])
                result.append({
                    'partner_id': partner.id,
                    'name': partner.name,
                    'email': partner.email,
                    'phone': partner.phone,
                    'total_revenue': item['amount_total'],
                    'order_count': item['partner_id_count'],
                    'credit_limit': partner.credit_limit,
                    'credit': partner.credit,
                    'country': partner.country_id.name if partner.country_id else None
                })

            return {
                'success': True,
                'data': result
            }

        except Exception as e:
            _logger.exception("Error getting top customers")
            return {'error': str(e), 'status': 500}
