export interface NotificationResponse {
  id: string
  user_id: string
  title: string
  message: string
  type: string
  link?: string
  is_read: boolean
  created_at: string
  updated_at: string
}

export interface NotificationList {
  notifications: NotificationResponse[]
  total: number
  page: number
  page_size: number
}

export interface UnreadNotificationsCount {
  count: number
}

export interface NotificationCreate {
  user_id: string
  title: string
  message: string
  type?: string
  link?: string
}

export interface NotificationUpdate {
  is_read?: boolean
}

