"""Financial calculation engine for invoices, taxes, and payments.

Handles monetary calculations for the accounting system.
CRITICAL: All amounts are in dollars and cents.
"""


class InvoiceCalculator:
    """Calculates invoice totals, taxes, and payment schedules."""

    def __init__(self, tax_rate=0.08):
        self.tax_rate = tax_rate  # 8% default

    def line_item_total(self, quantity, unit_price):
        """Calculate total for a line item.

        BUG: Uses float arithmetic which causes precision errors.
        """
        return quantity * unit_price

    def apply_discount(self, amount, discount_percent):
        """Apply a percentage discount to an amount."""
        return amount * (1 - discount_percent / 100)

    def calculate_tax(self, subtotal):
        """Calculate tax on a subtotal."""
        return subtotal * self.tax_rate

    def invoice_total(self, line_items, discount_percent=0):
        """Calculate the full invoice total from line items.

        Each line item is a dict with 'quantity' and 'unit_price'.
        BUG: Accumulates floating point errors across multiple items.
        """
        subtotal = 0.0
        for item in line_items:
            subtotal += self.line_item_total(
                item["quantity"], item["unit_price"])
        if discount_percent:
            subtotal = self.apply_discount(subtotal, discount_percent)
        tax = self.calculate_tax(subtotal)
        return subtotal + tax

    def split_payment(self, total, num_installments):
        """Split a total into equal installments.

        BUG: Float division may leave an unaccounted remainder.
        """
        installment = total / num_installments
        return [round(installment, 2) for _ in range(num_installments)]


class PaymentLedger:
    """Tracks payments against invoices, ensuring balances are correct."""

    def __init__(self):
        self._entries = []  # list of (amount, description) tuples

    def record_payment(self, amount, description=""):
        """Record a payment."""
        self._entries.append((amount, description))

    def balance(self):
        """Calculate current balance.

        BUG: Float accumulation causes precision drift over many entries.
        """
        return sum(amount for amount, _ in self._entries)

    def is_balanced(self, tolerance=0.01):
        """Check if the ledger balances within tolerance.

        BUG: Uses float tolerance which is unreliable for exact cents.
        """
        return abs(self.balance()) < tolerance