import React, { useState } from 'react';

const OperatorPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'search' | 'submit' | 'stats'>('search');
  const [submitForm, setSubmitForm] = useState({
    contract_id: '',
    incident_date: '',
    description: '',
    claim_amount: '',
    documents: [] as string[],
    priority: 'normal',
    customer_contact: '',
    witnesses: [] as string[]
  });
  const [submitResult, setSubmitResult] = useState<any>(null);
  const [submitLoading, setSubmitLoading] = useState(false);

  const handleSubmitClaim = async () => {
    setSubmitLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/claims/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...submitForm,
          claim_amount: parseFloat(submitForm.claim_amount),
          contract_id: parseInt(submitForm.contract_id)
        })
      });

      if (response.ok) {
        const result = await response.json();
        setSubmitResult(result);
      } else {
        const error = await response.json();
        setSubmitResult({ error: error.detail || 'Ошибка отправки заявки' });
      }
    } catch (error) {
      setSubmitResult({ error: 'Ошибка соединения' });
    }
    setSubmitLoading(false);
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Рабочее место оператора</h1>
        <div className="operator-status">
          <span className="status-indicator active"></span>
          <span>В работе</span>
        </div>
      </div>

      <div className="tab-buttons">
        <button 
          className={`tab-btn ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => setActiveTab('search')}
        >
          🔍 Поиск клиентов
        </button>
        <button 
          className={`tab-btn ${activeTab === 'submit' ? 'active' : ''}`}
          onClick={() => setActiveTab('submit')}
        >
          📝 Отправка заявки
        </button>
        <button 
          className={`tab-btn ${activeTab === 'stats' ? 'active' : ''}`}
          onClick={() => setActiveTab('stats')}
        >
          📊 Статистика
        </button>
      </div>

      {activeTab === 'search' && (
        <div className="search-section">
          <h2>🔍 Поиск клиентов и договоров</h2>
          <div className="search-box">
            <input
              type="text"
              placeholder="Поиск по ФИО, email, телефону..."
              className="search-input"
            />
          </div>
          <div className="no-results">
            <p>Введите запрос для поиска клиентов</p>
          </div>
        </div>
      )}

      {activeTab === 'submit' && (
        <div className="submit-section">
          <h2>📝 Отправка заявки урегулировщику</h2>
          
          <div className="claim-form">
            <div className="form-group">
              <label>ID договора:</label>
              <input
                type="number"
                value={submitForm.contract_id}
                onChange={(e) => setSubmitForm({...submitForm, contract_id: e.target.value})}
                placeholder="Введите ID договора"
              />
            </div>

            <div className="form-group">
              <label>Дата происшествия:</label>
              <input
                type="date"
                value={submitForm.incident_date}
                onChange={(e) => setSubmitForm({...submitForm, incident_date: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label>Описание происшествия:</label>
              <textarea
                value={submitForm.description}
                onChange={(e) => setSubmitForm({...submitForm, description: e.target.value})}
                placeholder="Подробное описание происшествия (минимум 20 символов)"
                rows={4}
              />
              <small className={submitForm.description.length >= 20 ? 'text-success' : 'text-warning'}>
                {submitForm.description.length}/20+ символов
              </small>
            </div>

            <div className="form-group">
              <label>Сумма ущерба:</label>
              <input
                type="number"
                value={submitForm.claim_amount}
                onChange={(e) => setSubmitForm({...submitForm, claim_amount: e.target.value})}
                placeholder="Сумма в рублях"
              />
            </div>

            <div className="form-group">
              <label>Приоритет:</label>
              <select
                value={submitForm.priority}
                onChange={(e) => setSubmitForm({...submitForm, priority: e.target.value})}
              >
                <option value="low">Низкий</option>
                <option value="normal">Обычный</option>
                <option value="high">Высокий</option>
                <option value="urgent">Срочный</option>
              </select>
            </div>

            <div className="form-group">
              <label>Контакт клиента:</label>
              <input
                type="text"
                value={submitForm.customer_contact}
                onChange={(e) => setSubmitForm({...submitForm, customer_contact: e.target.value})}
                placeholder="Телефон или email для связи"
              />
            </div>

            <div className="form-actions">
              <button 
                onClick={handleSubmitClaim}
                disabled={submitLoading}
                className="submit-btn"
              >
                {submitLoading ? 'Отправка...' : 'Отправить заявку'}
              </button>
            </div>
          </div>

          {submitResult && (
            <div className="submit-result">
              {submitResult.error ? (
                <div className="error-result">
                  <h3>❌ Ошибка отправки</h3>
                  <p>{submitResult.error}</p>
                </div>
              ) : (
                <div className="success-result">
                  <h3>✅ Заявка успешно отправлена</h3>
                  <div className="result-details">
                    <p><strong>Номер заявки:</strong> {submitResult.claim_number}</p>
                    <p><strong>Статус:</strong> {submitResult.status}</p>
                    <p><strong>Время обработки:</strong> {submitResult.estimated_processing_time}</p>
                    <p><strong>Урегулировщик назначен:</strong> {submitResult.adjuster_assigned ? 'Да' : 'Нет'}</p>
                    
                    <div className="validation-checklist">
                      <h4>Чек-лист валидации:</h4>
                      {Object.entries(submitResult.validation_checklist).map(([key, value]) => (
                        <div key={key} className={`checklist-item ${value ? 'valid' : 'invalid'}`}>
                          {value ? '✅' : '❌'} {key}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'stats' && (
        <div className="stats-section">
          <h2>📊 Статистика работы</h2>
          <div className="operator-stats">
            <div className="stat-card">
              <h3>Сегодня</h3>
              <div className="stat-details">
                <p>Обработано обращений: <strong>12</strong></p>
                <p>Создано заявок: <strong>8</strong></p>
                <p>Консультаций: <strong>15</strong></p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OperatorPage; 