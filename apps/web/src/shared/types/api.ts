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

// Типы для бронирований
export interface Booking {
  id: string
  student_id: string
  mentor_id: string
  starts_at: string
  ends_at: string
  duration_minutes: number
  status: BookingStatus
  price_amount: number
  price_currency: string
  hold_expires_at: string | null
  google_meet_link: string | null
  google_calendar_event_id: string | null
  intake_form: Record<string, any>
  notes: string | null
  created_at: string
  updated_at: string
  
  // Связанные данные
  mentor_name: string
  mentor_avatar_url: string | null
  student_name: string
}

export enum BookingStatus {
  HOLD = 'HOLD',
  AWAITING_VERIFICATION = 'AWAITING_VERIFICATION',
  CONFIRMED = 'CONFIRMED',
  CANCELLED = 'CANCELLED',
  COMPLETED = 'COMPLETED',
  REJECTED = 'REJECTED',
  NO_SHOW_STUDENT = 'NO_SHOW_STUDENT',
  NO_SHOW_MENTOR = 'NO_SHOW_MENTOR',
  EXPIRED = 'EXPIRED',
}

export interface BookingIntakeForm {
  goals: string
  current_situation: string
  specific_questions: string[]
  preparation_level?: string
  previous_experience?: string
  expected_outcome?: string
  additional_info?: string
}

export interface CreateBookingRequest {
  mentor_id: string
  starts_at: string
  duration_minutes: number
  intake_form: BookingIntakeForm
  notes?: string
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
