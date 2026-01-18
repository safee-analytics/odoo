#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DOPPLER_PROJECT="${DOPPLER_PROJECT:-odoo}"
DOPPLER_CONFIG="${DOPPLER_CONFIG:-dev}"

echo "📥 Pulling secrets from Doppler (project: $DOPPLER_PROJECT, config: $DOPPLER_CONFIG)..."

DOPPLER_ARGS="--project $DOPPLER_PROJECT --config $DOPPLER_CONFIG"
if [ -n "${DOPPLER_TOKEN:-}" ]; then
    DOPPLER_ARGS="$DOPPLER_ARGS --token $DOPPLER_TOKEN"
fi

doppler secrets download $DOPPLER_ARGS --no-file --format env > "$SCRIPT_DIR/.env"

echo "⚙️ Rendering Odoo config..."
set -a
source "$SCRIPT_DIR/.env"
set +a

envsubst < "$SCRIPT_DIR/odoo.conf" > "$SCRIPT_DIR/odoo.conf.rendered"
chmod 644 "$SCRIPT_DIR/odoo.conf.rendered"

echo "✅ Config rendered to $SCRIPT_DIR/odoo.conf.rendered"
echo "   DB_HOST: $DB_HOST"
echo "   DB_NAME: $DB_NAME"
