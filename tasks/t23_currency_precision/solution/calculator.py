"""Financial calculation engine for invoices, taxes, and payments.

Handles monetary calculations for the accounting system.
CRITICAL: All amounts are in dollars and cents. Uses Decimal for
exact monetary arithmetic to avoid floating point precision errors.
"""

from decimal import Decimal, ROUND_HALF_UP


def _D(amount):
    """Convert a number to Decimal with 2 decimal places."""
    if isinstance(amount, Decimal):
        return amount
    return Decimal(str(amount))


class InvoiceCalculator:
    """Calculates invoice totals, taxes, and payment schedules."""

    def __init__(self, tax_rate=0.08):
        self.tax_rate = _D(tax_rate)

    def line_item_total(self, quantity, unit_price):
        """Calculate total for a line item using Decimal arithmetic."""
        return _D(quantity) * _D(unit_price)

    def apply_discount(self, amount, discount_percent):
        """Apply a percentage discount to an amount."""
        amount = _D(amount)
        return amount * (1 - _D(discount_percent) / 100)

    def calculate_tax(self, subtotal):
        """Calculate tax on a subtotal."""
        return _D(subtotal) * self.tax_rate

    def invoice_total(self, line_items, discount_percent=0):
        """Calculate the full invoice total from line items."""
        subtotal = Decimal("0")
        for item in line_items:
            subtotal += self.line_item_total(
                item["quantity"], item["unit_price"])
        if discount_percent:
            subtotal = self.apply_discount(subtotal, discount_percent)
        tax = self.calculate_tax(subtotal)
        total = subtotal + tax
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def split_payment(self, total, num_installments):
        """Split a total into equal installments."""
        total = _D(total)
        installment = total / _D(num_installments)
        # Round each installment to 2 decimal places
        rounded = installment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        installments = [rounded for _ in range(num_installments)]
        # Adjust last installment to account for rounding
        total_rounded = rounded * num_installments
        diff = total - total_rounded
        if diff != 0:
            installments[-1] = (rounded + diff).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP)
        return installments


class PaymentLedger:
    """Tracks payments against invoices, ensuring balances are correct."""

    def __init__(self):
        self._entries = []

    def record_payment(self, amount, description=""):
        """Record a payment using Decimal."""
        self._entries.append((_D(amount), description))

    def balance(self):
        """Calculate current balance using Decimal."""
        return sum((amount for amount, _ in self._entries), Decimal("0"))

    def is_balanced(self, tolerance=0.005):
        """Check if the ledger balances within tolerance."""
        return abs(self.balance()) < _D(tolerance)