import { useEffect, useRef } from 'react'
import { useQueryClient } from 'react-query'

import { useAuthStore } from '@/shared/store/auth'

const API_BASE = (import.meta.env.VITE_API_URL || '/api/v1').replace(/\/$/, '')
const WS_BASE = API_BASE.replace(/^http/, 'ws')
const WS_NOTIFICATIONS_URL = `${WS_BASE}/notifications/ws`

export const useNotificationsSocket = () => {
  const { tokens, user } = useAuthStore()
  const queryClient = useQueryClient()
  const wsRef = useRef<WebSocket | null>(null)
  const retryRef = useRef(0)
  const timerRef = useRef<number | null>(null)

  useEffect(() => {
    const accessToken = tokens?.access_token
    if (!accessToken || !user?.id) {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
      if (timerRef.current) {
        clearTimeout(timerRef.current)
        timerRef.current = null
      }
      return
    }

    const connect = () => {
      const ws = new WebSocket(`${WS_NOTIFICATIONS_URL}?token=${accessToken}`)
      wsRef.current = ws

      ws.onopen = () => {
        retryRef.current = 0
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (typeof data?.unread_count === 'number') {
            queryClient.setQueryData(['unread-notifications-count', user.id], { count: data.unread_count })
          } else {
            queryClient.invalidateQueries(['unread-notifications-count', user.id])
          }
        } catch {
          queryClient.invalidateQueries(['unread-notifications-count', user.id])
        }
        queryClient.invalidateQueries(['recent-notifications', user.id])
      }

      ws.onerror = () => {
        ws.close()
      }

      ws.onclose = () => {
        wsRef.current = null
        const delay = Math.min(30000, 1000 * 2 ** retryRef.current)
        retryRef.current += 1
        timerRef.current = window.setTimeout(connect, delay)
      }
    }

    connect()

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current)
        timerRef.current = null
      }
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [tokens?.access_token, user?.id, queryClient])
}
