#!/bin/bash

# Останавливаем при ошибках
set -e

# Создаём venv
python3 -m venv venv

# Активируем окружение
source venv/bin/activate

# Устанавливаем зависимости
pip install --upgrade pip
pip install py-cord python-dotenv

# Создаём .env если его ещё нет
if [ ! -f .env ]; then
    echo "DISCORD_TOKEN=вставь_сюда_свой_токен" > .env
    echo ".env файл создан! Не забудь вставить токен."
else
    echo ".env уже существует, пропускаем."
fi

echo "Готово! Активируй окружение командой:"
echo "source venv/bin/activate"
