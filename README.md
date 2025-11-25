# 🎓 MasterConnect - Платформа онлайн консультаций с менторами

**Статус**: ✅ **Готов к запуску**  
**Версия**: 1.0.0  
**Дата**: 2025-10-09

---

## 📖 Описание

**MasterConnect** - это платформа для онлайн консультаций, которая соединяет студентов с опытными менторами для помощи в поступлении в университеты и развитии карьеры.

### 🎯 Основные возможности

- 🔍 **Каталог менторов** с фильтрами и поиском
- 📅 **Бронирование консультаций** с выбором времени
- 💳 **Ручная система оплаты** с загрузкой чеков
- ⭐ **Система отзывов** с рейтингами
- 📊 **Админская панель** для управления платформой
- 🕐 **Управление расписанием** для менторов
- 👤 **Профили** студентов и менторов

---

## 🚀 Быстрый старт

### Требования
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### Установка

```bash
# 1. Клонировать репозиторий
git clone <repository-url>
cd masterconnect

# 2. Настроить Backend
cd apps/api
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Создать .env файл в apps/api/
# Скопируйте env.example в apps/api/.env и настройте DATABASE_URL
# ВАЖНО: Используйте абсолютный путь к БД для единообразия:
# DATABASE_URL=sqlite+aiosqlite:///C:/Users/ultua/PycharmProjects/masterconnect/apps/api/test.db

# 4. Запустить Backend (канонический способ, запускать из apps/api)
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Альтернативы (необязательно):
# - PowerShell скрипт: ./start_backend.ps1
# - Python скрипт: python run_server.py
# - Если вы находитесь внутри папки src: python -m uvicorn main:app --reload

# 5. Настроить Frontend (в новом терминале)
cd apps/web
npm install
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env

# 6. Запустить Frontend
npm run dev
```

**Готово!** 🎉
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

📚 **Подробная инструкция**: См. `QUICK_START.md`

---

## 🏗️ Архитектура

### Backend (FastAPI)
```
apps/api/src/
├── core/              # Ядро (config, auth, exceptions)
├── db/                # База данных
├── modules/           # Бизнес-модули
│   ├── admin/        # Админская панель
│   ├── auth/         # Аутентификация
│   ├── availability/ # Расписание
│   ├── bookings/     # Бронирования
│   ├── mentors/      # Менторы
│   ├── payments/     # Оплата
│   ├── reviews/      # Отзывы
│   └── users/        # Пользователи
└── main.py           # Точка входа
```

### Frontend (React + TypeScript)
```
apps/web/src/
├── app/              # Конфигурация
├── pages/            # Страницы
│   ├── admin/       # Админ-панель
│   ├── auth/        # Авторизация
│   ├── mentor/      # Страницы ментора
│   ├── mentors/     # Каталог менторов
│   ├── public/      # Публичные страницы
│   └── student/     # Страницы студента
└── shared/          # Общие компоненты
    ├── api/         # API клиенты
    ├── components/  # Компоненты
    ├── layouts/     # Layouts
    ├── store/       # State management
    ├── types/       # TypeScript типы
    └── ui/          # UI компоненты
```

---

## 🎨 Технологический стек

### Backend
- **FastAPI** - Современный веб-фреймворк
- **SQLAlchemy 2.0** - ORM для работы с БД
- **PostgreSQL** - Реляционная база данных
- **Pydantic v2** - Валидация данных
- **JWT** - Аутентификация
- **Alembic** - Миграции БД

### Frontend
- **React 18** - UI библиотека
- **TypeScript** - Типизация
- **React Router v6** - Роутинг
- **React Query** - Управление данными
- **Zustand** - State management
- **React Hook Form** - Формы
- **Zod** - Валидация
- **Tailwind CSS** - Стилизация
- **Axios** - HTTP клиент

---

## 📚 Документация

- 📖 **[QUICK_START.md](QUICK_START.md)** - Быстрый старт и установка
- 📊 **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Статус проекта
- 💳 **[PAYMENT_SYSTEM.md](PAYMENT_SYSTEM.md)** - Документация системы оплаты
- 🔍 **[AUDIT_REPORT.md](AUDIT_REPORT.md)** - Отчет о полном аудите

---

## 🔑 Основные функции

### Для студентов
- Поиск и выбор менторов
- Бронирование консультаций
- Загрузка доказательств оплаты
- Управление своими сессиями
- Оставление отзывов
- Редактирование профиля

### Для менторов
- Настройка расписания
- Управление бронированиями
- Просмотр отзывов
- Редактирование профиля
- Добавление образования и опыта

### Для администраторов
- Дашборд с общей статистикой
- Управление пользователями
- Верификация менторов
- Проверка оплат
- Модерация бронирований
- Просмотр аналитики

---

## 🎯 Roadmap

### **v1.1** (Ближайшие 2 недели)
- [ ] Email уведомления
- [ ] Unit тесты (50%+ coverage)
- [ ] Rate limiting
- [ ] Логирование в файлы

### **v1.2** (1 месяц)
- [ ] Google Calendar интеграция
- [ ] Фоновые задачи (Celery)
- [ ] Redis кэширование
- [ ] Система чата

### **v2.0** (2-3 месяца)
- [ ] Видео-консультации
- [ ] Мобильное приложение
- [ ] Push-уведомления
- [ ] ML рекомендации
- [ ] Платежная система (Kaspi, Stripe)

---

## 🤝 Вклад в проект

Проект находится в активной разработке. Если вы хотите внести вклад:

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

---

## 📄 Лицензия

Proprietary - Все права защищены

---

## 📞 Контакты

- **Email**: support@masterconnect.kz
- **Website**: https://masterconnect.kz
- **Telegram**: @masterconnect_support

---

## 🙏 Благодарности

Спасибо всем, кто внес вклад в развитие проекта!

---

**Made with ❤️ by MasterConnect Team**