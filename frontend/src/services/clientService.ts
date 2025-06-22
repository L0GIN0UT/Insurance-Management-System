import ApiService from './apiService';

export interface Client {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  address?: string;
  date_of_birth?: string;
  identification_number?: string;
  created_at: string;
  updated_at?: string;
  created_by?: number;
}

export interface ClientCreate {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  address?: string;
  date_of_birth?: string;
  identification_number?: string;
}

export interface ClientUpdate {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  address?: string;
  date_of_birth?: string;
  identification_number?: string;
}

export interface ClientList {
  clients: Client[];
  total: number;
  skip: number;
  limit: number;
}

class ClientService {
  async getClients(skip = 0, limit = 100): Promise<ClientList> {
    return ApiService.get<ClientList>(`/clients/?skip=${skip}&limit=${limit}`);
  }

  async getClient(clientId: number): Promise<Client> {
    return ApiService.get<Client>(`/clients/${clientId}/`);
  }

  async createClient(clientData: ClientCreate): Promise<Client> {
    return ApiService.post<Client>('/clients/', clientData);
  }

  async updateClient(clientId: number, clientData: ClientUpdate): Promise<Client> {
    return ApiService.put<Client>(`/clients/${clientId}/`, clientData);
  }

  async deleteClient(clientId: number): Promise<{ message: string }> {
    return ApiService.delete<{ message: string }>(`/clients/${clientId}/`);
  }
}

export default new ClientService(); 