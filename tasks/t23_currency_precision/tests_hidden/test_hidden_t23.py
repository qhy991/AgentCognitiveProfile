"""Hidden tests for t23_currency_precision — floating point errors."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calculator import InvoiceCalculator, PaymentLedger


def test_invoice_total_simple():
    calc = InvoiceCalculator(tax_rate=0.08)
    items = [{"quantity": 2, "unit_price": 10.00}]
    total = float(calc.invoice_total(items))
    assert abs(total - 21.60) < 0.01, f"Expected 21.60, got {total}"


def test_invoice_total_multiple_items():
    calc = InvoiceCalculator(tax_rate=0.10)
    items = [{"quantity": 3, "unit_price": 0.33}, {"quantity": 5, "unit_price": 0.17}, {"quantity": 7, "unit_price": 0.11}]
    total = float(calc.invoice_total(items))
    assert abs(total - 2.87) < 0.01, f"Expected 2.87, got {total}"


def test_split_payment_exact():
    calc = InvoiceCalculator()
    installments = calc.split_payment(100.00, 3)
    assert len(installments) == 3
    assert abs(sum(float(x) for x in installments) - 100.00) < 0.01


def test_ledger_balance_exact():
    ledger = PaymentLedger()
    for _ in range(100):
        ledger.record_payment(0.33)
    assert abs(float(ledger.balance()) - 33.00) < 0.01


def test_discount_and_tax_exact():
    calc = InvoiceCalculator(tax_rate=0.075)
    items = [{"quantity": 1, "unit_price": 19.99}, {"quantity": 2, "unit_price": 5.49}]
    total = float(calc.invoice_total(items, discount_percent=10))
    assert abs(total - 29.96) < 0.01, f"Expected 29.96, got {total}"