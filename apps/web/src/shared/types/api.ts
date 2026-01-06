// Общие типы для API
export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface ApiError {
  detail: string
  code?: string
  field?: string
}

export interface ValidationError {
  loc: (string | number)[]
  msg: string
  type: string
}

// Типы для менторов
export interface Mentor {
  id: string
  user_id: string
  bio: string | null
  experience_years: number
  specialization: string[]
  languages: string[]
  price_30: number | null
  price_45: number | null
  price_60: number | null
  rating: number | null
  reviews_count: number
  avatar_url: string | null
  created_at: string
  updated_at: string
  
  // Связанные данные
  user: {
    id: string
    name: string | null
    email: string
  }
  universities: MentorUniversity[]
}

export interface MentorCard {
  id: string
  name: string
  bio: string | null
  specialization: string[]
  languages: string[]
  rating: number | null
  reviews_count: number
  price_from: number | null
  avatar_url: string | null
}

export interface MentorUniversity {
  id: string
  mentor_id: string
  university_name: string
  faculty: string | null
  degree: string | null
  graduation_year: number | null
  created_at: string
}

export interface MentorFilters {
  languages?: string[]
  subjects?: string[]
  countries?: string[]
  price_min?: number
  price_max?: number
  rating_min?: number
}

export enum MentorSortOptions {
  RATING_DESC = 'rating_desc',
  RATING_ASC = 'rating_asc',
  PRICE_ASC = 'price_asc',
  PRICE_DESC = 'price_desc',
  CREATED_DESC = 'created_desc',
}


// Типы для доступности
export interface TimeSlot {
  start: string
  end: string
  duration_minutes: number
  is_available: boolean
  price: number | null
}

export interface AvailabilityCalendar {
  mentor_id: string
  date_from: string
  date_to: string
  timezone: string
  slots: TimeSlot[]
}

// Типы для студентского профиля
export interface StudentProfile {
  user_id: string
  goals: string | null
  country: string | null
  city: string | null
  created_at: string
  updated_at: string
}
