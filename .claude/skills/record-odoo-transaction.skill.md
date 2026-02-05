---
name: record-odoo-transaction
description: Record business transactions (invoices, payments, expenses) in Odoo accounting system
version: 1.0.0
author: AI Employee Gold Tier
created: 2026-02-05
---

# Record Odoo Transaction

Record business transactions in Odoo Community Edition accounting system.

## Usage

This skill allows you to:
- Create customer invoices
- Record payments received
- Track business expenses

All transactions are automatically synced to Odoo and logged in the audit trail.

## Prerequisites

- Odoo Community Edition v19+ installed and running
- Odoo credentials configured in `.env` file
- Odoo MCP server running on port 3100

## Commands

### Create Invoice

```
Create an invoice for [customer name] for $[amount] for [description]
```

**Example:**
```
Create an invoice for Acme Corp for $2500 for "Website Development - Phase 1"
```

**What happens:**
1. AI Employee connects to Odoo via MCP server
2. Creates or finds the customer in Odoo
3. Creates invoice with specified amount and description
4. Sets payment terms (default: 30 days)
5. Logs transaction in audit log
6. Returns invoice ID and confirmation

### Record Payment

```
Record a payment of $[amount] for invoice [invoice_id] via [payment_method]
```

**Example:**
```
Record a payment of $2500 for invoice 42 via bank transfer
```

**Payment Methods:**
- `bank_transfer` (default)
- `cash`
- `check`
- `credit_card`
- `paypal`
- `other`

**What happens:**
1. AI Employee retrieves invoice from Odoo
2. Creates payment record
3. Links payment to invoice
4. Updates invoice status to "paid"
5. Logs transaction in audit log

### Record Expense

```
Record an expense of $[amount] for [category] - [description]
```

**Example:**
```
Record an expense of $150 for Office Supplies - "Printer paper and toner"
```

**Common Categories:**
- Office Supplies
- Travel
- Software Subscriptions
- Marketing
- Professional Services
- Utilities
- Other

**What happens:**
1. AI Employee creates vendor bill in Odoo
2. Categorizes expense for accounting
3. Logs transaction in audit log
4. Queues for retry if Odoo unavailable

## Error Handling

If Odoo is unavailable:
- Transaction is queued locally
- Automatic retry with exponential backoff
- User notified after 24 hours if still failing

## Examples

### Example 1: Create Invoice with Line Items

```
Create an invoice for Tech Solutions Inc with the following items:
- Web Development: 40 hours at $100/hour
- Design Services: 10 hours at $80/hour
Total: $4800
```

### Example 2: Record Multiple Expenses

```
Record the following expenses from today:
1. $45 for Office Supplies - "Notebooks and pens"
2. $120 for Software Subscriptions - "Adobe Creative Cloud monthly"
3. $85 for Utilities - "Internet service"
```

### Example 3: Invoice and Payment Flow

```
1. Create an invoice for Global Industries for $5000 for "Q1 Consulting Services"
2. [Wait for invoice ID, e.g., 123]
3. Record a payment of $5000 for invoice 123 via bank transfer
```

## Integration with CEO Briefing

All Odoo transactions are automatically included in the weekly CEO Briefing:
- Revenue summary (invoices and payments)
- Expense analysis by category
- Top customers by revenue
- Cash flow trends

## Audit Trail

Every Odoo transaction is logged with:
- Timestamp
- Transaction type (invoice/payment/expense)
- Amount and currency
- Customer/vendor name
- Approval status
- Result (success/failure)
- Error details (if failed)

View audit logs: `AI_Employee_Vault/Audit_Logs/YYYY-MM-DD.json`

## Configuration

### Environment Variables (.env)

```bash
# Odoo Connection
ODOO_URL=http://localhost:8069
ODOO_DATABASE=gold_tier_accounting
ODOO_USERNAME=ai_employee
ODOO_PASSWORD=your_password_here

# MCP Server
ODOO_MCP_PORT=3100
MCP_API_KEY=your_api_key_here
```

### Odoo Configuration (config/odoo_config.json)

```json
{
  "odoo_url": "http://localhost:8069",
  "database": "gold_tier_accounting",
  "username": "ai_employee",
  "connection_timeout": 30,
  "retry_attempts": 3,
  "accounting_module": {
    "chart_of_accounts": "US GAAP",
    "default_currency": "USD"
  }
}
```

## Troubleshooting

### "Odoo service unavailable"
- Check Odoo is running: `http://localhost:8069`
- Verify credentials in `.env`
- Check MCP server is running: `http://localhost:3100/health`
- Transaction will be queued for automatic retry

### "Invalid credentials"
- Verify ODOO_USERNAME and ODOO_PASSWORD in `.env`
- Check user has Accounting/Manager permissions in Odoo
- Test connection: `python -c "from services.odoo_service import OdooService; OdooService().connect()"`

### "Customer not found"
- Customer will be created automatically on first invoice
- Ensure customer name is spelled consistently
- Check Odoo Partners list: Settings → Contacts

### "Transaction queued for retry"
- Normal behavior when Odoo is temporarily unavailable
- Check queue status: `AI_Employee_Vault/Queue/`
- Queue processes every 5 minutes automatically
- Manual retry: Run queue processor

## API Reference

### Odoo MCP Server Endpoints

**Base URL:** `http://localhost:3100`

**Authentication:** X-API-Key header

#### POST /invoices
Create a new invoice

**Request:**
```json
{
  "customer_name": "Acme Corp",
  "amount": 2500.00,
  "description": "Website Development",
  "invoice_date": "2026-02-05",
  "due_date": "2026-03-07"
}
```

**Response:**
```json
{
  "odoo_record_id": 42,
  "customer_name": "Acme Corp",
  "amount": 2500.00,
  "status": "draft",
  "created_at": "2026-02-05T10:30:00Z"
}
```

#### POST /payments
Record a payment

**Request:**
```json
{
  "invoice_id": 42,
  "amount": 2500.00,
  "payment_date": "2026-02-10",
  "payment_method": "bank_transfer"
}
```

#### POST /expenses
Record an expense

**Request:**
```json
{
  "amount": 150.00,
  "expense_date": "2026-02-05",
  "category": "Office Supplies",
  "description": "Printer paper and toner",
  "vendor_name": "Office Depot"
}
```

#### GET /transactions/summary
Get transaction summary for date range

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

**Response:**
```json
{
  "start_date": "2026-02-01",
  "end_date": "2026-02-28",
  "revenue": {
    "total": 15000.00,
    "invoice_count": 6,
    "average_invoice_value": 2500.00
  },
  "expenses": {
    "total": 3500.00,
    "expense_count": 12,
    "by_category": [
      {"category": "Office Supplies", "amount": 450.00},
      {"category": "Software Subscriptions", "amount": 1200.00}
    ]
  },
  "net_income": 11500.00
}
```

## Best Practices

1. **Consistent Naming:** Use consistent customer/vendor names for accurate reporting
2. **Detailed Descriptions:** Include clear descriptions for better tracking
3. **Timely Recording:** Record transactions promptly for accurate cash flow
4. **Category Consistency:** Use standard expense categories from Business_Goals.md
5. **Regular Review:** Check CEO Briefing weekly for financial insights

## Related Skills

- `/generate-ceo-briefing` - Generate weekly business intelligence report
- `/process-with-loop` - Process multiple transactions autonomously

## Support

For issues or questions:
- Check audit logs: `AI_Employee_Vault/Audit_Logs/`
- Check queue status: `AI_Employee_Vault/Queue/`
- Review Odoo logs: Odoo → Settings → Technical → Logging
- Test MCP server: `curl http://localhost:3100/health`
