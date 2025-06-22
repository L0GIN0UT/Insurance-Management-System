import React, { useState, useEffect } from 'react';
import ClientService, { Client, ClientCreate, ClientUpdate } from '../services/clientService';
import ClientModal from './ClientModal';

const ClientsPage: React.FC = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalClients, setTotalClients] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [showModal, setShowModal] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | undefined>();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<Client | null>(null);

  const pageSize = 10;

  useEffect(() => {
    loadClients();
  }, [currentPage]);

  const loadClients = async () => {
    try {
      setLoading(true);
      const skip = (currentPage - 1) * pageSize;
      const response = await ClientService.getClients(skip, pageSize);
      setClients(response.clients);
      setTotalClients(response.total);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки клиентов');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateClient = () => {
    setEditingClient(undefined);
    setShowModal(true);
  };

  const handleEditClient = (client: Client) => {
    setEditingClient(client);
    setShowModal(true);
  };

  const handleSaveClient = async (clientData: ClientCreate | ClientUpdate) => {
    try {
      if (editingClient) {
        await ClientService.updateClient(editingClient.id, clientData as ClientUpdate);
      } else {
        await ClientService.createClient(clientData as ClientCreate);
      }
      
      setShowModal(false);
      setEditingClient(undefined);
      await loadClients();
      
      // Show success message
      alert(editingClient ? 'Клиент успешно обновлен!' : 'Клиент успешно создан!');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при сохранении клиента');
    }
  };

  const handleDeleteClient = async (client: Client) => {
    try {
      await ClientService.deleteClient(client.id);
      setShowDeleteConfirm(null);
      await loadClients();
      alert('Клиент успешно удален!');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при удалении клиента');
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('ru-RU');
  };

  const totalPages = Math.ceil(totalClients / pageSize);

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading">Загрузка клиентов...</div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Управление клиентами</h1>
        <button className="btn-primary" onClick={handleCreateClient}>
          + Добавить клиента
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={loadClients} className="btn-secondary">
            Повторить
          </button>
        </div>
      )}

      <div className="clients-stats">
        <div className="stat-card">
          <h3>Всего клиентов</h3>
          <p className="stat-number">{totalClients}</p>
        </div>
      </div>

      <div className="table-container">
        <table className="clients-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>ФИО</th>
              <th>Email</th>
              <th>Телефон</th>
              <th>Дата рождения</th>
              <th>Дата создания</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {clients.map((client) => (
              <tr key={client.id}>
                <td>{client.id}</td>
                <td>{`${client.first_name} ${client.last_name}`}</td>
                <td>{client.email}</td>
                <td>{client.phone || '-'}</td>
                <td>{formatDate(client.date_of_birth || '')}</td>
                <td>{formatDate(client.created_at)}</td>
                <td className="actions">
                  <button 
                    className="btn-edit"
                    onClick={() => handleEditClient(client)}
                  >
                    Редактировать
                  </button>
                  <button 
                    className="btn-delete"
                    onClick={() => setShowDeleteConfirm(client)}
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {clients.length === 0 && !loading && (
          <div className="empty-state">
            <p>Клиенты не найдены</p>
            <button className="btn-primary" onClick={handleCreateClient}>
              Добавить первого клиента
            </button>
          </div>
        )}
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button 
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(currentPage - 1)}
            className="btn-secondary"
          >
            Предыдущая
          </button>
          
          <span className="page-info">
            Страница {currentPage} из {totalPages}
          </span>
          
          <button 
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage(currentPage + 1)}
            className="btn-secondary"
          >
            Следующая
          </button>
        </div>
      )}

      <ClientModal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          setEditingClient(undefined);
        }}
        onSave={handleSaveClient}
        client={editingClient}
        title={editingClient ? 'Редактировать клиента' : 'Добавить клиента'}
      />

      {showDeleteConfirm && (
        <div className="modal-overlay">
          <div className="modal-content confirm-modal">
            <h3>Подтвердите удаление</h3>
            <p>
              Вы уверены, что хотите удалить клиента{' '}
              <strong>{showDeleteConfirm.first_name} {showDeleteConfirm.last_name}</strong>?
            </p>
            <p className="warning">Это действие нельзя отменить.</p>
            <div className="modal-footer">
              <button 
                className="btn-secondary"
                onClick={() => setShowDeleteConfirm(null)}
              >
                Отмена
              </button>
              <button 
                className="btn-danger"
                onClick={() => handleDeleteClient(showDeleteConfirm)}
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClientsPage; 