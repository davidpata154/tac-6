"""
Tests for the export endpoints (table export and query results export)
"""

import pytest
import sqlite3
import os
import csv
import io
import shutil
from fastapi.testclient import TestClient


@pytest.fixture
def setup_test_db():
    """Set up test database in the expected location"""
    # Ensure db directory exists
    os.makedirs("db", exist_ok=True)

    # Backup existing database if it exists
    db_path = "db/database.db"
    backup_path = "db/database.db.backup"
    had_existing = os.path.exists(db_path)

    if had_existing:
        shutil.copy2(db_path, backup_path)

    # Create fresh test database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop existing tables if any
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        if not table[0].startswith('sqlite_'):
            cursor.execute(f"DROP TABLE IF EXISTS [{table[0]}]")

    # Create test table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            age INTEGER
        )
    ''')

    # Insert test data
    cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                   ('Alice', 'alice@example.com', 30))
    cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                   ('Bob', 'bob@example.com', 25))
    cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                   ('Charlie', 'charlie@example.com', 35))

    # Create an empty table for edge case testing
    cursor.execute('''
        CREATE TABLE empty_table (
            id INTEGER PRIMARY KEY,
            value TEXT
        )
    ''')

    # Create a table with special characters in data
    cursor.execute('''
        CREATE TABLE special_chars (
            id INTEGER PRIMARY KEY,
            description TEXT
        )
    ''')
    cursor.execute("INSERT INTO special_chars (description) VALUES (?)",
                   ('Value with, comma',))
    cursor.execute("INSERT INTO special_chars (description) VALUES (?)",
                   ('Value with "quotes"',))
    cursor.execute("INSERT INTO special_chars (description) VALUES (?)",
                   ('Value with\nnewline',))

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup - restore original database if it existed
    if had_existing:
        shutil.copy2(backup_path, db_path)
        os.unlink(backup_path)
    else:
        os.unlink(db_path)


@pytest.fixture
def client(setup_test_db):
    """Create a test client"""
    from server import app
    return TestClient(app)


class TestTableExport:
    """Tests for the table export endpoint"""

    def test_export_valid_table_returns_csv(self, client):
        """Test that exporting a valid table returns CSV content"""
        response = client.get("/api/table/users/export")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        assert "users.csv" in response.headers["content-disposition"]

        # Parse CSV content
        content = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Verify header
        assert rows[0] == ['id', 'name', 'email', 'age']

        # Verify data rows
        assert len(rows) == 4  # header + 3 data rows

    def test_export_invalid_table_name_returns_400(self, client):
        """Test that an invalid table name returns 400 error"""
        # SQL injection attempt
        response = client.get("/api/table/users'; DROP TABLE users; --/export")
        assert response.status_code == 400

    def test_export_nonexistent_table_returns_404(self, client):
        """Test that exporting a non-existent table returns 404 error"""
        response = client.get("/api/table/nonexistent_table/export")
        assert response.status_code == 404

    def test_export_empty_table_returns_csv_with_headers_only(self, client):
        """Test that exporting an empty table returns CSV with headers only"""
        response = client.get("/api/table/empty_table/export")

        assert response.status_code == 200

        content = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Should have only the header row
        assert len(rows) == 1
        assert rows[0] == ['id', 'value']

    def test_export_table_with_special_characters(self, client):
        """Test that special characters in data are properly escaped in CSV"""
        response = client.get("/api/table/special_chars/export")

        assert response.status_code == 200

        content = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Verify data with special characters is properly escaped
        assert len(rows) == 4  # header + 3 data rows

        # Check that commas, quotes, and newlines are handled
        descriptions = [row[1] for row in rows[1:]]
        assert 'Value with, comma' in descriptions
        assert 'Value with "quotes"' in descriptions
        assert 'Value with\nnewline' in descriptions

    def test_sql_injection_attempts_blocked(self, client):
        """Test that SQL injection attempts are blocked"""
        injection_attempts = [
            "users; DROP TABLE users",
            "users' OR '1'='1",
            "users UNION SELECT * FROM sqlite_master",
            "'; DELETE FROM users WHERE '1'='1",
            "users--",
        ]

        for attempt in injection_attempts:
            response = client.get(f"/api/table/{attempt}/export")
            assert response.status_code == 400, f"Injection attempt not blocked: {attempt}"


class TestQueryResultsExport:
    """Tests for the query results export endpoint"""

    def test_export_results_returns_valid_csv(self, client):
        """Test that exporting query results returns valid CSV"""
        request_data = {
            "columns": ["id", "name", "email"],
            "results": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"}
            ]
        }

        response = client.post("/api/export-results", json=request_data)

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        assert "query_results.csv" in response.headers["content-disposition"]

        # Parse CSV content
        content = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Verify header
        assert rows[0] == ["id", "name", "email"]

        # Verify data rows
        assert len(rows) == 3  # header + 2 data rows

    def test_export_empty_results_returns_csv_with_headers(self, client):
        """Test that empty results return CSV with headers only"""
        request_data = {
            "columns": ["id", "name"],
            "results": []
        }

        response = client.post("/api/export-results", json=request_data)

        assert response.status_code == 200

        content = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Should have only the header row
        assert len(rows) == 1
        assert rows[0] == ["id", "name"]

    def test_export_results_with_custom_filename(self, client):
        """Test that custom filename is used in Content-Disposition header"""
        request_data = {
            "columns": ["id", "name"],
            "results": [{"id": 1, "name": "Test"}],
            "filename": "custom_export.csv"
        }

        response = client.post("/api/export-results", json=request_data)

        assert response.status_code == 200
        assert "custom_export.csv" in response.headers["content-disposition"]

    def test_export_results_with_special_characters(self, client):
        """Test that special characters in results are properly escaped"""
        request_data = {
            "columns": ["description"],
            "results": [
                {"description": "Value with, comma"},
                {"description": 'Value with "quotes"'},
                {"description": "Value with\nnewline"}
            ]
        }

        response = client.post("/api/export-results", json=request_data)

        assert response.status_code == 200

        content = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Verify data with special characters is properly escaped
        descriptions = [row[0] for row in rows[1:]]
        assert 'Value with, comma' in descriptions
        assert 'Value with "quotes"' in descriptions
        assert 'Value with\nnewline' in descriptions

    def test_export_results_with_null_values(self, client):
        """Test that null values are handled correctly"""
        request_data = {
            "columns": ["id", "name", "optional_field"],
            "results": [
                {"id": 1, "name": "Alice", "optional_field": None},
                {"id": 2, "name": "Bob", "optional_field": "has_value"}
            ]
        }

        response = client.post("/api/export-results", json=request_data)

        assert response.status_code == 200

        content = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Verify null is handled (should be empty string)
        assert rows[1][2] == ""  # None should become empty string
        assert rows[2][2] == "has_value"
