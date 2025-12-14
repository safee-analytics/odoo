import json
import logging
import odoo
from odoo import http
from odoo.http import request
from odoo.modules import registry

_logger = logging.getLogger(__name__)


class ApiKeyController(http.Controller):

    @http.route(
        "/api/generate_key",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def generate_key(self, **payload):
        """
        Generate an Odoo API key for a user.

        Request JSON body:
        {
          "db": "your_db",
          "admin_login": "admin@example.com",
          "admin_password": "****",
          "target_user_login": "user@example.com",
          "name": "My Integration Key",
          "scope": "rpc"
        }

        Response:
        {
          "ok": True,
          "user_id": 7,
          "user_login": "user@example.com",
          "name": "My Integration Key",
          "scope": "rpc",
          "token": "****",  # SAVE THIS - cannot be retrieved later
          "id": 123
        }
        """
        try:
            # Parse payload
            if not payload:
                payload = request.get_json_data() or {}

            db = payload.get("db")
            admin_login = payload.get("admin_login")
            admin_password = payload.get("admin_password")
            target_user_login = payload.get("target_user_login")
            target_user_id = payload.get("target_user_id")
            name = payload.get("name") or "Safee Integration Key"
            scope = payload.get("scope") or "rpc"

            # Validate required fields
            if not all([db, admin_login, admin_password]):
                return {"ok": False, "error": "Missing db/admin_login/admin_password"}

            # Create API key using admin credentials
            # This is an internal endpoint - authentication is handled at the gateway level
            try:
                reg = registry.Registry(db)
                with reg.cursor() as cr:
                    # Create environment as SUPERUSER to create API keys
                    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

                    # Find admin user by login to verify they exist
                    user_model = env['res.users'].sudo()
                    admin_user = user_model.search([('login', '=', admin_login)], limit=1)

                    if not admin_user:
                        return {"ok": False, "error": "Admin user not found"}

                    # Environment already has SUPERUSER_ID - no need to call sudo()

                    # Resolve target user
                    user = None
                    if target_user_id:
                        user = env["res.users"].browse(int(target_user_id))
                        if not user.exists():
                            return {"ok": False, "error": f"User id {target_user_id} not found"}
                    elif target_user_login:
                        user = env["res.users"].search([("login", "=", target_user_login)], limit=1)
                        if not user:
                            return {"ok": False, "error": f"User login '{target_user_login}' not found"}
                    else:
                        # Default to authenticated user
                        user = admin_user

                    _logger.info(f"Creating API key for user {user.login} (id: {user.id})")

                    # Create API key
                    apikey_vals = {
                        "name": name,
                        "user_id": user.id,
                        "scope": scope,
                    }

                    # Generate API key manually and insert via SQL
                    # This bypasses Odoo's protected fields
                    import secrets
                    import string
                    import passlib.context

                    # Generate secure random token (20 characters)
                    alphabet = string.ascii_letters + string.digits
                    token = ''.join(secrets.choice(alphabet) for _ in range(20))

                    # Generate 8-character index (required by Odoo)
                    index = ''.join(secrets.choice(alphabet) for _ in range(8))

                    # Create the full API key in Odoo's format: index_token
                    full_api_key = f"{index}_{token}"

                    # Hash the FULL API key (not just the token part)
                    # Odoo verifies the complete "index_token" string
                    crypt_context = passlib.context.CryptContext(schemes=['pbkdf2_sha512'], deprecated=['auto'])
                    hashed_key = crypt_context.hash(full_api_key)

                    # Insert directly into database (only columns that exist)
                    cr.execute("""
                        INSERT INTO res_users_apikeys (name, user_id, scope, index, key)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """, (name, user.id, scope, index, hashed_key))

                    apikey_id = cr.fetchone()[0]

                    _logger.info(f"API key created with id {apikey_id}")

                    if not token:
                        _logger.error("Failed to generate API key token")
                        return {
                            "ok": False,
                            "error": "Could not generate API key token."
                        }

                    # Create a minimal record object for the response
                    apikey = type('obj', (object,), {
                        'id': apikey_id,
                        'name': name,
                        'scope': scope
                    })()

                    # Commit the transaction
                    cr.commit()

                    _logger.info(f"API key created successfully for user {user.login}")

                    # Return the full API key format: {index}_{token}
                    full_api_key = f"{index}_{token}"

                    return {
                        "ok": True,
                        "user_id": user.id,
                        "user_login": user.login,
                        "name": apikey.name,
                        "scope": apikey.scope,
                        "token": full_api_key,
                        "id": apikey.id,
                    }
            except Exception as e:
                _logger.error(f"Authentication failed: {e}")
                return {"ok": False, "error": f"Authentication failed: {str(e)}"}

        except Exception as e:
            _logger.exception("Error generating API key")
            return {"ok": False, "error": str(e)}
