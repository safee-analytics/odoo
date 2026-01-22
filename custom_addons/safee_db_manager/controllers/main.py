import logging
import threading
import uuid
import urllib.request
import json
import odoo
from odoo import http
from odoo.http import request, Response
from odoo.service import db as db_service

_logger = logging.getLogger(__name__)

_pending_jobs = {}


def _run_duplication(job_id, source_db, new_db, neutralize, webhook_url, organization_id):
    try:
        _logger.info("[%s] Starting duplication: %s -> %s", job_id, source_db, new_db)
        _pending_jobs[job_id] = {"status": "running", "source_db": source_db, "new_db": new_db}

        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                db_service.exp_duplicate_database(source_db, new_db, neutralize)
                _logger.info("[%s] Successfully duplicated: %s -> %s", job_id, source_db, new_db)
                _pending_jobs[job_id] = {"status": "completed", "source_db": source_db, "new_db": new_db}
                _send_webhook(webhook_url, job_id, new_db, organization_id, True, None)
                return
            except Exception as e:
                last_error = e
                error_str = str(e)
                if "being accessed by other users" in error_str and attempt < max_retries - 1:
                    _logger.warning("[%s] Retry %d/%d: %s", job_id, attempt + 1, max_retries, error_str)
                    import time
                    time.sleep(2)
                    continue
                break

        error_msg = str(last_error) if last_error else "Unknown error"
        _logger.exception("[%s] Failed to duplicate: %s -> %s: %s", job_id, source_db, new_db, error_msg)
        _pending_jobs[job_id] = {"status": "failed", "error": error_msg}
        _send_webhook(webhook_url, job_id, new_db, organization_id, False, error_msg)

    except Exception as e:
        error_msg = str(e)
        _logger.exception("[%s] Duplication thread error: %s", job_id, error_msg)
        _pending_jobs[job_id] = {"status": "failed", "error": error_msg}
        _send_webhook(webhook_url, job_id, new_db, organization_id, False, error_msg)


def _send_webhook(webhook_url, job_id, database_name, organization_id, success, error):
    if not webhook_url:
        _logger.warning("[%s] No webhook URL provided, skipping callback", job_id)
        return

    try:
        payload = json.dumps({
            "job_id": job_id,
            "database_name": database_name,
            "organization_id": organization_id,
            "success": success,
            "error": error,
        }).encode("utf-8")

        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            _logger.info("[%s] Webhook sent successfully: %s", job_id, resp.status)
    except Exception as e:
        _logger.exception("[%s] Failed to send webhook to %s: %s", job_id, webhook_url, e)


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
    def duplicate_database(self, master_pwd, source_db, new_db, webhook_url=None, organization_id=None, neutralize=False):
        try:
            db_service.check_super(master_pwd)
        except Exception as e:
            _logger.warning("Unauthorized duplicate attempt: %s -> %s", source_db, new_db)
            return {"success": False, "error": "Unauthorized"}

        job_id = str(uuid.uuid4())
        _logger.info("[%s] Queueing duplication: %s -> %s (webhook: %s)", job_id, source_db, new_db, webhook_url)

        thread = threading.Thread(
            target=_run_duplication,
            args=(job_id, source_db, new_db, neutralize, webhook_url, organization_id),
            daemon=True,
        )
        thread.start()

        return {"success": True, "job_id": job_id, "message": "Duplication started"}

    @http.route(
        "/safee/db/job_status",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def job_status(self, master_pwd, job_id):
        try:
            db_service.check_super(master_pwd)
        except Exception as e:
            return {"success": False, "error": "Unauthorized"}

        job = _pending_jobs.get(job_id)
        if not job:
            return {"success": False, "error": "Job not found"}

        return {"success": True, "job": job}
