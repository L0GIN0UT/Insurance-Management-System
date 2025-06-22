import React, { useState } from 'react';

interface LoginFormProps {
  onLogin: (credentials: { username: string; password: string }) => Promise<void>;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');                                         
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!username || !password) {
      setError('Заполните все поля');
      return;
    }

    setLoading(true);
    try {
      await onLogin({ username, password });
    } catch (error: any) {
      setError(error.message || 'Ошибка входа');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="auth-form">
      <div className="form-group">
        <label htmlFor="username">Имя пользователя или email</label>
        <input
          id="username"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Введите имя пользователя или email"
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="password">Пароль</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Введите пароль"
          disabled={loading}
        />
      </div>

      {error && <div className="error">{error}</div>}

      <button type="submit" className="auth-btn" disabled={loading}>
        {loading ? (
          <>
            <div className="spinner"></div>
            Вход...
          </>
        ) : (
          'Войти'
        )}
      </button>
    </form>
  );
}; 