# -*- coding: utf-8 -*-
from odoo import models


class HrDepartment(models.Model):
    _name = 'hr.department'
    _inherit = ['hr.department', 'safee.webhook.mixin']

    def _get_webhook_endpoint(self):
        """Return webhook endpoint for departments"""
        return '/webhooks/odoo/departments'
