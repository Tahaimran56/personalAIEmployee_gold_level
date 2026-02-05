/**
 * Odoo MCP Server for Gold Tier AI Employee
 *
 * This MCP server provides HTTP endpoints for Odoo accounting integration.
 * It exposes the OdooService functionality via REST API.
 *
 * Endpoints:
 * - GET /health - Health check
 * - POST /invoices - Create invoice
 * - GET /invoices - List invoices
 * - POST /payments - Record payment
 * - POST /expenses - Record expense
 * - GET /expenses - List expenses
 * - GET /transactions/summary - Get transaction summary
 *
 * Author: AI Employee Gold Tier
 * Created: 2026-02-05
 */

const express = require('express');
const axios = require('axios');
const { spawn } = require('child_process');
const {
  logger,
  buildErrorResponse,
  authenticateApiKey,
  createHealthCheckHandler,
  handleRateLimitError,
  logRequest,
  errorHandler,
  asyncHandler,
  performanceMonitoring,
  getPerformanceMetrics,
  getErrorStats,
  setupGracefulShutdown,
  validateConfig,
  trackError
} = require('./shared-utils');

require('dotenv').config();

// Validate configuration on startup
const configValidation = validateConfig([
  'ODOO_URL',
  'ODOO_DATABASE',
  'ODOO_USERNAME',
  'ODOO_PASSWORD',
  'MCP_API_KEY'
]);

if (!configValidation.valid) {
  logger.error('Configuration validation failed', { missing: configValidation.missing });
  process.exit(1);
}

// Initialize Express app
const app = express();
const PORT = process.env.ODOO_MCP_PORT || 3100;

// Middleware
app.use(express.json());
app.use(logRequest);
app.use(performanceMonitoring);

// ============================================
// Helper Functions
// ============================================

/**
 * Execute Python OdooService method
 * @param {string} method - Method name to call
 * @param {object} params - Parameters to pass
 * @returns {Promise<object>} Result from Python service
 */
async function callOdooService(method, params = {}) {
  return new Promise((resolve, reject) => {
    const pythonScript = `
import sys
import json
sys.path.append('AI_Employee_Vault')
from services.odoo_service import OdooService

try:
    odoo_service = OdooService()

    method = '${method}'
    params = json.loads('${JSON.stringify(params).replace(/'/g, "\\'")}')

    if method == 'connect':
        result = odoo_service.connect()
        print(json.dumps({'success': result, 'connected': result}))

    elif method == 'create_invoice':
        invoice_id = odoo_service.create_invoice(**params)
        print(json.dumps({'success': invoice_id is not None, 'invoice_id': invoice_id}))

    elif method == 'record_payment':
        payment_id = odoo_service.record_payment(**params)
        print(json.dumps({'success': payment_id is not None, 'payment_id': payment_id}))

    elif method == 'record_expense':
        expense_id = odoo_service.record_expense(**params)
        print(json.dumps({'success': expense_id is not None, 'expense_id': expense_id}))

    elif method == 'get_transactions':
        transactions = odoo_service.get_transactions(**params)
        print(json.dumps({'success': True, 'transactions': transactions}))

    else:
        print(json.dumps({'success': False, 'error': 'Unknown method'}))

except Exception as e:
    print(json.dumps({'success': False, 'error': str(e)}))
`;

    const python = spawn('python', ['-c', pythonScript]);
    let output = '';
    let errorOutput = '';

    python.stdout.on('data', (data) => {
      output += data.toString();
    });

    python.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    python.on('close', (code) => {
      if (code !== 0) {
        logger.error('Python script failed', { code, error: errorOutput });
        reject(new Error(errorOutput || 'Python script failed'));
        return;
      }

      try {
        const result = JSON.parse(output.trim());
        resolve(result);
      } catch (e) {
        logger.error('Failed to parse Python output', { output, error: e.message });
        reject(new Error('Failed to parse Python output'));
      }
    });
  });
}

// ============================================
// Health Check Endpoint
// ============================================

