# Базовый образ Python
FROM python:3.11-slim

# Устанавливаем Node.js (для фронтенда сборки, если нужно)
RUN apt-get update && \
    apt-get install -y curl build-essential && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Сборка фронтенда (если используешь npm)
RUN if [ -f package.json ]; then npm install && npm run build; fi

# Открываем порт для FastAPI
EXPOSE 8000

# Команда для запуска сервера
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
