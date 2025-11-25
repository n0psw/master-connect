// Административные типы данных

// Общая статистика системы
export interface SystemStats {
  users: {
    total: number
    students: number
    mentors: number
    admins: number
    active_this_month: number
    new_this_month: number
  }
  bookings: {
    total: number
    pending: number
    confirmed: number
    completed: number
    cancelled: number
    revenue_this_month: number
    revenue_total: number
  }
  mentors: {
    verified: number
    unverified: number
    with_completed_profile: number
    average_rating: number
  }
}

// Статистика по периодам
export interface PeriodStats {
  period: string // 'day', 'week', 'month'
  date: string
  users_registered: number
  bookings_created: number
  bookings_completed: number
  revenue: number
}

// Пользователь для админки
export interface AdminUser {
  id: string
  email: string
  name: string | null
  role: 'student' | 'mentor' | 'admin'
  is_active: boolean
  timezone: string
  locale: string
  phone: string | null
  created_at: string
  last_login_at: string | null
  // Дополнительная информация
  total_bookings?: number
  mentor_rating?: number
}

export interface AdminUsersResponse {
  items: AdminUser[]
  total: number
  page: number
  pages: number
  page_size: number
}

export interface AdminUserSearchParams {
  page?: number
  page_size?: number
  search?: string
  role?: 'student' | 'mentor' | 'admin'
  is_active?: boolean
  sort?: 'created_asc' | 'created_desc' | 'name_asc' | 'name_desc' | 'email_asc' | 'email_desc'
}

// Бронирование для админки
export interface AdminBooking {
  id: string
  student_name: string
  student_email: string
  mentor_name: string
  mentor_email: string
  duration_minutes: 30 | 45 | 60
  starts_at: string
  status: 'HOLD' | 'AWAITING_VERIFICATION' | 'CONFIRMED' | 'COMPLETED' | 'CANCELLED' | 'REJECTED' | 'NO_SHOW_STUDENT' | 'NO_SHOW_MENTOR' | 'EXPIRED'
  price_usd: number
  created_at: string
  updated_at: string
  intake_form?: {
    goals?: string
    specific_questions?: string
    preferred_language?: string
  }
}

export interface AdminBookingsResponse {
  items: AdminBooking[]
  total: number
  page: number
  pages: number
  page_size: number
}

export interface AdminBookingSearchParams {
  page?: number
  page_size?: number
  search?: string
  status?: string[]
  mentor_id?: string
  student_id?: string
  date_from?: string
  date_to?: string
  sort?: 'created_asc' | 'created_desc' | 'scheduled_asc' | 'scheduled_desc' | 'price_asc' | 'price_desc'
}

// Действия администратора
export interface AdminUserAction {
  action: 'activate' | 'deactivate' | 'verify_mentor' | 'unverify_mentor' | 'change_role'
  user_id: string
  new_role?: 'student' | 'mentor' | 'admin'
  reason?: string
}

export interface AdminBookingAction {
  action: 'confirm' | 'reject' | 'cancel' | 'mark_completed' | 'mark_no_show'
  booking_id: string
  reason?: string
  no_show_type?: 'student' | 'mentor'
}

// Отчеты
export interface RevenueReport {
  period: 'daily' | 'weekly' | 'monthly'
  data: {
    date: string
    total_revenue: number
    bookings_count: number
    average_price: number
  }[]
}

export interface MentorPerformanceReport {
  mentor_id: string
  mentor_name: string
  mentor_email: string
  total_bookings: number
  completed_bookings: number
  cancelled_bookings: number
  total_revenue: number
  average_rating: number
  completion_rate: number
}

// === МЕНТОРЫ ===

export interface AdminMentorCreateData {
  // Данные пользователя
  email: string
  name: string
  password: string
  phone?: string
  timezone?: string
  locale?: string
  
  // Данные профиля ментора
  headline?: string
  bio?: string
  price_30?: number
  price_45?: number
  price_60?: number
  languages?: string[]
  subjects?: string[]
  avatar_url?: string
}

export interface AdminMentorUpdateData {
  // Данные пользователя
  name?: string
  phone?: string
  timezone?: string
  locale?: string
  is_active?: boolean
  
  // Данные профиля ментора
  headline?: string
  bio?: string
  price_30?: number
  price_45?: number
  price_60?: number
  languages?: string[]
  subjects?: string[]
  avatar_url?: string
}

export interface AdminMentorDetail {
  mentor: {
    id: string
    user_id: string
    headline: string | null
    bio: string | null
    price_30: number | null
    price_45: number | null
    price_60: number | null
    languages: string[]
    subjects: string[]
    rating_avg: number
    rating_count: number
    avatar_url: string | null
    created_at: string
    updated_at: string
  }
  user: {
    id: string
    email: string
    name: string
    phone: string | null
    timezone: string
    locale: string
    is_active: boolean
    created_at: string
    updated_at: string
  }
  universities: any[]
  reviews_count: number
  total_consultations: number
  completed_consultations: number
}

export interface AdminMentorSearchParams {
  page?: number
  page_size?: number
  search?: string
  rating_min?: number
  languages?: string[]
  subjects?: string[]
  countries?: string[]
  sort?: 'name_asc' | 'name_desc' | 'rating_desc' | 'rating_asc' | 'created_desc'
}

export interface AdminMentorAction {
  id: string
  action: 'view' | 'edit' | 'delete' | 'block' | 'unblock'
  label: string
  icon: any
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'
}

export interface PopularTimeSlots {
  hour: number
  day_of_week: number
  bookings_count: number
}

// Настройки системы
export interface SystemSettings {
  booking_settings: {
    max_advance_days: number
    min_advance_hours: number
    auto_confirmation: boolean
    cancellation_deadline_hours: number
  }
  payment_settings: {
    commission_rate: number
    minimum_payout: number
  }
  notification_settings: {
    email_notifications: boolean
    booking_reminders: boolean
    reminder_hours_before: number
  }
}

// Создание ментора (упрощенная версия)
export interface CreateMentorRequest {
  email: string
  password: string
  name: string
  phone?: string
  bio?: string
  headline?: string
  price_30?: number
  price_45?: number
  price_60?: number
  languages?: string[]
  avatar_url?: string
  send_welcome_email?: boolean
}

export interface CreateMentorResponse {
  user_id: string
  mentor_id: string
  email: string
  name: string
  message: string
}


