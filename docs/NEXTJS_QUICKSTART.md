# Next.js + Odoo REST API - Complete Guide

## Overview

```
┌─────────────────┐          ┌─────────────────┐
│   Next.js App   │  HTTP    │  Odoo REST API  │
│   (Frontend)    │ ────────>│   (Backend)     │
│  localhost:3000 │          │ localhost:8069  │
└─────────────────┘          └─────────────────┘
```

**What you're building:**
- Next.js frontend for users to interact with
- Calls Odoo REST API to get/save data
- Type-safe with TypeScript

---

## Part 1: Setup Next.js Project

### 1. Create Next.js App

```bash
cd ~/projects
npx create-next-app@latest safee-frontend

# Select:
✔ TypeScript? … Yes
✔ ESLint? … Yes
✔ Tailwind CSS? … Yes
✔ App Router? … Yes
✔ Import alias? … No

cd safee-frontend
npm install
```

### 2. Install Dependencies

```bash
npm install axios
npm install @tanstack/react-query
npm install zustand  # for state management
```

---

## Part 2: Create Odoo API Client

### File: `lib/odoo-client.ts`

```typescript
// lib/odoo-client.ts
import axios, { AxiosInstance } from 'axios';

const ODOO_URL = process.env.NEXT_PUBLIC_ODOO_URL || 'http://localhost:8069';

interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: number;
    name: string;
    login: string;
    email: string;
  };
}

interface JsonRpcRequest {
  jsonrpc: '2.0';
  method: 'call';
  params: any;
  id: number;
}

interface JsonRpcResponse<T> {
  jsonrpc: '2.0';
  result: T;
  id: number;
}

class OdooClient {
  private api: AxiosInstance;
  private token: string | null = null;
  private requestId = 1;

  constructor() {
    this.api = axios.create({
      baseURL: ODOO_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Load token from localStorage on client side
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('odoo_token');
      if (this.token) {
        this.setToken(this.token);
      }
    }
  }

  private setToken(token: string) {
    this.token = token;
    this.api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    if (typeof window !== 'undefined') {
      localStorage.setItem('odoo_token', token);
    }
  }

  // Login
  async login(login: string, password: string, db: string = 'odoo_db'): Promise<LoginResponse> {
    const response = await this.api.post<JsonRpcResponse<LoginResponse>>('/api/auth/login', {
      jsonrpc: '2.0',
      method: 'call',
      params: { login, password, db },
      id: this.requestId++,
    });

    const result = response.data.result;
    this.setToken(result.access_token);
    return result;
  }

  // Logout
  logout() {
    this.token = null;
    delete this.api.defaults.headers.common['Authorization'];
    if (typeof window !== 'undefined') {
      localStorage.removeItem('odoo_token');
    }
  }

  // Generic search
  async search<T = any>(
    model: string,
    domain: any[] = [],
    fields: string[] = [],
    limit: number = 80,
    offset: number = 0
  ): Promise<T[]> {
    const response = await this.api.post<JsonRpcResponse<{ success: boolean; data: T[] }>>(
      `/api/${model}`,
      {
        jsonrpc: '2.0',
        method: 'call',
        params: { domain, fields, limit, offset },
        id: this.requestId++,
      }
    );

    return response.data.result.data;
  }

  // Read single record
  async read<T = any>(model: string, id: number, fields: string[] = []): Promise<T> {
    const response = await this.api.post<JsonRpcResponse<{ success: boolean; data: T }>>(
      `/api/${model}/${id}`,
      {
        jsonrpc: '2.0',
        method: 'call',
        params: { fields },
        id: this.requestId++,
      }
    );

    return response.data.result.data;
  }

  // Create record
  async create<T = any>(model: string, vals: any): Promise<T> {
    const response = await this.api.post<JsonRpcResponse<{ success: boolean; data: T }>>(
      `/api/${model}`,
      {
        jsonrpc: '2.0',
        method: 'call',
        params: { vals },
        id: this.requestId++,
      }
    );

    return response.data.result.data;
  }

  // Update record
  async update<T = any>(model: string, id: number, vals: any): Promise<T> {
    const response = await this.api.put<JsonRpcResponse<{ success: boolean; data: T }>>(
      `/api/${model}/${id}`,
      {
        jsonrpc: '2.0',
        method: 'call',
        params: { vals },
        id: this.requestId++,
      }
    );

    return response.data.result.data;
  }

  // Delete record
  async delete(model: string, id: number): Promise<void> {
    await this.api.delete(`/api/${model}/${id}`, {
      data: {
        jsonrpc: '2.0',
        method: 'call',
        params: {},
        id: this.requestId++,
      },
    });
  }

  // Call method
  async callMethod<T = any>(
    model: string,
    id: number,
    method: string,
    args: any[] = [],
    kwargs: any = {}
  ): Promise<T> {
    const response = await this.api.post<JsonRpcResponse<{ success: boolean; result: T }>>(
      `/api/${model}/${id}/call/${method}`,
      {
        jsonrpc: '2.0',
        method: 'call',
        params: { args, kwargs },
        id: this.requestId++,
      }
    );

    return response.data.result.result;
  }
}

// Export singleton instance
export const odooClient = new OdooClient();
```

