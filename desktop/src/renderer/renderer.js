// Renderer process script for Insurance Management System

const API_BASE_URL = 'http://localhost:8001'; // Auth service URL

class APIClient {
    constructor() {
        this.token = localStorage.getItem('auth_token');
        this.baseURL = API_BASE_URL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        if (this.token) {
            config.headers.Authorization = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

      async login(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await this.request('/auth/login', {
      method: 'POST',
      headers: {},
      body: formData
    });

    if (response.access_token) {
      this.token = response.access_token;
      localStorage.setItem('auth_token', this.token);
      localStorage.setItem('user_data', JSON.stringify(response.user));
    }

    return response;
  }

  async register(userData) {
    const response = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    });

    return response;
  }

    async logout() {
        try {
            await this.request('/auth/logout', { method: 'POST' });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.token = null;
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_data');
        }
    }

    async verifyToken() {
        if (!this.token) return false;
        
        try {
            await this.request('/auth/verify-token', { method: 'POST' });
            return true;
        } catch (error) {
            this.logout();
            return false;
        }
    }
}

class AuthManager {
    constructor() {
        this.apiClient = new APIClient();
        this.currentUser = this.loadUserData();
    }

    loadUserData() {
        const userData = localStorage.getItem('user_data');
        return userData ? JSON.parse(userData) : null;
    }

    async login(username, password) {
        try {
            const response = await this.apiClient.login(username, password);
            this.currentUser = response.user;
            return response;
        } catch (error) {
            throw error;
        }
    }

    async register(userData) {
        try {
            const response = await this.apiClient.register(userData);
            return response;
        } catch (error) {
            throw error;
        }
    }

    async logout() {
        await this.apiClient.logout();
        this.currentUser = null;
    }

    isAuthenticated() {
        return !!this.apiClient.token && !!this.currentUser;
    }

    async checkAuth() {
        if (!this.isAuthenticated()) return false;
        return await this.apiClient.verifyToken();
    }
}

// UI Manager
class UIManager {
    constructor() {
        this.authManager = new AuthManager();
        this.isLogin = true; // переключатель между входом и регистрацией
        this.initializeEventListeners();
        this.checkInitialAuth();
    }

    initializeEventListeners() {
        const authForm = document.getElementById('authForm');
        const loginToggle = document.getElementById('loginToggle');
        const registerToggle = document.getElementById('registerToggle');
        
        if (authForm) {
            authForm.addEventListener('submit', this.handleAuth.bind(this));
        }
        
        if (loginToggle) {
            loginToggle.addEventListener('click', () => this.toggleAuthMode(true));
        }
        
        if (registerToggle) {
            registerToggle.addEventListener('click', () => this.toggleAuthMode(false));
        }
    }

    toggleAuthMode(loginMode) {
        this.isLogin = loginMode;
        
        const loginToggle = document.getElementById('loginToggle');
        const registerToggle = document.getElementById('registerToggle');
        const authSubtitle = document.getElementById('authSubtitle');
        const authBtn = document.getElementById('authBtn');
        const extraFields = document.getElementById('extraFields');
        const confirmPasswordGroup = document.getElementById('confirmPasswordGroup');
        const messageEl = document.getElementById('message');
        
        // Обновляем кнопки переключения
        loginToggle.classList.toggle('active', loginMode);
        registerToggle.classList.toggle('active', !loginMode);
        
        // Обновляем интерфейс
        if (loginMode) {
            authSubtitle.textContent = 'Войдите в систему для продолжения';
            authBtn.textContent = 'Войти';
            extraFields.style.display = 'none';
            confirmPasswordGroup.style.display = 'none';
        } else {
            authSubtitle.textContent = 'Создайте новый аккаунт';
            authBtn.textContent = 'Зарегистрироваться';
            extraFields.style.display = 'block';
            confirmPasswordGroup.style.display = 'block';
        }
        
        // Очищаем сообщения
        messageEl.innerHTML = '';
    }

    async checkInitialAuth() {
        if (await this.authManager.checkAuth()) {
            this.showDashboard();
        }
    }

    async handleAuth(event) {
        event.preventDefault();
        
        const authBtn = document.getElementById('authBtn');
        const messageEl = document.getElementById('message');

        // Show loading state
        authBtn.disabled = true;
        messageEl.innerHTML = '';

        try {
            if (this.isLogin) {
                // Обработка входа
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                authBtn.innerHTML = '<div class="spinner"></div>Вход...';
                await this.authManager.login(username, password);
                this.showMessage('Успешный вход!', 'success');
                
                setTimeout(() => {
                    this.showDashboard();
                }, 1000);
                
            } else {
                // Обработка регистрации
                const userData = {
                    username: document.getElementById('username').value,
                    email: document.getElementById('email').value,
                    password: document.getElementById('password').value,
                    full_name: document.getElementById('fullName').value,
                    role: document.getElementById('role').value
                };
                
                // Проверка совпадения паролей
                const confirmPassword = document.getElementById('confirmPassword').value;
                if (userData.password !== confirmPassword) {
                    throw new Error('Пароли не совпадают');
                }
                
                authBtn.innerHTML = '<div class="spinner"></div>Регистрация...';
                await this.authManager.register(userData);
                this.showMessage('Регистрация успешна! Теперь можете войти.', 'success');
                
                setTimeout(() => {
                    this.toggleAuthMode(true); // переключаем на форму входа
                }, 2000);
            }

        } catch (error) {
            this.showMessage(error.message || (this.isLogin ? 'Ошибка входа' : 'Ошибка регистрации'), 'error');
        } finally {
            authBtn.disabled = false;
            authBtn.innerHTML = this.isLogin ? 'Войти' : 'Зарегистрироваться';
        }
    }

