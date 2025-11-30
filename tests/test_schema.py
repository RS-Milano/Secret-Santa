"""Tests for schema.py"""
from schema import User, UserStatistics, Statistics


class TestUserModel:
    """Test User schema model."""

    def test_user_creation(self) -> None:
        """Test creating User with all fields."""
        user = User(id=123, tg_name="@testuser", name="Test User", desire="A book")
        assert user.id == 123
        assert user.tg_name == "@testuser"
        assert user.name == "Test User"
        assert user.desire == "A book"

    def test_user_default_values(self) -> None:
        """Test User with default values."""
        user = User(id=456)
        assert user.id == 456
        assert user.tg_name == ""
        assert user.name == ""
        assert user.desire == ""

    def test_user_partial_fields(self) -> None:
        """Test User with some fields."""
        user = User(id=789, tg_name="@another", desire="Laptop")
        assert user.id == 789
        assert user.tg_name == "@another"
        assert user.name == ""
        assert user.desire == "Laptop"


class TestUserStatisticsModel:
    """Test UserStatistics schema model."""

    def test_user_statistics_registered(self) -> None:
        """Test UserStatistics for registered user."""
        stat = UserStatistics(tg_name="@user1", name="User One", is_registered=True)
        assert stat.tg_name == "@user1"
        assert stat.name == "User One"
        assert stat.is_registered is True

    def test_user_statistics_not_registered(self) -> None:
        """Test UserStatistics for unregistered user."""
        stat = UserStatistics(tg_name="@user2", name="User Two", is_registered=False)
        assert stat.tg_name == "@user2"
        assert stat.name == "User Two"
        assert stat.is_registered is False


class TestStatisticsModel:
    """Test Statistics schema model."""

    def test_statistics_empty(self) -> None:
        """Test Statistics with no users."""
        stats = Statistics(users=[])
        assert len(stats.users) == 0

    def test_statistics_single_user(self) -> None:
        """Test Statistics with one user."""
        user_stat = UserStatistics(tg_name="@single", name="Single User", is_registered=True)
        stats = Statistics(users=[user_stat])
        assert len(stats.users) == 1
        assert stats.users[0].is_registered is True

    def test_statistics_multiple_users(self) -> None:
        """Test Statistics with multiple users."""
        users = [
            UserStatistics(tg_name="@user1", name="User One", is_registered=True),
            UserStatistics(tg_name="@user2", name="User Two", is_registered=False),
            UserStatistics(tg_name="@user3", name="User Three", is_registered=True),
        ]
        stats = Statistics(users=users)
        assert len(stats.users) == 3

    def test_statistics_str_empty(self) -> None:
        """Test __str__ method with no users."""
        stats = Statistics(users=[])
        result = str(stats)
        assert "Зарегистрировано пользователей: 0 из 0" in result

    def test_statistics_str_with_users(self) -> None:
        """Test __str__ method with multiple users."""
        users = [
            UserStatistics(tg_name="@user1", name="User One", is_registered=True),
            UserStatistics(tg_name="@user2", name="User Two", is_registered=False),
        ]
        stats = Statistics(users=users)
        result = str(stats)
        assert "Зарегистрировано пользователей: 1 из 2" in result
        assert "✅ @user1 (User One)" in result
        assert "❌ @user2 (User Two)" in result

    def test_statistics_count_registered(self) -> None:
        """Test correct counting of registered users in __str__."""
        users = [
            UserStatistics(tg_name="@a", name="A", is_registered=True),
            UserStatistics(tg_name="@b", name="B", is_registered=True),
            UserStatistics(tg_name="@c", name="C", is_registered=False),
            UserStatistics(tg_name="@d", name="D", is_registered=True),
        ]
        stats = Statistics(users=users)
        result = str(stats)
        assert "Зарегистрировано пользователей: 3 из 4" in result
