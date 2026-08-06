"""Data access layer — fetches records from the "database".

Simulates a database with in-memory storage. The query API supports
filtering, but each filter call fetches records individually.
"""

import time


class Database:
    """Simulated database with in-memory storage."""

    def __init__(self):
        self._tables = {}

    def create_table(self, name, columns):
        self._tables[name] = {"columns": columns, "rows": []}

    def insert(self, table, **values):
        self._tables[table]["rows"].append(values)

    def insert_many(self, table, rows):
        for row in rows:
            self.insert(table, **row)

    def fetch_one(self, table, **filters):
        """Fetch a single record matching filters. Simulates a DB query."""
        time.sleep(0.001)  # simulate network latency
        rows = self._tables[table]["rows"]
        for row in rows:
            if all(row.get(k) == v for k, v in filters.items()):
                return dict(row)
        return None

    def fetch_all(self, table, **filters):
        """Fetch all records matching filters. Simulates a batch query."""
        time.sleep(0.002)  # batch query is slightly slower than single
        rows = self._tables[table]["rows"]
        if not filters:
            return [dict(r) for r in rows]
        return [dict(r) for r in rows
                if all(r.get(k) == v for k, v in filters.items())]


class UserStore:
    """High-level API for user-related queries.

    Used by the web application to fetch user data.
    BUG: The `get_users_by_ids` method uses N+1 queries — for each
    user ID, it makes a separate fetch_one call. With 100 users,
    this is 100 individual queries instead of 1 batch query.
    """

    def __init__(self, db):
        self.db = db

    def get_user(self, user_id):
        """Get a single user by ID."""
        return self.db.fetch_one("users", id=user_id)

    def get_users_by_ids(self, user_ids):
        """Get multiple users by their IDs.

        BUG: Makes N individual queries instead of 1 batch query.
        """
        users = []
        for uid in user_ids:
            user = self.db.fetch_one("users", id=uid)
            if user:
                users.append(user)
        return users

    def get_active_users(self):
        """Get all active users."""
        return self.db.fetch_all("users", active=True)

    def get_users_by_department(self, department):
        """Get all users in a department, then enrich with manager info.

        BUG: Also uses N+1 — fetches each manager individually.
        """
        users = self.db.fetch_all("users", department=department)
        for user in users:
            manager_id = user.get("manager_id")
            if manager_id:
                manager = self.db.fetch_one("users", id=manager_id)
                user["manager_name"] = manager["name"] if manager else "N/A"
        return users