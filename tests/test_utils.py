"""Tests for utils.py"""
from utils import create_name


class TestCreateName:
    """Test create_name function."""

    def test_with_all_fields(self) -> None:
        """Test creating name with first name, last name, and username."""
        result = create_name("John", "Doe", "johndoe")
        assert result == "@johndoe John Doe"

    def test_without_last_name(self) -> None:
        """Test creating name without last name."""
        result = create_name("John", None, "johndoe")
        assert result == "@johndoe John"

    def test_without_username(self) -> None:
        """Test creating name without username."""
        result = create_name("John", "Doe", None)
        assert result == "John Doe"

    def test_without_username_and_last_name(self) -> None:
        """Test creating name with only first name."""
        result = create_name("John", None, None)
        assert result == "John"

    def test_empty_strings(self) -> None:
        """Test with empty strings."""
        result = create_name("John", "", "")
        assert result == "John"

    def test_only_last_name_none_username_empty(self) -> None:
        """Test with last name, empty username, and username."""
        result = create_name("Jane", "Smith", None)
        assert result == "Jane Smith"

    def test_unicode_names(self) -> None:
        """Test with unicode/cyrillic characters."""
        result = create_name("Иван", "Петров", "ivanov")
        assert result == "@ivanov Иван Петров"

    def test_unicode_without_username(self) -> None:
        """Test unicode names without username."""
        result = create_name("Иван", "Петров", None)
        assert result == "Иван Петров"
