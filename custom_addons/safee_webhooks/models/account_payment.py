# -*- coding: utf-8 -*-
from odoo import models


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['account.payment', 'safee.webhook.mixin']

    def _get_webhook_endpoint(self):
        """Return webhook endpoint for payments"""
        return '/webhooks/odoo/payments'
