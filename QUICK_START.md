# 🚀 Быстрый старт MasterConnect

## Предварительные требования

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Git

---

## 📦 Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd masterconnect
```

### 2. Настройка Backend

```bash
cd apps/api

# Создать виртуальное окружение
python -m venv venv

# Активировать (Windows)
venv\Scripts\activate

# Активировать (Linux/Mac)
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

### 3. Настройка базы данных

Создайте PostgreSQL базу данных:

```sql
CREATE DATABASE masterconnect;
CREATE USER masterconnect_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE masterconnect TO masterconnect_user;
```

### 4. Настройка переменных окружения Backend (dev)

**ВАЖНО:** Создайте файл `apps/api/.env` с абсолютным путем к БД для единообразия при любом способе запуска.

Скопируйте `env.example` в `apps/api/.env` и настройте:

```env
# Dev defaults (SQLite)
APP_ENV=development
APP_NAME=MasterConnect API
APP_VERSION=1.0.0
DEBUG=True
API_PREFIX=/api/v1

SECRET_KEY=dev-secret-change-me
JWT_SECRET_KEY=dev-jwt-secret-change-me
JWT_ALGORITHM=HS256
JWT_EXPIRES_MINUTES=60
REFRESH_TOKEN_EXPIRES_DAYS=30

# ВАЖНО: Используйте абсолютный путь к БД для единообразия
# Замените путь на ваш реальный путь к проекту
DATABASE_URL=sqlite+aiosqlite:///C:/Users/ultua/PycharmProjects/masterconnect/apps/api/test.db
DATABASE_ECHO=False

BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:8080"]

REDIS_URL=redis://localhost:6379/0

S3_BUCKET=dummy
S3_ACCESS_KEY=dummy
S3_SECRET_KEY=dummy
S3_REGION=us-east-1

EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=dummy@example.com
EMAIL_SMTP_PASSWORD=dummy
EMAIL_FROM=dummy@example.com
EMAIL_USE_TLS=True

GOOGLE_SERVICE_ACCOUNT_JSON_B64=dummy
GOOGLE_CALENDAR_ID=dummy

KASPI_PAYMENT_URL=dummy

MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf,jpg,jpeg,png,docx
BOOKING_HOLD_DURATION_MINUTES=10
```

**Примечание:** Абсолютный путь гарантирует, что все способы запуска (uvicorn, скрипты) будут использовать одну и ту же БД.

### 5. Инициализация базы данных

```bash
# Из директории apps/api с активированным venv
python -m alembic upgrade head

# Или создать таблицы напрямую (для разработки)
python -c "from src.db.session import init_db; import asyncio; asyncio.run(init_db())"
```

### 6. Запуск Backend (канонический способ)

**ВАЖНО:** Убедитесь, что создан файл `apps/api/.env` с правильным `DATABASE_URL` (см. шаг 4).

```bash
# Из директории apps/api
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Альтернативные способы (необязательно):**
- PowerShell: `./start_backend.ps1` (теперь использует .env)
- Python: `python run_server.py` (теперь использует .env)
- Если запуск из папки src: `python -m uvicorn main:app --reload`

Все способы теперь используют единый `.env` файл, поэтому БД будет одна и та же.

Backend будет доступен на: http://localhost:8000  
API документация: http://localhost:8000/docs

### 7. Настройка Frontend

Откройте новый терминал:

```bash
cd apps/web

# Установить зависимости
npm install

# Создать .env файл
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env
```

### 8. Запуск Frontend

```bash
# Из директории apps/web
npm run dev
```

Frontend будет доступен на: http://localhost:3000

---

## 👤 Создание тестовых пользователей

### Через API (http://localhost:8000/docs):

#### 1. Создать студента

```json
POST /api/v1/auth/register
{
  "email": "student@test.com",
  "password": "password123",
  "name": "Тестовый Студент",
  "role": "STUDENT"
}
```

#### 2. Создать ментора

```json
POST /api/v1/auth/register
{
  "email": "mentor@test.com",
  "password": "password123",
  "name": "Тестовый Ментор",
  "role": "MENTOR"
}
```

#### 3. Создать админа (через БД)

```sql
-- Сначала создайте пользователя через регистрацию, затем:
UPDATE users SET role = 'ADMIN' WHERE email = 'admin@test.com';
```

---

## 🧪 Тестирование

### 1. Проверка Backend

```bash
# Health check
curl http://localhost:8000/health

