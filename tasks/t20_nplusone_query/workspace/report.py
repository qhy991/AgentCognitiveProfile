"""Report generator using the user store.

Builds reports about users, departments, and activity.
"""


class ReportBuilder:
    """Generates reports from user data."""

    def __init__(self, user_store):
        self.store = user_store

    def department_summary(self, department):
        """Generate a summary of users in a department."""
        users = self.store.get_users_by_department(department)
        total = len(users)
        active = sum(1 for u in users if u.get("active"))
        managers = set()
        for u in users:
            mn = u.get("manager_name")
            if mn:
                managers.add(mn)
        return {
            "department": department,
            "total_users": total,
            "active_users": active,
            "unique_managers": len(managers),
            "users": users,
        }

    def user_list_report(self, user_ids):
        """Build a report for specific users."""
        users = self.store.get_users_by_ids(user_ids)
        return {
            "count": len(users),
            "users": users,
        }