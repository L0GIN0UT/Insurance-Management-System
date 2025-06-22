import React, { useState, useEffect } from 'react';
import './App.css';

// API Client для связи с auth-service
class APIClient {
  constructor() {
    this.token = localStorage.getItem('auth_token');
    this.baseURL = 'http://localhost:8001'; // Auth service URL
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
      return false;
    }
  }
}

const apiClient = new APIClient();

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loginLoading, setLoginLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [activeSection, setActiveSection] = useState('overview');
  const [isLogin, setIsLogin] = useState(true); // переключатель между входом и регистрацией

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const userData = localStorage.getItem('user_data');
    if (userData && await apiClient.verifyToken()) {
      setUser(JSON.parse(userData));
      setIsAuthenticated(true);
    }
    setLoading(false);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const username = formData.get('username');
    const password = formData.get('password');

    setLoginLoading(true);
    setMessage('');

    try {
      const response = await apiClient.login(username, password);
      setUser(response.user);
      setIsAuthenticated(true);
      setMessage('Успешный вход!');
      setMessageType('success');
    } catch (error) {
      setMessage(error.message || 'Ошибка входа');
      setMessageType('error');
    } finally {
      setLoginLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    const userData = {
      username: formData.get('username'),
      email: formData.get('email'),
      password: formData.get('password'),
      full_name: formData.get('full_name'),
      role: formData.get('role') || 'agent'
    };

    // Проверка совпадения паролей
    const confirmPassword = formData.get('confirm_password');
    if (userData.password !== confirmPassword) {
      setMessage('Пароли не совпадают');
      setMessageType('error');
      return;
    }

    setLoginLoading(true);
    setMessage('');

    try {
      await apiClient.register(userData);
      setMessage('Регистрация успешна! Теперь можете войти.');
      setMessageType('success');
      setIsLogin(true); // переключаем на форму входа
    } catch (error) {
      setMessage(error.message || 'Ошибка регистрации');
      setMessageType('error');
    } finally {
      setLoginLoading(false);
    }
  };

  const handleLogout = async () => {
    await apiClient.logout();
    setIsAuthenticated(false);
    setUser(null);
    setActiveSection('overview');
  };

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  if (!isAuthenticated) {
    return (
      <div className="login-container">
        <div className="login-box">
          <div className="logo">IMS</div>
          <h1>Insurance Management System</h1>
          <p className="subtitle">
            {isLogin ? 'Войдите в систему для продолжения' : 'Создайте новый аккаунт'}
          </p>
          
          <div className="auth-toggle">
            <button 
              className={`toggle-btn ${isLogin ? 'active' : ''}`}
              onClick={() => {setIsLogin(true); setMessage('');}}
            >
              Вход
            </button>
            <button 
              className={`toggle-btn ${!isLogin ? 'active' : ''}`}
              onClick={() => {setIsLogin(false); setMessage('');}}
            >
              Регистрация
            </button>
          </div>
          
          <form onSubmit={isLogin ? handleLogin : handleRegister}>
            <div className="form-group">
              <label htmlFor="username">Имя пользователя:</label>
              <input type="text" name="username" required />
            </div>
            
            {!isLogin && (
              <>
                <div className="form-group">
                  <label htmlFor="full_name">Полное имя:</label>
                  <input type="text" name="full_name" required />
                </div>
                
                <div className="form-group">
                  <label htmlFor="email">Email:</label>
                  <input type="email" name="email" required />
                </div>
                
                <div className="form-group">
                  <label htmlFor="role">Роль:</label>
                  <select name="role" defaultValue="agent">
                    <option value="agent">Страховой агент</option>
                    <option value="adjuster">Урегулировщик убытков</option>
                    <option value="operator">Офис-менеджер</option>
                    <option value="manager">Руководство</option>
                    <option value="admin">Администратор</option>
                  </select>
                </div>
              </>
            )}
            
            <div className="form-group">
              <label htmlFor="password">Пароль:</label>
              <input type="password" name="password" required />
            </div>
            
            {!isLogin && (
              <div className="form-group">
                <label htmlFor="confirm_password">Подтвердите пароль:</label>
                <input type="password" name="confirm_password" required />
              </div>
            )}
            
            <button type="submit" className="btn" disabled={loginLoading}>
              {loginLoading ? (isLogin ? 'Вход...' : 'Регистрация...') : (isLogin ? 'Войти' : 'Зарегистрироваться')}
            </button>
          </form>
          
          {message && (
            <div className={`message ${messageType}`}>
              {message}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="header">
        <div>
          <h1>Insurance Management System</h1>
          <p>Добро пожаловать, {user.full_name || user.username}!</p>
        </div>
        <button onClick={handleLogout} className="logout-btn">
          Выйти
        </button>
      </header>

      <div className="dashboard-cards">
        <div className="dashboard-card" onClick={() => setActiveSection('clients')}>
          <h3>👥 Клиенты</h3>
          <p>Управление базой клиентов</p>
        </div>
        
        <div className="dashboard-card" onClick={() => setActiveSection('contracts')}>
          <h3>📋 Договоры</h3>
          <p>Страховые договоры</p>
        </div>
        
        <div className="dashboard-card" onClick={() => setActiveSection('claims')}>
          <h3>🔍 Страховые случаи</h3>
          <p>Обработка заявлений</p>
        </div>
        
        <div className="dashboard-card" onClick={() => setActiveSection('analytics')}>
          <h3>📊 Аналитика</h3>
          <p>Отчеты и статистика</p>
        </div>
      </div>

      <div className="content">
        <h2>
          {activeSection === 'overview' && 'Обзор системы'}
          {activeSection === 'clients' && 'Клиенты'}
          {activeSection === 'contracts' && 'Договоры'}
          {activeSection === 'claims' && 'Страховые случаи'}
          {activeSection === 'analytics' && 'Аналитика'}
        </h2>
        
        {activeSection === 'overview' && (
          <div>
            <p>Выберите раздел для работы из меню выше.</p>
            <div style={{ marginTop: '1rem' }}>
              <p><strong>Роль:</strong> {user.role}</p>
              <p><strong>Email:</strong> {user.email || 'Не указан'}</p>
            </div>
          </div>
        )}
        
        {activeSection !== 'overview' && (
          <p>Раздел "{activeSection}" в разработке...</p>
        )}
      </div>
    </div>
  );
}

export default App; 