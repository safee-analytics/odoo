# 🚀 Quick Start: Odoo REST API

## What You Now Have

I've created a complete REST API module for your Odoo installation with:

✅ **JWT Authentication** - Secure token-based auth
✅ **CRUD Operations** - Create, Read, Update, Delete any model
✅ **Custom Method Calls** - Execute any Odoo business logic
✅ **OpenAPI/Swagger Docs** - Interactive API documentation
✅ **CORS Support** - Call from any frontend

---

## Files Created

```
/Users/mahmoudabdelhadi/odoo/addons/api_rest/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   ├── auth_controller.py      # JWT auth endpoints
│   ├── api_controller.py       # CRUD endpoints
│   └── openapi_controller.py   # API docs
└── security/
    └── ir.model.access.csv
```

---

## Installation

### 1. Install Dependencies

```bash
pip3 install pyjwt
```

### 2. Start Odoo

```bash
cd /Users/mahmoudabdelhadi/odoo
./odoo-bin -c odoo.conf
```

### 3. Install the Module

1. Open Odoo: http://localhost:8069
2. Log in as admin
3. Go to **Apps** → **Update Apps List**
4. Search for **"REST API"**
5. Click **Install**

### 4. View API Documentation

Visit: **http://localhost:8069/api/docs**

You'll see a Swagger UI with all available endpoints!

---

## Quick Test

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

### Get Sales Orders

```bash
# Use the token from login response
curl -X GET "http://localhost:8069/api/sale.order" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
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

---

## Next Steps

### Option 1: Use API Directly from Any Frontend

You can call these endpoints from:
- React
- Vue
- Angular
- Mobile apps (React Native, Flutter)
- Anything that can make HTTP requests!

### Option 2: Build Express + tRPC Gateway

For type-safe APIs, follow the guide in:
`/Users/mahmoudabdelhadi/odoo/README_API.md`

This shows how to:
- Create an Express.js API gateway
- Use tRPC for type-safe endpoints
- Build a React frontend with full TypeScript support

---

## Available Endpoints

### Authentication
- `POST /api/auth/login` - Get JWT token
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh` - Refresh token

### CRUD Operations
- `GET /api/{model}` - Search records
- `GET /api/{model}/{id}` - Read record
- `POST /api/{model}` - Create record
- `PUT /api/{model}/{id}` - Update record
- `DELETE /api/{model}/{id}` - Delete record

### Custom Methods
- `POST /api/{model}/{id}/call/{method}` - Call record method
- `POST /api/{model}/call/{method}` - Call model method

### Models Available
- `sale.order` - Sales orders
- `purchase.order` - Purchase orders
- `product.product` - Products
- `res.partner` - Customers/Suppliers
- `account.move` - Invoices
- `stock.picking` - Deliveries
- `project.project` - Projects
- `project.task` - Tasks
- `hr.employee` - Employees
- And **any other Odoo model**!

---

## Security Notes

⚠️ **IMPORTANT**: Change the JWT secret before production!

In `/Users/mahmoudabdelhadi/odoo/addons/api_rest/controllers/auth_controller.py`:

```python
JWT_SECRET = 'your-secret-key-change-this-in-production'
```

Change this to a strong random string and store in environment variables.

---

## Troubleshooting

### Module not showing in Apps
```bash
# Restart Odoo with update flag
./odoo-bin -c odoo.conf -u api_rest
```

### CORS errors
The module has CORS enabled by default with `cors='*'`. If you need to restrict it:

Edit the routes in `api_controller.py` and `auth_controller.py`:
```python
@http.route('/api/...', cors='https://yourfrontend.com')
```

### JWT errors
Make sure PyJWT is installed:
```bash
pip3 install pyjwt
```

---

## Support

For full documentation, see:
- **API Guide**: `/Users/mahmoudabdelhadi/odoo/README_API.md`
- **Swagger UI**: http://localhost:8069/api/docs
- **Odoo Docs**: https://www.odoo.com/documentation/

---

🎉 **You're all set!** Your Odoo backend is now a fully accessible REST API!
