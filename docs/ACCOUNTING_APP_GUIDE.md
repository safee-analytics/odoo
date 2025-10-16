# Building Accounting App with Next.js + Odoo

Let's build a real accounting dashboard step by step!

---

## What We're Building

**An accounting dashboard with:**
1. 📊 **Dashboard** - Key metrics (revenue, expenses, profit)
2. 📄 **Invoices List** - View all invoices
3. ✅ **Post Invoice** - Post invoices with one click
4. 💰 **Register Payment** - Mark invoices as paid
5. 📈 **Reports** - Balance sheet, P&L, cash flow

---

## Step 1: Setup Next.js Project

```bash
cd ~/projects
npx create-next-app@latest accounting-app

# Choose:
✔ TypeScript? … Yes
✔ Tailwind CSS? … Yes
✔ App Router? … Yes

cd accounting-app
npm install axios
npm install @tanstack/react-query
```

---

## Step 2: Create Odoo Client

### File: `lib/odoo-client.ts`

```typescript
import axios, { AxiosInstance } from 'axios';

const ODOO_URL = 'http://localhost:8069';

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

    // Load token from localStorage
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('odoo_token');
      if (this.token) {
        this.api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
      }
    }
  }

  async login(login: string, password: string, db: string = 'odoo_db') {
    const response = await this.api.post('/api/auth/login', {
      jsonrpc: '2.0',
      method: 'call',
      params: { login, password, db },
      id: this.requestId++,
    });

    const result = response.data.result;
    this.token = result.access_token;
    this.api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;

    if (typeof window !== 'undefined') {
      localStorage.setItem('odoo_token', this.token);
    }

    return result;
  }

  // Generic search
  async search<T = any>(model: string, domain: any[] = [], fields: string[] = [], limit = 80) {
    const response = await this.api.post(`/api/${model}`, {
      jsonrpc: '2.0',
      method: 'call',
      params: { domain, fields, limit },
      id: this.requestId++,
    });

    return response.data.result.data as T[];
  }

  // Call method
  async callMethod<T = any>(model: string, id: number, method: string, args: any[] = [], kwargs: any = {}) {
    const response = await this.api.post(`/api/${model}/${id}/call/${method}`, {
      jsonrpc: '2.0',
      method: 'call',
      params: { args, kwargs },
      id: this.requestId++,
    });

    return response.data.result as T;
  }

  // Accounting specific methods

  // Get invoices list
  async getInvoices(type: 'out_invoice' | 'in_invoice' = 'out_invoice', state?: string) {
    const response = await this.api.post('/api/accounting/invoices/list', {
      jsonrpc: '2.0',
      method: 'call',
      params: { type, state, limit: 50 },
      id: this.requestId++,
    });

    return response.data.result.data;
  }

  // Post invoice
  async postInvoice(invoiceId: number) {
    const response = await this.api.post(`/api/accounting/invoice/${invoiceId}/post`, {
      jsonrpc: '2.0',
      method: 'call',
      params: {},
      id: this.requestId++,
    });

    return response.data.result;
  }

  // Register payment
  async registerPayment(invoiceId: number, amount: number, paymentDate: string) {
    const response = await this.api.post(`/api/accounting/invoice/${invoiceId}/register_payment`, {
      jsonrpc: '2.0',
      method: 'call',
      params: { amount, payment_date: paymentDate },
      id: this.requestId++,
    });

    return response.data.result;
  }

  // Get Balance Sheet
  async getBalanceSheet(date?: string) {
    const response = await this.api.post('/api/accounting/reports/balance_sheet', {
      jsonrpc: '2.0',
      method: 'call',
      params: { date },
      id: this.requestId++,
    });

    return response.data.result.data;
  }

  // Get Profit & Loss
  async getProfitLoss(dateFrom?: string, dateTo?: string) {
    const response = await this.api.post('/api/accounting/reports/profit_loss', {
      jsonrpc: '2.0',
      method: 'call',
      params: { date_from: dateFrom, date_to: dateTo },
      id: this.requestId++,
    });

    return response.data.result.data;
  }

  // Get Aged Receivables
  async getAgedReceivables(date?: string) {
    const response = await this.api.post('/api/accounting/reports/aged_receivables', {
      jsonrpc: '2.0',
      method: 'call',
      params: { date },
      id: this.requestId++,
    });

    return response.data.result.data;
  }
}

export const odooClient = new OdooClient();
```

