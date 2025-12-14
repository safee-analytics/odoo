# -*- coding: utf-8 -*-
from odoo import models


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'safee.webhook.mixin']

    def _get_webhook_endpoint(self):
        """Return webhook endpoint for contacts"""
        return '/webhooks/odoo/contacts'
