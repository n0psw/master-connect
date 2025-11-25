import { api } from './client'

import type {
  Mentor,
  MentorCard,
  MentorDetail,
  MentorSearchParams,
  MentorListResponse,
  MentorStats,
  PopularLanguages,
  PopularSubjects,
  UniversitySuggestion,
  MentorCreateData,
  MentorUpdateData
} from '@/shared/types/mentors'
import type { AdminMentorCreateData, AdminMentorUpdateData, AdminMentorDetail } from '../types/admin'

export const mentorsApi = {
  // Получение списка менторов
  async getMentors(params: MentorSearchParams = {}): Promise<MentorListResponse> {
    const response = await api.get<MentorListResponse>('/mentors', {
      params: {
        ...params,
        languages: params.languages?.join(','),
        subjects: params.subjects?.join(','),
        countries: params.countries?.join(','),
        search: params.search,
      }
    })
    return response.data
  },

  // Получение конкретного ментора
  async getMentor(mentorId: string): Promise<MentorDetail> {
    const response = await api.get<MentorDetail>(`/mentors/${mentorId}`)
    return response.data
  },

  // Получение популярных языков
  async getPopularLanguages(): Promise<PopularLanguages[]> {
    const response = await api.get<PopularLanguages[]>('/mentors/suggestions/languages')
    return response.data
  },

  // Получение популярных предметов
  async getPopularSubjects(): Promise<PopularSubjects[]> {
    const response = await api.get<PopularSubjects[]>('/mentors/suggestions/subjects')
    return response.data
  },

  // Получение предложений университетов
  async getUniversitySuggestions(query?: string): Promise<UniversitySuggestion[]> {
    const response = await api.get<UniversitySuggestion[]>('/mentors/suggestions/universities', {
      params: { q: query }
    })
    return response.data
  },

  // Получение статистики менторов
  async getMentorStats(): Promise<MentorStats> {
    const response = await api.get<MentorStats>('/mentors/stats/overview')
    return response.data
  },

  // Создание профиля ментора (для текущего пользователя)
  async createMentorProfile(data: MentorCreateData): Promise<Mentor> {
    const response = await api.post<Mentor>('/mentors/me/profile', data)
    return response.data
  },

  // Обновление профиля ментора (для текущего пользователя)
  async updateMentorProfile(data: MentorUpdateData): Promise<Mentor> {
    const response = await api.put<Mentor>('/mentors/me/profile', data)
    return response.data
  },

  // Получение профиля текущего ментора
  async getMyMentorProfile(): Promise<Mentor> {
    const response = await api.get<Mentor>('/mentors/me/profile')
    return response.data
  },

  // === АДМИНСКИЕ МЕТОДЫ ===

  // Создание ментора (только для админов)
  async createMentor(data: AdminMentorCreateData): Promise<AdminMentorDetail> {
    const response = await api.post<AdminMentorDetail>('/mentors/admin', data)
    return response.data
  },

  // Получение ментора (только для админов)
  async getMentorAdmin(mentorId: string): Promise<AdminMentorDetail> {
    const response = await api.get<AdminMentorDetail>(`/mentors/admin/${mentorId}`)
    return response.data
  },

  // Обновление ментора (только для админов)
  async updateMentor(mentorId: string, data: AdminMentorUpdateData): Promise<AdminMentorDetail> {
    const response = await api.put<AdminMentorDetail>(`/mentors/admin/${mentorId}`, data)
    return response.data
  },

  // Удаление ментора (только для админов)
  async deleteMentor(mentorId: string): Promise<void> {
    await api.delete(`/mentors/admin/${mentorId}`)
  },
}