import re
import sqlite3
from flask import current_app


REGISTRY_SCHEMA = """
CREATE TABLE IF NOT EXISTS authorized_students (
    enrollment TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    branch TEXT NOT NULL,
    graduation_year INTEGER NOT NULL
)
"""

DUMMY_STUDENTS = (
    ("23UCS0033", "student@college.edu", "+91 98765 43210", "Computer Science", 2027),
    ("24UCS0001", "newstudent@college.edu", "+91 98765 43211", "Computer Science", 2028),
    ("24UEC0002", "electronics.student@college.edu", "+91 98765 43212", "Electronics", 2028),
)


def normalize_phone(phone):
    return re.sub(r"\D", "", phone or "")


def init_registry(app):
    """Create the separate dummy college roster used to verify student signups."""
    connection = sqlite3.connect(app.config["STUDENT_REGISTRY_DATABASE"])
    try:
        connection.executescript(REGISTRY_SCHEMA)
        connection.executemany(
            "INSERT OR IGNORE INTO authorized_students(enrollment,email,phone,branch,graduation_year) VALUES(?,?,?,?,?)",
            DUMMY_STUDENTS,
        )
        connection.commit()
    finally:
        connection.close()


def verify_student_record(enrollment, email, phone):
    """Return registry details only when all three submitted identifiers match."""
    connection = sqlite3.connect(current_app.config["STUDENT_REGISTRY_DATABASE"])
    connection.row_factory = sqlite3.Row
    try:
        record = connection.execute(
            "SELECT * FROM authorized_students WHERE enrollment=? AND lower(email)=?",
            (enrollment.upper(), email.lower()),
        ).fetchone()
    finally:
        connection.close()
    if record and normalize_phone(record["phone"]) == normalize_phone(phone):
        return record
    return None
