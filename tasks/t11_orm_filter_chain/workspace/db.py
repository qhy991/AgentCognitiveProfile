"""In-memory database — stores all records in a dict of lists."""

class Database:
    """A simple in-memory database.

    Usage:
        db = Database()
        db.insert(User(id=1, name="Alice"))
        users = db.query(User).filter(age=30).all()
    """

    def __init__(self):
        self._tables = {}  # {tablename: [record1, record2, ...]}

    def insert(self, instance):
        """Insert a model instance into the database."""
        tablename = instance._tablename
        if tablename not in self._tables:
            self._tables[tablename] = []
        self._tables[tablename].append(instance.to_dict())

    def insert_many(self, instances):
        """Insert multiple model instances at once."""
        for inst in instances:
            self.insert(inst)

    def get_table(self, tablename):
        """Return all rows for a given table."""
        return list(self._tables.get(tablename, []))

    def query(self, model_class):
        """Start a query against the given model's table."""
        from query import Query
        return Query(self, model_class)

    def clear(self):
        """Remove all data (useful for testing)."""
        self._tables.clear()