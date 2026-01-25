// Типы для работы с расписанием и доступностью менторов

// ВОЗМОЖНОСТИ БЭКА: 0 = Monday, ..., 6 = Sunday (совместимо с FastAPI/Pydantic)
export type DayOfWeek = 0 | 1 | 2 | 3 | 4 | 5 | 6 // 0=Пн, 6=Вс

export interface TimeSlot {
  start_time: string // HH:MM формат
  end_time: string   // HH:MM формат
}

export interface WeeklySchedule {
  monday: TimeSlot[]
  tuesday: TimeSlot[]
  wednesday: TimeSlot[]
  thursday: TimeSlot[]
  friday: TimeSlot[]
  saturday: TimeSlot[]
  sunday: TimeSlot[]
}

export interface AvailabilitySettings {
  id?: string
  mentor_id: string
  timezone: string
  buffer_time_minutes: number // время между консультациями
  max_bookings_per_day: number
  advance_booking_days: number // за сколько дней можно бронировать
  created_at?: string
  updated_at?: string
}

export interface AvailabilityException {
  id?: string
  mentor_id: string
  date: string // YYYY-MM-DD
  is_available: boolean
  time_slots?: TimeSlot[]
  reason?: string
  created_at?: string
  updated_at?: string
}

export interface MentorAvailability {
  settings: AvailabilitySettings
  weekly_schedule: WeeklySchedule
  time_offs: AvailabilityException[]
}

// Запросы для API
export interface UpdateWeeklyScheduleRequest {
  day_of_week: DayOfWeek
  time_slots: TimeSlot[]
  is_available: boolean
}

export interface UpdateAvailabilitySettingsRequest {
  timezone?: string
  buffer_time_minutes?: number
  max_bookings_per_day?: number
  advance_booking_days?: number
}

export interface CreateAvailabilityExceptionRequest {
  date: string
  is_available: boolean
  time_slots?: TimeSlot[]
  reason?: string
}

// Константы
export const DEFAULT_BUFFER_TIME = 15 // минут
export const DEFAULT_MAX_BOOKINGS = 8 // в день
export const DEFAULT_ADVANCE_DAYS = 30 // дней

export const DAY_NAMES = {
  0: 'Понедельник',
  1: 'Вторник', 
  2: 'Среда',
  3: 'Четверг',
  4: 'Пятница',
  5: 'Суббота',
  6: 'Воскресенье',
} as const

export const DAY_NAMES_SHORT = {
  0: 'Пн',
  1: 'Вт', 
  2: 'Ср',
  3: 'Чт',
  4: 'Пт',
  5: 'Сб',
  6: 'Вс',
} as const

// Утилиты
export const generateTimeSlots = (startHour = 8, endHour = 22, intervalMinutes = 30): string[] => {
  const slots: string[] = []
  
  for (let hour = startHour; hour < endHour; hour++) {
    for (let minutes = 0; minutes < 60; minutes += intervalMinutes) {
      const timeString = `${hour.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`
      slots.push(timeString)
    }
  }
  
  return slots
}

export const formatTimeRange = (startTime: string, endTime: string): string => {
  return `${startTime} - ${endTime}`
}

export const isTimeSlotValid = (slot: TimeSlot): boolean => {
  const start = new Date(`2000-01-01T${slot.start_time}:00`)
  const end = new Date(`2000-01-01T${slot.end_time}:00`)
  return start < end
}







