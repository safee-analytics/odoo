# Odoo REST API - Frontend Integration Guide

## Overview

You now have a complete REST API for Odoo! This guide shows how to build a separate frontend using Express + tRPC + React.

---

## Architecture

```
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   React Frontend │ ◄─────► │  Express + tRPC  │ ◄─────► │  Odoo Backend    │
│   (Next.js/Vite) │  HTTP   │  API Gateway     │  HTTP   │  REST API        │
└──────────────────┘         └──────────────────┘         └──────────────────┘
```

---

## 1. Install & Start Odoo REST API Module

```bash
cd /Users/mahmoudabdelhadi/odoo

# Install PyJWT for JWT authentication
pip3 install pyjwt

# Start Odoo
./odoo-bin -c odoo.conf

# In Odoo web interface:
# 1. Go to Apps
# 2. Update Apps List
# 3. Search for "REST API"
# 4. Install the module
```

---

## 2. API Documentation

After installing the module, visit:

**Swagger UI**: http://localhost:8069/api/docs

This provides interactive API documentation!

---

## 3. API Endpoints

### Authentication

```bash
# Login
POST /api/auth/login
Body: {
  "login": "admin",
  "password": "admin",
  "db": "odoo"
}

Response: {
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "user": { "id": 2, "name": "Admin", ... }
}

# Get Current User
GET /api/auth/me
Headers: Authorization: Bearer <token>
```

### CRUD Operations

```bash
# Search Records
GET /api/sale.order?domain=[["state","=","sale"]]&fields=["name","partner_id"]&limit=10
Headers: Authorization: Bearer <token>

# Read Record
GET /api/sale.order/42
Headers: Authorization: Bearer <token>

# Create Record
POST /api/sale.order
Headers: Authorization: Bearer <token>
Body: {
  "vals": {
    "partner_id": 5,
    "date_order": "2025-10-14"
  }
}

# Update Record
PUT /api/sale.order/42
Headers: Authorization: Bearer <token>
Body: {
  "vals": {
    "state": "sale"
  }
}

# Delete Record
DELETE /api/sale.order/42
Headers: Authorization: Bearer <token>

# Call Custom Method
POST /api/sale.order/42/call/action_confirm
Headers: Authorization: Bearer <token>
Body: {
  "args": [],
  "kwargs": {}
}
```

---

## 4. Express + tRPC Backend (API Gateway)

Create a new project:

```bash
cd /Users/mahmoudabdelhadi/odoo
mkdir -p api-gateway
cd api-gateway
npm init -y
npm install express @trpc/server @trpc/client @trpc/react-query axios zod cors dotenv
npm install -D typescript @types/express @types/node @types/cors tsx
```

**`api-gateway/src/server.ts`**:

