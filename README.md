# 🏢 Система управления страхованием

Полнофункциональная система управления страхованием с веб-интерфейсом, REST API и 5 ролями пользователей.

## 📋 Содержание

- [Обзор системы](#обзор-системы)
- [Архитектура](#архитектура)
- [Требования](#требования)
- [Быстрый старт](#быстрый-старт)
- [Подробная инструкция по запуску](#подробная-инструкция-по-запуску)
- [Тестирование](#тестирование)
- [Роли пользователей](#роли-пользователей)
- [API документация](#api-документация)
- [Структура проекта](#структура-проекта)
- [Устранение неполадок](#устранение-неполадок)

## 🎯 Обзор системы

Система управления страхованием предоставляет полный цикл работы со страховыми продуктами:

- **Управление клиентами** - регистрация, редактирование, поиск клиентов
- **Продажа полисов** - создание и активация страховых договоров
- **Обработка заявок** - подача, рассмотрение и урегулирование страховых случаев
- **Аналитика и отчеты** - финансовая аналитика, отчеты по активности
- **Управление пользователями** - система ролей и прав доступа

## 🏗️ Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │  Auth Service   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (FastAPI)     │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 8001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                         │
                              ▼                         ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │  Main Database  │    │  Auth Database  │
                    │  (PostgreSQL)   │    │  (PostgreSQL)   │
                    │  Port: 5432     │    │  Port: 5433     │
                    └─────────────────┘    └─────────────────┘
```

**Компоненты:**
- **Frontend** - React-приложение с современным UI
- **Backend** - FastAPI сервер с бизнес-логикой
- **Auth Service** - Микросервис аутентификации и авторизации
- **Databases** - PostgreSQL для хранения данных

## 💻 Требования

### Обязательные требования:
- **Docker Desktop** (версия 4.0+)
- **Docker Compose** (версия 2.0+)
- **Python 3.9+** (для запуска тестов)
- **Git** (для клонирования репозитория)

### Системные требования:
- **RAM**: минимум 4 ГБ (рекомендуется 8 ГБ)
- **Диск**: минимум 2 ГБ свободного места
- **ОС**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+

## 🚀 Быстрый старт

```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd diplom_gowna

# 2. Перейдите в папку web
cd web

# 3. Запустите систему
docker-compose up -d

# 4. Дождитесь запуска (2-3 минуты)
# Проверьте статус:
docker-compose ps

# 5. Создайте тестовых пользователей
cd ..
python test/01_setup_test_users.py

# 6. Инициализируйте тестовые данные
cd web
docker-compose exec backend python init_sample_data.py

# 7. Откройте браузер: http://localhost:3000
```

## 🐳 Управление Docker контейнерами

### Запуск системы

```bash
# Перейдите в папку web
cd web

# Запуск всех сервисов в фоновом режиме
docker-compose up -d

# Запуск с отображением логов в реальном времени
docker-compose up

# Запуск с пересборкой контейнеров
docker-compose up --build -d
```

### Проверка статуса

```bash
# Проверить статус всех контейнеров
docker-compose ps

# Посмотреть логи всех сервисов
docker-compose logs

# Посмотреть логи конкретного сервиса
docker-compose logs backend
docker-compose logs frontend
docker-compose logs auth-service

# Следить за логами в реальном времени
docker-compose logs -f backend
```

### Управление сервисами

```bash
# Остановить все сервисы
docker-compose down

# Остановить с удалением volumes (УДАЛЯЕТ ВСЕ ДАННЫЕ!)
docker-compose down -v

# Перезапустить конкретный сервис
docker-compose restart backend

# Пересобрать и перезапустить сервис
docker-compose up --build -d backend

# Подключиться к контейнеру
docker-compose exec backend bash
docker-compose exec auth-service bash
```

### Инициализация данных

```bash
# Создать тестовых пользователей (из корневой папки)
cd ..
python test/01_setup_test_users.py

# Создать тестовые данные (из папки web)
cd web
docker-compose exec backend python init_sample_data.py

# Или запустить внутри контейнера
docker-compose exec backend bash
# Внутри контейнера:
python init_sample_data.py
```

## 🖥️ Desktop версия (Electron)

### Требования для Desktop

```bash
# Установите Node.js (версия 18 или выше)
# Windows: Скачайте с https://nodejs.org/
# macOS: brew install node
# Linux: sudo apt install nodejs npm

# Проверьте установку
node --version  # должно быть 18+
npm --version   # должно быть 8+
```

### Установка зависимостей

```bash
# Из корневой папки проекта
cd diplom_gowna

# Установите все зависимости workspace
npm install

# Это установит зависимости для:
# - frontend/ (React приложение)
# - desktop/ (Electron приложение)
```

### Запуск Desktop версии

```bash
# ВАЖНО: Сначала убедитесь что Docker контейнеры запущены!
cd web
docker-compose up -d
cd ..

# Способ 1: Запуск через корневой package.json
npm run dev:desktop

# Способ 2: Запуск из папки desktop
cd desktop
npm run dev

# Способ 3: Ручной запуск (если нужно больше контроля)
# Терминал 1 - запуск frontend dev сервера:
npm run dev:web
# Терминал 2 - запуск Electron:
cd desktop && npm run dev:electron
```

### Сборка Desktop приложения

```bash
# Сборка для текущей платформы
npm run build:desktop

# Или из папки desktop
cd desktop
npm run build

# Результат будет в desktop/release/
```

### Поддерживаемые платформы

- **Windows**: .exe установщик (NSIS)
- **macOS**: .dmg образ
- **Linux**: AppImage

### Архитектура Desktop версии

```
Desktop App Architecture:
┌─────────────────────────────────────┐
│           Electron Main             │
│         (Node.js процесс)           │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│         Electron Renderer           │
│      (Chromium + React App)         │
│                                     │
│  ┌─────────────────────────────┐    │
│  │     Frontend React App      │    │
│  │   (localhost:3000 или       │    │
│  │    собранные файлы)         │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│        Backend Services             │
│     (Docker контейнеры)             │
│   - FastAPI Backend :8000           │
│   - Auth Service :8001              │
│   - PostgreSQL Databases           │
└─────────────────────────────────────┘
```

### Особенности Desktop версии

- **🔒 Безопасность**: Context Isolation включен, Node Integration отключен
- **🚀 Производительность**: Использует тот же React код что и веб-версия
- **📱 Нативность**: Нативные уведомления, меню, горячие клавиши
- **🔄 Автообновления**: Поддержка автоматических обновлений
- **💾 Локальное хранение**: Может кэшировать данные локально

### Устранение проблем Desktop версии

#### Проблема: Desktop не запускается

```bash
# 1. Проверьте что frontend dev сервер запущен
curl http://localhost:3000
# Должен отвечать

# 2. Проверьте что Docker контейнеры работают
cd web
docker-compose ps
# Все должны быть Up

# 3. Переустановите зависимости
rm -rf node_modules frontend/node_modules desktop/node_modules
npm install

# 4. Очистите кэш Electron
# Windows: %APPDATA%\insurance-desktop
# macOS: ~/Library/Application Support/insurance-desktop
# Linux: ~/.config/insurance-desktop
```

#### Проблема: Electron показывает белый экран

```bash
# 1. Откройте Developer Tools в Electron (Ctrl+Shift+I)
# 2. Проверьте консоль на ошибки
# 3. Убедитесь что frontend сервер доступен
curl http://localhost:3000

# 4. Проверьте что backend API отвечает
curl http://localhost:8000/docs
curl http://localhost:8001/health
```

#### Проблема: Ошибки сборки Desktop

```bash
# Очистите все кэши
rm -rf node_modules
rm -rf frontend/node_modules  
rm -rf desktop/node_modules
rm -rf frontend/dist
rm -rf desktop/dist

# Переустановите зависимости
npm install

# Пересоберите frontend
npm run build:web

# Пересоберите desktop
npm run build:desktop
```

## 📖 Подробная инструкция по запуску

### Шаг 1: Подготовка окружения

1. **Установите Docker Desktop**:
   - Windows: Скачайте с [docker.com](https://www.docker.com/products/docker-desktop)
   - macOS: Установите через Homebrew или скачайте с официального сайта
   - Linux: Установите через пакетный менеджер

2. **Проверьте установку**:
   ```bash
   docker --version
   docker-compose --version
   ```

3. **Убедитесь что Docker запущен**:
   ```bash
   docker ps
   ```

### Шаг 2: Клонирование и подготовка проекта

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd diplom_gowna

# Проверьте структуру проекта
ls -la
# Должны видеть папки: web/, frontend/, desktop/, test/
```

### Шаг 3: Запуск системы

```bash
# Перейдите в папку с Docker конфигурацией
cd web

# Запустите все сервисы
docker-compose up -d

# Проверьте что все контейнеры запустились
docker-compose ps
```

**Ожидаемый вывод:**
```
NAME                   IMAGE            STATUS
insurance_auth         web-auth         Up
insurance_backend      web-backend      Up  
insurance_frontend     web-frontend     Up
insurance_main_db      postgres:15      Up
insurance_auth_db      postgres:15      Up
```

### Шаг 4: Инициализация данных

```bash
# Создайте тестовых пользователей (из корневой папки проекта)
cd ..
python test/01_setup_test_users.py

# Вернитесь в web и создайте тестовые данные
cd web
docker-compose exec backend python init_sample_data.py
```

### Шаг 5: Проверка работоспособности

1. **Откройте браузер**: http://localhost:3000
2. **Войдите с тестовыми данными** (см. раздел "Роли пользователей")
3. **Проверьте API**: http://localhost:8000/docs

## ✅ Тестирование

Система включает комплексные тесты для всех ролей пользователей:

```bash
# Запустите все тесты (из папки web)
cd web

# Тест каждой роли отдельно:
python ../test/02_test_agent_role.py      # Агент
python ../test/03_test_adjuster_role.py   # Урегулировщик  
python ../test/04_test_operator_role.py   # Оператор
python ../test/05_test_manager_role.py    # Менеджер
python ../test/06_test_admin_role.py      # Администратор
```

**Ожидаемые результаты**: Все тесты должны показывать 100% успешности.

## 👥 Роли пользователей

### 🔐 Тестовые аккаунты

| Роль | Логин | Пароль | Права доступа |
|------|-------|--------|---------------|
| **Агент** | `test_agent` | `TestAgent123!` | Клиенты, Договоры |
| **Урегулировщик** | `test_adjuster` | `TestAdjuster123!` | Заявки, Решения |
| **Оператор** | `test_operator` | `TestOperator123!` | Заявки, Отправка |
| **Менеджер** | `test_manager` | `TestManager123!` | Аналитика, Отчеты |
| **Администратор** | `test_admin` | `TestAdmin123!` | Полный доступ |

### 📋 Функции по ролям

#### 🏢 Агент
- ✅ Создание и редактирование клиентов
- ✅ Создание страховых договоров
- ✅ Просмотр своих продаж
- ✅ Базовая аналитика по клиентам

#### ⚖️ Урегулировщик  
- ✅ Просмотр поданных заявок
- ✅ Принятие решений по заявкам
- ✅ Одобрение/отклонение выплат
- ✅ Работа с документами

#### 📞 Оператор
- ✅ Первичная обработка заявок
- ✅ Отправка заявок урегулировщику
- ✅ Поиск клиентов и договоров
- ✅ Фильтрация заявок

#### 📊 Менеджер
- ✅ Аналитические дашборды
- ✅ Финансовые отчеты
- ✅ Отчеты по активности
- ✅ Просмотр пользователей
- ✅ Экспорт данных

#### 👑 Администратор
- ✅ Управление пользователями
- ✅ Назначение ролей
- ✅ Аудит системы
- ✅ Полный доступ ко всем функциям

## 📚 API документация

### Основные эндпоинты:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Аутентификация:
```bash
# Получение токена
POST http://localhost:8001/auth/login
Content-Type: application/x-www-form-urlencoded

username=test_agent&password=TestAgent123!
```

### Примеры запросов:
```bash
# Получение списка клиентов
GET http://localhost:8000/api/v1/clients/
Authorization: Bearer <token>

# Создание заявки
POST http://localhost:8000/api/v1/claims/
Authorization: Bearer <token>
Content-Type: application/json

{
  "contract_id": 1,
  "incident_date": "2024-01-15",
  "description": "Описание страхового случая",
  "claim_amount": 50000
}
```

## 📁 Структура проекта

```
diplom_gowna/
├── web/                          # Основные сервисы
│   ├── docker-compose.yml        # Конфигурация Docker
│   ├── backend/                  # FastAPI backend
│   │   ├── app/
│   │   │   ├── routers/          # API эндпоинты
│   │   │   ├── functions/        # Бизнес-логика
│   │   │   ├── db/              # Модели базы данных
│   │   │   └── schemas/         # Pydantic схемы
│   │   ├── init_sample_data.py   # Инициализация данных
│   │   └── requirements.txt      # Python зависимости
│   ├── auth-service/             # Сервис аутентификации
│   └── frontend/                 # React frontend
├── frontend/                     # Standalone frontend
│   ├── src/
│   │   ├── components/          # React компоненты
│   │   └── services/           # API сервисы
│   └── package.json
├── test/                        # Тесты системы
│   ├── 01_setup_test_users.py   # Создание пользователей
│   ├── 02_test_agent_role.py    # Тесты агента
│   ├── 03_test_adjuster_role.py # Тесты урегулировщика
│   ├── 04_test_operator_role.py # Тесты оператора
│   ├── 05_test_manager_role.py  # Тесты менеджера
│   └── 06_test_admin_role.py    # Тесты администратора
└── desktop/                     # Electron приложение
```

## 🔧 Устранение неполадок

### Проблема: Контейнеры не запускаются

```bash
# Проверьте логи
docker-compose logs

# Перезапустите систему
docker-compose down
docker-compose up -d
```

### Проблема: Порты заняты

```bash
# Найдите процессы на портах 3000, 8000, 8001
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :8001

# Остановите процессы или измените порты в docker-compose.yml
```

### Проблема: Ошибки авторизации

```bash
# Пересоздайте пользователей
python test/01_setup_test_users.py

# Проверьте что auth-service работает
curl http://localhost:8001/health
```

### Проблема: База данных недоступна

```bash
# Проверьте статус контейнеров БД
docker-compose ps | grep db

# Перезапустите базы данных
docker-compose restart insurance_main_db insurance_auth_db

# Подождите 30 секунд и повторите инициализацию
docker-compose exec backend python init_sample_data.py
```

### Проблема: Frontend не загружается

```bash
# Проверьте логи frontend
docker-compose logs insurance_frontend

# Пересоберите frontend
docker-compose build frontend
docker-compose up -d frontend
```

## 🆘 Получение помощи

### Полезные команды для диагностики:

```bash
# Статус всех сервисов
docker-compose ps

# Логи всех сервисов
docker-compose logs

# Логи конкретного сервиса
docker-compose logs backend

# Подключение к контейнеру
docker-compose exec backend bash

# Проверка сети
docker network ls
docker network inspect web_insurance_network
```

### Сброс системы:

```bash
# ВНИМАНИЕ: Удаляет все данные!
docker-compose down -v
docker system prune -f
docker-compose up -d

# Пересоздайте данные
python test/01_setup_test_users.py
docker-compose exec backend python init_sample_data.py
```

## 📞 Контакты

При возникновении проблем:
1. Проверьте раздел "Устранение неполадок"
2. Изучите логи контейнеров
3. Убедитесь что все требования выполнены
4. Проверьте что порты свободны

---

## 📋 Краткая справка команд

### 🐳 Docker команды
| Команда | Описание |
|---------|----------|
| `docker-compose up -d` | Запустить все сервисы в фоне |
| `docker-compose down` | Остановить все сервисы |
| `docker-compose ps` | Показать статус контейнеров |
| `docker-compose logs backend` | Показать логи backend |
| `docker-compose exec backend bash` | Подключиться к backend |
| `docker-compose restart backend` | Перезапустить backend |
| `docker-compose up --build -d` | Пересобрать и запустить |

### 🖥️ Desktop команды  
| Команда | Описание |
|---------|----------|
| `npm install` | Установить зависимости |
| `npm run dev:desktop` | Запустить desktop версию |
| `npm run build:desktop` | Собрать desktop приложение |
| `npm run dev:web` | Запустить только frontend |

### 🧪 Тестирование
| Команда | Описание |
|---------|----------|
| `python test/01_setup_test_users.py` | Создать тестовых пользователей |
| `python test/02_test_agent_role.py` | Тест агента |
| `python test/03_test_adjuster_role.py` | Тест урегулировщика |
| `python test/04_test_operator_role.py` | Тест оператора |
| `python test/05_test_manager_role.py` | Тест менеджера |
| `python test/06_test_admin_role.py` | Тест администратора |

### 🌐 Доступ к сервисам
| Сервис | URL | Описание |
|--------|-----|----------|
| Frontend | http://localhost:3000 | Веб-интерфейс |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger документация |
| Auth Service | http://localhost:8001 | Сервис аутентификации |

## 🎉 Готово!

После выполнения всех шагов у вас будет полностью работающая система управления страхованием с веб-интерфейсом по адресу http://localhost:3000

**Удачи в использовании системы!** 🚀 