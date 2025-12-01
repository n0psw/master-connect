import { api } from './client'
import { bookingsApi } from './bookings'
import type {
  SystemStats,
  PeriodStats,
  AdminUsersResponse,
  AdminUserSearchParams,
  AdminUser,
  AdminBookingsResponse,
  AdminBookingSearchParams,
  AdminUserAction,
  AdminBookingAction,
  RevenueReport,
  MentorPerformanceReport,
  PopularTimeSlots,
  SystemSettings,
  CreateMentorRequest,
  CreateMentorResponse,
} from '@/shared/types/admin'

export const adminApi = {
  // Дашборд и аналитика (соответствие бэкенду)
  async getDashboard() {
    const response = await api.get('/admin/dashboard')
    return response.data
  },

  async getAnalytics() {
    const response = await api.get('/admin/analytics')
    return response.data
  },

  // Аудит лог
  async getAuditLog(params?: any) {
    const response = await api.get('/admin/audit-log', { params })
    return response.data
  },

  // Система
  async getSystemHealth() {
    const response = await api.get('/admin/system/health')
    return response.data
  },

  async getSystemMetrics() {
    const response = await api.get('/admin/system/metrics')
    return response.data
  },

  // Экспорт
  async exportUsers(payload: any) {
    const response = await api.post('/admin/export/users', payload, { responseType: 'blob' })
    return response.data
  },

  async exportBookings(payload: any) {
    const response = await api.post('/admin/export/bookings', payload, { responseType: 'blob' })
    return response.data
  },

  // Быстрая статистика
  async getQuickStats() {
    const response = await api.get('/admin/stats/quick')
    return response.data
  },

  // Утилиты
  async sendTestEmail(payload: any) {
    const response = await api.post('/admin/utils/send-test-email', payload)
    return response.data
  },

  async clearCache(payload?: any) {
    const response = await api.post('/admin/utils/clear-cache', payload)
    return response.data
  },

  // Проверка модуля
  async health() {
    const response = await api.get('/admin/health')
    return response.data
  },

  // ===== Бронирования (админ) =====
  async getBookings(params: AdminBookingSearchParams) {
    // Бэкенд: GET /bookings/admin/all возвращает BookingList с полем "bookings"
    // Преобразуем в AdminBookingsResponse с полем "items"
    const response = await api.get<any>('/bookings/admin/all', {
      params: {
        page: params.page,
        page_size: params.page_size,
        status: params.status?.length ? params.status : undefined,
        mentor_id: params.mentor_id,
        student_id: params.student_id,
        date_from: params.date_from,
        date_to: params.date_to,
        search: params.search,
        sort: params.sort || 'created_desc',
      }
    })
    
    const data = response.data
    
    const bookings = (data.bookings || data.items || []).map((booking: any) => ({
      ...booking,
      price_usd: Number(booking.price_amount || booking.price_usd || 0),
      student_email: booking.student_email || booking.student?.user?.email || '',
      mentor_email: booking.mentor_email || booking.mentor?.user?.email || '',
      student_name: booking.student_name || booking.student?.user?.name || 'Студент',
      mentor_name: booking.mentor_name || booking.mentor?.user?.name || 'Ментор',
    }))
    
    return {
      items: bookings,
      total: data.total || 0,
      page: data.page || 1,
      pages: data.total_pages || Math.ceil((data.total || 0) / (data.page_size || 20)),
      page_size: data.page_size || 20,
    } as AdminBookingsResponse
  },

  async performBookingAction(action: AdminBookingAction) {
    const { action: kind, booking_id, reason, no_show_type } = action
    switch (kind) {
      case 'confirm':
        return bookingsApi.confirmPayment(booking_id, {
          payment_confirmed: true,
          payment_notes: reason
        })
      case 'reject':
        return bookingsApi.confirmPayment(booking_id, {
          payment_confirmed: false,
          payment_notes: reason || 'Оплата отклонена администратором'
        })
      case 'cancel':
        return bookingsApi.cancelBooking(booking_id, { reason: reason || 'Отменено администратором' })
      case 'mark_completed':
        return bookingsApi.markCompleted(booking_id)
      case 'mark_no_show':
        return bookingsApi.markNoShow(booking_id, { no_show_type: no_show_type || 'student' })
      default:
        throw { detail: 'Неизвестное действие' }
    }
  },

  // === Создание ментора ===
  async createMentor(data: CreateMentorRequest) {
    const response = await api.post<CreateMentorResponse>('/admin/mentors/create', data)
    return response.data
  },
}