# Должен вернуть:
# {"status":"healthy","app":"MasterConnect API","version":"1.0.0","environment":"development"}
```

### 2. Проверка Frontend

Откройте браузер: http://localhost:3000

- Должна открыться главная страница
- Попробуйте зарегистрироваться
- Войдите в систему

### 3. Основные сценарии

#### Студент:
1. Зарегистрируйтесь как студент
2. Заполните профиль
3. Перейдите в каталог менторов
4. Выберите ментора и забронируйте консультацию
5. Загрузите доказательство оплаты
6. После завершения - оставьте отзыв

#### Ментор:
1. Зарегистрируйтесь как ментор
2. Заполните профиль (био, образование)
3. Настройте расписание
4. Просмотрите свои бронирования

#### Админ:
1. Войдите как админ
2. Проверьте дашборд
3. Проверьте оплату студента
4. Верифицируйте ментора
5. Просмотрите статистику

---

## 🔧 Полезные команды

### Backend

```bash
# Запуск с автоперезагрузкой
python -m uvicorn src.main:app --reload

# Запуск на другом порту
python -m uvicorn src.main:app --reload --port 8001

# Проверка зависимостей
pip list

# Обновление зависимостей
pip install --upgrade -r requirements.txt

# Создание миграции (если используете Alembic)
alembic revision --autogenerate -m "Description"

# Применение миграций
alembic upgrade head
```

### Frontend

```bash
# Запуск dev сервера
npm run dev

# Сборка для production
npm run build

# Предпросмотр production сборки
npm run preview

# Проверка типов TypeScript
npm run type-check

# Линтинг
npm run lint
```

---

## 📁 Структура файлов

```
masterconnect/
├── apps/
│   ├── api/                 # Backend
│   │   ├── src/
│   │   │   ├── core/       # Ядро (config, auth, exceptions)
│   │   │   ├── db/         # База данных
│   │   │   ├── modules/    # Бизнес-модули
│   │   │   └── main.py     # Точка входа
│   │   ├── .env            # Переменные окружения (создать)
│   │   └── requirements.txt
│   │
│   └── web/                 # Frontend
│       ├── src/
│       │   ├── app/        # Конфигурация
│       │   ├── pages/      # Страницы
│       │   └── shared/     # Общие компоненты
│       ├── .env            # Переменные окружения (создать)
│       └── package.json
│
├── uploads/                 # Загруженные файлы (создается автоматически)
├── .gitignore
├── PAYMENT_SYSTEM.md       # Документация системы оплаты
├── PROJECT_STATUS.md       # Статус проекта
└── QUICK_START.md          # Этот файл
```

---

## ⚠️ Частые проблемы

### Backend не запускается

**Проблема**: `ModuleNotFoundError`
**Решение**: Убедитесь, что виртуальное окружение активировано и зависимости установлены

```bash
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**Проблема**: `Connection refused` к БД
**Решение**: Проверьте что PostgreSQL запущен и DATABASE_URL правильный

```bash
# Windows
net start postgresql-x64-14

# Linux
sudo systemctl start postgresql
```

### Frontend не запускается

**Проблема**: `ECONNREFUSED` при запросах к API
**Решение**: Проверьте что backend запущен и .env файл создан

```bash
# Проверить backend
curl http://localhost:8000/health

# Проверить .env
cat apps/web/.env
# Должно быть: VITE_API_URL=http://localhost:8000/api/v1
```

**Проблема**: `Module not found`
**Решение**: Переустановите зависимости

```bash
rm -rf node_modules package-lock.json
npm install
```

### CORS ошибки

**Проблема**: `CORS policy` ошибка в браузере
**Решение**: Добавьте frontend URL в BACKEND_CORS_ORIGINS в .env

```env
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

---

## 📞 Поддержка

Если возникли проблемы:

1. **Проверьте логи backend**: `apps/api/logs/` (если настроены)
2. **Проверьте консоль браузера**: F12 → Console
3. **Проверьте терминал**: Ошибки выводятся в терминал
4. **Проверьте .env файлы**: Убедитесь что все переменные заданы
5. **Проверьте БД**: Убедитесь что PostgreSQL запущен

---

## 🎉 Готово!

Теперь у вас должен быть запущен полнофункциональный MasterConnect!

**Следующие шаги:**
1. Создайте тестовых пользователей
2. Протестируйте основные функции
3. Настройте production окружение (если нужно)
4. Добавьте реальные данные

**Полезные ссылки:**
- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Документация системы оплаты: `PAYMENT_SYSTEM.md`
- Статус проекта: `PROJECT_STATUS.md`







