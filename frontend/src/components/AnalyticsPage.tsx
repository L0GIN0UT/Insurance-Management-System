import React, { useState, useEffect } from 'react';
import { analyticsService, DashboardData, FinanceReport, ActivityReport } from '../services/analyticsService';

const AnalyticsPage: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [financeReport, setFinanceReport] = useState<FinanceReport | null>(null);
  const [activityReport, setActivityReport] = useState<ActivityReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'finance' | 'activity'>('dashboard');
  const [dateRange, setDateRange] = useState({
    start: new Date(new Date().getFullYear(), new Date().getMonth() - 3, 1).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    loadData();
  }, [activeTab, dateRange]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      if (activeTab === 'dashboard') {
        const data = await analyticsService.getDashboardData();
        setDashboardData(data);
      } else if (activeTab === 'finance') {
        const data = await analyticsService.getFinanceReport(dateRange.start, dateRange.end);
        setFinanceReport(data);
      } else if (activeTab === 'activity') {
        const data = await analyticsService.getActivityReport(dateRange.start, dateRange.end);
        setActivityReport(data);
      }
    } catch (err) {
      setError('Ошибка загрузки данных аналитики');
      console.error('Ошибка аналитики:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB'
    }).format(amount);
  };

  const formatPercent = (value: number, total: number) => {
    return total > 0 ? `${((value / total) * 100).toFixed(1)}%` : '0%';
  };

  const exportReport = async (type: 'finance' | 'activity') => {
    try {
      const blob = await analyticsService.exportReport(type, dateRange.start, dateRange.end);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${type}-report-${dateRange.start}-${dateRange.end}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert('Ошибка экспорта отчета');
    }
  };

  const renderDashboard = () => {
    if (!dashboardData) return null;

    return (
      <div className="dashboard-section">
        <h2>📊 Общий дашборд</h2>
        
        <div className="analytics-kpi-grid">
          <div className="kpi-card">
            <div className="kpi-header">
              <h3>👥 Клиенты</h3>
              <span className="kpi-icon">👥</span>
            </div>
            <div className="kpi-metrics">
              <div className="kpi-main">
                <span className="kpi-number">{dashboardData.clients.total}</span>
                <span className="kpi-label">Всего</span>
              </div>
              <div className="kpi-sub">
                <div className="kpi-subitem">
                  <span className="kpi-subnumber">{dashboardData.clients.active}</span>
                  <span className="kpi-sublabel">Активных</span>
                </div>
                <div className="kpi-subitem">
                  <span className="kpi-subnumber success">{dashboardData.clients.new_this_month}</span>
                  <span className="kpi-sublabel">Новых в месяце</span>
                </div>
              </div>
            </div>
          </div>

          <div className="kpi-card">
            <div className="kpi-header">
              <h3>📄 Договоры</h3>
              <span className="kpi-icon">📄</span>
            </div>
            <div className="kpi-metrics">
              <div className="kpi-main">
                <span className="kpi-number">{dashboardData.contracts.total}</span>
                <span className="kpi-label">Всего</span>
              </div>
              <div className="kpi-sub">
                <div className="kpi-subitem">
                  <span className="kpi-subnumber">{dashboardData.contracts.active}</span>
                  <span className="kpi-sublabel">Активных</span>
                </div>
                <div className="kpi-subitem">
                  <span className="kpi-subnumber warning">{dashboardData.contracts.expired}</span>
                  <span className="kpi-sublabel">Истекших</span>
                </div>
              </div>
            </div>
          </div>

          <div className="kpi-card">
            <div className="kpi-header">
              <h3>🔍 Заявки</h3>
              <span className="kpi-icon">🔍</span>
            </div>
            <div className="kpi-metrics">
              <div className="kpi-main">
                <span className="kpi-number">{dashboardData.claims.total}</span>
                <span className="kpi-label">Всего</span>
              </div>
              <div className="kpi-sub">
                <div className="kpi-subitem">
                  <span className="kpi-subnumber warning">{dashboardData.claims.pending}</span>
                  <span className="kpi-sublabel">Ожидают</span>
                </div>
                <div className="kpi-subitem">
                  <span className="kpi-subnumber success">{dashboardData.claims.approved}</span>
                  <span className="kpi-sublabel">Одобрено</span>
                </div>
              </div>
            </div>
          </div>

          <div className="kpi-card">
            <div className="kpi-header">
              <h3>💰 Выручка</h3>
              <span className="kpi-icon">💰</span>
            </div>
            <div className="kpi-metrics">
              <div className="kpi-main">
                <span className="kpi-number">{formatCurrency(dashboardData.revenue.total)}</span>
                <span className="kpi-label">Общая</span>
              </div>
              <div className="kpi-sub">
                <div className="kpi-subitem">
                  <span className="kpi-subnumber success">{formatCurrency(dashboardData.revenue.monthly)}</span>
                  <span className="kpi-sublabel">За месяц</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="charts-section">
          <div className="chart-card">
            <h3>Распределение заявок по статусам</h3>
            <div className="pie-chart-placeholder">
              <div className="chart-legend">
                <div className="legend-item">
                  <span className="legend-color pending"></span>
                  <span>Ожидают ({dashboardData.claims.pending})</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color approved"></span>
                  <span>Одобрено ({dashboardData.claims.approved})</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color rejected"></span>
                  <span>Отклонено ({dashboardData.claims.rejected})</span>
                </div>
              </div>
            </div>
          </div>

          <div className="chart-card">
            <h3>Активность</h3>
            <div className="bar-chart-placeholder">
              <div className="progress-bars">
                <div className="progress-bar">
                  <label>Активные клиенты</label>
                  <div className="progress">
                    <div 
                      className="progress-fill active"
                      style={{ width: formatPercent(dashboardData.clients.active, dashboardData.clients.total) }}
                    ></div>
                  </div>
                  <span>{formatPercent(dashboardData.clients.active, dashboardData.clients.total)}</span>
                </div>
                <div className="progress-bar">
                  <label>Активные договоры</label>
                  <div className="progress">
                    <div 
                      className="progress-fill contracts"
                      style={{ width: formatPercent(dashboardData.contracts.active, dashboardData.contracts.total) }}
                    ></div>
                  </div>
                  <span>{formatPercent(dashboardData.contracts.active, dashboardData.contracts.total)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderFinanceReport = () => {
    if (!financeReport) return null;

    return (
      <div className="finance-section">
        <div className="section-header">
          <h2>💰 Финансовый отчет</h2>
          <button className="btn-export" onClick={() => exportReport('finance')}>
            📥 Экспорт в Excel
          </button>
        </div>

        <div className="finance-summary">
          <div className="summary-card">
            <h3>Общие показатели</h3>
            <div className="summary-metrics">
              <div className="metric">
                <span className="metric-label">Общие премии:</span>
                <span className="metric-value success">{formatCurrency(financeReport.total_premiums)}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Общие выплаты:</span>
                <span className="metric-value danger">{formatCurrency(financeReport.total_claims)}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Прибыль:</span>
                <span className={`metric-value ${financeReport.profit >= 0 ? 'success' : 'danger'}`}>
                  {formatCurrency(financeReport.profit)}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="finance-tables">
          <div className="table-card">
            <h3>Помесячная динамика</h3>
            <div className="table-container">
              <table className="analytics-table">
                <thead>
                  <tr>
                    <th>Месяц</th>
                    <th>Премии</th>
                    <th>Выплаты</th>
                    <th>Прибыль</th>
                    <th>Рентабельность</th>
                  </tr>
                </thead>
                <tbody>
                  {financeReport.by_month.map((month, index) => (
                    <tr key={index}>
                      <td>{month.month}</td>
                      <td className="amount-cell success">{formatCurrency(month.premiums)}</td>
                      <td className="amount-cell danger">{formatCurrency(month.claims)}</td>
                      <td className={`amount-cell ${month.profit >= 0 ? 'success' : 'danger'}`}>
                        {formatCurrency(month.profit)}
                      </td>
                      <td>
                        {month.premiums > 0 
                          ? `${((month.profit / month.premiums) * 100).toFixed(1)}%`
                          : '0%'
                        }
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="table-card">
            <h3>По страховым продуктам</h3>
            <div className="table-container">
              <table className="analytics-table">
                <thead>
                  <tr>
                    <th>Продукт</th>
                    <th>Количество</th>
                    <th>Премии</th>
                    <th>Выплаты</th>
                    <th>Средняя премия</th>
                  </tr>
                </thead>
                <tbody>
                  {financeReport.by_product.map((product, index) => (
                    <tr key={index}>
                      <td>{product.product_name}</td>
                      <td>{product.count}</td>
                      <td className="amount-cell success">{formatCurrency(product.premiums)}</td>
                      <td className="amount-cell danger">{formatCurrency(product.claims)}</td>
                      <td className="amount-cell">
                        {formatCurrency(product.count > 0 ? product.premiums / product.count : 0)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderActivityReport = () => {
    if (!activityReport) return null;

    return (
      <div className="activity-section">
        <div className="section-header">
          <h2>📈 Отчет активности</h2>
          <button className="btn-export" onClick={() => exportReport('activity')}>
            📥 Экспорт в Excel
          </button>
        </div>

        <div className="activity-summary">
          <div className="summary-card">
            <h3>Пользователи системы</h3>
            <div className="summary-metrics">
              <div className="metric">
                <span className="metric-label">Всего пользователей:</span>
                <span className="metric-value">{activityReport.total_users}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Активных:</span>
                <span className="metric-value success">{activityReport.active_users}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Активность:</span>
                <span className="metric-value">
                  {formatPercent(activityReport.active_users, activityReport.total_users)}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="activity-tables">
          <div className="table-card">
            <h3>Пользователи по ролям</h3>
            <div className="table-container">
              <table className="analytics-table">
                <thead>
                  <tr>
                    <th>Роль</th>
                    <th>Всего</th>
                    <th>Активных</th>
                    <th>% Активности</th>
                  </tr>
                </thead>
                <tbody>
                  {activityReport.by_role.map((role, index) => (
                    <tr key={index}>
                      <td>{role.role}</td>
                      <td>{role.count}</td>
                      <td>{role.active}</td>
                      <td>{formatPercent(role.active, role.count)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="table-card">
            <h3>Топ агентов</h3>
            <div className="table-container">
              <table className="analytics-table">
                <thead>
                  <tr>
                    <th>Агент</th>
                    <th>Договоров</th>
                    <th>Общая премия</th>
                    <th>Средняя премия</th>
                  </tr>
                </thead>
                <tbody>
                  {activityReport.top_agents.map((agent, index) => (
                    <tr key={index}>
                      <td>
                        <span className="rank">#{index + 1}</span>
                        {agent.agent_name}
                      </td>
                      <td>{agent.contracts_count}</td>
                      <td className="amount-cell success">{formatCurrency(agent.total_premium)}</td>
                      <td className="amount-cell">
                        {formatCurrency(
                          agent.contracts_count > 0 
                            ? agent.total_premium / agent.contracts_count 
                            : 0
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Аналитика и отчеты</h1>
        <div className="header-controls">
          <div className="date-range-picker">
            <label>Период:</label>
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
            />
            <span>—</span>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
            />
          </div>
        </div>
      </div>

      <div className="tab-buttons">
        <button 
          className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Дашборд
        </button>
        <button 
          className={`tab-btn ${activeTab === 'finance' ? 'active' : ''}`}
          onClick={() => setActiveTab('finance')}
        >
          💰 Финансы
        </button>
        <button 
          className={`tab-btn ${activeTab === 'activity' ? 'active' : ''}`}
          onClick={() => setActiveTab('activity')}
        >
          📈 Активность
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={loadData} className="btn-secondary">
            Повторить
          </button>
        </div>
      )}

      {loading ? (
        <div className="loading">Загрузка данных аналитики...</div>
      ) : (
        <>
          {activeTab === 'dashboard' && renderDashboard()}
          {activeTab === 'finance' && renderFinanceReport()}
          {activeTab === 'activity' && renderActivityReport()}
        </>
      )}
    </div>
  );
};

export default AnalyticsPage; 