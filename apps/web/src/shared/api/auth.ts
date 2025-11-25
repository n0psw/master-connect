import { api } from './client'

import type {
  User,
  AuthResponse,
  TokenResponse,
  LoginRequest,
  RegisterRequest,
  RefreshTokenRequest,
  PasswordResetRequest,
  PasswordResetConfirm,
  PasswordChangeRequest,
} from '@/shared/types/auth'

export const authApi = {
  // Аутентификация
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/login', credentials)
    return response.data
  },

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/register', userData)
    return response.data
  },

  async refreshToken(data: RefreshTokenRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/refresh', data)
    return response.data
  },

  async logout(): Promise<void> {
    // Используем logout-all, так как /auth/logout требует refresh_token в теле
    await api.post('/auth/logout-all')
  },

  async logoutAll(): Promise<void> {
    await api.post('/auth/logout-all')
  },

  // Профиль пользователя
  async getProfile(): Promise<User> {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  // Сброс пароля
  async requestPasswordReset(data: PasswordResetRequest): Promise<void> {
    await api.post('/auth/password-reset/request', data)
  },

  async confirmPasswordReset(data: PasswordResetConfirm): Promise<void> {
    await api.post('/auth/password-reset/confirm', data)
  },

  async changePassword(data: PasswordChangeRequest): Promise<void> {
    await api.post('/auth/password/change', data)
  },

  // Проверка доступности email
  async checkEmailAvailability(email: string): Promise<{ available: boolean }> {
    const response = await api.get<{ available: boolean }>(
      `/auth/check-email?email=${encodeURIComponent(email)}`
    )
    return response.data
  },
}
