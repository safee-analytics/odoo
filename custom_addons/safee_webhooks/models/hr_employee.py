# -*- coding: utf-8 -*-
from odoo import models


class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'safee.webhook.mixin']

    def _get_webhook_endpoint(self):
        """Return webhook endpoint for employees"""
        return '/webhooks/odoo/employees'
