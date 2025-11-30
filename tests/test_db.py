"""Tests for db.py"""
import pytest
import sqlite3
import os
from tempfile import TemporaryDirectory
from unittest.mock import patch

# We need to handle DB_PATH patching for imports
class TestDatabase:
    """Test database operations."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Initialize database before each test with a fresh temp database."""
        # Create a temporary directory for this test
        self.temp_dir = TemporaryDirectory()
        self.test_db_path = os.path.join(self.temp_dir.name, "test.db")
        
        # Patch DB_PATH and import db functions
        with patch("db.DB_PATH", self.test_db_path):
            from db import init_db
            init_db()
        
        yield
        
        # Cleanup
        self.temp_dir.cleanup()

    def _get_db_connection(self):
        """Helper to get database connection."""
        return sqlite3.connect(self.test_db_path)

    def _patch_and_run(self, func, *args):
        """Helper to run db function with patched DB_PATH."""
        with patch("db.DB_PATH", self.test_db_path):
            return func(*args)

    def test_init_db_creates_table(self) -> None:
        """Test that init_db creates users table."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        result = cursor.fetchone()
        conn.close()
        assert result is not None
        assert result[0] == "users"

    def test_add_user(self) -> None:
        """Test adding a user."""
        from db import add_user
        self._patch_and_run(add_user, 123, "@testuser")

        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, tg_name FROM users WHERE id = ?", (123,))
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == 123
        assert result[1] == "@testuser"

    def test_add_duplicate_user(self) -> None:
        """Test adding duplicate user (should be ignored)."""
        from db import add_user
        self._patch_and_run(add_user, 456, "@user1")
        self._patch_and_run(add_user, 456, "@user2")  # Should be ignored

        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT tg_name FROM users WHERE id = ?", (456,))
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == "@user1"  # Should remain unchanged

    def test_update_name(self) -> None:
        """Test updating user name."""
        from db import add_user, update_name
        self._patch_and_run(add_user, 789, "@user")
        self._patch_and_run(update_name, 789, "Test User")

        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE id = ?", (789,))
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == "Test User"

    def test_update_desire(self) -> None:
        """Test updating user desire."""
        from db import add_user, update_desire
        self._patch_and_run(add_user, 111, "@user")
        self._patch_and_run(update_desire, 111, "A laptop")

        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT desire, is_registered FROM users WHERE id = ?", (111,))
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == "A laptop"
        assert result[1] == 1  # is_registered should be set to 1

    def test_get_user_exists(self) -> None:
        """Test getting existing user."""
        from db import add_user, update_name, update_desire, get_user
        self._patch_and_run(add_user, 222, "@testuser")
        self._patch_and_run(update_name, 222, "Test User")
        self._patch_and_run(update_desire, 222, "A book")

        user = self._patch_and_run(get_user, 222)

        assert user is not None
        assert user.id == 222
        assert user.tg_name == "@testuser"
        assert user.name == "Test User"
        assert user.desire == "A book"

    def test_get_user_not_exists(self) -> None:
        """Test getting non-existent user."""
        from db import get_user
        user = self._patch_and_run(get_user, 999)
        assert user is None

    def test_get_statistics_empty(self) -> None:
        """Test getting statistics with no users."""
        from db import get_statistics
        stats = self._patch_and_run(get_statistics)

        assert stats is not None
        assert len(stats.users) == 0

    def test_get_statistics_with_users(self) -> None:
        """Test getting statistics with multiple users."""
        from db import add_user, update_name, update_desire, get_statistics
        self._patch_and_run(add_user, 1, "@user1")
        self._patch_and_run(update_name, 1, "User One")
        self._patch_and_run(update_desire, 1, "Gift 1")

        self._patch_and_run(add_user, 2, "@user2")
        self._patch_and_run(update_name, 2, "User Two")
        # Don't register user 2

        stats = self._patch_and_run(get_statistics)

        assert len(stats.users) == 2
        assert stats.users[0].tg_name == "@user1"
        assert stats.users[0].is_registered is True
        assert stats.users[1].tg_name == "@user2"
        assert stats.users[1].is_registered is False

    def test_get_data_only_registered(self) -> None:
        """Test that get_data returns only registered users."""
        from db import add_user, update_name, update_desire, get_data
        self._patch_and_run(add_user, 1, "@user1")
        self._patch_and_run(update_name, 1, "User One")
        self._patch_and_run(update_desire, 1, "Gift 1")

        self._patch_and_run(add_user, 2, "@user2")
        self._patch_and_run(update_name, 2, "User Two")
        # Not registered

        data = self._patch_and_run(get_data)

        assert len(data) == 1
        assert data[0].id == 1
        assert data[0].name == "User One"

    def test_get_data_empty(self) -> None:
        """Test get_data with no registered users."""
        from db import get_data
        data = self._patch_and_run(get_data)
        assert len(data) == 0

    def test_user_fields_default_values(self) -> None:
        """Test that user fields have correct default values."""
        from db import add_user, get_user
        self._patch_and_run(add_user, 333, "@user")
        user = self._patch_and_run(get_user, 333)

        assert user is not None
        assert user.name == ""
        assert user.desire == ""
        assert user.tg_name == "@user"
