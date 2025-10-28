# Использовать минимальный образ Python 3.11 на базе Alpine
FROM python:3.11-slim



# Создать рабочую директорию в контейнере
WORKDIR /app

# Скопировать файл зависимостей и установить их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать сам скрипт в контейнер
COPY bot.py .

# Установить переменную окружения, чтобы Python не буферизовал вывод
ENV PYTHONUNBUFFERED 1

# Команда, которая будет выполняться при запуске контейнера
CMD ["python", "bot.py"]