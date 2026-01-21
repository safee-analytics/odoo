# -*- coding: utf-8 -*-
import hmac
import hashlib
import json
import logging
import requests
from datetime import datetime

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """
    Called when the module is installed.
    Sends a webhook notification that the database is ready using Safee webhook infrastructure.
    """
    db_name = env.cr.dbname
    _logger.info('Database %s initialization complete, sending ready webhook', db_name)

    IrConfigParameter = env['ir.config_parameter'].sudo()

    webhook_url = IrConfigParameter.get_param('safee.webhook_url', '')
    webhook_secret = IrConfigParameter.get_param('safee.webhook_secret', '')
    organization_id = IrConfigParameter.get_param('safee.organization_id', '')

    if not webhook_url or not webhook_secret:
        _logger.info('Webhook not configured yet, skipping database_ready notification')
        IrConfigParameter.set_param('safee.database_ready', 'True')
        return

    payload = {
        'event': 'database_ready',
        'model': 'ir.module.module',
        'record_id': 0,
        'organization_id': organization_id,
        'database': db_name,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
    }

    payload_json = json.dumps(payload, sort_keys=True)

    org_secret = hmac.new(
        webhook_secret.encode('utf-8'),
        organization_id.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    signature = hmac.new(
        org_secret.encode('utf-8'),
        payload_json.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    try:
        response = requests.post(
            webhook_url.rstrip('/') + '/webhooks/odoo/database-ready',
            data=payload_json,
            headers={
                'Content-Type': 'application/json',
                'X-Odoo-Signature': signature,
            },
            timeout=10
        )
        _logger.info(
            'Database ready webhook sent for %s: status=%s',
            db_name, response.status_code
        )
    except Exception as e:
        _logger.warning(
            'Failed to send database ready webhook for %s: %s',
            db_name, str(e)
        )

    IrConfigParameter.set_param('safee.database_ready', 'True')
    _logger.info('Set safee.database_ready=True for database %s', db_name)
