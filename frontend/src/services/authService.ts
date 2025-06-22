const API_BASE_URL = 'http://localhost:8001';

interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export class AuthService {
  private token: string | null;
  private baseURL = API_BASE_URL;

  constructor() {
    this.token = localStorage.getItem('auth_token');
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    if (this.token) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${this.token}`
      };
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  async login(username: string, password: string): Promise<LoginResponse> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await this.request('/auth/login', {
      method: 'POST',
      headers: {},
      body: formData
    });

    if (response.access_token) {
      this.token = response.access_token;
      localStorage.setItem('auth_token', response.access_token);
      localStorage.setItem('user_data', JSON.stringify(response.user));
    }

    return response;
  }

  async register(userData: {
    username: string;
    email: string;
    password: string;
    full_name: string;
    role: string;
  }) {
    const response = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    });

    return response;
  }

  async logout() {
    try {
      if (this.token) {
        await this.request('/auth/logout', { method: 'POST' });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.token = null;
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
    }
  }

  async verifyToken(): Promise<boolean> {
    if (!this.token) return false;
    
    try {
      await this.request('/auth/verify-token', { method: 'POST' });
      return true;
    } catch (error) {
      await this.logout();
      return false;
    }
  }

  getCurrentUser(): User | null {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  }

  isAuthenticated(): boolean {
    return !!this.token && !!this.getCurrentUser();
  }
} 