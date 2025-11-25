import { api } from './client'

export enum NotificationType {
  BOOKING_CREATED = 'booking_created',
  BOOKING_CONFIRMED = 'booking_confirmed',
  BOOKING_CANCELLED = 'booking_cancelled',
  BOOKING_RESCHEDULED = 'booking_rescheduled',
  BOOKING_REMINDER = 'booking_reminder',
  PAYMENT_VERIFIED = 'payment_verified',
  PAYMENT_REQUIRED = 'payment_required',
  REVIEW_RECEIVED = 'review_received',
  MESSAGE_RECEIVED = 'message_received',
  SUPPORT_TICKET_UPDATE = 'support_ticket_update',
  SYSTEM_ANNOUNCEMENT = 'system_announcement',
}

export interface Notification {
  id: string
  user_id: string
  type: NotificationType
  title: string
  message: string
  is_read: boolean
  related_entity_type?: string
  related_entity_id?: string
  action_url?: string
  created_at: string
  read_at?: string
}

export interface NotificationList {
  notifications: Notification[]
  total: number
  unread_count: number
  page: number
  page_size: number
}

export interface UnreadCount {
  count: number
}

export const notificationsApi = {
  // Получение списка уведомлений
  async getNotifications(
    page: number = 1,
    pageSize: number = 20,
    isRead?: boolean
  ): Promise<NotificationList> {
    const params: any = { page, page_size: pageSize }
    if (isRead !== undefined) {
      params.is_read = isRead
    }

    const response = await api.get<NotificationList>('/notifications', { params })
    return response.data
  },

  // Получение количества непрочитанных
  async getUnreadCount(): Promise<UnreadCount> {
    const response = await api.get<UnreadCount>('/notifications/unread/count')
    return response.data
  },

  // Отметить как прочитанное
  async markAsRead(notificationId: string): Promise<Notification> {
    const response = await api.patch<Notification>(`/notifications/${notificationId}/read`)
    return response.data
  },

  // Отметить все как прочитанные
  async markAllAsRead(): Promise<{ marked_count: number }> {
    const response = await api.post<{ marked_count: number }>('/notifications/mark-all-read')
    return response.data
  },

  // Удалить уведомление
  async deleteNotification(notificationId: string): Promise<void> {
    await api.delete(`/notifications/${notificationId}`)
  },
}

