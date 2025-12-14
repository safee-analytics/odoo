# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    safee_webhooks_enabled = fields.Boolean(
        string='Enable Safee Webhooks',
        config_parameter='safee.webhooks_enabled',
    )
    safee_webhook_url = fields.Char(
        string='Safee Webhook URL',
        config_parameter='safee.webhook_url',
        help='Base URL for Safee webhooks (e.g., https://api.safee.analytics)',
    )
    safee_webhook_secret = fields.Char(
        string='Webhook Secret',
        config_parameter='safee.webhook_secret',
        help='Secret key for HMAC-SHA256 signature verification',
    )
    safee_organization_id = fields.Char(
        string='Organization ID',
        config_parameter='safee.organization_id',
        help='Your Safee organization ID',
    )
