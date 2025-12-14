# -*- coding: utf-8 -*-
from odoo import models


class HrLeave(models.Model):
    _name = 'hr.leave'
    _inherit = ['hr.leave', 'safee.webhook.mixin']

    def _get_webhook_endpoint(self):
        """Return webhook endpoint for leave requests"""
        return '/webhooks/odoo/leaves'
