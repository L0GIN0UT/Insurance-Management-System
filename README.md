# Insurance Management System

Автоматизированная информационная система для страховой компании.

## Описание проекта

Система для автоматизации работы страховой компании, включает:

- Учёт клиентов и договоров
- Оформление страховых случаев  
- Аналитика и отчётность
- Разграничение ролей пользователей
- REST API и JWT-аутентификация

## Архитектура проекта

Проект построен как монорепозиторий с двумя основными частями:

### `/web` - Веб-приложение
Контейнеризованное приложение с микросервисной архитектурой:

- **PostgreSQL** - База данных
- **Auth-сервис** - Аутентификация и авторизация (FastAPI)
- **Backend** - Основная бизнес-логика (FastAPI)
- **Frontend** - Пользовательский интерфейс (React + TypeScript)

### `/desktop` - Десктоп-приложение
Electron приложение с React UI, синхронизированное с веб-версией.

## Роли пользователей

- **agent** - Страховой агент (оформление, расчёты)
- **adjuster** - Урегулировщик убытков
- **operator** - Офис-менеджер (база, оплата, контроль)
- **manager** - Руководство (аналитика, отчёты)
- **admin** - Администратор (права, учётки, доступ)

## Быстрый старт

### Веб-приложение

1. Перейдите в директорию `web`:
   ```bash
   cd web
   ```

2. Создайте файл `.env` с настройками окружения:
   ```env
   POSTGRES_DB=insurance_db
   POSTGRES_USER=insurance_user
   POSTGRES_PASSWORD=insurance_password_2024
   POSTGRES_PORT=5432
   FRONTEND_PORT=3000
   BACKEND_PORT=8000
   AUTH_SERVICE_PORT=8001
   JWT_SECRET_KEY=your_super_secret_jwt_key_change_in_production
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. Запустите все сервисы:
   ```bash
   docker-compose up -d
   ```

4. Откройте браузер: http://localhost:3000

### Десктоп-приложение

1. Перейдите в директорию `desktop`:
   ```bash
   cd desktop
   ```

2. Установите зависимости:
   ```bash
   npm install
   ```

3. Запустите в режиме разработки:
   ```bash
   npm run dev
   ```

## Структура проекта

```
/
├── web/                         # Веб-приложение
│   ├── docker-compose.yml      # Оркестрация контейнеров
│   ├── .env                     # Переменные окружения
│   ├── frontend/                # React SPA
│   │   ├── src/
│   │   │   ├── components/      # Переиспользуемые компоненты
│   │   │   ├── pages/          # Страницы приложения
│   │   │   ├── services/       # API клиенты
│   │   │   └── hooks/          # React хуки
│   │   └── package.json
│   ├── backend/                # FastAPI приложение
│   │   ├── app/
│   │   │   ├── routers/        # API endpoints
│   │   │   ├── modules/        # Бизнес-логика
│   │   │   ├── functions/      # Вспомогательные функции
│   │   │   ├── utils/          # Утилиты
│   │   │   ├── core/           # Конфигурация
│   │   │   └── db/             # Модели БД
│   │   └── main.py
│   ├── auth-service/           # Сервис аутентификации
│   │   ├── app/
│   │   │   ├── models/         # Модели пользователей
│   │   │   ├── routes/         # Роуты аутентификации
│   │   │   └── services/       # JWT сервисы
│   │   └── main.py
│   └── database/               # Инициализация БД
│       ├── init.sql
│       └── migrations/
└── desktop/                    # Electron приложение
    ├── src/
    │   ├── main/               # Основной процесс Electron
    │   └── renderer/           # React UI
    │       ├── components/
    │       ├── pages/
    │       └── services/
    └── package.json
```

## API Endpoints

### Аутентификация (Port 8001)
- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `POST /api/v1/auth/verify-token` - Проверка токена
- `POST /api/v1/auth/refresh` - Обновление токена
- `POST /api/v1/auth/logout` - Выход

### Основное API (Port 8000)
- `GET/POST /api/v1/clients` - Управление клиентами
- `GET/POST /api/v1/contracts` - Управление договорами
- `GET/POST /api/v1/claims` - Управление страховыми случаями
- `GET /api/v1/analytics` - Аналитика и отчёты

## Технологии

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT (PyJWT)
- Docker & Docker Compose

### Frontend
- React 18
- TypeScript
- Material-UI
- React Query
- React Hook Form
- Recharts (для аналитики)

### Desktop
- Electron
- React (тот же UI что и веб)
- TypeScript
- Webpack

## Безопасность

- JWT токены для аутентификации
- Роли и права доступа
- CORS настройки
- Валидация данных на всех уровнях
- Хэширование паролей (bcrypt)

## Разработка

Для разработки рекомендуется:

1. Запустить веб-версию через Docker Compose
2. Использовать hot-reload в режиме разработки
3. Синхронизировать изменения между веб и десктоп версиями

## Лицензия

MIT License 