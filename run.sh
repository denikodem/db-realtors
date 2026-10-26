#!/usr/bin/env bash
# Скрипт быстрого запуска учебного проекта без Docker.
set -euo pipefail

# Перейти в директорию, где лежит run.sh
cd "$(dirname "$0")"

# 1. Виртуальное окружение
if [ ! -d .venv ]; then
    echo "Создаю виртуальное окружение .venv ..."
    if ! python3 -m venv .venv; then
        echo "Не удалось создать виртуальное окружение."
        echo "Установи python3-venv и python3-pip, например:"
        echo "  Fedora/RHEL:      sudo dnf install python3-pip python3-virtualenv"
        echo "  Debian/Ubuntu:    sudo apt install python3-venv python3-pip"
        echo "  Arch/EndeavourOS: sudo pacman -S python python-pip"
        exit 1
    fi
fi

# shellcheck disable=SC1091
source .venv/bin/activate

# 2. Зависимости
echo "Обновляю pip и устанавливаю зависимости ..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 3. Файл окружения
if [ ! -f .env ]; then
    echo "Файл .env не найден — копирую из .env.example"
    cp .env.example .env
fi

# Загружаем переменные из .env
set -a
# shellcheck disable=SC1091
source .env
set +a

# 4. Тестовые данные (по желанию)
if [ "${1:-}" = "--seed" ]; then
    echo "Добавляю тестовые данные ..."
    python -m app.seed
fi

# 5. Запуск приложения
echo "Запускаю приложение на http://${APP_HOST:-127.0.0.1}:${APP_PORT:-8000} ..."
python -m uvicorn app.main:app --host "${APP_HOST:-127.0.0.1}" --port "${APP_PORT:-8000}" --reload