    showMessage(text, type = 'error') {
        const messageEl = document.getElementById('message');
        messageEl.innerHTML = `<div class="${type}">${text}</div>`;
    }

    showDashboard() {
        const user = this.authManager.currentUser;
        
        document.body.innerHTML = `
            <div style="padding: 2rem; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                <header style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #eee;">
                    <div>
                        <h1 style="color: #333; margin: 0;">Insurance Management System</h1>
                        <p style="color: #666; margin: 0.5rem 0 0 0;">Добро пожаловать, ${user.full_name || user.username}!</p>
                    </div>
                    <button onclick="uiManager.logout()" style="padding: 0.5rem 1rem; background: #e74c3c; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Выйти
                    </button>
                </header>

                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                    <div class="dashboard-card" onclick="this.showClients()">
                        <h3>👥 Клиенты</h3>
                        <p>Управление базой клиентов</p>
                    </div>
                    
                    <div class="dashboard-card" onclick="this.showContracts()">
                        <h3>📋 Договоры</h3>
                        <p>Страховые договоры</p>
                    </div>
                    
                    <div class="dashboard-card" onclick="this.showClaims()">
                        <h3>🔍 Страховые случаи</h3>
                        <p>Обработка заявлений</p>
                    </div>
                    
                    <div class="dashboard-card" onclick="this.showAnalytics()">
                        <h3>📊 Аналитика</h3>
                        <p>Отчеты и статистика</p>
                    </div>
                </div>

                <div id="content" style="background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2>Обзор системы</h2>
                    <p>Выберите раздел для работы из меню выше.</p>
                    <div style="margin-top: 1rem;">
                        <p><strong>Роль:</strong> ${user.role}</p>
                        <p><strong>Email:</strong> ${user.email || 'Не указан'}</p>
                    </div>
                </div>
            </div>

            <style>
                .dashboard-card {
                    background: white;
                    padding: 1.5rem;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    cursor: pointer;
                    transition: transform 0.2s, box-shadow 0.2s;
                    text-align: center;
                }
                
                .dashboard-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                }
                
                .dashboard-card h3 {
                    margin: 0 0 0.5rem 0;
                    color: #333;
                    font-size: 1.2rem;
                }
                
                .dashboard-card p {
                    margin: 0;
                    color: #666;
                    font-size: 0.9rem;
                }
            </style>
        `;
    }

    async logout() {
        await this.authManager.logout();
        location.reload(); // Reload the page to show login form
    }

    showClients() {
        document.getElementById('content').innerHTML = `
            <h2>👥 Управление клиентами</h2>
            <p>Здесь будет интерфейс для работы с клиентами.</p>
            <div style="margin-top: 1rem;">
                <button onclick="alert('Функция в разработке')" style="padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 0.5rem;">
                    Добавить клиента
                </button>
                <button onclick="alert('Функция в разработке')" style="padding: 0.5rem 1rem; background: #2ecc71; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Поиск клиентов
                </button>
            </div>
        `;
    }

    showContracts() {
        document.getElementById('content').innerHTML = `
            <h2>📋 Управление договорами</h2>
            <p>Здесь будет интерфейс для работы с договорами.</p>
            <div style="margin-top: 1rem;">
                <button onclick="alert('Функция в разработке')" style="padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 0.5rem;">
                    Новый договор
                </button>
                <button onclick="alert('Функция в разработке')" style="padding: 0.5rem 1rem; background: #2ecc71; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Список договоров
                </button>
            </div>
        `;
    }

    showClaims() {
        document.getElementById('content').innerHTML = `
            <h2>🔍 Страховые случаи</h2>
            <p>Здесь будет интерфейс для обработки страховых случаев.</p>
            <div style="margin-top: 1rem;">
                <button onclick="alert('Функция в разработке')" style="padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 0.5rem;">
                    Новое заявление
                </button>
                <button onclick="alert('Функция в разработке')" style="padding: 0.5rem 1rem; background: #e67e22; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    На рассмотрении
                </button>
            </div>
        `;
    }

    showAnalytics() {
        document.getElementById('content').innerHTML = `
            <h2>📊 Аналитика и отчеты</h2>
            <p>Здесь будет интерфейс для просмотра аналитики.</p>
            <div style="margin-top: 1rem;">
                <button onclick="alert('Функция в разработке')" style="padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 0.5rem;">
                    Отчет по продажам
                </button>
                <button onclick="alert('Функция в разработке')" style="padding: 0.5rem 1rem; background: #9b59b6; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Статистика
                </button>
            </div>
        `;
    }
}

// Initialize when DOM is loaded
let uiManager;
document.addEventListener('DOMContentLoaded', () => {
    uiManager = new UIManager();
});

// Make functions available globally for onclick handlers
window.uiManager = uiManager; 