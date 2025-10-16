# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class OpenAPIController(http.Controller):
    """OpenAPI/Swagger documentation endpoint"""

    @http.route('/api/docs', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def openapi_docs(self, **kwargs):
        """
        OpenAPI 3.0 Documentation
        Access at: http://localhost:8069/api/docs
        """
        openapi_spec = self._generate_openapi_spec()
        openapi_spec_json = json.dumps(openapi_spec)

        # Return Swagger UI HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Odoo REST API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    <style>
        body {{ margin: 0; padding: 0; }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                spec: {openapi_spec_json},
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            }})
        }}
    </script>
</body>
</html>"""
        return request.make_response(html, headers=[('Content-Type', 'text/html')])

    @http.route('/api/openapi.json', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def openapi_json(self, **kwargs):
        """Return OpenAPI spec as JSON"""
        spec = self._generate_openapi_spec()
        return request.make_response(
            json.dumps(spec),
            headers=[('Content-Type', 'application/json')]
        )

    def _generate_openapi_spec(self):
        """Generate OpenAPI 3.0 specification"""

        # Get available models (you can customize this list)
        common_models = [
            'sale.order',
            'sale.order.line',
            'res.partner',
            'product.product',
            'product.template',
            'account.move',
            'account.move.line',
            'stock.picking',
            'purchase.order',
            'hr.employee',
            'project.project',
            'project.task',
        ]

        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Odoo REST API",
                "version": "1.0.0",
                "description": "RESTful API for Odoo ERP system with JWT authentication",
                "contact": {
                    "name": "API Support",
                    "url": "https://yourcompany.com/support",
                    "email": "support@yourcompany.com"
                }
            },
            "servers": [
                {
                    "url": request.httprequest.host_url.rstrip('/'),
                    "description": "Current Odoo Instance"
                }
            ],
            "tags": [
                {"name": "Authentication", "description": "JWT authentication endpoints"},
                {"name": "Discovery", "description": "Discover available models, methods, and fields"},
                {"name": "CRUD Operations", "description": "Create, Read, Update, Delete operations"},
                {"name": "Custom Methods", "description": "Call custom model methods"},
                {"name": "Sales", "description": "Sales order operations"},
                {"name": "Products", "description": "Product operations"},
                {"name": "Partners", "description": "Partner/Customer operations"},
            ],
            "paths": {
                "/api/auth/login": {
                    "post": {
                        "tags": ["Authentication"],
                        "summary": "Login and get JWT token",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["login", "password"],
                                        "properties": {
                                            "login": {"type": "string", "example": "admin"},
                                            "password": {"type": "string", "example": "admin"},
                                            "db": {"type": "string", "example": "odoo"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/LoginResponse"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/auth/me": {
                    "get": {
                        "tags": ["Authentication"],
                        "summary": "Get current user info",
                        "security": [{"BearerAuth": []}],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/User"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/discover/models": {
                    "get": {
                        "tags": ["Discovery"],
                        "summary": "List all available models",
                        "description": "Discover all Odoo models you can use with the CRUD API (No auth required)",
                        "parameters": [
                            {
                                "name": "search",
                                "in": "query",
                                "description": "Search filter for model names",
                                "schema": {"type": "string"},
                                "example": "sale"
                            },
                            {
                                "name": "limit",
                                "in": "query",
                                "description": "Maximum number of results",
                                "schema": {"type": "integer", "default": 100}
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "success": {"type": "boolean"},
                                                "data": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "model": {"type": "string", "example": "sale.order"},
                                                            "name": {"type": "string", "example": "Sales Order"},
                                                            "info": {"type": "string"}
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/discover/methods/{model}": {
                    "get": {
                        "tags": ["Discovery"],
                        "summary": "List all methods for a model",
                        "description": "Discover all callable methods (action_*, create, write, etc.) for a specific model (No auth required)",
                        "parameters": [
                            {
                                "name": "model",
                                "in": "path",
                                "required": True,
                                "description": "Model name (e.g. sale.order)",
                                "schema": {"type": "string"},
                                "example": "sale.order"
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "success": {"type": "boolean"},
                                                "model": {"type": "string"},
                                                "method_count": {"type": "integer"},
                                                "data": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "name": {"type": "string", "example": "action_confirm"},
                                                            "doc": {"type": "string", "example": "Confirm the sales order"}
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/discover/method/{model}/{method}": {
                    "get": {
                        "tags": ["Discovery"],
                        "summary": "Get detailed info about a specific method",
                        "description": "Get documentation and signature for a specific method (No auth required)",
                        "parameters": [
                            {
                                "name": "model",
                                "in": "path",
                                "required": True,
                                "description": "Model name (e.g. sale.order)",
                                "schema": {"type": "string"},
                                "example": "sale.order"
                            },
                            {
                                "name": "method",
                                "in": "path",
                                "required": True,
                                "description": "Method name (e.g. action_confirm)",
                                "schema": {"type": "string"},
                                "example": "action_confirm"
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "success": {"type": "boolean"},
                                                "model": {"type": "string"},
                                                "method": {"type": "string"},
                                                "data": {
                                                    "type": "object",
                                                    "properties": {
                                                        "name": {"type": "string"},
                                                        "doc": {"type": "string"},
                                                        "signature": {"type": "string"},
                                                        "is_private": {"type": "boolean"},
                                                        "module": {"type": "string"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/discover/fields/{model}": {
                    "get": {
                        "tags": ["Discovery"],
                        "summary": "List all fields for a model",
                        "description": "Discover all fields (columns) available in a model with their types and properties (No auth required)",
                        "parameters": [
                            {
                                "name": "model",
                                "in": "path",
                                "required": True,
                                "description": "Model name (e.g. sale.order)",
                                "schema": {"type": "string"},
                                "example": "sale.order"
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "success": {"type": "boolean"},
                                                "model": {"type": "string"},
                                                "field_count": {"type": "integer"},
                                                "data": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "name": {"type": "string", "example": "partner_id"},
                                                            "type": {"type": "string", "example": "many2one"},
                                                            "string": {"type": "string", "example": "Customer"},
                                                            "help": {"type": "string"},
                                                            "required": {"type": "boolean"},
                                                            "readonly": {"type": "boolean"}
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
            },
            "components": {
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                },
                "schemas": {
                    "LoginResponse": {
                        "type": "object",
                        "properties": {
                            "access_token": {"type": "string"},
                            "token_type": {"type": "string", "example": "Bearer"},
                            "expires_in": {"type": "integer", "example": 86400},
                            "user": {"$ref": "#/components/schemas/User"}
                        }
                    },
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "login": {"type": "string"},
                            "email": {"type": "string"},
                            "company_id": {"type": "integer"},
                            "company_name": {"type": "string"}
                        }
                    },
                    "Error": {
                        "type": "object",
                        "properties": {
                            "error": {"type": "string"},
                            "status": {"type": "integer"}
                        }
                    }
                }
            }
        }

        # Add CRUD endpoints for each model
        for model in common_models:
            model_name = model.replace('.', '_')
            spec["paths"][f"/api/{model}"] = {
                "get": {
                    "tags": ["CRUD Operations"],
                    "summary": f"Search {model} records",
                    "security": [{"BearerAuth": []}],
                    "parameters": [
                        {
                            "name": "domain",
                            "in": "query",
                            "schema": {"type": "string"},
                            "example": '[[\"state\",\"=\",\"sale\"]]'
                        },
                        {
                            "name": "fields",
                            "in": "query",
                            "schema": {"type": "string"},
                            "example": '[\"name\",\"partner_id\",\"amount_total\"]'
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "schema": {"type": "integer", "default": 80}
                        },
                        {
                            "name": "offset",
                            "in": "query",
                            "schema": {"type": "integer", "default": 0}
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "data": {"type": "array", "items": {"type": "object"}},
                                            "count": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["CRUD Operations"],
                    "summary": f"Create {model} record",
                    "security": [{"BearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "vals": {"type": "object"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Success"}
                    }
                }
            }

            spec["paths"][f"/api/{model}/{{record_id}}"] = {
                "get": {
                    "tags": ["CRUD Operations"],
                    "summary": f"Read {model} record",
                    "security": [{"BearerAuth": []}],
                    "parameters": [
                        {
                            "name": "record_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {"description": "Success"}
                    }
                },
                "put": {
                    "tags": ["CRUD Operations"],
                    "summary": f"Update {model} record",
                    "security": [{"BearerAuth": []}],
                    "parameters": [
                        {
                            "name": "record_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "vals": {"type": "object"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Success"}
                    }
                },
                "delete": {
                    "tags": ["CRUD Operations"],
                    "summary": f"Delete {model} record",
                    "security": [{"BearerAuth": []}],
                    "parameters": [
                        {
                            "name": "record_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {"description": "Success"}
                    }
                }
            }

        return spec
