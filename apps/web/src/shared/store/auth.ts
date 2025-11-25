import { create } from 'zustand'
import { persist } from 'zustand/middleware'

import type { User, AuthTokens } from '@/shared/types/auth'
import { authApi } from '@/shared/api/auth'

interface AuthState {
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  isLoading: boolean
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>
  register: (data: any) => Promise<void>
  logout: () => Promise<void>
  refreshTokens: () => Promise<void>
  setUser: (user: User) => void
  clearAuth: () => void
  initializeAuth: () => Promise<void>
}

function normalizeUserRole(u: User): User {
  // Приводим роль к нижнему регистру для совместимости с backend
  const role = (u.role as unknown as string)?.toLowerCase?.() as any
  return { ...u, role }
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: true,

      // Actions
      login: async (email: string, password: string) => {
        try {
          set({ isLoading: true })
          
          const response = await authApi.login({ email, password })
          const { user, tokens } = response
          
          set({
            user: normalizeUserRole(user),
            tokens,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      register: async (data) => {
        try {
          set({ isLoading: true })
          
          const response = await authApi.register(data)
          const { user, tokens } = response
          
          set({
            user: normalizeUserRole(user),
            tokens,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: async () => {
        try {
          // Попытаемся вызвать logout на сервере
          await authApi.logout()
        } catch (error) {
          // Игнорируем ошибки logout на сервере
          console.warn('Server logout failed:', error)
        } finally {
          // В любом случае очищаем локальное состояние
          get().clearAuth()
        }
      },

      refreshTokens: async () => {
        const { tokens } = get()
        
        if (!tokens?.refresh_token) {
          throw new Error('No refresh token available')
        }

        try {
          const response = await authApi.refreshToken({
            refresh_token: tokens.refresh_token,
          })
          
          const newTokens = response
          
          set({
            tokens: newTokens,
            isAuthenticated: true,
          })
        } catch (error) {
          // Если refresh не удался, очищаем состояние
          get().clearAuth()
          throw error
        }
      },

      setUser: (user: User) => {
        set({ user: normalizeUserRole(user) })
      },

      clearAuth: () => {
        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
          isLoading: false,
        })
      },

      initializeAuth: async () => {
        try {
          const { tokens, user } = get()
          
          if (!tokens || !user) {
            set({ isLoading: false })
            return
          }

          set({ user: normalizeUserRole(user) })

          try {
            const now = Date.now() / 1000
            const tokenParts = tokens.access_token.split('.')
            
            if (tokenParts.length !== 3) {
              throw new Error('Invalid token format')
            }

            const payload = JSON.parse(atob(tokenParts[1]))
            const tokenExp = payload.exp
            
            if (tokenExp > now) {
              set({
                isAuthenticated: true,
                isLoading: false,
              })
            } else {
              try {
                await get().refreshTokens()
                set({ isLoading: false })
              } catch (error) {
                console.warn('Token refresh failed:', error)
                get().clearAuth()
              }
            }
          } catch (error) {
            console.warn('Token validation failed:', error)
            get().clearAuth()
          }
        } catch (error) {
          console.warn('Auth initialization failed:', error)
          set({ isLoading: false })
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
