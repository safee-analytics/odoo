# Actually Implemented Endpoints

## ✅ **Currently Working (33 endpoints)**

### **Authentication (3 endpoints)**
- ✅ `POST /api/auth/login` - Login with JWT
- ✅ `GET /api/auth/me` - Get current user
- ✅ `POST /api/auth/refresh` - Refresh token

### **Generic CRUD (7 endpoints - works for ALL models)**
- ✅ `GET /api/{model}` - Search records
- ✅ `GET /api/{model}/{id}` - Read single record
- ✅ `POST /api/{model}` - Create record
- ✅ `PUT /api/{model}/{id}` - Update record (also PATCH)
- ✅ `DELETE /api/{model}/{id}` - Delete record
- ✅ `POST /api/{model}/{id}/call/{method}` - Call method on record
- ✅ `POST /api/{model}/call/{method}` - Call static method

### **Sales (3 endpoints)**
- ✅ `GET /api/sales/dashboard` - Sales analytics dashboard
- ✅ `POST /api/sales/confirm/{order_id}` - Confirm sales order
- ✅ `POST /api/sales/{order_id}/create_invoice` - Create invoice from SO

### **Accounting (14 endpoints)**
**Invoices:**
- ✅ `POST /api/accounting/invoices/list` - List invoices with filters
- ✅ `POST /api/accounting/invoice/{id}/post` - Post invoice (journal entries)
- ✅ `POST /api/accounting/invoice/{id}/register_payment` - Register payment
- ✅ `POST /api/accounting/invoice/{id}/send_email` - Email invoice

**Payments:**
- ✅ `POST /api/accounting/payments/list` - List payments

**Reconciliation:**
- ✅ `GET /api/accounting/reconciliation/bank_statements` - Get bank statements
- ✅ `GET /api/accounting/reconciliation/suggestions/{line_id}` - Match suggestions

**Reports:**
- ✅ `POST /api/accounting/reports/balance_sheet` - Balance Sheet
- ✅ `POST /api/accounting/reports/profit_loss` - Profit & Loss
- ✅ `POST /api/accounting/reports/aged_receivables` - AR Aging Report
- ✅ `POST /api/accounting/reports/cash_flow` - Cash Flow Statement
- ✅ `POST /api/accounting/reports/tax_report` - Tax Report

**Legacy (duplicate):**
- ✅ `GET /api/accounting/receivables` - Receivables overview
- ✅ `POST /api/accounting/post_invoice/{id}` - (duplicate of above)
- ✅ `GET /api/reports/profit_loss` - (duplicate of above)

### **Inventory (2 endpoints)**
- ✅ `GET /api/inventory/stock_levels` - Stock levels with low stock alerts
- ✅ `POST /api/inventory/validate_delivery/{picking_id}` - Validate delivery

### **Customers (1 endpoint)**
- ✅ `GET /api/customers/top` - Top customers with analytics

### **Documentation (2 endpoints)**
- ✅ `GET /api/docs` - Swagger UI interface
- ✅ `GET /api/openapi.json` - OpenAPI spec JSON

---

## ❌ **NOT Yet Implemented (Use CRUD + Method Calling Instead)**

All of these can be done using the generic CRUD endpoints! Here's how:

### **Purchase**
```bash
# List purchase orders
GET /api/purchase.order?domain=[["state","=","draft"]]

# Create RFQ
POST /api/purchase.order
Body: {"vals": {"partner_id": 5}}

# Confirm PO
POST /api/purchase.order/123/call/button_confirm

# Cancel PO
POST /api/purchase.order/123/call/button_cancel

# Create bill
POST /api/purchase.order/123/call/action_create_invoice
```

### **CRM**
```bash
# List leads
GET /api/crm.lead

# Create lead
POST /api/crm.lead
Body: {"vals": {"name": "New Lead", "email_from": "test@example.com"}}

# Convert to opportunity
POST /api/crm.lead/10/call/convert_opportunity

# Mark won
POST /api/crm.lead/10/call/action_set_won

# Mark lost
POST /api/crm.lead/10/call/action_set_lost
```

### **HR - Employees**
```bash
# List employees
GET /api/hr.employee

# Create employee
POST /api/hr.employee
Body: {"vals": {"name": "John Doe", "work_email": "john@example.com"}}

# Get employee details
GET /api/hr.employee/5
```

### **HR - Attendance**
```bash
# Check in
POST /api/hr.attendance
Body: {"vals": {"employee_id": 5}}

# Check out (updates last record)
# First get the attendance record
GET /api/hr.attendance?domain=[["employee_id","=",5],["check_out","=",false]]

# Then call check out
POST /api/hr.attendance/123/call/action_check_out

# Get attendance history
GET /api/hr.attendance?domain=[["employee_id","=",5]]
```

