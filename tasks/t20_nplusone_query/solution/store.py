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
        """Fetch a single record matching filters."""
        time.sleep(0.001)
        rows = self._tables[table]["rows"]
        for row in rows:
            if all(row.get(k) == v for k, v in filters.items()):
                return dict(row)
        return None

    def fetch_all(self, table, **filters):
        """Fetch all records matching filters."""
        time.sleep(0.002)
        rows = self._tables[table]["rows"]
        if not filters:
            return [dict(r) for r in rows]
        return [dict(r) for r in rows
                if all(r.get(k) == v for k, v in filters.items())]

    def fetch_by_ids(self, table, ids, id_field="id"):
        """Fetch multiple records by their IDs in a single batch query."""
        time.sleep(0.002)
        id_set = set(ids)
        rows = self._tables[table]["rows"]
        return [dict(r) for r in rows if r.get(id_field) in id_set]


class UserStore:
    """High-level API for user-related queries."""

    def __init__(self, db):
        self.db = db

    def get_user(self, user_id):
        """Get a single user by ID."""
        return self.db.fetch_one("users", id=user_id)

    def get_users_by_ids(self, user_ids):
        """Get multiple users by their IDs using a single batch query."""
        return self.db.fetch_by_ids("users", user_ids, id_field="id")

    def get_active_users(self):
        """Get all active users."""
        return self.db.fetch_all("users", active=True)

    def get_users_by_department(self, department):
        """Get all users in a department, then enrich with manager info.

        Uses batch query to fetch all managers at once.
        """
        users = self.db.fetch_all("users", department=department)
        manager_ids = {u.get("manager_id") for u in users if u.get("manager_id")}
        if manager_ids:
            managers = self.db.fetch_by_ids("users", list(manager_ids))
            manager_map = {m["id"]: m["name"] for m in managers}
            for user in users:
                mid = user.get("manager_id")
                if mid:
                    user["manager_name"] = manager_map.get(mid, "N/A")
        return users