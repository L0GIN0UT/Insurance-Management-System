import React, { useState, useEffect } from 'react';
import './App.css';
import { AuthService } from '@/services/authService';
import { LoginForm } from '@/components/LoginForm';
import { RegisterForm } from '@/components/RegisterForm';
import { Dashboard } from '@/components/Dashboard';

interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: string;
}

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [loading, setLoading] = useState(true);

  const authService = new AuthService();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const isValid = await authService.verifyToken();
      if (isValid) {
        const userData = authService.getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (credentials: { username: string; password: string }) => {
    try {
      const response = await authService.login(credentials.username, credentials.password);
      setUser(response.user);
      setIsAuthenticated(true);
    } catch (error) {
      throw error;
    }
  };

  const handleRegister = async (userData: any) => {
    try {
      await authService.register(userData);
      // После успешной регистрации переключаемся на логин
      setAuthMode('login');
    } catch (error) {
      throw error;
    }
  };

  const handleLogout = async () => {
    try {
      await authService.logout();
      setIsAuthenticated(false);
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Загрузка...</p>
      </div>
    );
  }

  if (isAuthenticated && user) {
    return <Dashboard user={user} onLogout={handleLogout} />;
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="logo">IMS</div>
        <h1>Insurance Management System</h1>
        <p className="subtitle">
          {authMode === 'login' 
            ? 'Войдите в систему для продолжения' 
            : 'Создайте новый аккаунт'
          }
        </p>
        
        <div className="auth-toggle">
          <button 
            className={`toggle-btn ${authMode === 'login' ? 'active' : ''}`}
            onClick={() => setAuthMode('login')}
          >
            Вход
          </button>
          <button 
            className={`toggle-btn ${authMode === 'register' ? 'active' : ''}`}
            onClick={() => setAuthMode('register')}
          >
            Регистрация
          </button>
        </div>

        {authMode === 'login' ? (
          <LoginForm onLogin={handleLogin} />
        ) : (
          <RegisterForm onRegister={handleRegister} />
        )}
      </div>
    </div>
  );
};

export default App; 