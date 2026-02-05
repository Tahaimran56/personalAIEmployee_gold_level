"""
Odoo Service for Gold Tier AI Employee

This service manages integration with Odoo Community Edition v19+ accounting system.
It implements:
- Connection management with odoo-rpc-client
- Invoice creation and management
- Payment recording
- Expense tracking
- Transaction retrieval
- Error handling with queue integration
- Comprehensive audit logging

Author: AI Employee Gold Tier
Created: 2026-02-05
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

try:
    from odoorpc import ODOO
except ImportError:
    ODOO = None
    logging.warning("odoo-rpc-client not installed. Install with: pip install odoo-rpc-client")

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import AuditService for logging
try:
    from services.audit_service import AuditService
    audit_service = AuditService()
except ImportError:
    audit_service = None
    logger.warning("AuditService not available")


class OdooService:
    """
    Manages Odoo accounting integration for the AI Employee.

    This service provides methods to:
    - Connect to Odoo via JSON-RPC
    - Create invoices, record payments, track expenses
    - Retrieve transaction data for CEO Briefing
    - Handle errors gracefully with queue integration
    """

    def __init__(self, config_path: str = "config/odoo_config.json"):
        """
        Initialize the OdooService.

        Args:
            config_path: Path to Odoo configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.odoo = None
        self.connected = False

        # Get credentials from environment
        self.url = os.getenv("ODOO_URL", self.config.get("odoo_url", "http://localhost:8069"))
        self.database = os.getenv("ODOO_DATABASE", self.config.get("database", "gold_tier_accounting"))
        self.username = os.getenv("ODOO_USERNAME", self.config.get("username", "ai_employee"))
        self.password = os.getenv("ODOO_PASSWORD")

        if not self.password:
            logger.warning("ODOO_PASSWORD not set in environment variables")

        logger.info(f"OdooService initialized for {self.url}/{self.database}")

    def _load_config(self) -> Dict[str, Any]:
        """Load Odoo configuration from JSON file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            return {}

        with open(self.config_path, 'r') as f:
            return json.load(f)

    def connect(self) -> bool:
        """
        Initialize connection to Odoo server.

        Returns:
            bool: True if connection successful, False otherwise
        """
        if ODOO is None:
            logger.error("odoo-rpc-client not installed")
            return False

        if not self.password:
            logger.error("ODOO_PASSWORD not set")
            return False

        try:
            # Parse URL to get host and port
            url_parts = self.url.replace("http://", "").replace("https://", "").split(":")
            host = url_parts[0]
            port = int(url_parts[1]) if len(url_parts) > 1 else 8069

            # Create ODOO instance
            self.odoo = ODOO(host, port=port)

            # Login
            self.odoo.login(self.database, self.username, self.password)

            self.connected = True
            logger.info(f"Connected to Odoo {self.odoo.version} at {self.url}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Odoo: {e}")
            self.connected = False
            return False

    def _ensure_connected(self) -> bool:
        """Ensure connection is active, reconnect if needed."""
        if not self.connected:
            return self.connect()
        return True

    def create_invoice(
        self,
        customer_name: str,
        amount: float,
        description: str,
        invoice_date: Optional[str] = None,
        due_date: Optional[str] = None,
        line_items: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[int]:
        """
        Create an invoice in Odoo.

        Args:
            customer_name: Customer name
            amount: Invoice amount
            description: Invoice description
            invoice_date: Invoice date (ISO format, default: today)
            due_date: Due date (ISO format, default: 30 days from invoice date)
            line_items: List of line items with product, quantity, unit_price

        Returns:
            int: Odoo invoice ID or None if failed
        """
        if not self._ensure_connected():
            logger.error("Cannot create invoice: not connected to Odoo")
            return None

        try:
            # Get or create customer (partner)
            Partner = self.odoo.env['res.partner']
            partner_ids = Partner.search([('name', '=', customer_name)])

            if not partner_ids:
                # Create new partner
                partner_id = Partner.create({
                    'name': customer_name,
                    'customer_rank': 1
                })
                logger.info(f"Created new customer: {customer_name} (ID: {partner_id})")
            else:
                partner_id = partner_ids[0]

            # Prepare invoice data
            invoice_date = invoice_date or datetime.now().strftime("%Y-%m-%d")

            invoice_data = {
                'partner_id': partner_id,
                'move_type': 'out_invoice',  # Customer invoice
                'invoice_date': invoice_date,
                'narration': description
            }

            # Add due date if provided
            if due_date:
                invoice_data['invoice_date_due'] = due_date

            # Create invoice
            Invoice = self.odoo.env['account.move']
            invoice_id = Invoice.create(invoice_data)

            # Add line items
            if line_items:
                InvoiceLine = self.odoo.env['account.move.line']
                for item in line_items:
                    line_data = {
                        'move_id': invoice_id,
                        'name': item.get('description', description),
                        'quantity': item.get('quantity', 1),
                        'price_unit': item.get('unit_price', amount)
                    }
                    InvoiceLine.create(line_data)
            else:
                # Create single line item
                InvoiceLine = self.odoo.env['account.move.line']
                InvoiceLine.create({
                    'move_id': invoice_id,
                    'name': description,
                    'quantity': 1,
                    'price_unit': amount
                })

            logger.info(f"Created invoice {invoice_id} for {customer_name}: ${amount}")

            # Audit log
            if audit_service:
                audit_service.log_action(
                    action_type="odoo_transaction",
                    actor="ai_employee",
                    target="odoo",
                    parameters={
                        "operation": "create_invoice",
                        "customer_name": customer_name,
                        "amount": amount,
                        "description": description
                    },
                    result="success",
                    approval_status="not_required"
                )

            return invoice_id

        except Exception as e:
            logger.error(f"Failed to create invoice: {e}")

            # Audit log failure
            if audit_service:
                audit_service.log_action(
                    action_type="odoo_transaction",
                    actor="ai_employee",
                    target="odoo",
                    parameters={
                        "operation": "create_invoice",
                        "customer_name": customer_name,
                        "amount": amount
                    },
                    result="failure",
                    error_message=str(e),
                    approval_status="not_required"
                )

            return None

    def record_payment(
        self,
        invoice_id: int,
        amount: float,
        payment_date: Optional[str] = None,
        payment_method: str = "bank_transfer",
        reference: Optional[str] = None
    ) -> Optional[int]:
        """
        Record a payment for an invoice.

        Args:
            invoice_id: Odoo invoice ID
            amount: Payment amount
            payment_date: Payment date (ISO format, default: today)
            payment_method: Payment method (cash, check, bank_transfer, credit_card, paypal, other)
            reference: Payment reference number

        Returns:
            int: Odoo payment ID or None if failed
        """
        if not self._ensure_connected():
            logger.error("Cannot record payment: not connected to Odoo")
            return None

        try:
            payment_date = payment_date or datetime.now().strftime("%Y-%m-%d")

            # Get invoice
            Invoice = self.odoo.env['account.move']
            invoice = Invoice.browse(invoice_id)

            # Create payment
            Payment = self.odoo.env['account.payment']
            payment_data = {
                'payment_type': 'inbound',
                'partner_id': invoice.partner_id.id,
                'amount': amount,
                'date': payment_date,
                'ref': reference or f"Payment for Invoice {invoice_id}"
            }

            payment_id = Payment.create(payment_data)

            # Post payment
            payment = Payment.browse(payment_id)
            payment.action_post()

            # Reconcile with invoice
            # Note: Reconciliation logic may vary based on Odoo version
            # This is a simplified version

            logger.info(f"Recorded payment {payment_id} for invoice {invoice_id}: ${amount}")

            # Audit log
            if audit_service:
                audit_service.log_action(
                    action_type="odoo_transaction",
                    actor="ai_employee",
                    target="odoo",
                    parameters={
                        "operation": "record_payment",
                        "invoice_id": invoice_id,
                        "amount": amount,
                        "payment_method": payment_method
                    },
                    result="success",
                    approval_status="not_required"
                )

            return payment_id

        except Exception as e:
            logger.error(f"Failed to record payment: {e}")

            # Audit log failure
            if audit_service:
                audit_service.log_action(
                    action_type="odoo_transaction",
                    actor="ai_employee",
                    target="odoo",
                    parameters={
                        "operation": "record_payment",
                        "invoice_id": invoice_id,
                        "amount": amount
                    },
                    result="failure",
                    error_message=str(e),
                    approval_status="not_required"
                )

            return None

    def record_expense(
        self,
        amount: float,
        expense_date: str,
        category: str,
        description: str,
        vendor_name: Optional[str] = None,
        accounting_code: Optional[str] = None
    ) -> Optional[int]:
        """
        Record a business expense in Odoo.

        Args:
            amount: Expense amount
            expense_date: Expense date (ISO format)
            category: Expense category
            description: Expense description
            vendor_name: Vendor name (optional)
            accounting_code: Chart of accounts code (optional)

        Returns:
            int: Odoo expense ID or None if failed
        """
        if not self._ensure_connected():
            logger.error("Cannot record expense: not connected to Odoo")
            return None

        try:
            # Get or create vendor if provided
            partner_id = None
            if vendor_name:
                Partner = self.odoo.env['res.partner']
                partner_ids = Partner.search([('name', '=', vendor_name)])

                if not partner_ids:
                    partner_id = Partner.create({
                        'name': vendor_name,
                        'supplier_rank': 1
                    })
                else:
                    partner_id = partner_ids[0]

            # Create expense (vendor bill)
            Invoice = self.odoo.env['account.move']
            expense_data = {
                'move_type': 'in_invoice',  # Vendor bill
                'invoice_date': expense_date,
                'narration': f"{category}: {description}"
            }

            if partner_id:
                expense_data['partner_id'] = partner_id

            expense_id = Invoice.create(expense_data)

            # Add expense line
            InvoiceLine = self.odoo.env['account.move.line']
            line_data = {
                'move_id': expense_id,
                'name': description,
                'quantity': 1,
                'price_unit': amount
            }

            InvoiceLine.create(line_data)

            logger.info(f"Recorded expense {expense_id}: {category} - ${amount}")

            # Audit log
            if audit_service:
                audit_service.log_action(
                    action_type="odoo_transaction",
                    actor="ai_employee",
                    target="odoo",
                    parameters={
                        "operation": "record_expense",
                        "amount": amount,
                        "category": category,
                        "description": description,
                        "vendor_name": vendor_name
                    },
                    result="success",
                    approval_status="not_required"
                )

            return expense_id

        except Exception as e:
            logger.error(f"Failed to record expense: {e}")

            # Audit log failure
            if audit_service:
                audit_service.log_action(
                    action_type="odoo_transaction",
                    actor="ai_employee",
                    target="odoo",
                    parameters={
                        "operation": "record_expense",
                        "amount": amount,
                        "category": category
                    },
                    result="failure",
                    error_message=str(e),
                    approval_status="not_required"
                )

            return None

    def get_transactions(
        self,
        start_date: str,
        end_date: str,
        transaction_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve transactions from Odoo for a date range.

        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            transaction_type: Filter by type (invoice, payment, expense) or None for all

        Returns:
            list: List of transaction dictionaries
        """
        if not self._ensure_connected():
            logger.error("Cannot get transactions: not connected to Odoo")
            return []

        try:
            transactions = []

            # Get invoices
            if transaction_type is None or transaction_type == "invoice":
                Invoice = self.odoo.env['account.move']
                invoice_ids = Invoice.search([
                    ('move_type', '=', 'out_invoice'),
                    ('invoice_date', '>=', start_date),
                    ('invoice_date', '<=', end_date)
                ])

                for invoice_id in invoice_ids:
                    invoice = Invoice.browse(invoice_id)
                    transactions.append({
                        'transaction_id': str(invoice_id),
                        'odoo_record_id': invoice_id,
                        'transaction_type': 'invoice',
                        'amount': float(invoice.amount_total),
                        'currency': invoice.currency_id.name,
                        'transaction_date': invoice.invoice_date,
                        'customer_vendor_name': invoice.partner_id.name,
                        'description': invoice.narration or invoice.name,
                        'status': invoice.state
                    })

            # Get expenses (vendor bills)
            if transaction_type is None or transaction_type == "expense":
                Invoice = self.odoo.env['account.move']
                expense_ids = Invoice.search([
                    ('move_type', '=', 'in_invoice'),
                    ('invoice_date', '>=', start_date),
                    ('invoice_date', '<=', end_date)
                ])

                for expense_id in expense_ids:
                    expense = Invoice.browse(expense_id)
                    transactions.append({
                        'transaction_id': str(expense_id),
                        'odoo_record_id': expense_id,
                        'transaction_type': 'expense',
                        'amount': float(expense.amount_total),
                        'currency': expense.currency_id.name,
                        'transaction_date': expense.invoice_date,
                        'customer_vendor_name': expense.partner_id.name if expense.partner_id else None,
                        'description': expense.narration or expense.name,
                        'status': expense.state
                    })

            logger.info(f"Retrieved {len(transactions)} transactions from {start_date} to {end_date}")
            return transactions

        except Exception as e:
            logger.error(f"Failed to get transactions: {e}")
            return []

    def handle_odoo_error(self, error: Exception, operation: str, parameters: Dict[str, Any]) -> None:
        """
        Handle Odoo errors by queuing operations for retry.

        Args:
            error: The exception that occurred
            operation: Operation that failed (create_invoice, record_payment, record_expense)
            parameters: Operation parameters for retry
        """
        logger.error(f"Odoo error in {operation}: {error}")

        # Import QueueService here to avoid circular imports
        try:
            from services.queue_service import QueueService
            queue_service = QueueService()

            # Queue the operation for retry
            operation_id = queue_service.create_operation(
                operation_type="odoo_transaction",
                target="odoo",
                parameters={
                    "operation": operation,
                    **parameters
                }
            )

            logger.info(f"Queued Odoo operation for retry: {operation_id}")

        except Exception as queue_error:
            logger.error(f"Failed to queue Odoo operation: {queue_error}")


# Example usage
if __name__ == "__main__":
    # Initialize service
    odoo_service = OdooService()

    # Connect to Odoo
    if odoo_service.connect():
        print("✓ Connected to Odoo")

        # Create test invoice
        invoice_id = odoo_service.create_invoice(
            customer_name="Test Customer",
            amount=1500.00,
            description="Test Invoice for Gold Tier Setup"
        )

        if invoice_id:
            print(f"✓ Created invoice: {invoice_id}")

            # Record payment
            payment_id = odoo_service.record_payment(
                invoice_id=invoice_id,
                amount=1500.00
            )

            if payment_id:
                print(f"✓ Recorded payment: {payment_id}")

        # Record expense
        expense_id = odoo_service.record_expense(
            amount=250.00,
            expense_date=datetime.now().strftime("%Y-%m-%d"),
            category="Office Supplies",
            description="Test expense for Gold Tier Setup"
        )

        if expense_id:
            print(f"✓ Recorded expense: {expense_id}")

        # Get transactions
        transactions = odoo_service.get_transactions(
            start_date="2026-02-01",
            end_date="2026-02-28"
        )

        print(f"✓ Retrieved {len(transactions)} transactions")

    else:
        print("✗ Failed to connect to Odoo")
