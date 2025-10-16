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

            # Set up Odoo environment
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


class APIController(http.Controller):
    """RESTful API endpoints for Odoo models"""

    @http.route('/api/<string:model>', type='jsonrpc', auth='none', methods=['GET'], csrf=False, cors='*')
    @verify_token
    def search_records(self, model, **kwargs):
        """
        Search records
        GET /api/sale.order?domain=[["state","=","sale"]]&fields=["name","partner_id"]&limit=10
        """
        try:
            domain = kwargs.get('domain', [])
            fields = kwargs.get('fields', [])
            limit = kwargs.get('limit', 80)
            offset = kwargs.get('offset', 0)
            order = kwargs.get('order', 'id desc')

            if isinstance(domain, str):
                domain = json.loads(domain)
            if isinstance(fields, str):
                fields = json.loads(fields)

            Model = request.env[model]

            if not Model.check_access_rights('read', raise_exception=False):
                return {'error': 'Access denied', 'status': 403}

            records = Model.search_read(
                domain=domain,
                fields=fields,
                limit=limit,
                offset=offset,
                order=order
            )

            return {
                'success': True,
                'data': records,
                'count': len(records)
            }

        except KeyError:
            return {'error': f'Model {model} not found', 'status': 404}
        except Exception as e:
            _logger.exception(f"Error searching {model}")
            return {'error': str(e), 'status': 500}

    @http.route('/api/<string:model>/<int:record_id>', type='jsonrpc', auth='none', methods=['GET'], csrf=False, cors='*')
    @verify_token
    def read_record(self, model, record_id, **kwargs):
        """
        Read single record
        GET /api/sale.order/42?fields=["name","partner_id","amount_total"]
        """
        try:
            fields = kwargs.get('fields', [])
            if isinstance(fields, str):
                fields = json.loads(fields)

            Model = request.env[model]

            if not Model.check_access_rights('read', raise_exception=False):
                return {'error': 'Access denied', 'status': 403}

            record = Model.browse(record_id)
            if not record.exists():
                return {'error': 'Record not found', 'status': 404}

            data = record.read(fields)[0] if fields else record.read()[0]

            return {
                'success': True,
                'data': data
            }

        except KeyError:
            return {'error': f'Model {model} not found', 'status': 404}
        except Exception as e:
            _logger.exception(f"Error reading {model}/{record_id}")
            return {'error': str(e), 'status': 500}

    @http.route('/api/<string:model>', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def create_record(self, model, **kwargs):
        """
        Create record
        POST /api/sale.order
        Body: {"vals": {"partner_id": 5, "date_order": "2025-10-14"}}
        """
        try:
            vals = kwargs.get('vals', {})

            Model = request.env[model]

            if not Model.check_access_rights('create', raise_exception=False):
                return {'error': 'Access denied', 'status': 403}

            record = Model.create(vals)

            return {
                'success': True,
                'data': {
                    'id': record.id,
                    **record.read()[0]
                }
            }

        except ValidationError as e:
            return {'error': str(e), 'status': 400}
        except KeyError:
            return {'error': f'Model {model} not found', 'status': 404}
        except Exception as e:
            _logger.exception(f"Error creating {model}")
            return {'error': str(e), 'status': 500}

    @http.route('/api/<string:model>/<int:record_id>', type='jsonrpc', auth='none', methods=['PUT', 'PATCH'], csrf=False, cors='*')
    @verify_token
    def update_record(self, model, record_id, **kwargs):
        """
        Update record
        PUT /api/sale.order/42
        Body: {"vals": {"state": "sale"}}
        """
        try:
            vals = kwargs.get('vals', {})

            Model = request.env[model]

            if not Model.check_access_rights('write', raise_exception=False):
                return {'error': 'Access denied', 'status': 403}

            record = Model.browse(record_id)
            if not record.exists():
                return {'error': 'Record not found', 'status': 404}

            record.write(vals)

            return {
                'success': True,
                'data': record.read()[0]
            }

        except ValidationError as e:
            return {'error': str(e), 'status': 400}
        except KeyError:
            return {'error': f'Model {model} not found', 'status': 404}
        except Exception as e:
            _logger.exception(f"Error updating {model}/{record_id}")
            return {'error': str(e), 'status': 500}

    @http.route('/api/<string:model>/<int:record_id>', type='jsonrpc', auth='none', methods=['DELETE'], csrf=False, cors='*')
    @verify_token
    def delete_record(self, model, record_id, **kwargs):
        """
        Delete record
        DELETE /api/sale.order/42
        """
        try:
            Model = request.env[model]

            if not Model.check_access_rights('unlink', raise_exception=False):
                return {'error': 'Access denied', 'status': 403}

            record = Model.browse(record_id)
            if not record.exists():
                return {'error': 'Record not found', 'status': 404}

            record.unlink()

            return {
                'success': True,
                'message': f'Record {record_id} deleted'
            }

        except UserError as e:
            return {'error': str(e), 'status': 400}
        except KeyError:
            return {'error': f'Model {model} not found', 'status': 404}
        except Exception as e:
            _logger.exception(f"Error deleting {model}/{record_id}")
            return {'error': str(e), 'status': 500}

    @http.route('/api/<string:model>/<int:record_id>/call/<string:method>', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def call_method(self, model, record_id, method, **kwargs):
        """
        Call custom method on record
        POST /api/sale.order/42/call/action_confirm
        Body: {"args": [], "kwargs": {}}
        """
        try:
            args = kwargs.get('args', [])
            method_kwargs = kwargs.get('kwargs', {})

            Model = request.env[model]
            record = Model.browse(record_id)

            if not record.exists():
                return {'error': 'Record not found', 'status': 404}

            if not hasattr(record, method):
                return {'error': f'Method {method} not found', 'status': 404}

            result = getattr(record, method)(*args, **method_kwargs)

            return {
                'success': True,
                'result': result
            }

        except AccessError:
            return {'error': 'Access denied', 'status': 403}
        except Exception as e:
            _logger.exception(f"Error calling {model}/{record_id}/{method}")
            return {'error': str(e), 'status': 500}

    @http.route('/api/<string:model>/call/<string:method>', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    @verify_token
    def call_model_method(self, model, method, **kwargs):
        """
        Call model-level method (not on a specific record)
        POST /api/sale.order/call/create_from_template
        Body: {"args": [template_id], "kwargs": {}}
        """
        try:
            args = kwargs.get('args', [])
            method_kwargs = kwargs.get('kwargs', {})

            Model = request.env[model]

            if not hasattr(Model, method):
                return {'error': f'Method {method} not found', 'status': 404}

            result = getattr(Model, method)(*args, **method_kwargs)

            return {
                'success': True,
                'result': result
            }

        except AccessError:
            return {'error': 'Access denied', 'status': 403}
        except Exception as e:
            _logger.exception(f"Error calling {model}/{method}")
            return {'error': str(e), 'status': 500}
