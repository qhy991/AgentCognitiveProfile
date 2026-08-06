"""Hidden tests for t11_orm_filter_chain — ORM query filter chaining.

Each test uses a fresh in-memory database with a known set of records.
The bug is that chained .filter() calls overwrite instead of combining.
"""
import os
import sys

# Import from the same directory (works when grade.py copies both
# workspace files and test files into the same temp dir)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models import Model
from fields import IntegerField, StringField, FloatField, BooleanField
from db import Database
from query import Query


class User(Model):
    id = IntegerField()
    name = StringField()
    age = IntegerField()
    active = BooleanField(default=True)


class Product(Model):
    id = IntegerField()
    name = StringField()
    price = FloatField()
    category = StringField()


def _setup_users():
    db = Database()
    db.insert_many([
        User(id=1, name="Alice", age=30, active=True),
        User(id=2, name="Bob", age=25, active=True),
        User(id=3, name="Charlie", age=30, active=False),
        User(id=4, name="Diana", age=35, active=True),
        User(id=5, name="Eve", age=25, active=False),
    ])
    return db


def _setup_products():
    db = Database()
    db.insert_many([
        Product(id=1, name="Laptop", price=1200.0, category="electronics"),
        Product(id=2, name="Desk", price=350.0, category="furniture"),
        Product(id=3, name="Mouse", price=25.0, category="electronics"),
        Product(id=4, name="Chair", price=450.0, category="furniture"),
        Product(id=5, name="Keyboard", price=80.0, category="electronics"),
    ])
    return db


def test_chained_eq_filters():
    """Two chained exact-match filters should both apply (AND)."""
    db = _setup_users()
    results = db.query(User).filter(age=30).filter(active=True).all()
    # Should return only Alice (age=30 AND active=True), not Charlie (active=False)
    assert len(results) == 1, f"expected 1, got {len(results)}: {results}"
    assert results[0].name == "Alice"


def test_chained_operator_filters():
    """Chained range filters should both apply."""
    db = _setup_users()
    results = db.query(User).filter(age__gte=25).filter(age__lte=30).all()
    names = {r.name for r in results}
    # age >= 25 AND age <= 30 → Alice, Bob, Charlie, Eve
    assert len(results) == 4, f"expected 4, got {len(results)}: {results}"
    assert names == {"Alice", "Bob", "Charlie", "Eve"}


def test_three_chained_filters():
    """Three chained filters should all apply."""
    db = _setup_users()
    results = (db.query(User)
               .filter(age__gte=25)
               .filter(age__lte=35)
               .filter(active=True)
               .all())
    names = {r.name for r in results}
    assert names == {"Alice", "Bob", "Diana"}, f"got {names}"


def test_filter_on_different_fields():
    """Filters on different fields should both apply."""
    db = _setup_products()
    results = (db.query(Product)
               .filter(category="electronics")
               .filter(price__lt=100)
               .all())
    names = {r.name for r in results}
    assert names == {"Mouse", "Keyboard"}, f"got {names}"


def test_filter_chain_with_count():
    """Count should respect chained filters."""
    db = _setup_users()
    # All users
    assert db.query(User).count() == 5
    # Filtered
    n = db.query(User).filter(active=True).filter(age__gte=30).count()
    assert n == 2, f"expected 2 active users aged >= 30, got {n}"