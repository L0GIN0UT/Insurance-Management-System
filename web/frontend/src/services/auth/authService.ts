import axios from 'axios';

const AUTH_BASE_URL = process.env.REACT_APP_AUTH_URL || 'http://localhost:8001';
const API_BASE_URL = `${AUTH_BASE_URL}/api/v1/auth`;

interface LoginRequest {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface RefreshResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

interface VerifyTokenResponse {
  username: string;
  user_id: number;
  role: string;
  valid: boolean;
}

interface RegisterRequest {
  username: string;
  email: string;
  full_name: string;
  password: string;
  role?: string;
}

class AuthService {
  private getAuthHeader() {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await axios.post(`${API_BASE_URL}/login`, credentials);
    return response.data;
  }

  async register(userData: RegisterRequest): Promise<any> {
    const response = await axios.post(`${API_BASE_URL}/register`, userData);
    return response.data;
  }

  async verifyToken(): Promise<VerifyTokenResponse> {
    const response = await axios.post(
      `${API_BASE_URL}/verify-token`,
      {},
      {
        headers: this.getAuthHeader(),
      }
    );
    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<RefreshResponse> {
    const response = await axios.post(`${API_BASE_URL}/refresh`, {
      refresh_token: refreshToken,
    });
    return response.data;
  }

  async logout(): Promise<void> {
    await axios.post(
      `${API_BASE_URL}/logout`,
      {},
      {
        headers: this.getAuthHeader(),
      }
    );
  }
}

export const authService = new AuthService(); 