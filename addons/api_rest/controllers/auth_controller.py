# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
from datetime import datetime, timedelta
import jwt
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

# Configure this secret in your config file or environment variable
JWT_SECRET = 'your-secret-key-change-this-in-production'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24


class AuthController(http.Controller):
    """Authentication endpoints for JWT-based auth"""

    @http.route('/api/auth/login', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    def login(self, **kwargs):
        """
        Login endpoint
        POST /api/auth/login
        Body: {"login": "admin", "password": "admin", "db": "odoo"}
        Returns: {"access_token": "jwt_token", "user": {...}}
        """
        try:
            login = kwargs.get('login')
            password = kwargs.get('password')
            db = kwargs.get('db', request.db)

            if not all([login, password]):
                return {
                    'error': 'Missing login or password',
                    'status': 400
                }

            # Authenticate user
            uid = request.session.authenticate(db, login, password)

            if not uid:
                return {
                    'error': 'Invalid credentials',
                    'status': 401
                }

            # Get user info
            user = request.env['res.users'].browse(uid)

            # Generate JWT token
            payload = {
                'uid': uid,
                'login': login,
                'db': db,
                'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
                'iat': datetime.utcnow()
            }

            token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

            return {
                'access_token': token,
                'token_type': 'Bearer',
                'expires_in': JWT_EXPIRATION_HOURS * 3600,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'login': user.login,
                    'email': user.email,
                    'company_id': user.company_id.id,
                    'company_name': user.company_id.name,
                }
            }

        except Exception as e:
            _logger.exception("Login error")
            return {
                'error': str(e),
                'status': 500
            }

    @http.route('/api/auth/me', type='jsonrpc', auth='none', methods=['GET'], csrf=False, cors='*')
    def me(self, **kwargs):
        """
        Get current user info
        GET /api/auth/me
        Headers: Authorization: Bearer <token>
        """
        try:
            # Extract and verify token
            token = self._get_token_from_header()
            if not token:
                return {'error': 'Missing authorization token', 'status': 401}

            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            uid = payload.get('uid')

            # Switch to the user's database and load user
            request.session.db = payload.get('db')
            request.env.uid = uid

            user = request.env['res.users'].browse(uid)

            return {
                'id': user.id,
                'name': user.name,
                'login': user.login,
                'email': user.email,
                'company_id': user.company_id.id,
                'company_name': user.company_id.name,
            }

        except jwt.ExpiredSignatureError:
            return {'error': 'Token expired', 'status': 401}
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token', 'status': 401}
        except Exception as e:
            _logger.exception("Auth error")
            return {'error': str(e), 'status': 500}

    def _get_token_from_header(self):
        """Extract JWT token from Authorization header"""
        auth_header = request.httprequest.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        return None

    @http.route('/api/auth/refresh', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
    def refresh_token(self, **kwargs):
        """
        Refresh JWT token
        POST /api/auth/refresh
        Headers: Authorization: Bearer <token>
        """
        try:
            token = self._get_token_from_header()
            if not token:
                return {'error': 'Missing authorization token', 'status': 401}

            # Decode without verifying expiration
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})

            # Generate new token
            new_payload = {
                'uid': payload['uid'],
                'login': payload['login'],
                'db': payload['db'],
                'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
                'iat': datetime.utcnow()
            }

            new_token = jwt.encode(new_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

            return {
                'access_token': new_token,
                'token_type': 'Bearer',
                'expires_in': JWT_EXPIRATION_HOURS * 3600,
            }

        except jwt.InvalidTokenError:
            return {'error': 'Invalid token', 'status': 401}
        except Exception as e:
            _logger.exception("Token refresh error")
            return {'error': str(e), 'status': 500}
