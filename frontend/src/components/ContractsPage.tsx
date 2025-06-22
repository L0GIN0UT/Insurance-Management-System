import React, { useState, useEffect } from 'react';
import ContractService, { ContractWithDetails, PremiumCalculationParams, PremiumCalculationResult, ContractCreate } from '../services/contractService';
import ClientService, { Client } from '../services/clientService';

const ContractsPage: React.FC = () => {
  const [contracts, setContracts] = useState<ContractWithDetails[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalContracts, setTotalContracts] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [activeTab, setActiveTab] = useState<'list' | 'calculator' | 'create'>('list');
  
  // Calculator state
  const [calculatorParams, setCalculatorParams] = useState<PremiumCalculationParams>({
    product_id: 1,
    coverage_amount: 100000,
    client_age: 30,
    risk_factors: {},
    duration_months: 12
  });
  const [calculationResult, setCalculationResult] = useState<PremiumCalculationResult | null>(null);
  const [calculating, setCalculating] = useState(false);

  // Create contract state
  const [clients, setClients] = useState<Client[]>([]);
  const [contractForm, setContractForm] = useState<ContractCreate>({
    client_id: 0,
    product_id: 1,
    premium_amount: 0,
    coverage_amount: 100000,
    start_date: new Date().toISOString().split('T')[0],
    end_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    terms_conditions: ''
  });
  const [creating, setCreating] = useState(false);

  const pageSize = 10;

  useEffect(() => {
    loadContracts();
    loadClients();
  }, [currentPage]);

  const loadContracts = async () => {
    try {
      setLoading(true);
      const skip = (currentPage - 1) * pageSize;
      const response = await ContractService.getContracts(skip, pageSize);
      setContracts(response.contracts);
      setTotalContracts(response.total);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки договоров');
    } finally {
      setLoading(false);
    }
  };

  const loadClients = async () => {
    try {
      const response = await ClientService.getClients(0, 100);
      setClients(response.clients);
    } catch (err: any) {
      console.error('Ошибка загрузки клиентов:', err);
    }
  };

  const handleActivateContract = async (contractId: number) => {
    if (!confirm('Вы уверены, что хотите активировать этот договор?')) {
      return;
    }

    try {
      await ContractService.activateContract(contractId);
      alert('Договор успешно активирован!');
      loadContracts(); // Перезагружаем список
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка активации договора');
    }
  };

  const handleCalculatePremium = async () => {
    try {
      setCalculating(true);
      const result = await ContractService.calculatePremium(calculatorParams);
      setCalculationResult(result);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка расчёта премии');
    } finally {
      setCalculating(false);
    }
  };

  // Use calculation result to prefill contract form
  const useCalculationForContract = () => {
    if (calculationResult) {
      setContractForm({
        ...contractForm,
        product_id: calculatorParams.product_id,
        coverage_amount: calculatorParams.coverage_amount,
        premium_amount: calculationResult.final_premium
      });
      setActiveTab('create');
    }
  };

  const handleCreateContract = async () => {
    try {
      setCreating(true);
      
      if (!contractForm.client_id) {
        alert('Выберите клиента');
        return;
      }

      await ContractService.createContract(contractForm);
      alert('Договор успешно создан!');
      
      // Reset form
      setContractForm({
        client_id: 0,
        product_id: 1,
        premium_amount: 0,
        coverage_amount: 100000,
        start_date: new Date().toISOString().split('T')[0],
        end_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        terms_conditions: ''
      });
      
      // Reload contracts
      loadContracts();
      setActiveTab('list');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка создания договора');
    } finally {
      setCreating(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB'
    }).format(amount);
  };

  const totalPages = Math.ceil(totalContracts / pageSize);

  const renderCalculator = () => (
    <div className="calculator-section">
      <h2>🧮 Калькулятор страховых премий</h2>
      
      <div className="calculator-form">
        <div className="form-row">
          <div className="form-group">
            <label>Продукт страхования</label>
            <select
              value={calculatorParams.product_id}
              onChange={(e) => setCalculatorParams({
                ...calculatorParams,
                product_id: parseInt(e.target.value)
              })}
            >
              <option value={1}>Автострахование ОСАГО</option>
              <option value={2}>Автострахование КАСКО</option>
              <option value={3}>Страхование недвижимости</option>
              <option value={4}>Медицинское страхование</option>
              <option value={5}>Страхование путешествий</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>Сумма покрытия (₽)</label>
            <input
              type="number"
              value={calculatorParams.coverage_amount}
              onChange={(e) => setCalculatorParams({
                ...calculatorParams,
                coverage_amount: parseFloat(e.target.value) || 0
              })}
              min="1000"
              step="1000"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Возраст клиента</label>
            <input
              type="number"
              value={calculatorParams.client_age || ''}
              onChange={(e) => setCalculatorParams({
                ...calculatorParams,
                client_age: parseInt(e.target.value) || undefined
              })}
              min="18"
              max="100"
            />
          </div>
          
          <div className="form-group">
            <label>Срок (месяцев)</label>
            <input
              type="number"
              value={calculatorParams.duration_months}
              onChange={(e) => setCalculatorParams({
                ...calculatorParams,
                duration_months: parseInt(e.target.value) || 12
              })}
              min="1"
              max="60"
            />
          </div>
        </div>

        <div className="risk-factors">
          <h4>Факторы риска</h4>
          <div className="form-row">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={calculatorParams.risk_factors?.high_risk_area || false}
                onChange={(e) => setCalculatorParams({
                  ...calculatorParams,
                  risk_factors: {
                    ...calculatorParams.risk_factors,
                    high_risk_area: e.target.checked
                  }
                })}
              />
              Высокий риск региона
            </label>
            
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={calculatorParams.risk_factors?.security_systems || false}
                onChange={(e) => setCalculatorParams({
                  ...calculatorParams,
                  risk_factors: {
                    ...calculatorParams.risk_factors,
                    security_systems: e.target.checked
                  }
                })}
              />
              Система безопасности
            </label>
          </div>
          
          <div className="form-group">
            <label>Количество предыдущих страховых случаев</label>
            <input
              type="number"
              value={calculatorParams.risk_factors?.previous_claims || 0}
              onChange={(e) => setCalculatorParams({
                ...calculatorParams,
                risk_factors: {
                  ...calculatorParams.risk_factors,
                  previous_claims: parseInt(e.target.value) || 0
                }
              })}
              min="0"
              max="10"
            />
          </div>
        </div>

        <button 
          className="btn-primary calculate-btn"
          onClick={handleCalculatePremium}
          disabled={calculating}
        >
          {calculating ? 'Расчёт...' : 'Рассчитать премию'}
        </button>
      </div>

      {calculationResult && (
        <div className="calculation-result">
          <h3>📊 Результат расчёта</h3>
          <div className="result-grid">
            <div className="result-item">
              <span className="label">Базовая премия:</span>
              <span className="value">{formatCurrency(calculationResult.base_premium)}</span>
            </div>
            <div className="result-item">
              <span className="label">Коэффициент риска:</span>
              <span className="value">{calculationResult.risk_multiplier}x</span>
            </div>
            <div className="result-item highlight">
              <span className="label">Итоговая премия:</span>
              <span className="value">{formatCurrency(calculationResult.final_premium)}</span>
            </div>
            <div className="result-item">
              <span className="label">Ежемесячный платёж:</span>
              <span className="value">{formatCurrency(calculationResult.monthly_premium)}</span>
            </div>
          </div>
          
          <div className="calculation-details">
            <h4>Детали расчёта:</h4>
            <pre>{JSON.stringify(calculationResult.calculation_details, null, 2)}</pre>
          </div>

          <div className="calculation-actions">
            <button 
              className="btn-success"
              onClick={useCalculationForContract}
            >
              📝 Создать договор с этими данными
            </button>
          </div>
        </div>
      )}
    </div>
  );

  const renderCreateContract = () => (
    <div className="create-contract-section">
      <h2>📝 Создание нового договора</h2>
      
      <div className="contract-form">
        <div className="form-row">
          <div className="form-group">
            <label>Клиент *</label>
            <select
              value={contractForm.client_id}
              onChange={(e) => setContractForm({
                ...contractForm,
                client_id: parseInt(e.target.value)
              })}
              required
            >
              <option value={0}>Выберите клиента</option>
              {clients.map(client => (
                <option key={client.id} value={client.id}>
                  {client.first_name} {client.last_name} ({client.email})
                </option>
              ))}
            </select>
          </div>
          
          <div className="form-group">
            <label>Продукт страхования *</label>
            <select
              value={contractForm.product_id}
              onChange={(e) => setContractForm({
                ...contractForm,
                product_id: parseInt(e.target.value)
              })}
              required
            >
              <option value={1}>Автострахование ОСАГО</option>
              <option value={2}>Автострахование КАСКО</option>
              <option value={3}>Страхование недвижимости</option>
              <option value={4}>Медицинское страхование</option>
              <option value={5}>Страхование путешествий</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Сумма премии (₽) *</label>
            <input
              type="number"
              value={contractForm.premium_amount}
              onChange={(e) => setContractForm({
                ...contractForm,
                premium_amount: parseFloat(e.target.value) || 0
              })}
              min="100"
              step="100"
              required
            />
          </div>
          
          <div className="form-group">
            <label>Сумма покрытия (₽) *</label>
            <input
              type="number"
              value={contractForm.coverage_amount}
              onChange={(e) => setContractForm({
                ...contractForm,
                coverage_amount: parseFloat(e.target.value) || 0
              })}
              min="1000"
              step="1000"
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Дата начала *</label>
            <input
              type="date"
              value={contractForm.start_date}
              onChange={(e) => setContractForm({
                ...contractForm,
                start_date: e.target.value
              })}
              required
            />
          </div>
          
          <div className="form-group">
            <label>Дата окончания *</label>
            <input
              type="date"
              value={contractForm.end_date}
              onChange={(e) => setContractForm({
                ...contractForm,
                end_date: e.target.value
              })}
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label>Условия договора</label>
          <textarea
            value={contractForm.terms_conditions}
            onChange={(e) => setContractForm({
              ...contractForm,
              terms_conditions: e.target.value
            })}
            rows={4}
            placeholder="Укажите особые условия страхования..."
          />
        </div>

        <div className="form-actions">
          <button 
            className="btn-primary"
            onClick={handleCreateContract}
            disabled={creating || !contractForm.client_id}
          >
            {creating ? 'Создание...' : 'Создать договор'}
          </button>
          
          <button 
            className="btn-secondary"
            onClick={() => setActiveTab('calculator')}
          >
            📊 Сначала рассчитать премию
          </button>
        </div>
      </div>
    </div>
  );

  const renderContractsList = () => (
    <div className="contracts-list">
      <h2>📄 Список договоров</h2>
      
      {loading ? (
        <div className="loading">Загрузка договоров...</div>
      ) : (
        <>
          <div className="contracts-stats">
            <div className="stat-card">
              <h3>Всего договоров</h3>
              <p className="stat-number">{totalContracts}</p>
            </div>
          </div>

          <div className="table-container">
            <table className="contracts-table">
              <thead>
                <tr>
                  <th>Номер</th>
                  <th>Клиент</th>
                  <th>Продукт</th>
                  <th>Премия</th>
                  <th>Покрытие</th>
                  <th>Статус</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {contracts.map((contract) => (
                  <tr key={contract.id}>
                    <td>{contract.contract_number}</td>
                    <td>{contract.client_name || '-'}</td>
                    <td>{contract.product_name || '-'}</td>
                    <td>{formatCurrency(contract.premium_amount)}</td>
                    <td>{formatCurrency(contract.coverage_amount)}</td>
                    <td>
                      <span className={`status-badge status-${contract.status}`}>
                        {contract.status}
                      </span>
                    </td>
                    <td className="actions">
                      <button className="btn-edit">Просмотр</button>
                      {contract.status === 'draft' && (
                        <button 
                          className="btn-activate"
                          onClick={() => handleActivateContract(contract.id)}
                        >
                          Активировать
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {contracts.length === 0 && !loading && (
              <div className="empty-state">
                <p>Договоры не найдены</p>
                <button 
                  className="btn-primary"
                  onClick={() => setActiveTab('create')}
                >
                  Создать первый договор
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
        </>
      )}
    </div>
  );

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Управление договорами</h1>
        <div className="tab-buttons">
          <button 
            className={`tab-btn ${activeTab === 'list' ? 'active' : ''}`}
            onClick={() => setActiveTab('list')}
          >
            📄 Просмотр договоров
          </button>
          <button 
            className={`tab-btn ${activeTab === 'calculator' ? 'active' : ''}`}
            onClick={() => setActiveTab('calculator')}
          >
            🧮 Расчёт премии
          </button>
          <button 
            className={`tab-btn ${activeTab === 'create' ? 'active' : ''}`}
            onClick={() => setActiveTab('create')}
          >
            📝 Создать договор
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={loadContracts} className="btn-secondary">
            Повторить
          </button>
        </div>
      )}

      {activeTab === 'list' && renderContractsList()}
      {activeTab === 'calculator' && renderCalculator()}
      {activeTab === 'create' && renderCreateContract()}
    </div>
  );
};

export default ContractsPage; 