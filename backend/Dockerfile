# ==== Базовый образ ====
FROM python:3.12-slim AS base

# ==== Переменные окружения ====
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ==== Рабочая директория ====
WORKDIR /app

# ==== Системные зависимости ====
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev \
    postgresql-client \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# ==== Установка зависимостей ====
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==== Копирование проекта ====
COPY . .

# ==== Открываем порт ====
EXPOSE 8000

# ==== Запуск приложения ====
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
