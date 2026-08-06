"""Data fixtures for testing."""


def setup_database(db):
    """Populate the database with test data."""
    db.create_table("users", ["id", "name", "department", "active", "manager_id"])

    departments = ["engineering", "sales", "marketing", "support"]
    users = []
    for i in range(1, 501):
        dept = departments[i % 4]
        manager_id = (i // 10) * 10 if i % 10 != 0 else None
        users.append({
            "id": i,
            "name": f"User-{i}",
            "department": dept,
            "active": i % 3 != 0,
            "manager_id": manager_id,
        })
    db.insert_many("users", users)