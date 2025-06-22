import apiService from './apiService';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
}

export interface UserCreate {
  username: string;
  email: string;
  full_name: string;
  password: string;
  role: string;
}

export interface UserRoleUpdate {
  role: string;
}

export interface RoleAssignment {
  user_id: number;
  new_role: string;
  reason?: string;
}

export interface UsersList {
  users: User[];
  total: number;
  skip: number;
  limit: number;
}

class UserService {
  async getUsers(skip: number = 0, limit: number = 100): Promise<UsersList> {
    const params = new URLSearchParams({ 
      skip: skip.toString(), 
      limit: limit.toString() 
    });
    return await apiService.get<UsersList>(`/users/?${params.toString()}`);
  }

  async getUser(userId: number): Promise<User> {
    return await apiService.get<User>(`/users/${userId}`);
  }

  async createUser(userData: UserCreate): Promise<User> {
    return await apiService.post<User>('/users/', userData);
  }

  async updateUserRole(userId: number, roleData: UserRoleUpdate): Promise<User> {
    return await apiService.patch<User>(`/users/${userId}/role`, roleData);
  }

  async deleteUser(userId: number): Promise<void> {
    await apiService.delete(`/users/${userId}`);
  }

  async activateUser(userId: number): Promise<User> {
    return await apiService.patch<User>(`/users/${userId}/activate`);
  }

  async deactivateUser(userId: number): Promise<User> {
    return await apiService.patch<User>(`/users/${userId}/deactivate`);
  }

  async assignRole(roleAssignment: RoleAssignment): Promise<{ message: string }> {
    return await apiService.post<{ message: string }>('/users/admin/roles/assign', roleAssignment);
  }
}

export const userService = new UserService(); 