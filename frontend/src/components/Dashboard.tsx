import React, { useState } from 'react';
import ClientsPage from './ClientsPage';
import ContractsPage from './ContractsPage';
import ClaimsPage from './ClaimsPage';
import AnalyticsPage from './AnalyticsPage';
import UsersPage from './UsersPage';
import OperatorPage from './OperatorPage';

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

type MenuItem = {
  id: string;
  title: string;
  icon: string;
  description: string;
  roles: string[];
};

const menuItems: MenuItem[] = [
  {
    id: 'clients',
    title: 'Клиенты',
    icon: '👥',
    description: 'Управление базой клиентов',
    roles: ['agent', 'operator', 'admin']
  },
  {
    id: 'contracts',
    title: 'Договоры',
    icon: '📄',
    description: 'Оформление и управление договорами',
    roles: ['agent', 'operator']
  },
  {
    id: 'claims',
    title: 'Страховые случаи',
    icon: '🔍',
    description: 'Урегулирование страховых случаев',
    roles: ['adjuster']
  },
  {
    id: 'analytics',
    title: 'Аналитика',
    icon: '📊',
    description: 'Отчёты и статистика',
    roles: ['manager', 'admin']
  },
  {
    id: 'users',
    title: 'Пользователи',
    icon: '👤',
    description: 'Управление пользователями и ролями',
    roles: ['admin']
  },
  {
    id: 'operator',
    title: 'Рабочее место',
    icon: '💼',
    description: 'Обработка обращений и заявок',
    roles: ['operator']
  }
];

export const Dashboard: React.FC<DashboardProps> = ({ user, onLogout }) => {
  const [activeSection, setActiveSection] = useState<string | null>(null);

  const availableMenuItems = menuItems.filter(item => 
    item.roles.includes(user.role)
  );

  const handleMenuClick = (sectionId: string) => {
    setActiveSection(activeSection === sectionId ? null : sectionId);
  };

  const renderSection = () => {
    switch (activeSection) {
      case 'clients':
        return <ClientsPage />;
      case 'contracts':
        return <ContractsPage />;
      case 'claims':
        return <ClaimsPage />;
      case 'analytics':
        return <AnalyticsPage />;
      case 'users':
        return <UsersPage />;
      case 'operator':
        return <OperatorPage />;
      default:
        return null;
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="logo">IMS</div>
          <h1>Insurance Management System</h1>
          <div className="user-info">
            <span>Добро пожаловать, {user.full_name}</span>
            <span className="role-badge">{getRoleDisplayName(user.role)}</span>
            <button onClick={onLogout} className="logout-btn">Выйти</button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-content">
          {activeSection ? (
            <div className="section-content">
              <button 
                onClick={() => setActiveSection(null)} 
                className="back-btn"
              >
                ← Назад к главной
              </button>
              {renderSection()}
            </div>
          ) : (
            <>
          <div className="welcome-card">
            <h2>Добро пожаловать в систему управления страхованием!</h2>
            <p>Ваша роль: <strong>{getRoleDisplayName(user.role)}</strong></p>
            <p>Email: {user.email}</p>
                <div className="role-permissions">
                  <h4>Доступные функции:</h4>
                  <ul>
                    {getRolePermissions(user.role).map((permission, index) => (
                      <li key={index}>{permission}</li>
                    ))}
                  </ul>
                </div>
          </div>

          <div className="features-grid">
                {availableMenuItems.map((item) => (
                  <div 
                    key={item.id} 
                    className="feature-card"
                    onClick={() => handleMenuClick(item.id)}
                  >
                    <div className="feature-icon">{item.icon}</div>
                    <h3>{item.title}</h3>
                    <p>{item.description}</p>
              <button className="feature-btn">Открыть</button>
            </div>
                ))}
            </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
};

function getRoleDisplayName(role: string): string {
  const roleNames: { [key: string]: string } = {
    'agent': 'Агент',
    'adjuster': 'Урегулировщик',
    'operator': 'Оператор',
    'manager': 'Менеджер',
    'admin': 'Администратор'
  };
  return roleNames[role] || role;
} 

function getRolePermissions(role: string): string[] {
  const permissions: { [key: string]: string[] } = {
    'agent': [
      'Работа с клиентами',
      'Оформление договоров',
      'Расчёт страховых премий',
      'Создание страховых случаев'
    ],
    'adjuster': [
      'Урегулирование страховых случаев',
      'Принятие решений по выплатам',
      'Просмотр документов по заявкам',
      'Изменение статусов заявок'
    ],
    'operator': [
      'Ведение базы клиентов',
      'Быстрый поиск информации',
      'Регистрация обращений',
      'Создание заявок для урегулировщиков'
    ],
    'manager': [
      'Просмотр отчётов и аналитики',
      'Финансовые отчёты',
      'Контроль активности',
      'Экспорт данных'
    ],
    'admin': [
      'Управление пользователями',
      'Настройка ролей и прав',
      'Полный доступ к системе',
      'Системные настройки'
    ]
  };
  return permissions[role] || [];
} 