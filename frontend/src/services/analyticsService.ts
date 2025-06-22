import apiService from './apiService';

export interface DashboardData {
  clients: {
    total: number;
    active: number;
    new_this_month: number;
  };
  contracts: {
    total: number;
    active: number;
    expired: number;
  };
  claims: {
    total: number;
    pending: number;
    approved: number;
    rejected: number;
  };
  revenue: {
    total: number;
    monthly: number;
  };
}

export interface FinanceReport {
  total_premiums: number;
  total_claims: number;
  profit: number;
  period: {
    start: string;
    end: string;
  };
  by_month: Array<{
    month: string;
    premiums: number;
    claims: number;
    profit: number;
  }>;
  by_product: Array<{
    product_name: string;
    premiums: number;
    claims: number;
    count: number;
  }>;
}

export interface ActivityReport {
  total_users: number;
  active_users: number;
  by_role: Array<{
    role: string;
    count: number;
    active: number;
  }>;
  top_agents: Array<{
    agent_name: string;
    contracts_count: number;
    total_premium: number;
  }>;
}

class AnalyticsService {
  async getDashboardData(): Promise<DashboardData> {
    return await apiService.get<DashboardData>('/analytics/dashboard');
  }

  async getFinanceReport(startDate?: string, endDate?: string): Promise<FinanceReport> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    return await apiService.get<FinanceReport>(`/analytics/reports/finance?${params.toString()}`);
  }

  async getActivityReport(startDate?: string, endDate?: string): Promise<ActivityReport> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    return await apiService.get<ActivityReport>(`/analytics/reports/activity?${params.toString()}`);
  }

  async exportReport(type: 'finance' | 'activity', startDate?: string, endDate?: string): Promise<Blob> {
    const params = new URLSearchParams({ format: 'excel' });
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    return await apiService.get<Blob>(`/analytics/reports/${type}/export?${params.toString()}`, {
      responseType: 'blob'
    });
  }
}

export const analyticsService = new AnalyticsService(); 