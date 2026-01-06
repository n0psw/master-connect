export interface NotificationResponse {
  id: string
  user_id: string
  type: string
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
  notifications: NotificationResponse[]
  total: number
  unread_count: number
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

