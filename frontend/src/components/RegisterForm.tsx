import React, { useState } from 'react';

interface RegisterFormProps {
  onRegister: (userData: {
    username: string;
    email: string;
    password: string;
    full_name: string;
    role: string;
  }) => Promise<void>;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onRegister }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    role: 'client'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const validateForm = () => {
    if (!formData.username || !formData.email || !formData.password || !formData.full_name) {
      return 'Заполните все обязательные поля';
    }

    if (formData.password.length < 6) {
      return 'Пароль должен содержать минимум 6 символов';
    }

    if (formData.password !== formData.confirmPassword) {
      return 'Пароли не совпадают';
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      return 'Введите корректный email';
    }

    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    try {
      await onRegister({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        role: formData.role
      });
      setSuccess('Регистрация успешна! Теперь можете войти в систему.');
      setFormData({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        full_name: '',
        role: 'client'
      });
    } catch (error: any) {
      setError(error.message || 'Ошибка регистрации');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="auth-form">
      <div className="form-group">
        <label htmlFor="username">Имя пользователя *</label>
        <input
          id="username"
          name="username"
          type="text"
          value={formData.username}
          onChange={handleChange}
          placeholder="Введите имя пользователя"
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="email">Email *</label>
        <input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          placeholder="Введите email"
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="full_name">Полное имя *</label>
        <input
          id="full_name"
          name="full_name"
          type="text"
          value={formData.full_name}
          onChange={handleChange}
          placeholder="Введите полное имя"
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="role">Роль</label>
        <select
          id="role"
          name="role"
          value={formData.role}
          onChange={handleChange}
          disabled={loading}
        >
          <option value="client">Клиент</option>
          <option value="agent">Агент</option>
          <option value="manager">Менеджер</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="password">Пароль *</label>
        <input
          id="password"
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="Введите пароль (минимум 6 символов)"
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="confirmPassword">Подтвердите пароль *</label>
        <input
          id="confirmPassword"
          name="confirmPassword"
          type="password"
          value={formData.confirmPassword}
          onChange={handleChange}
          placeholder="Подтвердите пароль"
          disabled={loading}
        />
      </div>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <button type="submit" className="auth-btn" disabled={loading}>
        {loading ? (
          <>
            <div className="spinner"></div>
            Регистрация...
          </>
        ) : (
          'Зарегистрироваться'
        )}
      </button>
    </form>
  );
}; 