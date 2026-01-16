# Copyright 2026 Safee Analytics
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Safee Storage Configuration",
    "summary": "Auto-configure Cloudflare R2 storage for Safee",
    "version": "18.0.1.0.0",
    "category": "Technical",
    "license": "AGPL-3",
    "author": "Safee Analytics",
    "website": "https://safee.dev",
    "depends": [
        "fs_storage",
        "fs_attachment",
        "fs_attachment_s3",
    ],
    "data": [
        "data/fs_storage.xml",
    ],
    "auto_install": True,  # Auto-install when dependencies are met
    "installable": True,
}
