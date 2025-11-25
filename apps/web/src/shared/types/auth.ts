export type UserRole = 'student' | 'mentor' | 'admin'

export interface User {
  id: string
  email: string
  name: string | null
  role: UserRole
  timezone: string
  locale: string
  phone: string | null
  avatar_url?: string | null
  is_active: boolean
  created_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  name: string
  role: UserRole
  timezone?: string
  locale?: string
  phone?: string
}

export interface AuthTokens {
  access_token: string
  token_type: string
  expires_in: number
  refresh_token?: string
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface AuthResponse {
  user: User
  tokens: TokenPair
}

export interface TokenResponse extends TokenPair {}

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface PasswordResetRequest {
  email: string
}

export interface PasswordResetConfirm {
  token: string
  new_password: string
}

export interface PasswordChangeRequest {
  current_password: string
  new_password: string
}
