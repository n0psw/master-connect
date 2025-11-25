import { api } from './client'

export interface UserSearchParams {
  page?: number
  page_size?: number
  role?: string
  search?: string
  is_active?: boolean
}

export interface UserActivationPayload {
  is_active: boolean
}

export const usersApi = {
  async list(params: UserSearchParams = {}) {
    const response = await api.get('/users', { params })
    return response.data
  },

  async create(payload: any) {
    const response = await api.post('/users', payload)
    return response.data
  },

  async getById(userId: string) {
    const response = await api.get(`/users/${userId}`)
    return response.data
  },

  async update(userId: string, payload: any) {
    const response = await api.put(`/users/${userId}`, payload)
    return response.data
  },

  async setActivation(userId: string, payload: UserActivationPayload) {
    const response = await api.patch(`/users/${userId}/activation`, payload)
    return response.data
  },

  async statsOverview() {
    const response = await api.get('/users/stats/overview')
    return response.data
  },
}

