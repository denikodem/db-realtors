# Дом и Ключ — сайт риелторских услуг

Учебный проект по курсу разработки баз данных: простой сайт агентства недвижимости на **FastAPI + PostgreSQL + HTML/CSS** (шаблоны Jinja2, без фронтенд-фреймворков).

Проект ведёт каталог объектов недвижимости, базу клиентов, список агентов и учёт сделок. Все данные хранятся в PostgreSQL.

## Технологии

- Python 3.11+
- FastAPI + Uvicorn
- SQLAlchemy 2.x (синхронный стиль)
- PostgreSQL (драйвер `psycopg[binary]`, схема подключения `postgresql+psycopg://`)
- Jinja2 шаблоны
- Обычный HTML + один файл CSS (`static/css/style.css`)
- python-dotenv для переменных окружения

Без Docker, без авторизации, без JS-фреймворков.

## Структура проекта

```
requirements.txt        зависимости
.env.example            пример переменных окружения
.env                    твои переменные (не в git)
run.sh                  скрипт быстрого запуска
sql/
  schema.sql            SQL-схема БД (эквивалент моделей SQLAlchemy)
  queries.sql           учебные SQL-запросы
app/
  main.py               приложение FastAPI
  db.py                 подключение к PostgreSQL, сессии
  models.py             модели SQLAlchemy (agents, clients, properties, deals)
  schemas.py            простые Pydantic-схемы
  crud.py               функции для работы с БД
  seed.py               тестовые данные
  routers/              home, properties, clients, agents, deals
templates/              Jinja2-шаблоны (base, index, .../list, detail, form)
static/css/style.css    стили
```

## Требования

- Python 3.11 или новее;
- установленный и запущенный локально PostgreSQL (без Docker);
- права на создание виртуального окружения (venv).

## Настройка PostgreSQL

### Fedora / RHEL

```bash
sudo dnf install postgresql-server postgresql-contrib python3-pip python3-virtualenv
sudo postgresql-setup --initdb
sudo systemctl enable --now postgresql
sudo -u postgres psql -c "CREATE ROLE realtor WITH LOGIN PASSWORD 'realtor';"
sudo -u postgres createdb -O realtor realtor_db
```

### EndeavourOS / Arch

```bash
sudo pacman -S postgresql python python-pip
sudo -u postgres initdb -D /var/lib/postgres/data
sudo systemctl enable --now postgresql
sudo -u postgres psql -c "CREATE ROLE realtor WITH LOGIN PASSWORD 'realtor';"
sudo -u postgres createdb -O realtor realtor_db
```

> Примечание: если PostgreSQL у тебя уже установлен и база создана, команды установки и инициализации выполнять **не нужно** — достаточно создать роль и базу (последние две команды).

Таблицы приложение создаёт само при старте (`Base.metadata.create_all`), отдельно выполнять `sql/schema.sql` не обязательно. Файл `sql/schema.sql` приведён как эквивалент моделей для отчёта по предмету.

## Настройка .env

```bash
cp .env.example .env
```

По умолчанию:

```
DATABASE_URL=postgresql+psycopg://realtor:realtor@127.0.0.1:5432/realtor_db
APP_HOST=127.0.0.1
APP_PORT=8000
```

- Если пароль пользователя БД другой — поменяй `DATABASE_URL` в `.env`.
- Если порт 8000 занят — поменяй `APP_PORT` в `.env`.

## Запуск

```bash
chmod +x run.sh      # если права на исполнение не выставлены
bash run.sh          # обычный запуск
bash run.sh --seed   # запуск с добавлением тестовых данных
```

Скрипт сам создаст `.venv`, установит зависимости, скопирует `.env` при отсутствии и запустит uvicorn. После запуска открой:

```
http://127.0.0.1:8000
```

Можно и вручную:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed            # тестовые данные (по желанию)
uvicorn app.main:app --reload
```

## Тестовые данные

`python -m app.seed` добавляет 3 агентов, 4 клиентов, 10 объектов и 3 сделки (повторный запуск ничего не дублирует). Данные правдоподобные, на русском языке, без реальных людей и телефонов.

## Страницы проекта

| Адрес | Что делает |
|---|---|
| `/` | Главная: статистика и последние объекты |
| `/properties` | Список объектов с фильтрами (поиск, тип, операция, район, макс. цена) |
| `/properties/new`, `/properties/{id}`, `/properties/{id}/edit` | Создание, просмотр, редактирование объекта |
| `/clients` | Список клиентов; CRUD через формы |
| `/agents` | Список агентов; CRUD через формы |
| `/deals` | Список сделок; форма создания новой сделки |

Удаление записи, на которую есть связанные данные (внешние ключи `ON DELETE RESTRICT`), показывает понятное сообщение об ошибке вместо падения.

## Специальные упрощения (для учебного проекта)

- Нет авторизации и ролей: любой, кто открыл сайт, может добавлять и удалять записи.
- Сделки можно только просматривать и создавать — редактирование и удаление сделок сознательно не реализованы, чтобы не усложнять проект.
- Загрузка фотографий объектов не сделана: описание хранится только текстом.
- Валидация форм минимальная: проверяются только обязательные поля, числа и допустимые значения статусов/типов.
- Pydantic-схемы (`app/schemas.py`) используются точечно, интерфейс работает через обычные серверные HTML-формы (POST + redirect), без JSON API и AJAX.
- Миграции не используются (нет Alembic): таблицы создаются через `create_all` при старте.
- Один файл CSS, JavaScript нет вообще.

## Полезные SQL-запросы

В `sql/queries.sql` лежат учебные запросы: объекты с именами агентов, выборки по району и цене, сделки с клиентом и агентом, количество объектов по статусу, суммы сделок по агентам и т.д. Выполнить их можно, например:

```bash
psql -U realtor -d realtor_db -f sql/queries.sql
```
