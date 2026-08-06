"""Invoice data model and validation."""


class Invoice:
    """Represents a customer invoice."""

    def __init__(self, customer_id, line_items, discount_percent=0):
        self.customer_id = customer_id
        self.line_items = line_items
        self.discount_percent = discount_percent

    def validate(self):
        """Validate invoice data."""
        if not self.line_items:
            return False, "No line items"
        for item in self.line_items:
            if "quantity" not in item or "unit_price" not in item:
                return False, f"Invalid line item: {item}"
            if item["quantity"] <= 0:
                return False, "Quantity must be positive"
            if item["unit_price"] < 0:
                return False, "Unit price cannot be negative"
        return True, ""


class TaxConfig:
    """Tax rate configuration by region."""

    DEFAULT_RATES = {
        "US": 0.08,
        "EU": 0.20,
        "JP": 0.10,
        "UK": 0.20,
    }

    @classmethod
    def get_rate(cls, region):
        return cls.DEFAULT_RATES.get(region, 0.0)