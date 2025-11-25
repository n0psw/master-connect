import { useState, useEffect, useRef } from 'react'
import { Bell, Check, CheckCheck, X } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/ru'

import { notificationsApi } from '@/shared/api/notifications'
import { Button } from '@/shared/ui/button'
import type { NotificationResponse } from '@/shared/types/notifications'

dayjs.extend(relativeTime)
dayjs.locale('ru')

export const NotificationBell = () => {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const queryClient = useQueryClient()

  // Получение счетчика непрочитанных уведомлений
  const { data: unreadCount } = useQuery(
    'unread-notifications-count',
    () => notificationsApi.getUnreadNotificationsCount(),
    {
      refetchInterval: 30000, // Обновляем каждые 30 секунд
      refetchOnWindowFocus: true,
    }
  )

  // Получение последних уведомлений
  const { data: notificationsData, isLoading } = useQuery(
    'recent-notifications',
    () => notificationsApi.getMyNotifications(1, 5),
    {
      enabled: isOpen, // Загружаем только когда dropdown открыт
    }
  )

  // Отметить как прочитанное
  const markAsReadMutation = useMutation(
    (notificationId: string) => notificationsApi.markNotificationAsRead(notificationId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('unread-notifications-count')
        queryClient.invalidateQueries('recent-notifications')
      },
    }
  )

  // Отметить все как прочитанные
  const markAllAsReadMutation = useMutation(
    () => notificationsApi.markAllNotificationsAsRead(),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('unread-notifications-count')
        queryClient.invalidateQueries('recent-notifications')
        setIsOpen(false)
      },
    }
  )

  // Закрытие dropdown при клике вне его
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleNotificationClick = (notification: NotificationResponse) => {
    if (!notification.is_read) {
      markAsReadMutation.mutate(notification.id)
    }

    // Если есть ссылка, переходим
    if (notification.link) {
      window.location.href = notification.link
    }

    setIsOpen(false)
  }

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'booking':
        return '📅'
      case 'chat':
        return '💬'
      case 'payment':
        return '💳'
      case 'success':
        return '✅'
      case 'warning':
        return '⚠️'
      case 'error':
        return '❌'
      default:
        return '📢'
    }
  }

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Кнопка колокольчика */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-lg hover:bg-accent transition-colors"
        aria-label="Уведомления"
      >
        <Bell className="h-5 w-5" />
        
        {/* Счетчик непрочитанных */}
        {unreadCount && unreadCount.count > 0 && (
          <span className="absolute top-0 right-0 flex items-center justify-center h-5 w-5 bg-red-500 text-white text-xs font-bold rounded-full border-2 border-background">
            {unreadCount.count > 9 ? '9+' : unreadCount.count}
          </span>
        )}
      </button>

      {/* Dropdown с уведомлениями */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-background border rounded-lg shadow-lg z-50">
          {/* Заголовок */}
          <div className="flex items-center justify-between p-4 border-b">
            <h3 className="font-semibold">Уведомления</h3>
            {unreadCount && unreadCount.count > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => markAllAsReadMutation.mutate()}
                disabled={markAllAsReadMutation.isLoading}
                className="text-sm"
              >
                <CheckCheck className="h-4 w-4 mr-1" />
                Прочитать все
              </Button>
            )}
          </div>

          {/* Список уведомлений */}
          <div className="max-h-[400px] overflow-y-auto">
            {isLoading ? (
              <div className="p-8 text-center text-muted-foreground">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="mt-2">Загрузка...</p>
              </div>
            ) : notificationsData && notificationsData.notifications.length > 0 ? (
              notificationsData.notifications.map((notification) => (
                <div
                  key={notification.id}
                  onClick={() => handleNotificationClick(notification)}
                  className={`p-4 border-b cursor-pointer transition-colors hover:bg-accent ${
                    !notification.is_read ? 'bg-blue-50/50' : ''
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    {/* Иконка типа уведомления */}
                    <div className="text-2xl flex-shrink-0">
                      {getNotificationIcon(notification.type)}
                    </div>

                    {/* Содержимое */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <h4 className={`text-sm font-medium ${!notification.is_read ? 'font-semibold' : ''}`}>
                          {notification.title}
                        </h4>
                        {!notification.is_read && (
                          <span className="ml-2 h-2 w-2 bg-blue-500 rounded-full flex-shrink-0 mt-1"></span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                        {notification.message}
                      </p>
                      <p className="text-xs text-muted-foreground mt-2">
                        {dayjs(notification.created_at).fromNow()}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-muted-foreground">
                <Bell className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>Нет уведомлений</p>
              </div>
            )}
          </div>

          {/* Футер */}
          {notificationsData && notificationsData.notifications.length > 0 && (
            <div className="p-3 border-t text-center">
              <a
                href="/notifications"
                className="text-sm text-primary hover:underline"
                onClick={() => setIsOpen(false)}
              >
                Посмотреть все уведомления
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

