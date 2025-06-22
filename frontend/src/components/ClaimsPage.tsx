import React, { useState, useEffect } from 'react';

// Типы данных для заявок
interface Claim {
  id: number;
  contract_id: number;
  client_name?: string;
  contract_number?: string;
  incident_date: string;
  description: string;
  claim_amount: number;
  status: 'submitted' | 'under_review' | 'investigating' | 'approved' | 'rejected';
  created_at: string;
  adjuster_id?: number;
  approved_amount?: number;
  rejection_reason?: string;
  documents?: string[];
}

interface ClaimDecision {
  decision: 'approved' | 'rejected' | 'requires_investigation';
  approved_amount?: number;
  rejection_reason?: string;
  notes?: string;
}

interface ClaimList {
  claims: Claim[];
  total: number;
  skip: number;
  limit: number;
}

const ClaimsPage: React.FC = () => {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [pendingClaims, setPendingClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'pending' | 'all' | 'details'>('pending');
  const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null);
  const [totalClaims, setTotalClaims] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  
  // Decision form state
  const [showDecisionForm, setShowDecisionForm] = useState(false);
  const [decisionForm, setDecisionForm] = useState<ClaimDecision>({
    decision: 'approved',
    approved_amount: 0,
    rejection_reason: '',
    notes: ''
  });
  const [submittingDecision, setSubmittingDecision] = useState(false);

  const pageSize = 10;

  useEffect(() => {
    loadClaims();
    if (activeTab === 'pending') {
      loadPendingClaims();
    }
  }, [currentPage, activeTab]);

  const loadClaims = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      const skip = (currentPage - 1) * pageSize;
      
      const response = await fetch(`http://localhost:8000/api/v1/claims/?skip=${skip}&limit=${pageSize}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data: ClaimList = await response.json();
        setClaims(data.claims);
        setTotalClaims(data.total);
      } else {
        setError('Ошибка загрузки заявок');
      }
    } catch (err) {
      setError('Ошибка подключения к серверу');
    } finally {
      setLoading(false);
    }
  };

  const loadPendingClaims = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`http://localhost:8000/api/v1/claims/pending?skip=0&limit=50`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setPendingClaims(data.pending_claims || []);
      }
    } catch (err) {
      console.error('Ошибка загрузки ожидающих заявок:', err);
    }
  };

  const handleClaimClick = async (claimId: number) => {
    try {
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`http://localhost:8000/api/v1/claims/${claimId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const claim = await response.json();
        setSelectedClaim(claim);
        setActiveTab('details');
      }
    } catch (err) {
      setError('Ошибка загрузки детальной информации');
    }
  };

  const handleMakeDecision = async () => {
    if (!selectedClaim) return;

    try {
      setSubmittingDecision(true);
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`http://localhost:8000/api/v1/claims/${selectedClaim.id}/decision`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(decisionForm)
      });

      if (response.ok) {
        alert('Решение принято успешно!');
        setShowDecisionForm(false);
        loadClaims();
        loadPendingClaims();
        setDecisionForm({
          decision: 'approved',
          approved_amount: 0,
          rejection_reason: '',
          notes: ''
        });
      } else {
        const errorData = await response.json();
        alert(errorData.detail || 'Ошибка при принятии решения');
      }
    } catch (err) {
      alert('Ошибка подключения к серверу');
    } finally {
      setSubmittingDecision(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusMap = {
      'submitted': { text: 'Подана', class: 'status-submitted' },
      'under_review': { text: 'На рассмотрении', class: 'status-review' },
      'investigating': { text: 'Расследование', class: 'status-investigating' },
      'approved': { text: 'Одобрена', class: 'status-approved' },
      'rejected': { text: 'Отклонена', class: 'status-rejected' }
    };
    
    const statusInfo = statusMap[status as keyof typeof statusMap] || { text: status, class: 'status-default' };
    
    return (
      <span className={`status-badge ${statusInfo.class}`}>
        {statusInfo.text}
      </span>
    );
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU');
  };

  const renderPendingClaims = () => (
    <div className="pending-claims-section">
      <h2>🔍 Заявки, ожидающие рассмотрения</h2>
      
      <div className="claims-stats">
        <div className="stat-card urgent">
          <h3>Срочные заявки</h3>
          <p className="stat-number">{pendingClaims.filter(c => c.claim_amount > 100000).length}</p>
          <small>Сумма &gt; 100,000 ₽</small>
        </div>
        <div className="stat-card">
          <h3>Всего к рассмотрению</h3>
          <p className="stat-number">{pendingClaims.length}</p>
          <small>Новые заявки</small>
        </div>
        <div className="stat-card">
          <h3>Средняя сумма</h3>
          <p className="stat-number">
            {pendingClaims.length > 0 
              ? formatCurrency(pendingClaims.reduce((sum, c) => sum + c.claim_amount, 0) / pendingClaims.length)
              : '0 ₽'
            }
          </p>
          <small>По ожидающим заявкам</small>
        </div>
      </div>

      {pendingClaims.length === 0 ? (
        <div className="empty-state">
          <p>✅ Нет заявок, ожидающих рассмотрения</p>
        </div>
      ) : (
        <div className="table-container">
          <table className="claims-table">
            <thead>
              <tr>
                <th>№ Заявки</th>
                <th>Клиент</th>
                <th>Договор</th>
                <th>Дата инцидента</th>
                <th>Сумма заявки</th>
                <th>Статус</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {pendingClaims.map((claim) => (
                <tr key={claim.id} className={claim.claim_amount > 100000 ? 'urgent-claim' : ''}>
                  <td>#{claim.id}</td>
                  <td>{claim.client_name || 'Неизвестно'}</td>
                  <td>{claim.contract_number || `#${claim.contract_id}`}</td>
                  <td>{formatDate(claim.incident_date)}</td>
                  <td className="amount-cell">{formatCurrency(claim.claim_amount)}</td>
                  <td>{getStatusBadge(claim.status)}</td>
                  <td className="actions">
                    <button 
                      className="btn-primary btn-sm"
                      onClick={() => handleClaimClick(claim.id)}
                    >
                      Рассмотреть
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

  const renderAllClaims = () => (
    <div className="all-claims-section">
      <h2>📋 Все страховые случаи</h2>
      
      {loading ? (
        <div className="loading">Загрузка заявок...</div>
      ) : (
        <>
          <div className="table-container">
            <table className="claims-table">
              <thead>
                <tr>
                  <th>№ Заявки</th>
                  <th>Клиент</th>
                  <th>Договор</th>
                  <th>Дата инцидента</th>
                  <th>Сумма заявки</th>
                  <th>Статус</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {claims.map((claim) => (
                  <tr key={claim.id}>
                    <td>#{claim.id}</td>
                    <td>{claim.client_name || 'Неизвестно'}</td>
                    <td>{claim.contract_number || `#${claim.contract_id}`}</td>
                    <td>{formatDate(claim.incident_date)}</td>
                    <td className="amount-cell">{formatCurrency(claim.claim_amount)}</td>
                    <td>{getStatusBadge(claim.status)}</td>
                    <td className="actions">
                      <button 
                        className="btn-edit"
                        onClick={() => handleClaimClick(claim.id)}
                      >
                        Подробнее
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {Math.ceil(totalClaims / pageSize) > 1 && (
            <div className="pagination">
              <button 
                disabled={currentPage === 1}
                onClick={() => setCurrentPage(currentPage - 1)}
                className="btn-secondary"
              >
                Предыдущая
              </button>
              
              <span className="page-info">
                Страница {currentPage} из {Math.ceil(totalClaims / pageSize)}
              </span>
              
              <button 
                disabled={currentPage === Math.ceil(totalClaims / pageSize)}
                onClick={() => setCurrentPage(currentPage + 1)}
                className="btn-secondary"
              >
                Следующая
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );

  const renderClaimDetails = () => {
    if (!selectedClaim) return null;

    return (
      <div className="claim-details-section">
        <div className="claim-header">
          <h2>📄 Детали заявки #{selectedClaim.id}</h2>
          <div className="claim-status">
            {getStatusBadge(selectedClaim.status)}
          </div>
        </div>

        <div className="claim-info-grid">
          <div className="info-card">
            <h3>Основная информация</h3>
            <div className="info-row">
              <label>Клиент:</label>
              <span>{selectedClaim.client_name || 'Неизвестно'}</span>
            </div>
            <div className="info-row">
              <label>Договор:</label>
              <span>{selectedClaim.contract_number || `#${selectedClaim.contract_id}`}</span>
            </div>
            <div className="info-row">
              <label>Дата инцидента:</label>
              <span>{formatDate(selectedClaim.incident_date)}</span>
            </div>
            <div className="info-row">
              <label>Дата подачи:</label>
              <span>{formatDate(selectedClaim.created_at)}</span>
            </div>
          </div>

          <div className="info-card">
            <h3>Финансовая информация</h3>
            <div className="info-row">
              <label>Заявленная сумма:</label>
              <span className="amount">{formatCurrency(selectedClaim.claim_amount)}</span>
            </div>
            {selectedClaim.approved_amount && (
              <div className="info-row">
                <label>Одобренная сумма:</label>
                <span className="amount approved">{formatCurrency(selectedClaim.approved_amount)}</span>
              </div>
            )}
            {selectedClaim.rejection_reason && (
              <div className="info-row">
                <label>Причина отказа:</label>
                <span className="rejection-reason">{selectedClaim.rejection_reason}</span>
              </div>
            )}
          </div>
        </div>

        <div className="claim-description">
          <h3>Описание случая</h3>
          <p className="description-text">{selectedClaim.description}</p>
        </div>

        {selectedClaim.documents && selectedClaim.documents.length > 0 && (
          <div className="claim-documents">
            <h3>Документы</h3>
            <div className="documents-list">
              {selectedClaim.documents.map((doc, index) => (
                <div key={index} className="document-item">
                  📎 {doc}
                </div>
              ))}
            </div>
          </div>
        )}

        {(selectedClaim.status === 'submitted' || selectedClaim.status === 'under_review') && (
          <div className="decision-actions">
            <button 
              className="btn-primary"
              onClick={() => setShowDecisionForm(true)}
            >
              📝 Принять решение
            </button>
          </div>
        )}

        {showDecisionForm && (
          <div className="decision-form">
            <h3>Принятие решения по заявке</h3>
            
            <div className="form-group">
              <label>Решение:</label>
              <select
                value={decisionForm.decision}
                onChange={(e) => setDecisionForm({
                  ...decisionForm,
                  decision: e.target.value as any
                })}
              >
                <option value="approved">Одобрить</option>
                <option value="rejected">Отклонить</option>
                <option value="requires_investigation">Требует дополнительного расследования</option>
              </select>
            </div>

            {decisionForm.decision === 'approved' && (
              <div className="form-group">
                <label>Одобренная сумма (₽):</label>
                <input
                  type="number"
                  value={decisionForm.approved_amount || ''}
                  onChange={(e) => setDecisionForm({
                    ...decisionForm,
                    approved_amount: parseFloat(e.target.value) || 0
                  })}
                  max={selectedClaim.claim_amount}
                  min="0"
                  step="100"
                />
              </div>
            )}

            {decisionForm.decision === 'rejected' && (
              <div className="form-group">
                <label>Причина отказа:</label>
                <textarea
                  value={decisionForm.rejection_reason || ''}
                  onChange={(e) => setDecisionForm({
                    ...decisionForm,
                    rejection_reason: e.target.value
                  })}
                  rows={3}
                  placeholder="Укажите причину отказа..."
                />
              </div>
            )}

            <div className="form-group">
              <label>Комментарии:</label>
              <textarea
                value={decisionForm.notes || ''}
                onChange={(e) => setDecisionForm({
                  ...decisionForm,
                  notes: e.target.value
                })}
                rows={3}
                placeholder="Дополнительные комментарии..."
              />
            </div>

            <div className="form-actions">
              <button 
                className="btn-primary"
                onClick={handleMakeDecision}
                disabled={submittingDecision}
              >
                {submittingDecision ? 'Сохранение...' : 'Сохранить решение'}
              </button>
              <button 
                className="btn-secondary"
                onClick={() => setShowDecisionForm(false)}
              >
                Отмена
              </button>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Управление страховыми случаями</h1>
        <div className="tab-buttons">
          <button 
            className={`tab-btn ${activeTab === 'pending' ? 'active' : ''}`}
            onClick={() => setActiveTab('pending')}
          >
            🔍 К рассмотрению ({pendingClaims.length})
          </button>
          <button 
            className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => setActiveTab('all')}
          >
            📋 Все заявки
          </button>
          {selectedClaim && (
            <button 
              className={`tab-btn ${activeTab === 'details' ? 'active' : ''}`}
              onClick={() => setActiveTab('details')}
            >
              📄 Заявка #{selectedClaim.id}
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={loadClaims} className="btn-secondary">
            Повторить
          </button>
        </div>
      )}

      {activeTab === 'pending' && renderPendingClaims()}
      {activeTab === 'all' && renderAllClaims()}
      {activeTab === 'details' && renderClaimDetails()}
    </div>
  );
};

export default ClaimsPage;