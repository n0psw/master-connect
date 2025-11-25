export type BookingStatus = 
  | 'HOLD'                    // Забронирован, ожидает оплаты
  | 'AWAITING_VERIFICATION'   // Оплачен студентом, ожидает подтверждения админом
  | 'CONFIRMED'               // Подтвержден, консультация состоится
  | 'COMPLETED'               // Завершен
  | 'CANCELLED'               // Отменен
  | 'REJECTED'                // Отклонено админом
  | 'NO_SHOW_STUDENT'         // Студент не пришел
  | 'NO_SHOW_MENTOR'          // Ментор не пришел
  | 'EXPIRED'                 // Истекло время HOLD

export interface BookingBase {
  mentor_id: string
  starts_at: string        // ISO datetime
  duration_minutes: number
  price_amount: number
  intake_form: Record<string, any>  // JSON с ответами студента
  notes?: string
}

export interface BookingCreate extends BookingBase {
  // При создании все поля из BookingBase обязательны, кроме notes
}

export interface Booking extends BookingBase {
  id: string
  student_id: string
  status: BookingStatus
  payment_confirmed_at?: string
  payment_proof_url?: string
  cancellation_reason?: string
  created_at: string
  updated_at: string
  
  // Связанные данные
  mentor: {
    user_id: string
    name: string | null
    avatar_url: string | null
  }
  student: {
    id: string
    name: string | null
    avatar_url?: string | null
  }
  
  // Информация об отзыве
  has_review?: boolean
}

export interface BookingDetail {
  booking: Booking
  can_cancel: boolean
  can_reschedule: boolean
  can_mark_payment: boolean
  cancellation_deadline?: string
  reschedule_deadline?: string
}

export interface BookingListResponse {
  bookings: Booking[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface BookingStats {
  total_bookings: number
  pending_payment: number
  confirmed: number
  completed: number
  cancelled: number
  today: number
  this_week: number
  this_month: number
  total_revenue: number
  pending_revenue: number
  average_session_duration: number
  average_price: number
}

export interface BookingFilters {
  status?: BookingStatus[]
  mentor_id?: string
  student_id?: string
  date_from?: string
  date_to?: string
  upcoming?: boolean
}

export interface BookingSearchParams extends BookingFilters {
  page?: number
  page_size?: number
  sort?: 'created_desc' | 'created_asc' | 'scheduled_desc' | 'scheduled_asc'
}

export interface BookingCancellationRequest {
  reason: string
}

export interface BookingRescheduleRequest {
  new_starts_at: string
  reason?: string
}

export interface BookingPaymentConfirmation {
  payment_proof_url?: string
  notes?: string
}

// Для модерации (админы)
export interface BookingModerationItem {
  id: string
  student_name: string | null
  mentor_name: string | null  
  starts_at: string
  price_amount: number
  payment_proof_url?: string
  created_at: string
}

export interface BookingModerationQueue {
  pending_payments: BookingModerationItem[]
  total_pending: number
}

// Статусы для отображения
export const BookingStatusLabels: Record<BookingStatus, string> = {
  'HOLD': 'Ожидает оплаты',
  'AWAITING_VERIFICATION': 'Ожидает подтверждения',
  'CONFIRMED': 'Подтвержден',
  'COMPLETED': 'Завершен',
  'CANCELLED': 'Отменен',
  'REJECTED': 'Отклонено',
  'NO_SHOW_STUDENT': 'Студент не пришел',
  'NO_SHOW_MENTOR': 'Ментор не пришел',
  'EXPIRED': 'Истекло'
}

export const BookingStatusColors: Record<BookingStatus, string> = {
  'HOLD': 'bg-yellow-100 text-yellow-800',
  'AWAITING_VERIFICATION': 'bg-blue-100 text-blue-800',
  'CONFIRMED': 'bg-green-100 text-green-800',
  'COMPLETED': 'bg-gray-100 text-gray-800',
  'CANCELLED': 'bg-red-100 text-red-800',
  'REJECTED': 'bg-red-100 text-red-800',
  'NO_SHOW_STUDENT': 'bg-orange-100 text-orange-800',
  'NO_SHOW_MENTOR': 'bg-orange-100 text-orange-800',
  'EXPIRED': 'bg-gray-100 text-gray-600'
}