### **HR - Leaves**
```bash
# List leave requests
GET /api/hr.leave

# Create leave request
POST /api/hr.leave
Body: {
  "vals": {
    "employee_id": 5,
    "holiday_status_id": 1,
    "request_date_from": "2025-10-20",
    "request_date_to": "2025-10-22"
  }
}

# Approve leave
POST /api/hr.leave/10/call/action_approve

# Refuse leave
POST /api/hr.leave/10/call/action_refuse
```

### **HR - Expenses**
```bash
# List expenses
GET /api/hr.expense

# Create expense
POST /api/hr.expense
Body: {
  "vals": {
    "employee_id": 5,
    "product_id": 10,
    "unit_amount": 50.00,
    "name": "Client Dinner"
  }
}

# Submit expense
POST /api/hr.expense/20/call/action_submit_expenses

# Approve expense
POST /api/hr.expense/20/call/approve_expense_sheets

# Post to accounting
POST /api/hr.expense/20/call/action_sheet_move_create
```

### **HR - Timesheets**
```bash
# List timesheets
GET /api/account.analytic.line?domain=[["project_id","!=",false]]

# Create timesheet
POST /api/account.analytic.line
Body: {
  "vals": {
    "employee_id": 5,
    "project_id": 10,
    "task_id": 50,
    "unit_amount": 8.0,
    "name": "Development work"
  }
}
```

### **Project Management**
```bash
# List projects
GET /api/project.project

# Create project
POST /api/project.project
Body: {"vals": {"name": "New Project", "partner_id": 5}}

# List tasks
GET /api/project.task

# Create task
POST /api/project.task
Body: {
  "vals": {
    "name": "Task name",
    "project_id": 10,
    "user_ids": [[6, 0, [5]]]
  }
}

# Mark task done
POST /api/project.task/123/call/action_done

# Assign task
PUT /api/project.task/123
Body: {"vals": {"user_ids": [[6, 0, [5, 10]]]}}
```

### **Manufacturing**
```bash
# List MOs
GET /api/mrp.production

# Create MO
POST /api/mrp.production
Body: {
  "vals": {
    "product_id": 10,
    "product_qty": 100,
    "bom_id": 5
  }
}

# Confirm MO
POST /api/mrp.production/50/call/action_confirm

# Mark done
POST /api/mrp.production/50/call/button_mark_done

# List BOMs
GET /api/mrp.bom
```

### **Mail & Messaging**
```bash
# Get messages
GET /api/mail.message

# Send message
POST /api/mail.message
Body: {
  "vals": {
    "body": "Message content",
    "model": "sale.order",
    "res_id": 123,
    "message_type": "comment"
  }
}

# List channels
GET /api/mail.channel

# Post to channel
POST /api/mail.channel/5/call/message_post
Body: {
  "args": [],
  "kwargs": {
    "body": "Hello channel!",
    "message_type": "comment"
  }
}

# Get activities
GET /api/mail.activity

# Create activity
POST /api/mail.activity
Body: {
  "vals": {
    "res_model": "sale.order",
    "res_id": 123,
    "activity_type_id": 1,
    "summary": "Follow up call",
    "user_id": 5
  }
}

# Mark activity done
POST /api/mail.activity/10/call/action_done
```

### **Inventory - Advanced**
```bash
# Get stock by location
GET /api/stock.quant?domain=[["location_id","=",8]]

# Create internal transfer
POST /api/stock.picking
Body: {
  "vals": {
    "picking_type_id": 5,
    "location_id": 8,
    "location_dest_id": 9,
    "move_ids_without_package": [[0, 0, {
      "product_id": 10,
      "product_uom_qty": 50
    }]]
  }
}

# Stock adjustment
POST /api/stock.quant/call/create
Body: {
  "vals": {
    "product_id": 10,
    "location_id": 8,
    "inventory_quantity": 100
  }
}
```

---

## 🎯 **Key Point: You Have Everything!**

The **7 generic CRUD endpoints** give you access to:
- **ALL 1000+ Odoo models**
- **ALL business logic methods**
- **ALL workflows**

You don't need dedicated endpoints for most things!

---

## 📊 **Model + Method Discovery**

### **How to find what you need:**

1. **Find the model name:**
   ```bash
   # In Odoo UI, open browser console
   # Go to the feature you want
   # Check Network tab for the model name
   ```

2. **Find available methods:**
   ```bash
   # Use CRUD read to see available methods
   GET /api/ir.model.methods?domain=[["model","=","purchase.order"]]
   ```

3. **Call any method:**
   ```bash
   POST /api/{model}/{id}/call/{method_name}
   ```

---

## 🔥 **Summary**

**Total Implemented: 33 endpoints**
- Authentication: 3
- Generic CRUD: 7 (works for EVERYTHING)
- Sales: 3
- Accounting: 14
- Inventory: 2
- Customers: 1
- Documentation: 2

**Total Accessible: UNLIMITED**
- Use CRUD + method calling for any Odoo operation
- Every model, every workflow, every business logic

---

**The generic CRUD API is the most powerful feature - it gives you 100% of Odoo!** 🎉
