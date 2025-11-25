import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

import type { ApiError } from '@/shared/types/api'

// Константы
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'
const REQUEST_TIMEOUT = 30000 // 30 seconds

// Создаем экземпляр axios
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Интерсептор для добавления токена авторизации
apiClient.interceptors.request.use(
  (config) => {
    // Получаем токен из localStorage (Zustand persist)
    const authStorage = localStorage.getItem('auth-storage')
    
    if (authStorage) {
      try {
        const { state } = JSON.parse(authStorage)
        const accessToken = state?.tokens?.access_token
        
        if (accessToken) {
          config.headers.Authorization = `Bearer ${accessToken}`
        }
      } catch (error) {
        console.warn('Failed to parse auth storage:', error)
      }
    }
    
    // Добавляем request ID для трейсинга
    // Используем полифилл для crypto.randomUUID для совместимости со старыми браузерами
    const generateUUID = () => {
      if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID()
      }
      // Fallback для старых браузеров
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = Math.random() * 16 | 0
        const v = c === 'x' ? r : (r & 0x3 | 0x8)
        return v.toString(16)
      })
    }
    config.headers['X-Request-ID'] = generateUUID()
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Интерсептор для обработки ошибок и автоматического refresh токена
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // Если получили 401 и это не запрос на refresh
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/refresh')
    ) {
      originalRequest._retry = true
      
      try {
        // Пытаемся обновить токены
        const authStorage = localStorage.getItem('auth-storage')
        
        if (authStorage) {
          const { state } = JSON.parse(authStorage)
          const refreshToken = state?.tokens?.refresh_token
          
          if (refreshToken) {
            const response = await axios.post(
              `${API_BASE_URL}/auth/refresh`,
              { refresh_token: refreshToken }
            )
            
            const newTokens = response.data?.tokens || response.data
            
            // Обновляем токены в localStorage
            const updatedStorage = {
              ...JSON.parse(authStorage),
              state: {
                ...state,
                tokens: newTokens,
              },
            }
            
            localStorage.setItem('auth-storage', JSON.stringify(updatedStorage))
            
            // Повторяем оригинальный запрос с новым токеном
            originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`
            
            return apiClient(originalRequest)
          }
        }
      } catch (refreshError) {
        // Если refresh не удался, очищаем localStorage и перенаправляем на логин
        localStorage.removeItem('auth-storage')
        window.location.href = '/login'
      }
    }
    
    return Promise.reject(transformError(error))
  }
)

// Функция для трансформации ошибок
function transformError(error: any): ApiError {
  if (error.response) {
    // Сервер ответил с кодом ошибки
    const { data, status } = error.response
    
    return {
      detail: data?.detail || data?.message || `HTTP ${status} Error`,
      code: data?.code,
      field: data?.field,
    }
  } else if (error.request) {
    // Запрос был отправлен, но ответ не получен
    return {
      detail: 'Сервер не отвечает. Проверьте подключение к интернету.',
      code: 'NETWORK_ERROR',
    }
  } else {
    // Что-то пошло не так при настройке запроса
    return {
      detail: error.message || 'Произошла неожиданная ошибка',
      code: 'UNKNOWN_ERROR',
    }
  }
}

// Типизированные методы API
export const api = {
  get: <T = any>(url: string, config?: AxiosRequestConfig) =>
    apiClient.get<T>(url, config),
    
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.post<T>(url, data, config),
    
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.put<T>(url, data, config),
    
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.patch<T>(url, data, config),
    
  delete: <T = any>(url: string, config?: AxiosRequestConfig) =>
    apiClient.delete<T>(url, config),
}

export default apiClient
