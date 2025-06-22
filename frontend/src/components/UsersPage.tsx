import React, { useState, useEffect } from 'react';
import { userService, User, UserCreate } from '../services/userService';

const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalUsers, setTotalUsers] = useState(0);
  const [activeTab, setActiveTab] = useState<'all' | 'create'>('all');
  
  // Форма создания пользователя
  const [createForm, setCreateForm] = useState<UserCreate>({
    username: '',
    email: '',
    full_name: '',
    password: '',
    role: 'agent'
  });

  const [submitting, setSubmitting] = useState(false);

  // Назначение ролей
  const [roleAssignModal, setRoleAssignModal] = useState<{
    show: boolean;
    user: User | null;
    newRole: string;
  }>({
    show: false,
    user: null,
    newRole: ''
  });
  const [assigningRole, setAssigningRole] = useState(false);

  const roles = [
    { value: 'agent', label: 'Агент' },
    { value: 'adjuster', label: 'Урегулировщик' },
    { value: 'operator', label: 'Оператор' },
    { value: 'manager', label: 'Менеджер' },
    { value: 'admin', label: 'Администратор' }
  ];

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await userService.getUsers(0, 100);
      setUsers(data.users);
      setTotalUsers(data.total);
    } catch (err) {
      setError('Ошибка загрузки пользователей');
      console.error('Ошибка загрузки пользователей:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async () => {
    if (!createForm.username || !createForm.email || !createForm.full_name || !createForm.password) {
      alert('Заполните все обязательные поля');
      return;
    }

    try {
      setSubmitting(true);
      await userService.createUser(createForm);
      alert('Пользователь создан успешно');
      setCreateForm({
        username: '',
        email: '',
        full_name: '',
        password: '',
        role: 'agent'
      });
      setActiveTab('all');
      loadUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка создания пользователя');
    } finally {
      setSubmitting(false);
    }
  };

  const openRoleAssignModal = (user: User) => {
    setRoleAssignModal({
      show: true,
      user: user,
      newRole: user.role
    });
  };

  const closeRoleAssignModal = () => {
    setRoleAssignModal({
      show: false,
      user: null,
      newRole: ''
    });
  };

  const handleAssignRole = async () => {
    if (!roleAssignModal.user || !roleAssignModal.newRole) {
      return;
    }

    if (roleAssignModal.newRole === roleAssignModal.user.role) {
      alert('Пользователь уже имеет эту роль');
      return;
    }

    try {
      setAssigningRole(true);
      await userService.assignRole({
        user_id: roleAssignModal.user.id,
        new_role: roleAssignModal.newRole,
        reason: `Назначение роли ${getRoleDisplayName(roleAssignModal.newRole)} администратором`
      });
      
      alert('Роль успешно назначена!');
      closeRoleAssignModal();
      loadUsers(); // Перезагружаем список пользователей
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка назначения роли');
    } finally {
      setAssigningRole(false);
    }
  };

  const getRoleDisplayName = (role: string) => {
    const roleObj = roles.find(r => r.value === role);
    return roleObj ? roleObj.label : role;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU');
  };

  const renderAllUsers = () => (
    <div className="users-section">
      <div className="section-header">
        <h2>👥 Управление пользователями</h2>
        <button 
          className="btn-primary"
          onClick={() => setActiveTab('create')}
        >
          ➕ Создать пользователя
        </button>
      </div>

      <div className="users-stats">
        <div className="stat-card">
          <h3>Всего пользователей</h3>
          <p className="stat-number">{totalUsers}</p>
        </div>
        <div className="stat-card">
          <h3>Активных</h3>
          <p className="stat-number">{users.filter(u => u.is_active).length}</p>
        </div>
        <div className="stat-card">
          <h3>Администраторов</h3>
          <p className="stat-number">{users.filter(u => u.role === 'admin').length}</p>
        </div>
      </div>

      {loading ? (
        <div className="loading">Загрузка пользователей...</div>
      ) : (
        <div className="table-container">
          <table className="users-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Пользователь</th>
                <th>Email</th>
                <th>Роль</th>
                <th>Статус</th>
                <th>Создан</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td>#{user.id}</td>
                  <td>
                    <div className="user-info">
                      <strong>{user.full_name}</strong>
                      <small>@{user.username}</small>
                    </div>
                  </td>
                  <td>{user.email}</td>
                  <td>
                    <span className={`role-badge role-${user.role}`}>
                      {getRoleDisplayName(user.role)}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge ${user.is_active ? 'status-active' : 'status-inactive'}`}>
                      {user.is_active ? 'Активен' : 'Неактивен'}
                    </span>
                  </td>
                  <td>{formatDate(user.created_at)}</td>
                  <td className="actions">
                    <button 
                      className="btn-edit"
                      onClick={() => openRoleAssignModal(user)}
                    >
                      Назначить роль
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  const renderCreateForm = () => (
    <div className="create-user-section">
      <h2>➕ Создание нового пользователя</h2>
      
      <div className="form-container">
        <div className="form-group">
          <label>Имя пользователя *</label>
          <input
            type="text"
            value={createForm.username}
            onChange={(e) => setCreateForm({ ...createForm, username: e.target.value })}
            placeholder="username"
            required
          />
        </div>

        <div className="form-group">
          <label>Email *</label>
          <input
            type="email"
            value={createForm.email}
            onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
            placeholder="user@example.com"
            required
          />
        </div>

        <div className="form-group">
          <label>Полное имя *</label>
          <input
            type="text"
            value={createForm.full_name}
            onChange={(e) => setCreateForm({ ...createForm, full_name: e.target.value })}
            placeholder="Иванов Иван Иванович"
            required
          />
        </div>

        <div className="form-group">
          <label>Пароль *</label>
          <input
            type="password"
            value={createForm.password}
            onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
            placeholder="Введите пароль"
            required
          />
        </div>

        <div className="form-group">
          <label>Роль</label>
          <select
            value={createForm.role}
            onChange={(e) => setCreateForm({ ...createForm, role: e.target.value })}
          >
            {roles.map(role => (
              <option key={role.value} value={role.value}>
                {role.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-actions">
          <button 
            className="btn-primary"
            onClick={handleCreateUser}
            disabled={submitting}
          >
            {submitting ? 'Создание...' : 'Создать пользователя'}
          </button>
          <button 
            className="btn-secondary"
            onClick={() => setActiveTab('all')}
          >
            Отмена
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Управление пользователями</h1>
        <div className="tab-buttons">
          <button 
            className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => setActiveTab('all')}
          >
            👥 Все пользователи
          </button>
          <button 
            className={`tab-btn ${activeTab === 'create' ? 'active' : ''}`}
            onClick={() => setActiveTab('create')}
          >
            ➕ Создать
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={loadUsers} className="btn-secondary">
            Повторить
          </button>
        </div>
      )}

      {activeTab === 'all' && renderAllUsers()}
      {activeTab === 'create' && renderCreateForm()}

      {/* Модальное окно назначения роли */}
      {roleAssignModal.show && (
        <div className="modal-overlay" onClick={closeRoleAssignModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Назначить роль пользователю</h2>
              <button className="close-button" onClick={closeRoleAssignModal}>
                ×
              </button>
            </div>
            
            <div className="modal-body">
              {roleAssignModal.user && (
                <>
                  <div className="user-info-modal">
                    <p><strong>Пользователь:</strong> {roleAssignModal.user.full_name}</p>
                    <p><strong>Email:</strong> {roleAssignModal.user.email}</p>
                    <p><strong>Текущая роль:</strong> 
                      <span className={`role-badge role-${roleAssignModal.user.role}`}>
                        {getRoleDisplayName(roleAssignModal.user.role)}
                      </span>
                    </p>
                  </div>

                  <div className="form-group">
                    <label>Новая роль:</label>
                    <select
                      value={roleAssignModal.newRole}
                      onChange={(e) => setRoleAssignModal({
                        ...roleAssignModal,
                        newRole: e.target.value
                      })}
                    >
                      {roles.map(role => (
                        <option key={role.value} value={role.value}>
                          {role.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}
            </div>
            
            <div className="modal-footer">
              <button 
                className="btn-primary"
                onClick={handleAssignRole}
                disabled={assigningRole || roleAssignModal.newRole === roleAssignModal.user?.role}
              >
                {assigningRole ? 'Назначение...' : 'Назначить роль'}
              </button>
              <button 
                className="btn-secondary"
                onClick={closeRoleAssignModal}
                disabled={assigningRole}
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UsersPage; 