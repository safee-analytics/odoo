# 📋 API Module Overview

## Everything is in `/Users/mahmoudabdelhadi/odoo`

---

## 📂 File Structure

```
/Users/mahmoudabdelhadi/odoo/
│
├── 📁 addons/
│   └── 📁 api_rest/                       ← THE REST API MODULE
│       ├── __init__.py
│       ├── __manifest__.py                ← Module metadata
│       ├── 📁 controllers/
│       │   ├── __init__.py
│       │   ├── auth_controller.py         ← JWT auth (login, refresh, me)
│       │   ├── api_controller.py          ← CRUD operations
│       │   └── openapi_controller.py      ← Swagger UI docs
│       └── 📁 security/
│           └── ir.model.access.csv        ← Permissions
│
├── 📄 QUICK_START.md                      ← START HERE! Installation guide
├── 📄 README_API.md                       ← Full Express + tRPC integration
├── 📄 README_REST_API.md                  ← Complete API reference
└── 📄 API_OVERVIEW.md                     ← This file
```

---

## 📖 Documentation Guide

| File | When to Read | What's Inside |
|------|--------------|---------------|
| **QUICK_START.md** | First! | Installation, basic testing, quick examples |
| **README_REST_API.md** | Second | Complete API reference, all endpoints, security |
| **README_API.md** | For advanced setup | Express + tRPC + React integration guide |
| **API_OVERVIEW.md** | Overview | This file - quick navigation |

---

## 🚀 Installation (3 Steps)

```bash
# 1. Install JWT library
pip3 install pyjwt

# 2. Start Odoo
cd /Users/mahmoudabdelhadi/odoo
./odoo-bin -c odoo.conf

# 3. In Odoo UI: Apps → Update Apps List → Search "REST API" → Install
```

**Then visit**: http://localhost:8069/api/docs

---

## 🎯 What Does This Module Do?

Converts your Odoo installation into a REST API backend that any frontend can use:

```
┌─────────────┐
│   React     │
├─────────────┤
│   Vue.js    │
├─────────────┤    HTTP/JSON        ┌──────────────┐
│   Angular   │ ◄─────────────────► │ Odoo Backend │
├─────────────┤      JWT Auth       │  REST API    │
│ React Native│                     └──────────────┘
├─────────────┤
│   Flutter   │
└─────────────┘
```

---

## 🔑 Key Features

✅ **JWT Authentication** - Secure token-based auth
✅ **Full CRUD** - Create, Read, Update, Delete ANY model
✅ **Custom Methods** - Call Odoo business logic (e.g., `action_confirm()`)
✅ **Swagger UI** - Interactive API documentation
✅ **CORS Enabled** - Works with any frontend origin
✅ **Type-Safe (optional)** - Use with TypeScript + tRPC

---

## 📝 Quick Examples

### Login
```bash
curl -X POST http://localhost:8069/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"login":"admin","password":"admin"}}'
```

### Get Sales Orders
```bash
curl -X GET http://localhost:8069/api/sale.order \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Product
```bash
curl -X POST http://localhost:8069/api/product.product \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"jsonrpc":"2.0","params":{"vals":{"name":"New Product","list_price":99.99}}}'
```

---

## 🌐 API Endpoints

### Auth
- `POST /api/auth/login` - Get token
- `GET /api/auth/me` - Current user
- `POST /api/auth/refresh` - Refresh token

### CRUD
- `GET /api/{model}` - Search
- `GET /api/{model}/{id}` - Read
- `POST /api/{model}` - Create
- `PUT /api/{model}/{id}` - Update
- `DELETE /api/{model}/{id}` - Delete

### Methods
- `POST /api/{model}/{id}/call/{method}` - Call method

---

## 📦 Available Models

Works with **ALL** Odoo models:

| Module | Models |
|--------|--------|
| **Sales** | `sale.order`, `sale.order.line` |
| **Purchase** | `purchase.order`, `purchase.order.line` |
| **Inventory** | `stock.picking`, `stock.move`, `product.product` |
| **Accounting** | `account.move`, `account.move.line`, `account.payment` |
| **CRM** | `crm.lead`, `crm.stage` |
| **Projects** | `project.project`, `project.task` |
| **HR** | `hr.employee`, `hr.attendance`, `hr.leave` |
| **Partners** | `res.partner`, `res.users`, `res.company` |

...and **any custom models** you create!

---

## 🧪 Testing

### With Swagger UI (Easiest)
1. Visit: http://localhost:8069/api/docs
2. Click "Authorize"
3. Login to get token
4. Try any endpoint!

### With Postman
1. Import OpenAPI spec from: http://localhost:8069/api/openapi.json
2. Set Authorization header: `Bearer YOUR_TOKEN`
3. Test endpoints

### With curl
See examples in **QUICK_START.md**

---

## 🔐 Security Checklist

Before going to production:

- [ ] Change JWT secret in `auth_controller.py`
- [ ] Use environment variables for secrets
- [ ] Configure CORS for specific domains
- [ ] Enable HTTPS
- [ ] Set up rate limiting (optional)
- [ ] Review Odoo access rights

---

## 🏗️ Frontend Integration Options

### Option 1: Direct HTTP Calls
**Good for**: Quick prototypes, simple apps
```typescript
const response = await fetch('http://localhost:8069/api/sale.order', {
  headers: { Authorization: `Bearer ${token}` }
});
```

### Option 2: Express + tRPC (Recommended)
**Good for**: Production apps, type safety
- Full TypeScript support
- Auto-generated types
- Better error handling
- API gateway pattern

See **README_API.md** for complete setup.

---

## 🚦 Next Steps

1. ✅ **Read QUICK_START.md** - Install and test the API
2. 🧪 **Try Swagger UI** - http://localhost:8069/api/docs
3. 💻 **Build frontend** - See README_API.md for Express+tRPC
4. 🔐 **Secure it** - Change JWT secret
5. 🚀 **Deploy** - See Odoo deployment docs

---

## 📞 Need Help?

- **Swagger Docs**: http://localhost:8069/api/docs (after installation)
- **Odoo Forum**: https://www.odoo.com/forum
- **Odoo Docs**: https://www.odoo.com/documentation/

---

## ✨ Summary

| What | Where |
|------|-------|
| **Module Code** | `/Users/mahmoudabdelhadi/odoo/addons/api_rest/` |
| **Installation Guide** | `QUICK_START.md` |
| **API Reference** | `README_REST_API.md` |
| **tRPC Integration** | `README_API.md` |
| **Swagger UI** | http://localhost:8069/api/docs |
| **This Overview** | `API_OVERVIEW.md` |

---

**Everything you need is now in `/Users/mahmoudabdelhadi/odoo`!** 🎉

Start with **QUICK_START.md** to get up and running in 5 minutes.