---

## Step 3: Login Page

### File: `app/page.tsx`

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
      await odooClient.login(login, password);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.result?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600">
      <div className="bg-white p-8 rounded-2xl shadow-2xl w-96">
        <h1 className="text-3xl font-bold mb-2 text-center text-gray-800">
          Accounting App
        </h1>
        <p className="text-gray-500 text-center mb-6">Sign in to continue</p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
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
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}
```

---

## Step 4: Dashboard Home

### File: `app/dashboard/page.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { odooClient } from '@/lib/odoo-client';
import Link from 'next/link';

interface DashboardStats {
  totalRevenue: number;
  totalExpenses: number;
  profit: number;
  unpaidInvoices: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    totalRevenue: 0,
    totalExpenses: 0,
    profit: 0,
    unpaidInvoices: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      // Get P&L data
      const pl = await odooClient.getProfitLoss();

      // Get unpaid invoices count
      const invoices = await odooClient.getInvoices('out_invoice');
      const unpaid = invoices.filter((inv: any) => inv.payment_state === 'not_paid').length;

      setStats({
        totalRevenue: pl.revenue.total || 0,
        totalExpenses: pl.expenses.total || 0,
        profit: pl.net_profit || 0,
        unpaidInvoices: unpaid,
      });
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading dashboard...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Accounting Dashboard</h1>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Revenue Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Revenue</p>
                <p className="text-2xl font-bold text-green-600">
                  ${stats.totalRevenue.toFixed(2)}
                </p>
              </div>
              <div className="bg-green-100 p-3 rounded-full">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Expenses Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Expenses</p>
                <p className="text-2xl font-bold text-red-600">
                  ${stats.totalExpenses.toFixed(2)}
                </p>
              </div>
              <div className="bg-red-100 p-3 rounded-full">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Profit Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Net Profit</p>
                <p className="text-2xl font-bold text-blue-600">
                  ${stats.profit.toFixed(2)}
                </p>
              </div>
              <div className="bg-blue-100 p-3 rounded-full">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
            </div>
          </div>

