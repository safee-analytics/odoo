# 🚀 Odoo REST API - Complete Guide

## 📁 Project Structure

```
/Users/mahmoudabdelhadi/odoo/
├── addons/
│   └── api_rest/                    # ✨ NEW: REST API Module
│       ├── __init__.py
│       ├── __manifest__.py
│       ├── controllers/
│       │   ├── __init__.py
│       │   ├── auth_controller.py   # JWT Authentication
│       │   ├── api_controller.py    # CRUD Operations
│       │   └── openapi_controller.py # API Documentation
│       └── security/
│           └── ir.model.access.csv
├── QUICK_START.md                   # ⚡ Quick installation guide
├── README_API.md                    # 📖 Full Express+tRPC integration
└── README_REST_API.md              # 📄 This file
```

---

## 🎯 What Is This?

A **complete REST API module** for Odoo that allows you to:

✅ **Decouple your frontend** - Build with React, Vue, Angular, or mobile apps
✅ **JWT Authentication** - Industry-standard secure authentication
✅ **Full CRUD Operations** - Create, Read, Update, Delete on ANY Odoo model
✅ **Custom Methods** - Call any Odoo business logic (like `action_confirm()`)
✅ **OpenAPI/Swagger Docs** - Interactive API documentation
✅ **CORS Enabled** - Call from any origin

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **QUICK_START.md** | Installation & basic usage (start here!) |
| **README_API.md** | Full guide for Express + tRPC + React integration |
| **README_REST_API.md** | This overview document |

---

## ⚡ Quick Start

### 1. Install Dependencies

```bash
cd /Users/mahmoudabdelhadi/odoo
pip3 install pyjwt
```

### 2. Start Odoo

```bash
./odoo-bin -c odoo.conf
```

### 3. Install Module

1. Go to http://localhost:8069
2. Navigate to **Apps** → **Update Apps List**
3. Search for **"REST API"**
4. Click **Install**

### 4. View Documentation

Visit: **http://localhost:8069/api/docs**

You'll see interactive Swagger UI documentation!

---

## 🔑 API Endpoints

### Authentication

```bash
POST /api/auth/login       # Get JWT token
GET  /api/auth/me          # Get current user info
POST /api/auth/refresh     # Refresh token
```

### CRUD Operations

```bash
GET    /api/{model}              # Search records
GET    /api/{model}/{id}         # Read single record
POST   /api/{model}              # Create record
PUT    /api/{model}/{id}         # Update record
DELETE /api/{model}/{id}         # Delete record
```

### Custom Methods

```bash
POST /api/{model}/{id}/call/{method}    # Call method on record
POST /api/{model}/call/{method}         # Call static method
```

### Available Models

Any Odoo model works! Common ones:

- `sale.order` - Sales Orders
- `purchase.order` - Purchase Orders
- `product.product` - Products
- `res.partner` - Customers/Suppliers
- `account.move` - Invoices
- `stock.picking` - Deliveries
- `project.project` - Projects
- `project.task` - Tasks
- `hr.employee` - Employees

---

## 💻 Usage Examples

### Login

```bash
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
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "user": {
    "id": 2,
    "name": "Administrator",
    "login": "admin",
    "email": "admin@example.com"
  }
}
```

### Get Sales Orders

```bash
curl -X GET "http://localhost:8069/api/sale.order" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "domain": [["state", "=", "sale"]],
      "fields": ["name", "partner_id", "amount_total"],
      "limit": 10
    },
    "id": 2
  }'
```

### Create Sales Order

```bash
curl -X POST http://localhost:8069/api/sale.order \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "vals": {
        "partner_id": 14,
        "date_order": "2025-10-14"
      }
    },
    "id": 3
  }'
```

### Confirm Sales Order

```bash
curl -X POST http://localhost:8069/api/sale.order/42/call/action_confirm \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "args": [],
      "kwargs": {}
    },
    "id": 4
  }'
```

---

## 🏗️ Architecture Options

