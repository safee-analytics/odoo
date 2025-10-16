# Odoo Setup Guide for Safee Monorepo

This directory contains a **forked version of Odoo 19.0** with custom REST API module for the Safee platform.

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Updating from Upstream](#updating-from-upstream)
- [Custom Modules](#custom-modules)
- [API Documentation](#api-documentation)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Fork and Clone Odoo

**First time setup:**

```bash
# 1. Fork odoo/odoo on GitHub to safee-analytics/odoo (or your account)
# 2. Clone your fork
cd ~/github/safee
git clone https://github.com/safee-analytics/odoo.git odoo
cd odoo

# 3. Add upstream remote for updates
git remote add upstream https://github.com/odoo/odoo.git
git fetch upstream

# 4. Checkout 19.0 branch
git checkout 19.0
```

### 2. Add Custom REST API Module

```bash
# Copy the custom api_rest module
cp -r ~/odoo/addons/api_rest ~/github/safee/odoo/addons/

# Commit the custom module
git add addons/api_rest
git commit -m "[ADD] api_rest: REST API module with JWT authentication"
git push origin 19.0
```

### 3. Start with Docker

```bash
# From the safee monorepo root
cd ~/github/safee

# Build and start Odoo (along with postgres)
docker-compose up odoo

# Or run in background
docker-compose up -d odoo
```

### 4. Access Odoo

- **Odoo Web UI:** http://localhost:8069
- **API Documentation:** http://localhost:8069/api/docs
- **Health Check:** http://localhost:8069/web/health

**Default Credentials:**
- Database: `odoo`
- Username: `admin`
- Password: `admin`

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Safee Monorepo                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐      ┌──────────────┐               │
│  │   Next.js    │─────>│  Odoo REST   │               │
│  │  Frontend    │      │     API      │               │
│  └──────────────┘      └──────┬───────┘               │
│        │                       │                        │
│        │              ┌────────▼───────┐               │
│        │              │  Odoo Docker   │               │
│        │              │   Container    │               │
│        │              └────────┬───────┘               │
│        │                       │                        │
│        │              ┌────────▼───────┐               │
│        └─────────────>│   PostgreSQL   │               │
│                       │    (Shared)    │               │
│                       └────────────────┘               │
└─────────────────────────────────────────────────────────┘
```

**Services in docker-compose.yml:**
- `postgres` - Shared PostgreSQL database (port 15432)
- `redis` - Redis cache (port 16379)
- `odoo` - Odoo ERP with REST API (port 8069)

---

## Updating from Upstream

To get the latest Odoo updates:

```bash
cd ~/github/safee/odoo

# Fetch latest from Odoo
git fetch upstream

# Merge upstream changes
git checkout 19.0
git merge upstream/19.0

# Resolve any conflicts (especially in addons/)
# Your custom api_rest module should not conflict

# Push to your fork
git push origin 19.0

# Rebuild Docker image
cd ~/github/safee
docker-compose build odoo
docker-compose up -d odoo
```

---

## Custom Modules

### Included Custom Modules

1. **api_rest** - REST API with JWT Authentication
   - Location: `addons/api_rest/`
   - Auto-installed on first run
   - Provides 37+ REST endpoints

### Adding New Custom Modules

```bash
# 1. Create your module in addons/
cd ~/github/safee/odoo/addons
mkdir my_custom_module

# 2. Create __manifest__.py, __init__.py, etc.

# 3. Mount it in docker-compose.yml (already configured)
# The volume ./odoo/addons:/mnt/extra-addons makes all addons available

# 4. Install via Odoo UI or command line
docker-compose exec odoo /opt/odoo/odoo-bin -c /etc/odoo/odoo.conf -d odoo -i my_custom_module --stop-after-init

# 5. Restart Odoo
docker-compose restart odoo
```

---

## API Documentation

### REST API Endpoints

The custom `api_rest` module provides:

**Authentication:**
- POST `/api/auth/login` - Get JWT token
- GET `/api/auth/me` - Get current user info
- POST `/api/auth/logout` - Invalidate token

**Discovery (Public):**
- GET `/api/discover/models` - List all Odoo models
- GET `/api/discover/methods/{model}` - List methods for a model
- GET `/api/discover/fields/{model}` - List fields for a model

**CRUD Operations (Authenticated):**
- GET `/api/{model}` - Search records
- POST `/api/{model}` - Create record
- GET `/api/{model}/{id}` - Read record
- PUT `/api/{model}/{id}` - Update record
- DELETE `/api/{model}/{id}` - Delete record

**Business Logic:**
- POST `/api/{model}/{id}/call/{method}` - Call any business method

**Full documentation:** http://localhost:8069/api/docs (Swagger UI)

### Example Usage

```bash
# 1. Login
curl -X POST http://localhost:8069/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "login": "admin",
      "password": "admin",
      "db": "odoo"
    },
    "id": 1
  }'

# 2. Use the token
TOKEN="your_jwt_token_here"

# 3. List sales orders
curl -X POST http://localhost:8069/api/sale.order \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "domain": [],
      "fields": ["name", "partner_id", "amount_total"],
      "limit": 10
    },
    "id": 2
  }'
