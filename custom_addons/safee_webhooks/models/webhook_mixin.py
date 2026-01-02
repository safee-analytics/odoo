# -*- coding: utf-8 -*-
import hmac
import hashlib
import json
import logging
import requests
from datetime import datetime
from odoo import models, api

_logger = logging.getLogger(__name__)


class SafeeWebhookMixin(models.AbstractModel):
    """
    Mixin for sending webhooks to Safee Analytics
    Provides common webhook functionality for all models
    """
    _name = 'safee.webhook.mixin'
    _description = 'Safee Webhook Mixin'

    def _get_safee_config(self):
        """Get Safee configuration from system parameters"""
        IrConfigParameter = self.env['ir.config_parameter'].sudo()

        return {
            'webhook_url': IrConfigParameter.get_param('safee.webhook_url', ''),
            'webhook_secret': IrConfigParameter.get_param('safee.webhook_secret', ''),
            'organization_id': IrConfigParameter.get_param('safee.organization_id', ''),
            'enabled': IrConfigParameter.get_param('safee.webhooks_enabled', 'False') == 'True',
        }

    def _derive_org_secret(self, master_secret, organization_id):
        """
        Derive per-organization webhook secret from master secret
        Must match the derivation in gateway webhookVerification.ts:
        crypto.createHmac("sha256", masterSecret).update(organizationId).digest("hex")
        """
        return hmac.new(
            master_secret.encode('utf-8'),
            organization_id.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _compute_signature(self, payload_json, secret):
        """Compute HMAC-SHA256 signature for webhook payload"""
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _send_safee_webhook(self, event, endpoint_path):
        """
        Send webhook to Safee Analytics

        Args:
            event: 'create', 'write', or 'unlink'
            endpoint_path: API endpoint path (e.g., '/webhooks/odoo/employees')
        """
        config = self._get_safee_config()

        # Skip if webhooks disabled
        if not config['enabled']:
            _logger.debug('Safee webhooks disabled, skipping')
            return

        # Validate configuration
        if not config['webhook_url'] or not config['webhook_secret'] or not config['organization_id']:
            _logger.warning('Safee webhook configuration incomplete, skipping webhook')
            return

        # Get current user
        user_id = self.env.user.id

        # Build payload
        payload = {
            'event': event,
            'model': self._name,
            'record_id': self.id,
            'organization_id': config['organization_id'],
            'user_id': str(user_id),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }

        payload_json = json.dumps(payload, sort_keys=True)

        # Derive per-org secret from master secret (matches gateway logic)
        org_secret = self._derive_org_secret(config['webhook_secret'], config['organization_id'])
        signature = self._compute_signature(payload_json, org_secret)

        # Build full URL
        webhook_url = config['webhook_url'].rstrip('/') + endpoint_path

        # Send webhook
        try:
            headers = {
                'Content-Type': 'application/json',
                'X-Odoo-Signature': signature,
            }

            response = requests.post(
                webhook_url,
                data=payload_json,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                _logger.info(
                    'Safee webhook sent successfully: %s %s (record_id=%s)',
                    event, self._name, self.id
                )
            else:
                _logger.warning(
                    'Safee webhook failed: %s %s (record_id=%s) - Status: %s, Response: %s',
                    event, self._name, self.id, response.status_code, response.text
                )

        except Exception as e:
            _logger.error(
                'Failed to send Safee webhook: %s %s (record_id=%s) - Error: %s',
                event, self._name, self.id, str(e)
            )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to send webhook"""
        records = super(SafeeWebhookMixin, self).create(vals_list)
        for record in records:
            record._send_webhook_after_commit('create')
        return records

    def write(self, vals):
        """Override write to send webhook"""
        result = super(SafeeWebhookMixin, self).write(vals)
        for record in self:
            record._send_webhook_after_commit('write')
        return result

    def unlink(self):
        """Override unlink to send webhook"""
        for record in self:
            record._send_webhook_after_commit('unlink')
        return super(SafeeWebhookMixin, self).unlink()

    def _send_webhook_after_commit(self, event):
        """Queue webhook to be sent after transaction commit"""
        endpoint_path = self._get_webhook_endpoint()

        @self.env.cr.postcommit.add
        def send_webhook():
            self._send_safee_webhook(event, endpoint_path)

    def _get_webhook_endpoint(self):
        """
        Override this method in each model to specify the webhook endpoint
        Must be implemented by inheriting models
        """
        raise NotImplementedError('_get_webhook_endpoint must be implemented')
