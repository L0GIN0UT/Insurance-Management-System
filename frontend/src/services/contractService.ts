import ApiService from './apiService';

export interface Contract {
  id: number;
  contract_number: string;
  client_id: number;
  product_id: number;
  agent_id: number;
  premium_amount: number;
  coverage_amount: number;
  start_date: string;
  end_date: string;
  status: string;
  terms_conditions?: string;
  created_at: string;
  updated_at?: string;
}

export interface ContractWithDetails extends Contract {
  client_name?: string;
  product_name?: string;
  agent_name?: string;
}

export interface ContractCreate {
  client_id: number;
  product_id: number;
  premium_amount: number;
  coverage_amount: number;
  start_date: string;
  end_date: string;
  terms_conditions?: string;
}

export interface PremiumCalculationParams {
  product_id: number;
  coverage_amount: number;
  client_age?: number;
  risk_factors?: Record<string, any>;
  duration_months?: number;
}

export interface PremiumCalculationResult {
  base_premium: number;
  risk_multiplier: number;
  final_premium: number;
  monthly_premium: number;
  calculation_details: Record<string, any>;
}

export interface ContractList {
  contracts: ContractWithDetails[];
  total: number;
  skip: number;
  limit: number;
}

class ContractService {
  async getContracts(skip = 0, limit = 100, clientId?: number): Promise<ContractList> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    
    if (clientId) {
      params.append('client_id', clientId.toString());
    }
    
    return ApiService.get<ContractList>(`/contracts/?${params.toString()}`);
  }

  async getContract(contractId: number): Promise<ContractWithDetails> {
    return ApiService.get<ContractWithDetails>(`/contracts/${contractId}/`);
  }

  async calculatePremium(params: PremiumCalculationParams): Promise<PremiumCalculationResult> {
    return ApiService.post<PremiumCalculationResult>('/contracts/calculate/', params);
  }

  async createContract(contractData: ContractCreate): Promise<Contract> {
    return ApiService.post<Contract>('/contracts/', contractData);
  }

  async updateContract(contractId: number, contractData: Partial<ContractCreate>): Promise<Contract> {
    return ApiService.put<Contract>(`/contracts/${contractId}/`, contractData);
  }

  async activateContract(contractId: number): Promise<{ message: string }> {
    return ApiService.post<{ message: string }>(`/contracts/${contractId}/activate/`);
  }
}

export default new ContractService(); 