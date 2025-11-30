# Third-party libraties imports
from pydantic import BaseModel


class User(BaseModel):
    id: int
    tg_name: str = ""
    name: str = ""
    desire: str = ""

class UserStatistics(BaseModel):
    tg_name: str
    name: str
    is_registered: bool

class Statistics(BaseModel):
    users: list[UserStatistics]

    def __str__(self) -> str:
        registered_count: int = sum(user.is_registered for user in self.users)
        total_count: int = len(self.users)
        result: str = f"Зарегистрировано пользователей: {registered_count} из {total_count}\n"
        for user in self.users:
            status: str = "✅" if user.is_registered else "❌"
            result += f"{status} {user.tg_name} ({user.name})\n"
        return result
