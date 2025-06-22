# Insurance Management System - Monorepo

Система управления страхованием с единой кодовой базой фронтенда.

## 🏗️ Архитектура Monorepo

```
diplom_gowna/
├── frontend/               # 🎯 Единый React/Vite фронтенд
│   ├── src/
│   │   ├── components/    # Компоненты React
│   │   ├── services/      # API сервисы  
│   │   ├── pages/         # Страницы
│   │   └── hooks/         # React hooks
│   ├── package.json       # Зависимости фронтенда
│   └── vite.config.ts     # Конфигурация Vite
├── desktop/               # 🖥️ Electron приложение
│   ├── src/main/          # Main процесс Electron
│   ├── vite.renderer.ts   # Конфиг для рендера (использует ../frontend)
│   └── package.json       # Electron зависимости
├── web/                   # 🌐 Веб-версия
│   ├── frontend/          # Docker конфиг (собирает ../frontend)
│   ├── backend/           # FastAPI бэкенд
│   └── docker-compose.yml
└── package.json           # Workspace root

```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Установка всех workspace зависимостей
npm install

# Или по отдельности
npm install --workspace=frontend
npm install --workspace=desktop
```

### 2. Development режим

#### Desktop приложение (Electron + Vite)
```bash
npm run dev:desktop
# или из папки desktop
cd desktop && npm run dev
```

#### Web SPA (только фронтенд)
```bash
npm run dev:web
# или
cd frontend && npm run dev
```

#### Полный web stack (с бэкендом)
```bash
cd web && docker-compose up --build
```

## 📦 Сборка

### Desktop
```bash
npm run build:desktop
# Результат: desktop/dist/
```

### Web
```bash
npm run build:web
# Результат: frontend/dist/
```

### Все сразу
```bash
npm run build:all
```

## 🛠️ Технологии

### Frontend (Общий)
- **React 18** + **TypeScript** 
- **Vite** - быстрая сборка
- **CSS3** с современными возможностями
- **Axios** для API запросов
- **React Hook Form** для форм

### Desktop
- **Electron 30** - кроссплатформенный desktop
- **Node.js 18** + **TypeScript**
- Использует единый `frontend/` как renderer процесс

### Web
- **Docker** + **nginx** для продакшена
- **FastAPI** (Python) бэкенд
- **PostgreSQL** база данных

## 🔧 Конфигурация

### Path aliases (@/...)
Настроены одинаково для всех окружений:
```typescript
'@/' → 'frontend/src/'
'@/components' → 'frontend/src/components'
'@/services' → 'frontend/src/services'
```

### Порты
- **Frontend dev**: `http://localhost:3000`
- **Desktop Electron**: использует frontend:3000
- **Web production**: `http://localhost` (nginx)
- **Backend API**: `http://localhost:8001`

## 📁 Структура frontend/

```
frontend/src/
├── App.tsx              # Главный компонент
├── main.tsx             # Точка входа React
├── App.css              # Глобальные стили
├── components/
│   ├── LoginForm.tsx    # Форма входа
│   ├── RegisterForm.tsx # Форма регистрации
│   └── Dashboard.tsx    # Панель управления
├── services/
│   └── authService.ts   # API аутентификации
├── pages/               # Страницы приложения
└── hooks/               # Кастомные хуки
```

## 🐛 Устранение неполадок

### Desktop не запускается
1. Проверьте что frontend dev сервер запущен на порту 3000
2. `npm run dev:web` должен быть запущен первым
3. Electron запустится автоматически через `wait-on`

### Ошибки сборки
```bash
# Очистить кеши
rm -rf node_modules frontend/node_modules desktop/node_modules
npm install

# Очистить dist папки
rm -rf frontend/dist desktop/dist
```

### TypeScript ошибки
- Убедитесь что используете правильные пути импортов (`@/components/...`)
- Перезапустите TypeScript сервер в IDE

## 🔒 Безопасность

### Electron Security
- ✅ Context Isolation включена
- ✅ Node Integration отключена в renderer
- ✅ CSP (Content Security Policy) настроена
- ✅ Preload скрипт для безопасной коммуникации

### Web Security  
- ✅ HTTPS для продакшена
- ✅ CORS правильно настроен
- ✅ JWT токены для аутентификации

## 📊 API Endpoints

### Аутентификация (`/auth`)
- `POST /auth/login` - Вход в систему
- `POST /auth/register` - Регистрация
- `POST /auth/logout` - Выход
- `POST /auth/verify-token` - Проверка токена

### Клиенты (`/clients`)
- `GET /clients` - Список клиентов
- `POST /clients` - Создание клиента
- `PUT /clients/{id}` - Обновление
- `DELETE /clients/{id}` - Удаление

### Договоры (`/contracts`)
- `GET /contracts` - Список договоров
- `POST /contracts` - Создание
- `GET /contracts/{id}` - Детали

### Заявки (`/claims`)
- `GET /claims` - Список заявок
- `POST /claims` - Подача заявки
- `PUT /claims/{id}` - Обновление статуса

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature ветку (`git checkout -b feature/amazing-feature`)
3. Commit изменений (`git commit -m 'Add amazing feature'`)
4. Push в ветку (`git push origin feature/amazing-feature`)
5. Создайте Pull Request

## 📝 Лицензия

MIT License - смотрите [LICENSE](LICENSE) файл.

---

**Система управления страхованием** - современное решение для автоматизации страховых процессов с единой кодовой базой для web и desktop приложений. 