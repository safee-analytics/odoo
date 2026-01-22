import logging
import odoo
from odoo import http
from odoo.http import request, Response
from odoo.service import db as db_service

_logger = logging.getLogger(__name__)


class SafeeDbManagerController(http.Controller):

    @http.route(
        "/safee/db/close_connections",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def close_connections(self, master_pwd, db_name):
        try:
            db_service.check_super(master_pwd)
        except Exception as e:
            _logger.warning("Unauthorized close_connections attempt for db: %s", db_name)
            return {"success": False, "error": "Unauthorized"}

        try:
            _logger.info("Closing Odoo connection pool for database: %s", db_name)
            odoo.sql_db.close_db(db_name)
            _logger.info("Successfully closed connections to database: %s", db_name)
            return {"success": True, "message": f"Closed connections to {db_name}"}
        except Exception as e:
            _logger.exception("Failed to close connections to database: %s", db_name)
            return {"success": False, "error": str(e)}

    @http.route(
        "/safee/db/duplicate",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def duplicate_database(self, master_pwd, source_db, new_db, neutralize=False):
        try:
            db_service.check_super(master_pwd)
        except Exception as e:
            _logger.warning("Unauthorized duplicate attempt: %s -> %s", source_db, new_db)
            return {"success": False, "error": "Unauthorized"}

        try:
            _logger.info("Duplicating database: %s -> %s", source_db, new_db)

            try:
                db = odoo.sql_db.db_connect("neondb")
                with db.cursor() as cr:
                    cr.execute("""
                        SELECT pid, usename, application_name, client_addr, state, query
                        FROM pg_stat_activity
                        WHERE datname = %s
                    """, (source_db,))
                    connections = cr.fetchall()
                    _logger.info("Active connections to %s: %d", source_db, len(connections))
                    for conn in connections:
                        _logger.info("  Connection: pid=%s user=%s app=%s addr=%s state=%s query=%s",
                            conn[0], conn[1], conn[2], conn[3], conn[4], conn[5][:100] if conn[5] else None)
            except Exception as diag_err:
                _logger.warning("Could not get connection diagnostics: %s", diag_err)

            max_retries = 3
            last_error = None

            for attempt in range(max_retries):
                try:
                    db_service.exp_duplicate_database(source_db, new_db, neutralize)
                    _logger.info("Successfully duplicated database: %s -> %s", source_db, new_db)
                    return {"success": True, "message": f"Duplicated {source_db} to {new_db}"}
                except Exception as e:
                    last_error = e
                    error_str = str(e)
                    if "being accessed by other users" in error_str and attempt < max_retries - 1:
                        _logger.warning("Retry %d/%d - connections still active: %s", attempt + 1, max_retries, error_str)
                        import time
                        time.sleep(1)
                        continue
                    raise

            raise last_error
        except Exception as e:
            _logger.exception("Failed to duplicate database: %s -> %s", source_db, new_db)
            return {"success": False, "error": str(e)}
