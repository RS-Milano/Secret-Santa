FROM astral/uv:python3.13-bookworm-slim
WORKDIR /app
COPY main.py db.py utils.py schema.py /app/
COPY pyproject.toml uv.lock .python-version /app/
ENV PYTHONUNBUFFERED=1
RUN uv sync --no-dev
CMD ["uv", "run", "main.py"]
