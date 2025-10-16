# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""
Discovery API - Find available models and methods
"""

import json
import logging
import jwt
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

JWT_SECRET = 'your-secret-key-change-this-in-production'
JWT_ALGORITHM = 'HS256'


def verify_token_http(func):
    """Decorator to verify JWT token for HTTP endpoints"""
    def wrapper(self, *args, **kwargs):
        try:
            auth_header = request.httprequest.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return request.make_response(
                    json.dumps({'error': 'Missing or invalid authorization header', 'status': 401}),
                    headers=[('Content-Type', 'application/json')],
                    status=401
                )

            token = auth_header[7:]
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

            db = payload.get('db')
            uid = payload.get('uid')

            request.session.db = db
            request.env.uid = uid
            request.uid = uid

            return func(self, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            return request.make_response(
                json.dumps({'error': 'Token expired', 'status': 401}),
                headers=[('Content-Type', 'application/json')],
                status=401
            )
        except jwt.InvalidTokenError:
            return request.make_response(
                json.dumps({'error': 'Invalid token', 'status': 401}),
                headers=[('Content-Type', 'application/json')],
                status=401
            )
        except Exception as e:
            _logger.exception("Token verification error")
            return request.make_response(
                json.dumps({'error': str(e), 'status': 500}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    return wrapper


class DiscoveryController(http.Controller):
    """Discover available models and methods"""

    @http.route('/api/discover/models', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def list_models(self, **kwargs):
        """
        List all available models
        GET /api/discover/models?search=sale
        """
        try:
            search = kwargs.get('search', '')
            limit = kwargs.get('limit', 100)

            # Get all models
            IrModel = request.env['ir.model']
            domain = [('transient', '=', False)]  # Exclude temporary models

            if search:
                domain.append(('model', 'ilike', search))

            models = IrModel.search(domain, limit=limit, order='model')

            result = {
                'success': True,
                'data': [{
                    'model': m.model,
                    'name': m.name,
                    'info': m.info,
                } for m in models]
            }
            return request.make_response(
                json.dumps(result),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.exception("Error listing models")
            return request.make_response(
                json.dumps({'error': str(e), 'status': 500}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/api/discover/methods/<string:model>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def list_methods(self, model, **kwargs):
        """
        List all available methods for a model
        GET /api/discover/methods/sale.order
        """
        try:
            Model = request.env[model]

            # Get all public methods (don't start with _)
            all_attrs = dir(Model)

            # Filter to only public methods
            public_methods = []
            for attr_name in all_attrs:
                # Skip private methods
                if attr_name.startswith('_'):
                    continue

                # Skip magic methods
                if attr_name.startswith('__'):
                    continue

                # Get the attribute
                attr = getattr(Model, attr_name, None)

                # Check if it's callable (a method)
                if callable(attr):
                    # Try to get docstring
                    doc = attr.__doc__ or "No documentation available"

                    public_methods.append({
                        'name': attr_name,
                        'doc': doc.strip() if doc else None
                    })

            # Sort by name
            public_methods.sort(key=lambda x: x['name'])

            result = {
                'success': True,
                'model': model,
                'method_count': len(public_methods),
                'data': public_methods
            }
            return request.make_response(
                json.dumps(result),
                headers=[('Content-Type', 'application/json')]
            )

        except KeyError:
            return request.make_response(
                json.dumps({'error': f'Model {model} not found', 'status': 404}),
                headers=[('Content-Type', 'application/json')],
                status=404
            )
        except Exception as e:
            _logger.exception(f"Error listing methods for {model}")
            return request.make_response(
                json.dumps({'error': str(e), 'status': 500}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/api/discover/method/<string:model>/<string:method>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def method_info(self, model, method, **kwargs):
        """
        Get detailed info about a specific method
        GET /api/discover/method/sale.order/action_confirm
        """
        try:
            Model = request.env[model]

            if not hasattr(Model, method):
                return request.make_response(
                    json.dumps({'error': f'Method {method} not found on {model}', 'status': 404}),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            method_obj = getattr(Model, method)

            if not callable(method_obj):
                return request.make_response(
                    json.dumps({'error': f'{method} is not a method', 'status': 400}),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            # Get method details
            import inspect

            result = {
                'success': True,
                'model': model,
                'method': method,
                'data': {
                    'name': method,
                    'doc': method_obj.__doc__ or "No documentation",
                    'signature': str(inspect.signature(method_obj)) if hasattr(inspect, 'signature') else None,
                    'is_private': method.startswith('_'),
                    'module': method_obj.__module__ if hasattr(method_obj, '__module__') else None,
                }
            }
            return request.make_response(
                json.dumps(result),
                headers=[('Content-Type', 'application/json')]
            )

        except KeyError:
            return request.make_response(
                json.dumps({'error': f'Model {model} not found', 'status': 404}),
                headers=[('Content-Type', 'application/json')],
                status=404
            )
        except Exception as e:
            _logger.exception(f"Error getting method info for {model}.{method}")
            return request.make_response(
                json.dumps({'error': str(e), 'status': 500}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/api/discover/fields/<string:model>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def list_fields(self, model, **kwargs):
        """
        List all fields for a model
        GET /api/discover/fields/sale.order
        """
        try:
            Model = request.env[model]

            # Get field definitions
            fields_info = Model.fields_get()

            # Format nicely
            fields_list = []
            for field_name, field_data in fields_info.items():
                fields_list.append({
                    'name': field_name,
                    'type': field_data.get('type'),
                    'string': field_data.get('string'),
                    'help': field_data.get('help'),
                    'required': field_data.get('required', False),
                    'readonly': field_data.get('readonly', False),
                })

            result = {
                'success': True,
                'model': model,
                'field_count': len(fields_list),
                'data': fields_list
            }
            return request.make_response(
                json.dumps(result),
                headers=[('Content-Type', 'application/json')]
            )

        except KeyError:
            return request.make_response(
                json.dumps({'error': f'Model {model} not found', 'status': 404}),
                headers=[('Content-Type', 'application/json')],
                status=404
            )
        except Exception as e:
            _logger.exception(f"Error listing fields for {model}")
            return request.make_response(
                json.dumps({'error': str(e), 'status': 500}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )
