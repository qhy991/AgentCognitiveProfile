"""Query builder — supports filtering, ordering, and slicing."""


class Query:
    """A query object that builds up filters and executes them lazily.

    Example:
        db.query(User).filter(age=30).filter(name="Alice").all()
        db.query(User).filter(age__gt=20).order_by("name").first()
        db.query(User).filter(age__gte=18).filter(age__lte=65).count()
    """

    def __init__(self, database, model_class):
        self._db = database
        self._model = model_class
        self._filters = {}
        self._ordering = None

    def _clone(self):
        """Return a shallow copy of this query."""
        q = Query(self._db, self._model)
        q._filters = dict(self._filters)
        q._ordering = self._ordering
        return q

    def filter(self, **kwargs):
        """Add filter conditions. Multiple calls should be combined with AND.

        Supported operators (via __suffix):
            age__gt=18   → greater than
            age__gte=18  → greater than or equal
            age__lt=65   → less than
            age__lte=65  → less than or equal
            name__ne="X" → not equal
            name__in=["A","B"] → in list
            Exact match is the default.
        """
        self._filters = dict(kwargs)  # BUG: should merge, not replace
        return self

    def order_by(self, field_name):
        """Set the ordering field (ascending)."""
        self._ordering = field_name
        return self

    def _matches(self, row):
        """Check if a row matches all current filters."""
        for key, value in self._filters.items():
            if "__" in key:
                field_name, op = key.rsplit("__", 1)
            else:
                field_name, op = key, "eq"
            row_value = row.get(field_name)
            if not self._compare(row_value, op, value):
                return False
        return True

    def _compare(self, row_value, op, filter_value):
        """Compare a row value against a filter value using the given operator."""
        try:
            if op == "eq":
                return row_value == filter_value
            elif op == "ne":
                return row_value != filter_value
            elif op == "gt":
                return row_value is not None and row_value > filter_value
            elif op == "gte":
                return row_value is not None and row_value >= filter_value
            elif op == "lt":
                return row_value is not None and row_value < filter_value
            elif op == "lte":
                return row_value is not None and row_value <= filter_value
            elif op == "in":
                return row_value in filter_value
            return True
        except TypeError:
            return False

    def all(self):
        """Return all matching rows as model instances."""
        rows = self._db.get_table(self._model._tablename)
        result = [self._model(**r) for r in rows if self._matches(r)]
        if self._ordering:
            result.sort(key=lambda inst: getattr(inst, self._ordering))
        return result

    def first(self):
        """Return the first matching row, or None."""
        results = self.all()
        return results[0] if results else None

    def count(self):
        """Return the number of matching rows."""
        return len(self.all())

    def __iter__(self):
        return iter(self.all())

    def __repr__(self):
        return (f"<Query model={self._model.__name__} "
                f"filters={self._filters} ordering={self._ordering}>")