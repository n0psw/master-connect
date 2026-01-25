import { api } from './client'

import type {
  Booking,
  BookingDetail,
  BookingCreate,
  BookingListResponse,
  BookingStats,
  BookingSearchParams,
  BookingCancellationRequest,
  BookingRescheduleRequest,
  BookingPaymentConfirmation,
  BookingModerationQueue
} from '@/shared/types/bookings'
import type { BookingRequest } from '@/shared/types/bookings'

export const bookingsApi = {
  // Создание бронирования
  async createBooking(bookingData: BookingCreate): Promise<Booking> {
    const payload: any = {
      mentor_id: bookingData.mentor_id,
      starts_at: bookingData.starts_at,
      duration_minutes: bookingData.duration_minutes,
      intake_form: bookingData.intake_form,
      notes: bookingData.notes,
    }
    const response = await api.post<Booking>('/bookings', payload)
    return response.data
  },

  // Получение моих бронирований
  async getMyBookings(params: BookingSearchParams = {}): Promise<BookingListResponse> {
    const response = await api.get<BookingListResponse>('/bookings/my', {
      params: {
        ...params,
        status: params.status?.join(','),
      }
    })
    return response.data
  },

  // Получение конкретного бронирования
  async getBooking(bookingId: string): Promise<BookingDetail> {
    const response = await api.get<BookingDetail>(`/bookings/${bookingId}`)
    return response.data
  },

  // Получение статистики моих бронирований
  async getMyBookingStats(): Promise<BookingStats> {
    const response = await api.get<BookingStats>('/bookings/my/stats')
    return response.data
  },

  // Отметка оплаты ("Я оплатил")
  async markPayment(bookingId: string, data: BookingPaymentConfirmation = {}): Promise<Booking> {
    const response = await api.post<Booking>(`/bookings/${bookingId}/mark-payment`, data)
    return response.data
  },

  // Отмена бронирования
  async cancelBooking(bookingId: string, data: BookingCancellationRequest): Promise<Booking> {
    const response = await api.post<Booking>(`/bookings/${bookingId}/cancel`, data)
    return response.data
  },

  // Перенос бронирования
  async rescheduleBooking(bookingId: string, data: BookingRescheduleRequest): Promise<Booking> {
    const response = await api.post<Booking>(`/bookings/${bookingId}/reschedule`, data)
    return response.data
  },

  // Запрос студента на отмену/перенос (с модерацией)
  async createBookingRequest(
    bookingId: string,
    data: { type: 'CANCEL' | 'RESCHEDULE'; desired_starts_at?: string; reason?: string }
  ) {
    const payload: any = {
      type: data.type,
      desired_starts_at: data.desired_starts_at,
      reason: data.reason,
    }
    const response = await api.post(`/bookings/${bookingId}/request`, payload)
    return response.data
  },

  // Список запросов на отмену/перенос (админ/ментор)
  async listBookingRequests(params: { status?: 'PENDING' | 'APPROVED' | 'REJECTED' } = {}) {
    const response = await api.get<BookingRequest[]>(`/bookings/admin/requests`, { params })
    return response.data
  },

  // Решение по запросу
  async decideBookingRequest(
    requestId: string,
    data: { action: 'APPROVED' | 'REJECTED'; admin_comment?: string; new_starts_at?: string }
  ) {
    const response = await api.post<BookingRequest>(`/bookings/admin/requests/${requestId}/decision`, data)
    return response.data
  },

  // Административные функции
  async getModerationQueue(): Promise<BookingModerationQueue> {
    const response = await api.get<BookingModerationQueue>('/bookings/admin/queue')
    return response.data
  },

  // Подтверждение оплаты админом
  async confirmPayment(
    bookingId: string,
    data: { payment_confirmed: boolean; payment_notes?: string; payment_reference?: string }
  ): Promise<Booking> {
    const response = await api.post<Booking>(`/bookings/${bookingId}/admin/confirm-payment`, data)
    return response.data
  },

  // Отклонение оплаты админом (использует confirm-payment с payment_confirmed: false)
  async rejectPayment(bookingId: string, reason: string): Promise<Booking> {
    return this.confirmPayment(bookingId, {
      payment_confirmed: false,
      payment_notes: reason
    })
  },


  // Отметить как завершенное (админ)
  async markCompleted(bookingId: string): Promise<Booking> {
    const response = await api.post<Booking>(`/bookings/${bookingId}/admin/mark-completed`)
    return response.data
  },

  // Завершить консультацию (ментор)
  async markCompletedByMentor(bookingId: string): Promise<Booking> {
    const response = await api.post<Booking>(`/bookings/${bookingId}/mentor/mark-completed`)
    return response.data
  },

  // Отметить как неявку (админ)
  async markNoShow(bookingId: string, data?: { no_show_type?: 'student' | 'mentor' }): Promise<Booking> {
    const params = new URLSearchParams()
    if (data?.no_show_type) {
      params.append('no_show_type', data.no_show_type)
    }
    const url = `/bookings/${bookingId}/admin/mark-no-show${params.toString() ? `?${params.toString()}` : ''}`
    const response = await api.post<Booking>(url)
    return response.data
  },

  // Установить Google Meet ссылку (ментор)
  async setMeetLink(bookingId: string, meetLink: string): Promise<Booking> {
    const response = await api.post<Booking>(`/bookings/${bookingId}/mentor/set-meet-link`, {
      meet_link: meetLink
    })
    return response.data
  }
}