---

## Part 3: Create Environment Variables

### File: `.env.local`

```bash
NEXT_PUBLIC_ODOO_URL=http://localhost:8069
```

---

## Part 4: Example - Login Page

### File: `app/login/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { odooClient } from '@/lib/odoo-client';

export default function LoginPage() {
  const router = useRouter();
  const [login, setLogin] = useState('admin');
  const [password, setPassword] = useState('admin');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await odooClient.login(login, password);
      console.log('Logged in:', result.user);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h1 className="text-2xl font-bold mb-6">Login to Odoo</h1>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Username
            </label>
            <input
              type="text"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700"
              required
            />
          </div>

          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full disabled:opacity-50"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
}
```

---

## Part 5: Example - Sales Orders List

### File: `app/dashboard/sales/page.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { odooClient } from '@/lib/odoo-client';

interface SaleOrder {
  id: number;
  name: string;
  partner_id: [number, string];
  date_order: string;
  amount_total: number;
  state: string;
}

export default function SalesOrdersPage() {
  const [orders, setOrders] = useState<SaleOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      const data = await odooClient.search<SaleOrder>(
        'sale.order',
        [], // domain: get all
        ['name', 'partner_id', 'date_order', 'amount_total', 'state'], // fields
        10 // limit
      );
      setOrders(data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load orders');
    } finally {
      setLoading(false);
    }
  };

  const confirmOrder = async (orderId: number) => {
    try {
      await odooClient.callMethod('sale.order', orderId, 'action_confirm');
      alert('Order confirmed!');
      loadOrders(); // Reload
    } catch (err: any) {
      alert('Failed to confirm: ' + (err.response?.data?.error || err.message));
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (error) return <div className="p-8 text-red-500">{error}</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Sales Orders</h1>

      <div className="bg-white shadow-md rounded">
        <table className="min-w-full">
          <thead>
            <tr className="bg-gray-100">
              <th className="px-6 py-3 text-left">Order #</th>
              <th className="px-6 py-3 text-left">Customer</th>
              <th className="px-6 py-3 text-left">Date</th>
              <th className="px-6 py-3 text-left">Total</th>
              <th className="px-6 py-3 text-left">State</th>
              <th className="px-6 py-3 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr key={order.id} className="border-b hover:bg-gray-50">
                <td className="px-6 py-4">{order.name}</td>
                <td className="px-6 py-4">{order.partner_id?.[1] || 'N/A'}</td>
                <td className="px-6 py-4">
                  {new Date(order.date_order).toLocaleDateString()}
                </td>
                <td className="px-6 py-4">${order.amount_total.toFixed(2)}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded text-sm ${
                    order.state === 'sale' ? 'bg-green-100 text-green-800' :
                    order.state === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {order.state}
                  </span>
                </td>
                <td className="px-6 py-4">
                  {order.state === 'draft' && (
                    <button
                      onClick={() => confirmOrder(order.id)}
                      className="bg-blue-500 hover:bg-blue-700 text-white text-sm px-3 py-1 rounded"
                    >
                      Confirm
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

---

## Part 6: Run Your App

```bash
# Terminal 1: Run Odoo
cd ~/odoo
./odoo-bin -c odoo.conf

# Terminal 2: Run Next.js
cd ~/projects/safee-frontend
npm run dev
```

Open browser:
- Next.js: http://localhost:3000
- Odoo API: http://localhost:8069

---

## The Flow (Simple Explanation)

### Example: User clicks "Confirm Order"

1. **User clicks button** in Next.js
   ```typescript
   <button onClick={() => confirmOrder(123)}>Confirm</button>
   ```

2. **Next.js calls Odoo API**
   ```typescript
   await odooClient.callMethod('sale.order', 123, 'action_confirm');
   ```

3. **HTTP request sent**
   ```
   POST http://localhost:8069/api/sale.order/123/call/action_confirm
   Authorization: Bearer <token>
   Body: {"jsonrpc":"2.0","method":"call","params":{"args":[],"kwargs":{}},"id":1}
   ```

4. **Odoo processes request**
   - Validates token
   - Finds sale order #123
   - Calls `action_confirm()` method
   - Creates delivery, reserves stock, etc.

5. **Odoo sends response**
   ```json
   {"jsonrpc":"2.0","result":{"success":true},"id":1}
   ```

6. **Next.js updates UI**
   ```typescript
   alert('Order confirmed!');
   loadOrders(); // Refresh the list
   ```

---

## Common Patterns

### Pattern 1: List Records
```typescript
const customers = await odooClient.search('res.partner', [], ['name', 'email']);
```

### Pattern 2: Read One Record
```typescript
const order = await odooClient.read('sale.order', 123, ['name', 'amount_total']);
```

### Pattern 3: Create Record
```typescript
const newOrder = await odooClient.create('sale.order', {
  partner_id: 5,
  date_order: '2025-10-15',
});
```

### Pattern 4: Update Record
```typescript
await odooClient.update('sale.order', 123, {
  state: 'cancel'
});
```

### Pattern 5: Call Business Logic
```typescript
// Confirm order
await odooClient.callMethod('sale.order', 123, 'action_confirm');

// Approve leave
await odooClient.callMethod('hr.leave', 456, 'action_approve');

// Mark as won
await odooClient.callMethod('crm.lead', 789, 'action_set_won');
```

---

## Folder Structure

```
safee-frontend/
├── app/
│   ├── login/
│   │   └── page.tsx          # Login page
│   ├── dashboard/
│   │   ├── page.tsx          # Dashboard home
│   │   ├── sales/
│   │   │   └── page.tsx      # Sales orders list
│   │   ├── customers/
│   │   │   └── page.tsx      # Customers list
│   │   └── inventory/
│   │       └── page.tsx      # Inventory view
│   └── layout.tsx            # Root layout
├── lib/
│   └── odoo-client.ts        # Odoo API client
├── .env.local                # Environment variables
└── package.json
```

---

## Next Steps

1. **Start with login** - Build the login page first
2. **Add one list page** - Start with sales orders or customers
3. **Add detail pages** - Click on a record to see details
4. **Add forms** - Create/edit records
5. **Add actions** - Confirm, cancel, approve buttons

**Don't try to build everything at once!** Start small and add features one by one.

---

## Quick Commands Reference

```bash
# Development
npm run dev              # Start Next.js dev server
npm run build            # Build for production
npm run start            # Start production server

# Odoo
./odoo-bin -c odoo.conf  # Start Odoo server
```

---

## Troubleshooting

### CORS Error?
Add this to Odoo config:
```
cors = *
```

### Token expired?
Call `odooClient.login()` again to get a new token.

### Can't connect to Odoo?
Make sure Odoo is running on port 8069 and API module is installed.

---

**You now have everything you need to build a Next.js app with Odoo!** 🚀

Start with the login page, then add one feature at a time.
