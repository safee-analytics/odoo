# Architecture Comparison: REST API vs Direct tRPC

## Option 1: Current Setup (REST API + Optional tRPC Gateway)

```
┌─────────────┐      ┌──────────────┐      ┌────────────┐
│   React     │─tRPC─│   Express    │─HTTP─│    Odoo    │
│  Frontend   │      │   Gateway    │      │  REST API  │
└─────────────┘      └──────────────┘      └────────────┘
```

### Pros
✅ **Separation of concerns** - Frontend doesn't know about Odoo internals
✅ **Multiple clients** - Mobile, web, partners all use same API
✅ **Caching layer** - Redis in Express for fast responses
✅ **Rate limiting** - Protect Odoo backend
✅ **Data transformation** - Clean up Odoo's complex responses
✅ **Technology agnostic** - Can swap Odoo for another ERP
✅ **Standard HTTP** - Works with any tool (Postman, curl, mobile SDKs)
✅ **API documentation** - OpenAPI/Swagger for partners

### Cons
⚠️ **Extra hop** - Adds 10-50ms latency
⚠️ **More infrastructure** - Need to deploy Express server
⚠️ **Double maintenance** - REST API + tRPC types

### Best For
- 🏢 **Enterprise** - Multiple teams, multiple frontends
- 🌍 **Public API** - External partners need access
- 📱 **Mobile apps** - Need REST API anyway
- 🔄 **Migration path** - Might replace Odoo later

---

## Option 2: Direct Odoo API (No Gateway)

```
┌─────────────┐      ┌────────────────────┐
│   React     │─HTTP─│    Odoo Backend    │
│  Frontend   │      │  (REST API)        │
└─────────────┘      └────────────────────┘
```

### Pros
✅ **Simpler** - One less server to manage
✅ **Faster** - Direct connection, no middleware
✅ **Less code** - No Express layer
✅ **Still type-safe** - Can generate TypeScript types from OpenAPI

### Cons
⚠️ **Tightly coupled** - Frontend knows Odoo structure
⚠️ **No caching layer** - Every request hits Odoo
⚠️ **Harder to scale** - Can't distribute load easily
⚠️ **Odoo exposed** - Frontend hits Odoo directly

### Best For
- 🚀 **Startups** - Move fast, simple architecture
- 👤 **Single frontend** - Only one web app
- 🔒 **Internal only** - No external API needed
- ⚡ **Speed to market** - Don't want to manage extra infrastructure

---

## Option 3: tRPC Directly in Odoo (Not Recommended)

```
┌─────────────┐      ┌────────────────────┐
│   React     │─tRPC─│    Odoo Backend    │
│  Frontend   │      │  (Python + tRPC)   │
└─────────────┘      └────────────────────┘
```

### Why This Is Hard
- ❌ **tRPC is TypeScript/JavaScript only** - No native Python support
- ❌ **Would need custom protocol** - Rebuild tRPC in Python
- ❌ **Breaking Odoo conventions** - Odoo expects JSON-RPC
- ❌ **Type safety issues** - Python → TypeScript type generation is complex

### To Make This Work You'd Need
1. Build a tRPC-compatible Python server (doesn't exist)
2. OR use gRPC (different from tRPC, but similar benefits)
3. OR use GraphQL (another option)

---

## Recommended Architecture

### For Your Case (SAFEE):

```
┌─────────────┐      ┌──────────────┐      ┌────────────┐
│   Next.js   │─tRPC─│   Express    │─HTTP─│    Odoo    │
│   Frontend  │      │   + tRPC     │      │  REST API  │
└─────────────┘      └──────────────┘      └────────────┘
                            │
                            ├─ Type-safe tRPC procedures
                            ├─ Redis caching
                            ├─ Rate limiting
                            ├─ Business logic
                            └─ Data transformation
```

**Why:**
1. **Frontend gets type safety** (tRPC between React ↔ Express)
2. **Backend stays standard** (REST between Express ↔ Odoo)
3. **Best of both worlds** - Type safety + flexibility

---

## Alternative: Direct REST (Simpler)

```
┌─────────────┐      ┌────────────┐
│   Next.js   │─HTTP─│    Odoo    │
│   Frontend  │      │  REST API  │
└─────────────┘      └────────────┘
        │
        └─ Generate TypeScript types from OpenAPI spec
```

**Use this if:**
- You don't need tRPC's features
- Want simplest possible setup
- OpenAPI type generation is enough

**Tools:**
- `openapi-typescript` - Generates types from OpenAPI spec
- `@hey-api/openapi-ts` - Better type generation
- `react-query` - Still get good DX without tRPC

---

## Code Examples

### Current Setup (REST API + tRPC Gateway)

**Express tRPC Router:**
```typescript
// server/trpc/router.ts
export const appRouter = router({
  sales: router({
    dashboard: publicProcedure.query(async () => {
      // Call Odoo REST API
      const response = await fetch('http://odoo:8069/api/sales/dashboard', {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.json();
    }),

    confirmOrder: publicProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input }) => {
        // Call Odoo REST API
        const response = await fetch(`http://odoo:8069/api/sales/confirm/${input.id}`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` }
        });
        return response.json();
      })
  })
});
```

**React Component:**
```typescript
// frontend/components/SalesDashboard.tsx
const { data } = trpc.sales.dashboard.useQuery();
const confirmMutation = trpc.sales.confirmOrder.useMutation();

// Full type safety!
```

---

### Alternative: Direct REST with Generated Types

**Generate types:**
```bash
npx openapi-typescript http://localhost:8069/api/openapi.json -o types/odoo-api.ts
```

**React Component:**
```typescript
// frontend/api/odoo.ts
import type { paths } from './types/odoo-api';

type SalesDashboard = paths['/api/sales/dashboard']['get']['responses']['200']['content']['application/json'];

// Use with react-query
const { data } = useQuery<SalesDashboard>({
  queryKey: ['sales', 'dashboard'],
  queryFn: () => fetch('/api/sales/dashboard').then(r => r.json())
});
```

---

## My Recommendation for SAFEE

**Phase 1: Start Simple (Now)**
```
React ──HTTP──> Odoo REST API
```
- Use OpenAPI type generation
- Use React Query for state management
- Get to market fast

**Phase 2: Add Gateway (Later)**
```
React ──tRPC──> Express ──> Odoo
```
- Add when you need caching
- Add when you need rate limiting
- Add when you have multiple frontends

**Don't start with complex architecture unless you need it!**

---

## Decision Matrix

| Feature | Direct REST | REST + Express | tRPC Direct |
|---------|-------------|----------------|-------------|
| Type Safety | ⚠️ (Generated) | ✅ (Native) | ✅ (Native) |
| Simplicity | ✅ | ⚠️ | ❌ |
| Performance | ✅ | ⚠️ (-50ms) | ✅ |
| Caching | ❌ | ✅ | ❌ |
| Multiple Clients | ✅ | ✅ | ❌ |
| Setup Time | 1 hour | 4 hours | Weeks |
| Maintenance | Low | Medium | High |

**For SAFEE: Start with Direct REST, add Express gateway only if needed.**