### Option 1: Direct API Calls

```
┌─────────────────┐
│   Your Frontend │
│ (React/Vue/etc) │ ──HTTP──► Odoo REST API
└─────────────────┘
```

**Pros**: Simple, direct
**Cons**: No type safety, manual error handling

### Option 2: Express + tRPC Gateway (Recommended)

```
┌───────────┐       ┌─────────────┐       ┌──────────┐
│  Frontend │ ◄───► │   Express   │ ◄───► │   Odoo   │
│  (React)  │ tRPC  │  + tRPC     │ HTTP  │   REST   │
└───────────┘       └─────────────┘       └──────────┘
```

**Pros**: Type-safe, better DX, abstraction layer
**Cons**: Extra server layer

See **README_API.md** for full Express + tRPC setup.

---

## 🔐 Security

### Important: Change JWT Secret!

Before production, change the JWT secret in:

`/Users/mahmoudabdelhadi/odoo/addons/api_rest/controllers/auth_controller.py`

```python
# Line 11
JWT_SECRET = 'your-secret-key-change-this-in-production'  # ⚠️ CHANGE THIS!
```

**Recommended**: Use environment variables

```python
import os
JWT_SECRET = os.environ.get('ODOO_JWT_SECRET', 'fallback-dev-secret')
```

### CORS Configuration

By default, CORS is open (`cors='*'`). To restrict:

```python
# In controllers
@http.route('/api/...', cors='https://yourfrontend.com')
```

---

## 🧪 Testing with Swagger UI

1. Visit: http://localhost:8069/api/docs
2. Click **"Authorize"** button
3. Login to get token
4. Paste token in format: `Bearer YOUR_TOKEN`
5. Try any endpoint!

---

## 🛠️ Development Workflow

### Adding Custom Endpoints

Edit `/Users/mahmoudabdelhadi/odoo/addons/api_rest/controllers/api_controller.py`:

```python
@http.route('/api/custom/my_endpoint', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
@verify_token
def my_custom_endpoint(self, **kwargs):
    """Your custom logic"""
    return {'success': True, 'data': 'Hello!'}
```

### Restarting After Changes

```bash
# Restart Odoo
./odoo-bin -c odoo.conf

# Or update module
./odoo-bin -c odoo.conf -u api_rest
```

---

## 🐛 Troubleshooting

### Module not showing in Apps

```bash
./odoo-bin -c odoo.conf -u api_rest
```

### Token Errors

Make sure PyJWT is installed:
```bash
pip3 install pyjwt
```

### CORS Issues

Check browser console. Module has CORS enabled by default.

### 401 Unauthorized

1. Check token is included: `Authorization: Bearer YOUR_TOKEN`
2. Check token hasn't expired (24h default)
3. Use `/api/auth/refresh` to get new token

---

## 📖 Next Steps

1. ✅ **Install the module** (see QUICK_START.md)
2. 📚 **Read API docs** at http://localhost:8069/api/docs
3. 🧪 **Test endpoints** with Swagger UI or Postman
4. 💻 **Build frontend** (see README_API.md for Express+tRPC)
5. 🚀 **Deploy** to production (change JWT secret first!)

---

## 📞 Support

- **Swagger Docs**: http://localhost:8069/api/docs
- **Odoo Docs**: https://www.odoo.com/documentation/
- **tRPC Docs**: https://trpc.io/

---

## ✨ Features Summary

| Feature | Included |
|---------|----------|
| JWT Authentication | ✅ |
| Token Refresh | ✅ |
| CRUD Operations | ✅ |
| Custom Methods | ✅ |
| OpenAPI/Swagger | ✅ |
| CORS Support | ✅ |
| Access Control | ✅ (Odoo permissions) |
| Multi-database | ✅ |
| Any Odoo Model | ✅ |

---

**🎉 You now have a production-ready REST API for Odoo!**

Start with **QUICK_START.md** for installation, then explore **README_API.md** for advanced integrations.
