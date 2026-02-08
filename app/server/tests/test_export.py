"""
Tests for CSV export functionality
"""

import pytest
import sqlite3
import tempfile
import os
import csv
import io
from fastapi.testclient import TestClient
from server import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def test_db_with_data():
    """Create a test database with sample data"""
    # Ensure db directory exists
    os.makedirs("db", exist_ok=True)

    # Create database
    conn = sqlite3.connect("db/database.db")
    cursor = conn.cursor()

    # Create test table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_export_table (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            age INTEGER
        )
    ''')

    # Clear existing data
    cursor.execute("DELETE FROM test_export_table")

    # Insert test data
    cursor.execute("INSERT INTO test_export_table (name, email, age) VALUES (?, ?, ?)",
                   ('Alice', 'alice@example.com', 30))
    cursor.execute("INSERT INTO test_export_table (name, email, age) VALUES (?, ?, ?)",
                   ('Bob', 'bob@example.com', 25))
    cursor.execute("INSERT INTO test_export_table (name, email, age) VALUES (?, ?, ?)",
                   ('Charlie', 'charlie@example.com', 35))

    conn.commit()
    conn.close()

    yield

    # Cleanup - remove test table
    conn = sqlite3.connect("db/database.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS test_export_table")
    conn.commit()
    conn.close()


class TestTableExport:
    """Test the table export endpoint"""

    def test_export_table_success(self, client, test_db_with_data):
        """Test exporting an existing table returns valid CSV"""
        response = client.get("/api/export/table/test_export_table")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert 'attachment; filename="test_export_table.csv"' in response.headers["content-disposition"]

        # Parse CSV content
        content = response.text
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Check header
        assert rows[0] == ['id', 'name', 'email', 'age']

        # Check data rows
        assert len(rows) == 4  # header + 3 data rows

        # Verify data content
        names = [row[1] for row in rows[1:]]
        assert 'Alice' in names
        assert 'Bob' in names
        assert 'Charlie' in names

    def test_export_table_invalid_name(self, client):
        """Test exporting with invalid table name returns 400"""
        response = client.get("/api/export/table/'; DROP TABLE users; --")

        assert response.status_code == 400

    def test_export_table_not_found(self, client):
        """Test exporting non-existent table returns 404"""
        response = client.get("/api/export/table/nonexistent_table_xyz")

        assert response.status_code == 404

    def test_export_table_sql_injection_blocked(self, client):
        """Test that SQL injection attempts are blocked"""
        # Test various injection patterns
        injection_attempts = [
            "test; DROP TABLE users",
            "test' OR '1'='1",
            "test UNION SELECT * FROM passwords",
            "../../../etc/passwd"
        ]

        for attempt in injection_attempts:
            response = client.get(f"/api/export/table/{attempt}")
            # Should return 400 (bad request) or 404 (not found), not 200
            assert response.status_code in [400, 404]


class TestResultsExport:
    """Test the results export endpoint"""

    def test_export_results_success(self, client):
        """Test exporting query results returns valid CSV"""
        payload = {
            "columns": ["id", "name", "email"],
            "results": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"}
            ]
        }

        response = client.post("/api/export/results", json=payload)

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert 'attachment; filename="query_results.csv"' in response.headers["content-disposition"]

        # Parse CSV content
        content = response.text
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Check header
        assert rows[0] == ['id', 'name', 'email']

        # Check data rows
        assert len(rows) == 3  # header + 2 data rows
        assert rows[1] == ['1', 'Alice', 'alice@example.com']
        assert rows[2] == ['2', 'Bob', 'bob@example.com']

    def test_export_results_empty(self, client):
        """Test exporting empty results returns CSV with only headers"""
        payload = {
            "columns": ["id", "name", "email"],
            "results": []
        }

        response = client.post("/api/export/results", json=payload)

        assert response.status_code == 200

        # Parse CSV content
        content = response.text
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Should have only header row
        assert len(rows) == 1
        assert rows[0] == ['id', 'name', 'email']

    def test_export_results_special_chars(self, client):
        """Test that results with special characters are properly escaped in CSV"""
        payload = {
            "columns": ["name", "description"],
            "results": [
                {"name": "Test, with comma", "description": 'Quote "test"'},
                {"name": "Normal", "description": "Line\nbreak"}
            ]
        }

        response = client.post("/api/export/results", json=payload)

        assert response.status_code == 200

        # Parse CSV content - csv module should handle escaping
        content = response.text
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        assert len(rows) == 3  # header + 2 data rows

        # CSV reader should properly unescape values
        assert rows[1][0] == "Test, with comma"
        assert rows[1][1] == 'Quote "test"'

    def test_export_results_null_values(self, client):
        """Test that null values are handled correctly"""
        payload = {
            "columns": ["id", "name", "optional_field"],
            "results": [
                {"id": 1, "name": "Alice", "optional_field": None},
                {"id": 2, "name": "Bob", "optional_field": "has value"}
            ]
        }

        response = client.post("/api/export/results", json=payload)

        assert response.status_code == 200

        # Parse CSV content
        content = response.text
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        assert len(rows) == 3
        # None should be converted to empty string or "None"
        assert rows[1][2] in ['', 'None']
        assert rows[2][2] == 'has value'

    def test_export_results_unicode(self, client):
        """Test that unicode characters are handled correctly"""
        payload = {
            "columns": ["name", "city"],
            "results": [
                {"name": "José García", "city": "São Paulo"},
                {"name": "田中太郎", "city": "東京"}
            ]
        }

        response = client.post("/api/export/results", json=payload)

        assert response.status_code == 200

        # Parse CSV content
        content = response.text
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        assert len(rows) == 3
        assert rows[1][0] == "José García"
        assert rows[2][1] == "東京"


class TestCSVFormatting:
    """Test CSV formatting and headers"""

    def test_csv_content_type_header(self, client, test_db_with_data):
        """Test that Content-Type header is set correctly"""
        response = client.get("/api/export/table/test_export_table")

        assert "text/csv" in response.headers["content-type"]

    def test_csv_content_disposition_header(self, client, test_db_with_data):
        """Test that Content-Disposition header is set correctly"""
        response = client.get("/api/export/table/test_export_table")

        assert "attachment" in response.headers["content-disposition"]
        assert "filename=" in response.headers["content-disposition"]

    def test_results_export_filename(self, client):
        """Test that results export has correct filename"""
        payload = {
            "columns": ["id"],
            "results": [{"id": 1}]
        }

        response = client.post("/api/export/results", json=payload)

        assert 'filename="query_results.csv"' in response.headers["content-disposition"]
