# -*- coding: utf-8 -*-
from odoo import models


class CrmLead(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'safee.webhook.mixin']

    def _get_webhook_endpoint(self):
        """Return webhook endpoint for leads/opportunities"""
        return '/webhooks/odoo/leads'
