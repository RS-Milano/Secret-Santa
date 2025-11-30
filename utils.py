def create_name(first_name: str, last_name: str | None, username: str | None) -> str:
    parts: list[str] = []
    if username:
        parts.append(f"@{username}")
    parts.append(first_name)
    if last_name:
        parts.append(last_name)
    return " ".join(parts)
