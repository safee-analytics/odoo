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

            odoo.sql_db.close_db(source_db)

            db = odoo.sql_db.db_connect(source_db)
            with db.cursor() as cr:
                cr.execute("""
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = %s AND pid != pg_backend_pid()
                """, (source_db,))
                terminated = cr.fetchall()
                _logger.info("Terminated %d connections to %s", len(terminated), source_db)

            odoo.sql_db.close_db(source_db)

            db_service.exp_duplicate_database(source_db, new_db, neutralize)
            _logger.info("Successfully duplicated database: %s -> %s", source_db, new_db)
            return {"success": True, "message": f"Duplicated {source_db} to {new_db}"}
        except Exception as e:
            _logger.exception("Failed to duplicate database: %s -> %s", source_db, new_db)
            return {"success": False, "error": str(e)}