\`\`\`typescript
import express from 'express';
import cors from 'cors';
import { createExpressMiddleware } from '@trpc/server/adapters/express';
import { appRouter } from './trpc/router';
import { createContext } from './trpc/context';

const app = express();

app.use(cors());
app.use(express.json());

// tRPC middleware
app.use(
  '/trpc',
  createExpressMiddleware({
    router: appRouter,
    createContext,
  })
);

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(\`API Gateway running on http://localhost:\${PORT}\`);
});
\`\`\`

**`api-gateway/src/trpc/context.ts`**:

\`\`\`typescript
import type { CreateExpressContextOptions } from '@trpc/server/adapters/express';

export const createContext = ({ req, res }: CreateExpressContextOptions) => {
  // Extract auth token from request
  const token = req.headers.authorization?.replace('Bearer ', '');

  return {
    token,
    req,
    res,
  };
};

export type Context = Awaited<ReturnType<typeof createContext>>;
\`\`\`

**`api-gateway/src/trpc/odoo-client.ts`**:

\`\`\`typescript
import axios from 'axios';

const ODOO_URL = process.env.ODOO_URL || 'http://localhost:8069';

export class OdooClient {
  private token?: string;

  constructor(token?: string) {
    this.token = token;
  }

  private async request(method: string, url: string, data?: any) {
    const headers: any = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = \`Bearer \${this.token}\`;
    }

    const response = await axios({
      method,
      url: \`\${ODOO_URL}\${url}\`,
      headers,
      data: {
        jsonrpc: '2.0',
        method: 'call',
        params: data || {},
        id: Math.random(),
      },
    });

    if (response.data.error) {
      throw new Error(response.data.error.message || 'Odoo API Error');
    }

    return response.data.result;
  }

  async login(login: string, password: string, db = 'odoo') {
    return this.request('POST', '/api/auth/login', { login, password, db });
  }

  async search(model: string, domain: any[] = [], fields: string[] = [], limit = 80) {
    return this.request('GET', \`/api/\${model}\`, { domain, fields, limit });
  }

  async read(model: string, id: number, fields: string[] = []) {
    return this.request('GET', \`/api/\${model}/\${id}\`, { fields });
  }

  async create(model: string, vals: any) {
    return this.request('POST', \`/api/\${model}\`, { vals });
  }

  async write(model: string, id: number, vals: any) {
    return this.request('PUT', \`/api/\${model}/\${id}\`, { vals });
  }

  async unlink(model: string, id: number) {
    return this.request('DELETE', \`/api/\${model}/\${id}\`);
  }

  async call(model: string, id: number, method: string, args: any[] = [], kwargs: any = {}) {
    return this.request('POST', \`/api/\${model}/\${id}/call/\${method}\`, { args, kwargs });
  }
}
\`\`\`

**`api-gateway/src/trpc/router.ts`**:

\`\`\`typescript
import { initTRPC, TRPCError } from '@trpc/server';
import { z } from 'zod';
import type { Context } from './context';
import { OdooClient } from './odoo-client';

const t = initTRPC.context<Context>().create();

const router = t.router;
const publicProcedure = t.procedure;

// Middleware to check auth
const protectedProcedure = publicProcedure.use(async ({ ctx, next }) => {
  if (!ctx.token) {
    throw new TRPCError({ code: 'UNAUTHORIZED', message: 'Not authenticated' });
  }
  return next({
    ctx: {
      ...ctx,
      token: ctx.token,
    },
  });
});

export const appRouter = router({
  // Auth
  auth: router({
    login: publicProcedure
      .input(z.object({
        login: z.string(),
        password: z.string(),
        db: z.string().optional(),
      }))
      .mutation(async ({ input }) => {
        const client = new OdooClient();
        return await client.login(input.login, input.password, input.db);
      }),
  }),

  // Sales Orders
  sales: router({
    list: protectedProcedure
      .input(z.object({
        domain: z.array(z.any()).optional(),
        limit: z.number().optional(),
      }))
      .query(async ({ ctx, input }) => {
        const client = new OdooClient(ctx.token);
        return await client.search(
          'sale.order',
          input.domain || [],
          ['name', 'partner_id', 'date_order', 'amount_total', 'state'],
          input.limit || 80
        );
      }),

    get: protectedProcedure
      .input(z.object({ id: z.number() }))
      .query(async ({ ctx, input }) => {
        const client = new OdooClient(ctx.token);
        return await client.read('sale.order', input.id);
      }),

    create: protectedProcedure
      .input(z.object({
        partner_id: z.number(),
        order_line: z.array(z.any()).optional(),
      }))
      .mutation(async ({ ctx, input }) => {
        const client = new OdooClient(ctx.token);
        return await client.create('sale.order', input);
      }),

    confirm: protectedProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ ctx, input }) => {
        const client = new OdooClient(ctx.token);
        return await client.call('sale.order', input.id, 'action_confirm');
      }),
  }),

  // Products
  products: router({
    list: protectedProcedure
      .input(z.object({
        search: z.string().optional(),
        limit: z.number().optional(),
      }))
      .query(async ({ ctx, input }) => {
        const client = new OdooClient(ctx.token);
        const domain = input.search
          ? [['name', 'ilike', input.search]]
          : [];
        return await client.search(
          'product.product',
          domain,
          ['name', 'list_price', 'qty_available'],
          input.limit || 50
        );
      }),
  }),

  // Partners
  partners: router({
    list: protectedProcedure.query(async ({ ctx }) => {
      const client = new OdooClient(ctx.token);
      return await client.search(
        'res.partner',
        [['customer_rank', '>', 0]],
        ['name', 'email', 'phone'],
        100
      );
    }),
  }),
});

export type AppRouter = typeof appRouter;
\`\`\`

---

## 5. React Frontend (with tRPC)

```bash
# Create React app
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
npm install @trpc/client @trpc/react-query @tanstack/react-query
```

**`frontend/src/utils/trpc.ts`**:

\`\`\`typescript
import { createTRPCReact } from '@trpc/react-query';
import type { AppRouter } from '../../../api-gateway/src/trpc/router';

export const trpc = createTRPCReact<AppRouter>();
\`\`\`

**`frontend/src/app/providers.tsx`**:

\`\`\`typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { httpBatchLink } from '@trpc/client';
import { useState } from 'react';
import { trpc } from '@/utils/trpc';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());
  const [trpcClient] = useState(() =>
    trpc.createClient({
      links: [
        httpBatchLink({
          url: 'http://localhost:3001/trpc',
          headers() {
            const token = localStorage.getItem('token');
            return token ? { authorization: \`Bearer \${token}\` } : {};
          },
        }),
      ],
    })
  );

  return (
    <trpc.Provider client={trpcClient} queryClient={queryClient}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </trpc.Provider>
  );
}
\`\`\`

**`frontend/src/app/page.tsx`**:

\`\`\`typescript
'use client';

import { trpc } from '@/utils/trpc';
import { useState } from 'react';

export default function Home() {
  const [token, setToken] = useState('');

  const loginMutation = trpc.auth.login.useMutation({
    onSuccess: (data) => {
      localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
    },
  });

  const { data: orders } = trpc.sales.list.useQuery(
    { limit: 10 },
    { enabled: !!token }
  );

  const confirmMutation = trpc.sales.confirm.useMutation({
    onSuccess: () => {
      alert('Order confirmed!');
    },
  });

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Odoo Frontend</h1>

      {!token ? (
        <div className="max-w-md">
          <h2 className="text-xl mb-4">Login</h2>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const form = e.target as HTMLFormElement;
              loginMutation.mutate({
                login: form.login.value,
                password: form.password.value,
              });
            }}
          >
            <input
              name="login"
              placeholder="Login"
              className="border p-2 w-full mb-2"
            />
            <input
              name="password"
              type="password"
              placeholder="Password"
              className="border p-2 w-full mb-2"
            />
            <button
              type="submit"
              className="bg-blue-500 text-white px-4 py-2 rounded"
            >
              Login
            </button>
          </form>
        </div>
      ) : (
        <div>
          <h2 className="text-xl mb-4">Sales Orders</h2>
          {orders?.data?.map((order: any) => (
            <div key={order.id} className="border p-4 mb-2">
              <p><strong>{order.name}</strong></p>
              <p>Total: ${order.amount_total}</p>
              <p>State: {order.state}</p>
              {order.state === 'draft' && (
                <button
                  onClick={() => confirmMutation.mutate({ id: order.id })}
                  className="bg-green-500 text-white px-3 py-1 rounded mt-2"
                >
                  Confirm Order
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
\`\`\`

---

## 6. Start Everything

```bash
# Terminal 1: Start Odoo
cd /Users/mahmoudabdelhadi/odoo
./odoo-bin -c odoo.conf

# Terminal 2: Start Express API Gateway
cd /Users/mahmoudabdelhadi/odoo/api-gateway
npx tsx src/server.ts

# Terminal 3: Start React Frontend
cd /Users/mahmoudabdelhadi/odoo/frontend
npm run dev
```

Now visit:
- **Odoo**: http://localhost:8069
- **API Gateway**: http://localhost:3001
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8069/api/docs

---

## Summary

✅ **Odoo REST API Module** - Provides JWT auth + CRUD endpoints
✅ **OpenAPI/Swagger Docs** - Auto-generated API documentation
✅ **Express + tRPC Gateway** - Type-safe API layer
✅ **React Frontend** - Separate UI consuming the API

You now have a fully decoupled architecture!
