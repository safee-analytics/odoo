# Complete Business Logic API Endpoints

This document lists ALL business logic endpoints available in the REST API.

## Quick Links
- [Accounting](#accounting)
- [Sales](#sales)
- [Purchase](#purchase)
- [Inventory](#inventory)
- [CRM](#crm)
- [HR](#hr)
- [Project](#project)
- [Manufacturing](#manufacturing)
- [Mail & Messaging](#mail--messaging)
- [Reports & Analytics](#reports--analytics)

---

## Accounting

### Invoices
- `POST /api/accounting/invoices/list` - List invoices with filters
- `POST /api/accounting/invoice/{id}/post` - Post invoice (creates journal entries)
- `POST /api/accounting/invoice/{id}/register_payment` - Register payment
- `POST /api/accounting/invoice/{id}/send_email` - Send invoice by email
- `POST /api/accounting/invoice/{id}/cancel` - Cancel invoice
- `POST /api/accounting/invoice/{id}/reset_to_draft` - Reset to draft

### Payments
- `POST /api/accounting/payments/list` - List payments
- `POST /api/accounting/payment/create` - Create payment
- `POST /api/accounting/payment/{id}/post` - Post payment

### Bank Reconciliation
- `GET /api/accounting/reconciliation/bank_statements` - Get open bank statements
- `GET /api/accounting/reconciliation/suggestions/{line_id}` - Get match suggestions
- `POST /api/accounting/reconciliation/process` - Process reconciliation

### Reports
- `POST /api/accounting/reports/balance_sheet` - Balance Sheet
- `POST /api/accounting/reports/profit_loss` - Profit & Loss (P&L)
- `POST /api/accounting/reports/aged_receivables` - AR Aging Report
- `POST /api/accounting/reports/aged_payables` - AP Aging Report  
- `POST /api/accounting/reports/cash_flow` - Cash Flow Statement
- `POST /api/accounting/reports/tax_report` - Tax Report
- `POST /api/accounting/reports/general_ledger` - General Ledger
- `POST /api/accounting/reports/trial_balance` - Trial Balance
- `POST /api/accounting/reports/partner_ledger` - Partner Ledger

---

## Sales

### Orders
- `POST /api/sales/orders/list` - List sales orders
- `POST /api/sales/order/create` - Create quotation
- `POST /api/sales/order/{id}/confirm` - Confirm order (triggers delivery, stock, invoicing)
- `POST /api/sales/order/{id}/cancel` - Cancel order
- `POST /api/sales/order/{id}/create_invoice` - Create invoice from order
- `POST /api/sales/order/{id}/send_email` - Send quotation by email
- `POST /api/sales/order/{id}/action_quotation_sent` - Mark as sent

### Analytics
- `GET /api/sales/dashboard` - Sales dashboard (revenue, trends, top customers)
- `GET /api/sales/revenue_by_period` - Revenue analysis by period
- `GET /api/sales/revenue_by_product` - Revenue by product
- `GET /api/sales/revenue_by_salesperson` - Revenue by salesperson
- `GET /api/sales/pipeline` - Sales pipeline analysis

### Products in Sales
- `GET /api/sales/products/bestsellers` - Best selling products
- `GET /api/sales/products/low_margin` - Products with low margins

---

## Purchase

### Purchase Orders
- `POST /api/purchase/orders/list` - List purchase orders
- `POST /api/purchase/order/create` - Create RFQ
- `POST /api/purchase/order/{id}/confirm` - Confirm purchase order
- `POST /api/purchase/order/{id}/cancel` - Cancel PO
- `POST /api/purchase/order/{id}/receive` - Mark as received
- `POST /api/purchase/order/{id}/create_bill` - Create vendor bill

### Vendors
- `GET /api/purchase/vendors/list` - List vendors
- `GET /api/purchase/vendors/top` - Top vendors by spend
- `GET /api/purchase/vendor/{id}/history` - Purchase history

### Analytics
- `GET /api/purchase/dashboard` - Purchase dashboard
- `GET /api/purchase/spend_analysis` - Spend analysis

---

## Inventory

### Stock
- `GET /api/inventory/stock_levels` - Current stock levels
- `GET /api/inventory/stock_by_location` - Stock by location
- `GET /api/inventory/stock_moves` - Stock movements
- `GET /api/inventory/low_stock_alert` - Products with low stock
- `GET /api/inventory/stock_valuation` - Stock valuation

### Warehouse Operations
- `POST /api/inventory/picking/{id}/validate` - Validate picking/delivery
- `POST /api/inventory/picking/{id}/cancel` - Cancel picking
- `POST /api/inventory/picking/create` - Create internal transfer
- `GET /api/inventory/pickings/list` - List pickings

### Products
- `POST /api/inventory/products/list` - List products with stock
- `GET /api/inventory/product/{id}/stock_history` - Product stock history
- `POST /api/inventory/product/{id}/adjust_stock` - Adjust stock quantity

### Reports
- `GET /api/inventory/reports/stock_moves_report` - Stock moves report
- `GET /api/inventory/reports/inventory_valuation` - Inventory valuation

---

## CRM

### Leads & Opportunities
- `POST /api/crm/leads/list` - List leads
- `POST /api/crm/lead/create` - Create lead
- `POST /api/crm/lead/{id}/convert_to_opportunity` - Convert to opportunity
- `POST /api/crm/lead/{id}/mark_won` - Mark as won
- `POST /api/crm/lead/{id}/mark_lost` - Mark as lost
- `POST /api/crm/lead/{id}/schedule_activity` - Schedule activity

### Pipeline
- `GET /api/crm/pipeline` - Pipeline overview
- `GET /api/crm/pipeline_by_stage` - Opportunities by stage
- `GET /api/crm/pipeline_by_team` - Pipeline by sales team

### Analytics
- `GET /api/crm/dashboard` - CRM dashboard
- `GET /api/crm/conversion_rates` - Lead conversion rates
- `GET /api/crm/revenue_forecast` - Revenue forecast
- `GET /api/crm/activities_summary` - Activities summary

---

## HR (Human Resources)

### Employees
- `POST /api/hr/employees/list` - List employees
- `POST /api/hr/employee/create` - Create employee
- `GET /api/hr/employee/{id}/details` - Employee details
- `POST /api/hr/employee/{id}/update` - Update employee

### Attendance
- `POST /api/hr/attendance/check_in` - Check in
- `POST /api/hr/attendance/check_out` - Check out
- `GET /api/hr/attendance/today` - Today's attendance
- `GET /api/hr/attendance/employee/{id}/history` - Attendance history

### Leaves (Time Off)
- `POST /api/hr/leaves/list` - List leave requests
- `POST /api/hr/leave/create` - Create leave request
- `POST /api/hr/leave/{id}/approve` - Approve leave
- `POST /api/hr/leave/{id}/refuse` - Refuse leave
- `GET /api/hr/leave/balance/{employee_id}` - Leave balance

### Expenses
- `POST /api/hr/expenses/list` - List expenses
- `POST /api/hr/expense/create` - Create expense
- `POST /api/hr/expense/{id}/submit` - Submit for approval
- `POST /api/hr/expense/{id}/approve` - Approve expense
- `POST /api/hr/expense/{id}/refuse` - Refuse expense
- `POST /api/hr/expense/{id}/post` - Post to accounting

### Timesheets
- `POST /api/hr/timesheets/list` - List timesheets
- `POST /api/hr/timesheet/create` - Create timesheet entry
- `GET /api/hr/timesheet/employee/{id}/summary` - Timesheet summary

### Recruitment
- `POST /api/hr/applicants/list` - List job applicants
- `POST /api/hr/applicant/{id}/hire` - Hire applicant
- `POST /api/hr/applicant/{id}/refuse` - Refuse applicant

### Analytics
- `GET /api/hr/dashboard` - HR dashboard
- `GET /api/hr/headcount` - Headcount report
- `GET /api/hr/attendance_report` - Attendance report

---

## Project Management

### Projects
- `POST /api/project/projects/list` - List projects
- `POST /api/project/create` - Create project
- `GET /api/project/{id}/overview` - Project overview

### Tasks
- `POST /api/project/tasks/list` - List tasks
- `POST /api/project/task/create` - Create task
- `POST /api/project/task/{id}/assign` - Assign task
- `POST /api/project/task/{id}/mark_done` - Mark task done
- `POST /api/project/task/{id}/add_timesheet` - Add timesheet

### Analytics
- `GET /api/project/dashboard` - Project dashboard
- `GET /api/project/{id}/progress` - Project progress
- `GET /api/project/{id}/profitability` - Project profitability
- `GET /api/project/burndown_chart` - Burndown chart

---

## Manufacturing (MRP)

### Manufacturing Orders
- `POST /api/mrp/orders/list` - List manufacturing orders
- `POST /api/mrp/order/create` - Create MO
- `POST /api/mrp/order/{id}/confirm` - Confirm MO
- `POST /api/mrp/order/{id}/mark_done` - Mark as done
- `POST /api/mrp/order/{id}/cancel` - Cancel MO

### Bill of Materials
- `POST /api/mrp/bom/list` - List BOMs
- `POST /api/mrp/bom/create` - Create BOM

### Work Centers
- `GET /api/mrp/workcenters/list` - List work centers
- `GET /api/mrp/workcenter/{id}/load` - Work center load

---

## Mail & Messaging

### Messages
- `POST /api/mail/messages/list` - List messages
- `POST /api/mail/message/send` - Send message
- `GET /api/mail/inbox` - User inbox
- `POST /api/mail/mark_as_read` - Mark messages as read

### Channels
- `POST /api/mail/channels/list` - List channels
- `POST /api/mail/channel/create` - Create channel
- `POST /api/mail/channel/{id}/post` - Post to channel
- `POST /api/mail/channel/{id}/join` - Join channel

### Notifications
- `GET /api/mail/notifications` - Get notifications
- `POST /api/mail/notifications/mark_read` - Mark as read

### Activities
- `POST /api/mail/activities/list` - List activities
- `POST /api/mail/activity/create` - Schedule activity
- `POST /api/mail/activity/{id}/mark_done` - Mark activity done

---

## Reports & Analytics

### Dashboard
- `GET /api/dashboard/overview` - Overall company dashboard
- `GET /api/dashboard/kpis` - Key performance indicators

### Custom Reports
- `POST /api/reports/execute` - Execute custom report
- `GET /api/reports/list` - List available reports

---

## Utility Endpoints

### File Management
- `POST /api/files/upload` - Upload attachment
- `GET /api/files/{id}/download` - Download attachment
- `DELETE /api/files/{id}/delete` - Delete attachment

### Search
- `POST /api/search/global` - Global search across all models
- `POST /api/search/recent` - Recently viewed records

### User Preferences
- `GET /api/user/preferences` - Get user preferences
- `POST /api/user/preferences/update` - Update preferences

### Company Settings
- `GET /api/company/info` - Company information
- `POST /api/company/update` - Update company info

---

## WebSocket / Real-time (Future)
- Live notifications
- Real-time updates
- Chat messaging

