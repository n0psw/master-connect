import { api } from './client'
import type {
  MentorAvailability,
  WeeklySchedule,
  AvailabilitySettings,
  AvailabilityException,
  UpdateWeeklyScheduleRequest,
  UpdateAvailabilitySettingsRequest,
  CreateAvailabilityExceptionRequest,
} from '@/shared/types/availability'

const transformBackendTimeSlotToFrontend = (backendSlot: any): { start_time: string; end_time: string } => {
  if (backendSlot.start_time && backendSlot.end_time) {
    return { start_time: backendSlot.start_time, end_time: backendSlot.end_time }
  }
  
  if (backendSlot.start && backendSlot.end) {
    let startTime = '00:00'
    let endTime = '00:00'
    
    if (backendSlot.time) {
      startTime = backendSlot.time
    } else {
      const start = typeof backendSlot.start === 'string' ? new Date(backendSlot.start) : backendSlot.start
      if (start instanceof Date) {
        const hours = start.getUTCHours().toString().padStart(2, '0')
        const minutes = start.getUTCMinutes().toString().padStart(2, '0')
        startTime = `${hours}:${minutes}`
      } else if (typeof backendSlot.start === 'string') {
        try {
          const date = new Date(backendSlot.start)
          if (!isNaN(date.getTime())) {
            const hours = date.getUTCHours().toString().padStart(2, '0')
            const minutes = date.getUTCMinutes().toString().padStart(2, '0')
            startTime = `${hours}:${minutes}`
          }
        } catch {
          startTime = '00:00'
        }
      }
    }
    
    const end = typeof backendSlot.end === 'string' ? new Date(backendSlot.end) : backendSlot.end
    if (end instanceof Date) {
      const hours = end.getUTCHours().toString().padStart(2, '0')
      const minutes = end.getUTCMinutes().toString().padStart(2, '0')
      endTime = `${hours}:${minutes}`
    } else if (typeof backendSlot.end === 'string') {
      try {
        const date = new Date(backendSlot.end)
        if (!isNaN(date.getTime())) {
          const hours = date.getUTCHours().toString().padStart(2, '0')
          const minutes = date.getUTCMinutes().toString().padStart(2, '0')
          endTime = `${hours}:${minutes}`
        }
      } catch {
        endTime = '00:00'
      }
    }
    
    return { start_time: startTime, end_time: endTime }
  }
  
  return { start_time: '00:00', end_time: '00:00' }
}

const transformBackendWeeklySchedule = (backendSchedule: any): WeeklySchedule => {
  if (!backendSchedule) {
    return {
      monday: [],
      tuesday: [],
      wednesday: [],
      thursday: [],
      friday: [],
      saturday: [],
      sunday: [],
    }
  }
  
  return {
    monday: backendSchedule.monday || [],
    tuesday: backendSchedule.tuesday || [],
    wednesday: backendSchedule.wednesday || [],
    thursday: backendSchedule.thursday || [],
    friday: backendSchedule.friday || [],
    saturday: backendSchedule.saturday || [],
    sunday: backendSchedule.sunday || [],
  }
}

export const availabilityApi = {
  // Получение полного расписания ментора (self)
  async getMyAvailability(): Promise<MentorAvailability> {
    const response = await api.get<any>('/availability/my/profile')
    const data = response.data
    
    return {
      ...data,
      weekly_schedule: transformBackendWeeklySchedule(data.weekly_schedule),
    }
  },

  // Получение настроек доступности
  async getMyAvailabilitySettings(): Promise<AvailabilitySettings> {
    const response = await api.get<AvailabilitySettings>('/availability/my/profile')
    return response.data
  },

  // Обновление настроек доступности
  async updateSettings(data: AvailabilitySettings): Promise<AvailabilitySettings> {
    const response = await api.put<AvailabilitySettings>('/availability/my/settings', data)
    return response.data
  },

  // Обновление недельного расписания
  async updateSchedule(schedule: WeeklySchedule): Promise<WeeklySchedule> {
    const response = await api.put<any>('/availability/my/schedule', schedule)
    return transformBackendWeeklySchedule(response.data)
  },

  // Получение недельного расписания
  async getWeeklySchedule(): Promise<WeeklySchedule[]> {
    const response = await api.get<WeeklySchedule[]>('/availability/my/profile')
    return response.data
  },

  // Обновление дня в недельном расписании
  async updateWeeklyScheduleDay(dayOfWeek: number, data: UpdateWeeklyScheduleRequest): Promise<WeeklySchedule> {
    const response = await api.put<WeeklySchedule>(`/availability/my/rules`, {
      day_of_week: dayOfWeek,
      ...data,
    })
    return response.data
  },

  // Получение исключений в расписании
  async getAvailabilityExceptions(startDate?: string, endDate?: string): Promise<AvailabilityException[]> {
    const response = await api.get<AvailabilityException[]>('/availability/my/time-off', {
      params: { start_date: startDate, end_date: endDate }
    })
    return response.data as unknown as AvailabilityException[]
  },

  // Создание исключения в расписании
  async createAvailabilityException(data: CreateAvailabilityExceptionRequest): Promise<AvailabilityException> {
    const response = await api.post<AvailabilityException>('/availability/my/time-off', data)
    return response.data
  },

  // Обновление исключения в расписании
  async updateAvailabilityException(
    exceptionId: string, 
    data: Partial<CreateAvailabilityExceptionRequest>
  ): Promise<AvailabilityException> {
    const response = await api.put<AvailabilityException>(`/availability/my/time-off/${exceptionId}`, data)
    return response.data
  },

  // Удаление исключения в расписании
  async deleteAvailabilityException(exceptionId: string): Promise<void> {
    await api.delete(`/availability/my/time-off/${exceptionId}`)
  },

  // Публичный календарь доступности для бронирования
  async getMentorAvailableCalendar(mentorId: string, dateFrom: string, dateTo: string, durationMinutes?: number, timezone?: string) {
    const response = await api.get(`/availability/mentors/${mentorId}/calendar`, {
      params: { date_from: dateFrom, date_to: dateTo, duration_minutes: durationMinutes, timezone }
    })
    return response.data
  },

  // Утилиты
  async getWeekdayNames() {
    const response = await api.get('/availability/utils/weekdays')
    return response.data
  },

  async getTimezones() {
    const response = await api.get('/availability/utils/timezones')
    return response.data
  },
}
