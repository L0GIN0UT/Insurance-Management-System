import React from 'react';

interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: string;
}

interface DashboardProps {
  user: User;
  onLogout: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ user, onLogout }) => {
  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="logo">IMS</div>
          <h1>Insurance Management System</h1>
          <div className="user-info">
            <span>Добро пожаловать, {user.full_name}</span>
            <button onClick={onLogout} className="logout-btn">Выйти</button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-content">
          <div className="welcome-card">
            <h2>Добро пожаловать в систему управления страхованием!</h2>
            <p>Ваша роль: <strong>{getRoleDisplayName(user.role)}</strong></p>
            <p>Email: {user.email}</p>
          </div>

          <div className="features-grid">
            <div className="feature-card">
              <h3>📋 Клиенты</h3>
              <p>Управление базой клиентов</p>
              <button className="feature-btn">Открыть</button>
            </div>

            <div className="feature-card">
              <h3>📄 Договоры</h3>
              <p>Просмотр и управление договорами</p>
              <button className="feature-btn">Открыть</button>
            </div>

            <div className="feature-card">
              <h3>🔍 Заявки</h3>
              <p>Обработка страховых заявок</p>
              <button className="feature-btn">Открыть</button>
            </div>

            <div className="feature-card">
              <h3>📊 Аналитика</h3>
              <p>Отчеты и статистика</p>
              <button className="feature-btn">Открыть</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

function getRoleDisplayName(role: string): string {
  const roleNames: { [key: string]: string } = {
    'client': 'Клиент',
    'agent': 'Агент',
    'manager': 'Менеджер',
    'admin': 'Администратор'
  };
  return roleNames[role] || role;
} 