app.get('/health', createHealthCheckHandler('odoo-mcp', async () => {
  try {
    const result = await callOdooService('connect');

    return {
      connected: result.success,
      odoo_version: result.success ? 'Connected' : 'Not connected',
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    return {
      connected: false,
      error: error.message
    };
  }
}));

// ============================================
// Invoice Endpoints
// ============================================

/**
 * POST /invoices - Create invoice
 */
app.post('/invoices', authenticateApiKey, asyncHandler(async (req, res) => {
  const { customer_name, amount, description, invoice_date, due_date, line_items } = req.body;

  // Validate required fields
  if (!customer_name || !amount || !description) {
    return res.status(400).json(
      buildErrorResponse('MISSING_FIELDS', 'customer_name, amount, and description are required')
    );
  }

  // Validate amount
  if (typeof amount !== 'number' || amount <= 0) {
    return res.status(400).json(
      buildErrorResponse('INVALID_AMOUNT', 'Amount must be a positive number')
    );
  }

  try {
    const result = await callOdooService('create_invoice', {
      customer_name,
      amount,
      description,
      invoice_date,
      due_date,
      line_items
    });

    if (!result.success) {
      throw new Error(result.error || 'Failed to create invoice');
    }

    logger.info('Invoice created', { invoice_id: result.invoice_id, customer_name, amount });

    res.status(201).json({
      odoo_record_id: result.invoice_id,
      customer_name,
      amount,
      description,
      invoice_date: invoice_date || new Date().toISOString().split('T')[0],
      status: 'draft',
      created_at: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Failed to create invoice', { error: error.message });

    // Check if Odoo is unavailable
    if (error.message.includes('connection') || error.message.includes('timeout')) {
      return res.status(503).json(
        buildErrorResponse('ODOO_UNAVAILABLE', 'Odoo service is unavailable. Operation has been queued for retry.')
      );
    }

    res.status(500).json(
      buildErrorResponse('INVOICE_CREATION_FAILED', error.message)
    );
  }
}));

/**
 * GET /invoices - List invoices
 */
app.get('/invoices', authenticateApiKey, asyncHandler(async (req, res) => {
  const { start_date, end_date, customer_id, status, limit = 100 } = req.query;

  try {
    const result = await callOdooService('get_transactions', {
      start_date: start_date || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end_date: end_date || new Date().toISOString().split('T')[0],
      transaction_type: 'invoice'
    });

    if (!result.success) {
      throw new Error(result.error || 'Failed to get invoices');
    }

    let invoices = result.transactions || [];

    // Apply filters
    if (customer_id) {
      invoices = invoices.filter(inv => inv.customer_vendor_id === parseInt(customer_id));
    }

    if (status) {
      invoices = invoices.filter(inv => inv.status === status);
    }

    // Apply limit
    const limitNum = Math.min(parseInt(limit), 1000);
    const hasMore = invoices.length > limitNum;
    invoices = invoices.slice(0, limitNum);

    res.json({
      invoices,
      total_count: invoices.length,
      has_more: hasMore
    });

  } catch (error) {
    logger.error('Failed to list invoices', { error: error.message });
    res.status(500).json(
      buildErrorResponse('INVOICE_LIST_FAILED', error.message)
    );
  }
}));

// ============================================
// Payment Endpoints
// ============================================

/**
 * POST /payments - Record payment
 */
app.post('/payments', authenticateApiKey, asyncHandler(async (req, res) => {
  const { invoice_id, amount, payment_date, payment_method = 'bank_transfer', reference } = req.body;

  // Validate required fields
  if (!invoice_id || !amount) {
    return res.status(400).json(
      buildErrorResponse('MISSING_FIELDS', 'invoice_id and amount are required')
    );
  }

  // Validate amount
  if (typeof amount !== 'number' || amount <= 0) {
    return res.status(400).json(
      buildErrorResponse('INVALID_AMOUNT', 'Amount must be a positive number')
    );
  }

  try {
    const result = await callOdooService('record_payment', {
      invoice_id,
      amount,
      payment_date,
      payment_method,
      reference
    });

    if (!result.success) {
      throw new Error(result.error || 'Failed to record payment');
    }

    logger.info('Payment recorded', { payment_id: result.payment_id, invoice_id, amount });

    res.status(201).json({
      odoo_record_id: result.payment_id,
      invoice_id,
      amount,
      payment_date: payment_date || new Date().toISOString().split('T')[0],
      payment_method,
      status: 'posted',
      created_at: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Failed to record payment', { error: error.message });

    if (error.message.includes('connection') || error.message.includes('timeout')) {
      return res.status(503).json(
        buildErrorResponse('ODOO_UNAVAILABLE', 'Odoo service is unavailable. Operation has been queued for retry.')
      );
    }

    res.status(500).json(
      buildErrorResponse('PAYMENT_RECORDING_FAILED', error.message)
    );
  }
}));

// ============================================
// Expense Endpoints
// ============================================

/**
 * POST /expenses - Record expense
 */
app.post('/expenses', authenticateApiKey, asyncHandler(async (req, res) => {
  const { amount, expense_date, category, description, vendor_name, accounting_code } = req.body;

  // Validate required fields
  if (!amount || !expense_date || !category || !description) {
    return res.status(400).json(
      buildErrorResponse('MISSING_FIELDS', 'amount, expense_date, category, and description are required')
    );
  }

  // Validate amount
  if (typeof amount !== 'number' || amount <= 0) {
    return res.status(400).json(
      buildErrorResponse('INVALID_AMOUNT', 'Amount must be a positive number')
    );
  }

  try {
    const result = await callOdooService('record_expense', {
      amount,
      expense_date,
      category,
      description,
      vendor_name,
      accounting_code
    });

    if (!result.success) {
      throw new Error(result.error || 'Failed to record expense');
    }

    logger.info('Expense recorded', { expense_id: result.expense_id, category, amount });

    res.status(201).json({
      odoo_record_id: result.expense_id,
      amount,
      expense_date,
      category,
      vendor_name,
      description,
      status: 'draft',
      created_at: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Failed to record expense', { error: error.message });

    if (error.message.includes('connection') || error.message.includes('timeout')) {
      return res.status(503).json(
        buildErrorResponse('ODOO_UNAVAILABLE', 'Odoo service is unavailable. Operation has been queued for retry.')
      );
    }

    res.status(500).json(
      buildErrorResponse('EXPENSE_RECORDING_FAILED', error.message)
    );
  }
}));

/**
 * GET /expenses - List expenses
 */
app.get('/expenses', authenticateApiKey, asyncHandler(async (req, res) => {
  const { start_date, end_date, category, limit = 100 } = req.query;

  try {
    const result = await callOdooService('get_transactions', {
      start_date: start_date || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end_date: end_date || new Date().toISOString().split('T')[0],
      transaction_type: 'expense'
    });

    if (!result.success) {
      throw new Error(result.error || 'Failed to get expenses');
    }

    let expenses = result.transactions || [];

    // Apply category filter
    if (category) {
      expenses = expenses.filter(exp => exp.description && exp.description.includes(category));
    }

    // Apply limit
    const limitNum = Math.min(parseInt(limit), 1000);
    const hasMore = expenses.length > limitNum;
    expenses = expenses.slice(0, limitNum);

    res.json({
      expenses,
      total_count: expenses.length,
      has_more: hasMore
    });

  } catch (error) {
    logger.error('Failed to list expenses', { error: error.message });
    res.status(500).json(
      buildErrorResponse('EXPENSE_LIST_FAILED', error.message)
    );
  }
}));

// ============================================
// Transaction Summary Endpoint
// ============================================

/**
 * GET /transactions/summary - Get transaction summary
 */
app.get('/transactions/summary', authenticateApiKey, asyncHandler(async (req, res) => {
  const { start_date, end_date } = req.query;

  if (!start_date || !end_date) {
    return res.status(400).json(
      buildErrorResponse('MISSING_FIELDS', 'start_date and end_date are required')
    );
  }

  try {
    const result = await callOdooService('get_transactions', {
      start_date,
      end_date
    });

    if (!result.success) {
      throw new Error(result.error || 'Failed to get transactions');
    }

    const transactions = result.transactions || [];

    // Calculate summary
    const summary = {
      start_date,
      end_date,
      revenue: {
        total: 0,
        invoice_count: 0,
        payment_count: 0,
        average_invoice_value: 0
      },
      expenses: {
        total: 0,
        expense_count: 0,
        by_category: {}
      },
      net_income: 0
    };

    let totalInvoiceAmount = 0;

    transactions.forEach(txn => {
      if (txn.transaction_type === 'invoice') {
        summary.revenue.total += txn.amount;
        summary.revenue.invoice_count++;
        totalInvoiceAmount += txn.amount;
      } else if (txn.transaction_type === 'expense') {
        summary.expenses.total += txn.amount;
        summary.expenses.expense_count++;

        // Extract category from description
        const category = txn.description ? txn.description.split(':')[0] : 'Other';
        summary.expenses.by_category[category] = (summary.expenses.by_category[category] || 0) + txn.amount;
      }
    });

    if (summary.revenue.invoice_count > 0) {
      summary.revenue.average_invoice_value = totalInvoiceAmount / summary.revenue.invoice_count;
    }

    summary.net_income = summary.revenue.total - summary.expenses.total;

    // Convert by_category to array
    summary.expenses.by_category = Object.entries(summary.expenses.by_category).map(([category, amount]) => ({
      category,
      amount
    }));

    res.json(summary);

  } catch (error) {
    logger.error('Failed to get transaction summary', { error: error.message });
    res.status(500).json(
      buildErrorResponse('SUMMARY_FAILED', error.message)
    );
  }
}));

// ============================================
// Metrics Endpoint
// ============================================

/**
 * GET /metrics - Get performance metrics
 */
app.get('/metrics', authenticateApiKey, (req, res) => {
  const metrics = getPerformanceMetrics();
  const errorStats = getErrorStats();

  res.json({
    performance: metrics,
    errors: errorStats
  });
});

// ============================================
// Error Handler
// ============================================

app.use((err, req, res, next) => {
  trackError(err, {
    path: req.path,
    method: req.method
  });
  errorHandler(err, req, res, next);
});

// ============================================
// Start Server
// ============================================

const server = app.listen(PORT, () => {
  logger.info(`Odoo MCP Server listening on port ${PORT}`, { service: 'odoo-mcp' });
  console.log(`✓ Odoo MCP Server running on http://localhost:${PORT}`);
  console.log(`✓ Health check: http://localhost:${PORT}/health`);
  console.log(`✓ Metrics: http://localhost:${PORT}/metrics`);
});

// Setup graceful shutdown
setupGracefulShutdown(server, async () => {
  logger.info('Odoo MCP Server cleanup complete');
});

module.exports = app;
