import { api } from './client'

import type {
  UserProfile,
  UserUpdateData,
  StudentProfile,
  StudentProfileUpdateData,
  UserWithProfile
} from '@/shared/types/profiles'

export const profilesApi = {
  // Основной профиль пользователя
  async getMyProfile(): Promise<UserWithProfile> {
    const response = await api.get<UserWithProfile>('/users/me')
    return response.data
  },

  async updateMyProfile(data: UserUpdateData): Promise<UserWithProfile> {
    const response = await api.put<UserWithProfile>('/users/me', data)
    return response.data
  },

  // Профиль студента
  async getMyStudentProfile(): Promise<StudentProfile> {
    const response = await api.get<StudentProfile>('/users/me/student-profile')
    return response.data
  },

  async updateMyStudentProfile(data: StudentProfileUpdateData): Promise<StudentProfile> {
    const response = await api.put<StudentProfile>('/users/me/student-profile', data)
    return response.data
  },

  async createMyStudentProfile(data: StudentProfileUpdateData): Promise<StudentProfile> {
    const response = await api.post<StudentProfile>('/users/me/student-profile', data)
    return response.data
  },

  // Загрузка аватара
  async uploadAvatar(file: File): Promise<{ avatar_url: string; message: string }> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post<{ avatar_url: string; message: string }>(
      '/users/me/avatar',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },
}