          {/* Unpaid Invoices Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Unpaid Invoices</p>
                <p className="text-2xl font-bold text-orange-600">
                  {stats.unpaidInvoices}
                </p>
              </div>
              <div className="bg-orange-100 p-3 rounded-full">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link
            href="/dashboard/invoices"
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
          >
            <h3 className="text-lg font-semibold mb-2">📄 Invoices</h3>
            <p className="text-gray-600">View and manage all invoices</p>
          </Link>

          <Link
            href="/dashboard/reports"
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
          >
            <h3 className="text-lg font-semibold mb-2">📊 Reports</h3>
            <p className="text-gray-600">Financial reports and analytics</p>
          </Link>

          <Link
            href="/dashboard/receivables"
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
          >
            <h3 className="text-lg font-semibold mb-2">💰 Receivables</h3>
            <p className="text-gray-600">Track outstanding payments</p>
          </Link>
        </div>
      </div>
    </div>
  );
}
```

---

## Step 5: Invoices List

### File: `app/dashboard/invoices/page.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { odooClient } from '@/lib/odoo-client';
import Link from 'next/link';

interface Invoice {
  id: number;
  name: string;
  partner_id: number;
  partner_name: string;
  invoice_date: string;
  invoice_date_due: string;
  amount_total: number;
  amount_residual: number;
  state: string;
  payment_state: string;
}

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'draft' | 'posted' | 'paid'>('all');

  useEffect(() => {
    loadInvoices();
  }, [filter]);

  const loadInvoices = async () => {
    setLoading(true);
    try {
      const state = filter === 'all' ? undefined :
                   filter === 'posted' ? 'posted' :
                   filter === 'draft' ? 'draft' : undefined;

      const data = await odooClient.getInvoices('out_invoice', state);
      setInvoices(data);
    } catch (err) {
      console.error('Failed to load invoices:', err);
    } finally {
      setLoading(false);
    }
  };

  const postInvoice = async (invoiceId: number) => {
    if (!confirm('Post this invoice?')) return;

    try {
      await odooClient.postInvoice(invoiceId);
      alert('Invoice posted successfully!');
      loadInvoices();
    } catch (err: any) {
      alert('Failed to post invoice: ' + (err.message || 'Unknown error'));
    }
  };

  const registerPayment = async (invoice: Invoice) => {
    const amount = prompt(`Enter payment amount (due: $${invoice.amount_residual}):`);
    if (!amount) return;

    try {
      await odooClient.registerPayment(invoice.id, parseFloat(amount), new Date().toISOString().split('T')[0]);
      alert('Payment registered!');
      loadInvoices();
    } catch (err: any) {
      alert('Failed to register payment: ' + (err.message || 'Unknown error'));
    }
  };

  const getStateBadge = (state: string) => {
    const colors: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-800',
      posted: 'bg-blue-100 text-blue-800',
      cancel: 'bg-red-100 text-red-800',
    };
    return colors[state] || 'bg-gray-100 text-gray-800';
  };

  const getPaymentBadge = (state: string) => {
    const colors: Record<string, string> = {
      not_paid: 'bg-orange-100 text-orange-800',
      paid: 'bg-green-100 text-green-800',
      partial: 'bg-yellow-100 text-yellow-800',
    };
    return colors[state] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/dashboard" className="text-gray-500 hover:text-gray-700">
                ← Back
              </Link>
              <h1 className="text-3xl font-bold text-gray-900">Invoices</h1>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex gap-2">
            {['all', 'draft', 'posted', 'paid'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f as any)}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  filter === f
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Invoices Table */}
        {loading ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            Loading invoices...
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Invoice #</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Due Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Due</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payment</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {invoices.map((invoice) => (
                  <tr key={invoice.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap font-medium">{invoice.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{invoice.partner_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {invoice.invoice_date ? new Date(invoice.invoice_date).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {invoice.invoice_date_due ? new Date(invoice.invoice_date_due).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">${invoice.amount_total.toFixed(2)}</td>
                    <td className="px-6 py-4 whitespace-nowrap">${invoice.amount_residual.toFixed(2)}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStateBadge(invoice.state)}`}>
                        {invoice.state}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPaymentBadge(invoice.payment_state)}`}>
                        {invoice.payment_state}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex gap-2">
                        {invoice.state === 'draft' && (
                          <button
                            onClick={() => postInvoice(invoice.id)}
                            className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
                          >
                            Post
                          </button>
                        )}
                        {invoice.state === 'posted' && invoice.payment_state === 'not_paid' && (
                          <button
                            onClick={() => registerPayment(invoice)}
                            className="text-xs bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700"
                          >
                            Pay
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {invoices.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                No invoices found
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## Step 6: Run the App

```bash
# Terminal 1: Odoo
cd ~/odoo
./odoo-bin -c odoo.conf

# Terminal 2: Next.js
cd ~/projects/accounting-app
npm run dev
```

Open: http://localhost:3000

---

## What You Can Do Now

✅ **Login** - Sign in with your Odoo credentials
✅ **View Dashboard** - See revenue, expenses, profit
✅ **View Invoices** - List all customer invoices
✅ **Post Invoice** - Click "Post" to finalize draft invoices
✅ **Register Payment** - Click "Pay" to mark invoice as paid

---

## Next Steps

1. **Add Reports Page** - Show Balance Sheet, P&L charts
2. **Add Vendor Bills** - Manage payables
3. **Add Bank Reconciliation** - Match bank statements
4. **Add Charts** - Use Chart.js for visualizations

Want me to add any of these next?
