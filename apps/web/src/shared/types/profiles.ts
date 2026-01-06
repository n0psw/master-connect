import type { UserRole } from './auth'

export interface UserProfile {
  id: string
  email: string
  name: string | null
  role: UserRole
  timezone: string
  locale: string
  phone: string | null
  is_active: boolean
  created_at: string
}

export interface UserUpdateData {
  name?: string
  phone?: string
  timezone?: string
  locale?: string
}

export interface StudentProfile {
  user_id: string
  goals: string | null
  country: string | null
  city: string | null
  avatar_url: string | null
  created_at: string
  updated_at: string
}

export interface StudentProfileUpdateData {
  goals?: string
  country?: string
  city?: string
  avatar_url?: string
}

export interface UserWithProfile extends UserProfile {
  student_profile?: StudentProfile
}

// Константы для селектов
export const TIMEZONES = [
  { value: 'Etc/GMT-5', label: 'Алматы (UTC+5)' },
  { value: 'Asia/Tashkent', label: 'Ташкент (UTC+5)' },
  { value: 'Asia/Bishkek', label: 'Бишкек (UTC+6)' },
  { value: 'Asia/Dushanbe', label: 'Душанбе (UTC+5)' },
  { value: 'Europe/Moscow', label: 'Москва (UTC+3)' },
  { value: 'Europe/London', label: 'Лондон (UTC+0)' },
  { value: 'America/New_York', label: 'Нью-Йорк (UTC-5)' },
  { value: 'America/Los_Angeles', label: 'Лос-Анджелес (UTC-8)' },
]

export const LOCALES = [
  { value: 'ru', label: 'Русский' },
  { value: 'en', label: 'English' },
  { value: 'kk', label: 'Қазақша' },
]

export const COUNTRIES = [
  'Казахстан',
  'Кыргызстан', 
  'Узбекистан',
  'Таджикистан',
  'Туркменистан',
  'Россия',
  'Беларусь',
  'Украина',
  'США',
  'Канада',
  'Великобритания',
  'Германия',
  'Франция',
  'Нидерланды',
  'Швеция',
  'Норвегия',
  'Дания',
  'Финляндия',
  'Швейцария',
  'Австрия',
  'Италия',
  'Испания',
  'Польша',
  'Чехия',
  'Венгрия',
  'Австралия',
  'Новая Зеландия',
  'Япония',
  'Южная Корея',
  'Сингапур',
  'Китай',
  'Индия',
]








