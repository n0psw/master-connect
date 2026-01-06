import { api } from './client'

export enum NotificationType {
  BOOKING_CREATED = 'BOOKING_CREATED',
  BOOKING_CONFIRMED = 'BOOKING_CONFIRMED',
  BOOKING_CANCELLED = 'BOOKING_CANCELLED',
  BOOKING_RESCHEDULED = 'BOOKING_RESCHEDULED',
  BOOKING_REMINDER = 'BOOKING_REMINDER',
  BOOKING_COMPLETED = 'BOOKING_COMPLETED',
  BOOKING_NO_SHOW = 'BOOKING_NO_SHOW',
  BOOKING_EXPIRED = 'BOOKING_EXPIRED',
  PAYMENT_VERIFIED = 'PAYMENT_VERIFIED',
  PAYMENT_REQUIRED = 'PAYMENT_REQUIRED',
  REVIEW_RECEIVED = 'REVIEW_RECEIVED',
  REVIEW_CREATED = 'REVIEW_CREATED',
  MESSAGE_RECEIVED = 'MESSAGE_RECEIVED',
  SUPPORT_TICKET_UPDATE = 'SUPPORT_TICKET_UPDATE',
  SYSTEM_ANNOUNCEMENT = 'SYSTEM_ANNOUNCEMENT',
  ADMIN_MODERATION = 'ADMIN_MODERATION',
  ADMIN_PAYMENT_QUEUE = 'ADMIN_PAYMENT_QUEUE',
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
  async getNotifications(page: number = 1, pageSize: number = 20, isRead?: boolean): Promise<NotificationList> {
    const params: Record<string, any> = { page, page_size: pageSize }
    if (isRead !== undefined) params.is_read = isRead
    const response = await api.get<NotificationList>('/notifications', { params })
    return response.data
  },

  async getMyNotifications(page: number = 1, pageSize: number = 20, isRead?: boolean): Promise<NotificationList> {
    return this.getNotifications(page, pageSize, isRead)
  },

  async getUnreadCount(): Promise<UnreadCount> {
    const response = await api.get<UnreadCount>('/notifications/unread/count')
    return response.data
  },

  async getUnreadNotificationsCount(): Promise<UnreadCount> {
    return this.getUnreadCount()
  },

  async markAsRead(notificationId: string): Promise<Notification> {
    const response = await api.patch<Notification>(`/notifications/${notificationId}/read`)
    return response.data
  },

  async markNotificationAsRead(notificationId: string): Promise<Notification> {
    return this.markAsRead(notificationId)
  },

  async markAllAsRead(): Promise<{ marked_count: number }> {
    const response = await api.post<{ marked_count: number }>('/notifications/mark-all-read')
    return response.data
  },

  async markAllNotificationsAsRead(): Promise<{ marked_count: number }> {
    return this.markAllAsRead()
  },

  async deleteNotification(notificationId: string): Promise<void> {
    await api.delete(`/notifications/${notificationId}`)
  },
}

