import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { formatDateTime, formatFromNow, getClientTimezone } from '@/shared/lib/dayjs'
import { useMutation, useQuery, useQueryClient } from 'react-query'
import { Send, MessageSquare, AlertCircle, GraduationCap, User } from 'lucide-react'
import { toast } from 'sonner'

import { chatApi } from '@/shared/api/chat'
import { useAuthStore } from '@/shared/store/auth'
import type { ChatDialog, ChatMessage } from '@/shared/types/chat'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader } from '@/shared/ui/card'
import { Textarea } from '@/shared/ui/textarea'
import { cn } from '@/shared/utils/cn'

export const ChatPage = () => {
  const params = useParams<{ dialogId?: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user } = useAuthStore()
  const [searchParams, setSearchParams] = useSearchParams()
  const tz = useMemo(() => getClientTimezone(user?.timezone), [user?.timezone])

  const basePath =
    user?.role === 'mentor'
      ? '/mentor/chat'
      : user?.role === 'student'
      ? '/student/chat'
      : '/admin/chat'

  const [activeDialogId, setActiveDialogId] = useState<string | null>(params.dialogId ?? null)
  const [messageText, setMessageText] = useState('')
  const [isManualSelection, setIsManualSelection] = useState(false)

  const {
    data: dialogsData,
    isLoading: dialogsLoading,
    isFetching: dialogsFetching,
  } = useQuery(['chat-dialogs'], chatApi.getDialogs, {
    staleTime: 30 * 1000,  // 30 секунд
    cacheTime: 2 * 60 * 1000,  // 2 минуты
    refetchInterval: false,  // WebSocket обновляет
    refetchOnWindowFocus: true,
  })

  const dialogs = dialogsData?.dialogs ?? []

  useEffect(() => {
    if (!dialogs.length) {
      setActiveDialogId(null)
      setIsManualSelection(false)
      return
    }

    const bookingFilter = searchParams.get('booking')

    if (bookingFilter) {
      const target = dialogs.find((d) => d.booking_id === bookingFilter)
      if (target) {
        setActiveDialogId(target.id)
        setIsManualSelection(false)
        setSearchParams((prev) => {
          const next = new URLSearchParams(prev)
          next.delete('booking')
          return next
        }, { replace: true })
        return
      }
    }

    // Если диалог выбран вручную, не переключать автоматически
    if (isManualSelection && activeDialogId && dialogs.some((d) => d.id === activeDialogId)) {
      return
    }

    if (params.dialogId && dialogs.some((d) => d.id === params.dialogId)) {
      setActiveDialogId(params.dialogId)
      setIsManualSelection(false)
      return
    }

    // Автоматически выбираем первый диалог только если нет активного
    if (!activeDialogId || !dialogs.some((d) => d.id === activeDialogId)) {
      const firstDialog = dialogs[0]
      if (firstDialog) {
        setActiveDialogId(firstDialog.id)
        setIsManualSelection(false)
        navigate(`${basePath}/${firstDialog.id}`, { replace: true })
      }
    }
  }, [dialogs, activeDialogId, params.dialogId, navigate, basePath, searchParams, setSearchParams, isManualSelection])

  useEffect(() => {
    // Обновляем URL только если он отличается от текущего
    if (activeDialogId && params.dialogId !== activeDialogId) {
      navigate(`${basePath}/${activeDialogId}`, { replace: true })
    }
  }, [activeDialogId, navigate, basePath, params.dialogId])

  const {
    data: messagesData,
    isLoading: messagesLoading,
    isFetching: messagesFetching,
    refetch: refetchMessages,
    error: messagesError,
  } = useQuery(
    ['chat-messages', activeDialogId],
    () => chatApi.getDialogMessages(activeDialogId!),
    {
      enabled: !!activeDialogId,
      staleTime: 15 * 1000,  // 15 секунд
      cacheTime: 1 * 60 * 1000,  // 1 минута
      refetchInterval: false,  // WebSocket обновляет
      refetchOnWindowFocus: true,
      keepPreviousData: false,
      retry: 1,
      onError: (error: any) => {
        // Не показывать ошибку, если это просто пустой диалог
        if (error?.status !== 404) {
          console.error('Error loading messages:', error)
        }
      },
    }
  )

  const sendMutation = useMutation(
    (payload: { dialogId: string; text: string }) =>
      chatApi.sendMessage(payload.dialogId, { text: payload.text }),
    {
      onSuccess: (_, variables) => {
        setMessageText('')
        // Принудительно обновляем кеш сообщений и диалогов
        queryClient.invalidateQueries(['chat-dialogs'])
        queryClient.invalidateQueries(['chat-messages', variables.dialogId])
        // Немедленно перезагружаем сообщения
        refetchMessages()
      },
      onError: (error: any) => {
        toast.error('Не удалось отправить сообщение: ' + (error?.detail || error?.message))
      },
    }
  )

  const handleSelectDialog = (dialogId: string) => {
    // Проверяем, что диалог существует
    const dialogExists = dialogs.some((d) => d.id === dialogId)
    if (!dialogExists) {
      return
    }

    // Очищаем старые сообщения из кэша перед переключением
    if (activeDialogId && activeDialogId !== dialogId) {
      queryClient.removeQueries(['chat-messages', activeDialogId])
    }
    
    setIsManualSelection(true) // Помечаем, что выбор сделан вручную
    setActiveDialogId(dialogId)
    setMessageText('') // Сбрасываем текст сообщения
  }

  const handleSendMessage = () => {
    if (!activeDialogId || !messageText.trim()) return
    sendMutation.mutate({ dialogId: activeDialogId, text: messageText })
  }

  const activeDialog: ChatDialog | undefined = useMemo(
    () => dialogs.find((d) => d.id === activeDialogId || (params.dialogId && d.id === params.dialogId)),
    [dialogs, activeDialogId, params.dialogId]
  )

  const messages = messagesData?.messages ?? []

  // Функция для определения, является ли сообщение от ментора (для админа)
  const isFromMentor = (message: ChatMessage) => {
    if (user?.role === 'admin' && activeDialog) {
      return message.sender_id === activeDialog.mentor_id
    }
    return message.is_own
  }

  // Функция для получения имени отправителя (для админа)
  const getSenderName = (message: ChatMessage) => {
    if (user?.role === 'admin' && activeDialog) {
      if (message.sender_id === activeDialog.mentor_id) {
        return activeDialog.mentor_name || 'Ментор'
      } else if (message.sender_id === activeDialog.student_id) {
        return activeDialog.student_name || 'Студент'
      }
    }
    return null
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Чат</h1>
        <p className="text-muted-foreground">
          Общайтесь с вашим ментором или студентом. Новые сообщения обновляются автоматически.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-6">
        <Card className="h-[70vh]">
          <CardHeader className="border-b">
            <div className="flex items-center justify-between">
              <span className="font-semibold">Диалоги</span>
              {dialogsFetching && <span className="text-xs text-muted-foreground">Обновление…</span>}
            </div>
          </CardHeader>
          <CardContent className="p-0 h-full overflow-y-auto">
            {dialogsLoading ? (
              <div className="p-6 text-muted-foreground">Загружаем диалоги…</div>
            ) : dialogs.length === 0 ? (
              <div className="p-6 text-muted-foreground flex flex-col items-center text-center gap-2">
                <MessageSquare className="h-8 w-8 text-muted-foreground" />
                <p>Диалоги пока не найдены</p>
                <p className="text-sm">Начните диалог с ментора после бронирования консультации.</p>
              </div>
            ) : (
              <div className="divide-y">
                {dialogs.map((dialog) => (
                  <button
                    key={dialog.id}
                    onClick={() => handleSelectDialog(dialog.id)}
                    className={cn(
                      'w-full text-left p-4 hover:bg-muted transition',
                      dialog.id === activeDialogId && 'bg-muted'
                    )}
                  >
                    <div className="flex justify-between items-start gap-2">
                      <div>
                        <div className="font-semibold">
                          {user?.role === 'mentor' ? dialog.student_name || 'Студент' : dialog.mentor_name || 'Ментор'}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          Бронирование #{dialog.booking_id.slice(0, 6)}
                        </div>
                      </div>
                      {dialog.unread_count > 0 && (
                        <span className="inline-flex h-6 min-w-[1.5rem] items-center justify-center rounded-full bg-primary/10 text-primary text-xs font-semibold">
                          {dialog.unread_count}
                        </span>
                      )}
                    </div>
                    <div className="mt-2 text-sm text-muted-foreground line-clamp-2">
                      {dialog.last_message_preview || 'Сообщений пока нет'}
                    </div>
                    {dialog.last_message_at && (
                      <div className="mt-1 text-xs text-muted-foreground">
                        {formatFromNow(dialog.last_message_at, tz)}
                      </div>
                    )}
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="h-[70vh] flex flex-col">
          <CardHeader className="border-b">
            {activeDialog ? (
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  {user?.role === 'admin' ? (
                    <>
                      <div className="flex items-center gap-3 font-semibold text-lg">
                        <div className="flex items-center gap-2">
                          <GraduationCap className="h-5 w-5 text-primary" />
                          <span>{activeDialog.mentor_name || 'Ментор'}</span>
                        </div>
                        <span className="text-muted-foreground">↔</span>
                        <div className="flex items-center gap-2">
                          <User className="h-5 w-5 text-muted-foreground" />
                          <span>{activeDialog.student_name || 'Студент'}</span>
                        </div>
                      </div>
                      <div className="text-sm text-muted-foreground mt-1">
                        Бронирование #{activeDialog.booking_id.slice(0, 6)}
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="font-semibold text-lg">
                        {user?.role === 'mentor'
                          ? activeDialog.student_name || 'Студент'
                          : activeDialog.mentor_name || 'Ментор'}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Бронирование #{activeDialog.booking_id.slice(0, 6)}
                      </div>
                    </>
                  )}
                </div>
                <Button variant="ghost" size="sm" onClick={() => refetchMessages()}>
                  Обновить
                </Button>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-muted-foreground">
                <AlertCircle className="h-4 w-4" />
                <span>Выберите диалог слева</span>
              </div>
            )}
          </CardHeader>
          <CardContent className="flex-1 flex flex-col p-0">
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {!activeDialog ? (
                <div className="h-full flex items-center justify-center text-muted-foreground">
                  Выберите диалог, чтобы начать общение
                </div>
              ) : messagesLoading ? (
                <div className="h-full flex items-center justify-center text-muted-foreground">
                  Загружаем сообщения…
                </div>
              ) : messagesError && !messagesData ? (
                <div className="h-full flex items-center justify-center text-muted-foreground">
                  <div className="text-center">
                    <AlertCircle className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                    <p>Не удалось загрузить сообщения</p>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => refetchMessages()}
                      className="mt-2"
                    >
                      Попробовать снова
                    </Button>
                  </div>
                </div>
              ) : messages.length === 0 ? (
                <div className="h-full flex items-center justify-center text-muted-foreground">
                  Сообщений пока нет. Напишите первое сообщение!
                </div>
              ) : (
                messages.map((message) => {
                  const isMentorMessage = isFromMentor(message)
                  const senderName = getSenderName(message)
                  return (
                    <div
                      key={message.id}
                      className={cn(
                        'flex flex-col max-w-[80%]',
                        isMentorMessage ? 'ml-auto items-end' : 'items-start'
                      )}
                    >
                      {user?.role === 'admin' && senderName && (
                        <div className={cn(
                          'flex items-center gap-1.5 mb-1 text-xs font-medium',
                          isMentorMessage ? 'flex-row-reverse' : 'flex-row'
                        )}>
                          {isMentorMessage ? (
                            <GraduationCap className="h-3.5 w-3.5 text-primary" />
                          ) : (
                            <User className="h-3.5 w-3.5 text-muted-foreground" />
                          )}
                          <span className={cn(
                            isMentorMessage ? 'text-primary' : 'text-muted-foreground'
                          )}>
                            {senderName}
                          </span>
                        </div>
                      )}
                      <div
                        className={cn(
                          'rounded-2xl px-4 py-2 shadow-sm',
                          isMentorMessage
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted text-foreground'
                        )}
                      >
                        <div className="text-sm whitespace-pre-wrap break-words">{message.text}</div>
                      </div>
                      <span className="mt-1 text-xs text-muted-foreground">
                        {formatDateTime(message.created_at, tz, 'DD.MM.YYYY HH:mm')}
                      </span>
                    </div>
                  )
                })
              )}
              {messagesFetching && activeDialog && !messagesLoading && (
                <div className="text-xs text-muted-foreground text-center">Обновление…</div>
              )}
            </div>

            <div className="border-t p-4 space-y-3 bg-background">
              <Textarea
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                placeholder="Введите сообщение…"
                rows={3}
                disabled={!activeDialog || sendMutation.isLoading}
              />
              <div className="flex justify-between items-center">
                <div className="text-xs text-muted-foreground">
                  Сообщения обновляются автоматически каждые 10 секунд
                </div>
                <Button
                  onClick={handleSendMessage}
                  disabled={!activeDialog || !messageText.trim() || sendMutation.isLoading}
                >
                  <Send className="h-4 w-4 mr-2" />
                  Отправить
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