```

---

## Environment Variables

Configure in `.env` file or `docker-compose.yml`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `postgres` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | `postgres` | Database password |
| `ODOO_DB` | `odoo` | Odoo database name |
| `ADMIN_PASSWORD` | `admin` | Odoo master password |

---

## Troubleshooting

### Odoo won't start

```bash
# Check logs
docker-compose logs odoo

# Check if postgres is ready
docker-compose ps postgres

# Restart postgres first
docker-compose restart postgres
docker-compose up odoo
```

### Database initialization failed

```bash
# Remove the database and start fresh
docker-compose exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS odoo;"
docker-compose restart odoo
```

### Module not found

```bash
# Check addons path
docker-compose exec odoo cat /etc/odoo/odoo.conf | grep addons_path

# List available addons
docker-compose exec odoo ls -la /opt/odoo/addons
docker-compose exec odoo ls -la /mnt/extra-addons
```

### Port already in use

```bash
# Check what's using port 8069
lsof -i :8069

# Kill the process or change the port in docker-compose.yml
# Change "8069:8069" to "8070:8069" for example
```

### Rebuild from scratch

```bash
# Stop and remove everything
docker-compose down -v

# Remove odoo image
docker-compose rm -f odoo
docker image rm safee-odoo

# Rebuild
docker-compose build odoo
docker-compose up odoo
```

---

## Development Workflow

### 1. Make changes to api_rest module

```bash
# Edit files in addons/api_rest/
vim ~/github/safee/odoo/addons/api_rest/controllers/api_controller.py

# Restart Odoo to reload
docker-compose restart odoo

# Or upgrade the module
docker-compose exec odoo /opt/odoo/odoo-bin -c /etc/odoo/odoo.conf -d odoo -u api_rest --stop-after-init
docker-compose restart odoo
```

### 2. Test API changes

```bash
# Check API docs
open http://localhost:8069/api/docs

# Test endpoints
curl http://localhost:8069/api/discover/models?search=sale
```

### 3. Commit and push

```bash
cd ~/github/safee/odoo
git add addons/api_rest/
git commit -m "[IMP] api_rest: improved error handling"
git push origin 19.0
```

---

## Next.js Integration

See the **ACCOUNTING_APP_GUIDE.md** and **NEXTJS_QUICKSTART.md** in the parent Odoo directory for complete guides on building Next.js frontends that use this API.

Quick example:

```typescript
// lib/odoo-client.ts
import axios from 'axios';

const ODOO_URL = 'http://localhost:8069';

class OdooClient {
  async login(username: string, password: string) {
    const response = await axios.post(`${ODOO_URL}/api/auth/login`, {
      jsonrpc: '2.0',
      method: 'call',
      params: { login: username, password, db: 'odoo' },
      id: 1
    });
    return response.data.result;
  }
}

export const odooClient = new OdooClient();
```

---

## Production Deployment

For production:

1. **Change default passwords** in `.env`
2. **Enable SSL/TLS** with reverse proxy (nginx)
3. **Set workers** in `odoo.conf` based on CPU cores
4. **Configure backup** for PostgreSQL volumes
5. **Set up monitoring** for health checks
6. **Use secrets** for JWT_SECRET and ADMIN_PASSWORD

---

## Resources

- **Odoo Official Docs:** https://www.odoo.com/documentation/19.0/
- **Odoo GitHub:** https://github.com/odoo/odoo
- **REST API Module:** `~/github/safee/odoo/addons/api_rest/`
- **Safee Monorepo:** `~/github/safee/`

---

**Need help?** Check the logs, API docs, or ask the team!
