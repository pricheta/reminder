FROM python:3.14-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --no-dev

COPY .env .env
COPY main.py main.py
COPY database.py database.py
COPY vk_client.py vk_client.py
COPY database.py database.py

COPY server server
COPY worker worker

EXPOSE 8000

CMD ["uv", "run", "main.py"]
