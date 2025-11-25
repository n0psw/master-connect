import { useState } from 'react'
import { Helmet } from 'react-helmet-async'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import {
  HelpCircle,
  Plus,
  MessageSquare,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
} from 'lucide-react'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'

import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Textarea } from '@/shared/ui/textarea'
import { supportApi, TicketStatus } from '@/shared/api/support'

dayjs.locale('ru')

const createTicketSchema = z.object({
  subject: z.string().min(1, 'Тема обязательна').max(255, 'Тема слишком длинная'),
  body: z.string().min(10, 'Описание должно содержать минимум 10 символов'),
})

type CreateTicketFormData = z.infer<typeof createTicketSchema>

const getStatusColor = (status: TicketStatus) => {
  switch (status) {
    case TicketStatus.OPEN:
      return 'bg-blue-100 text-blue-700'
    case TicketStatus.IN_PROGRESS:
      return 'bg-yellow-100 text-yellow-700'
    case TicketStatus.RESOLVED:
      return 'bg-green-100 text-green-700'
    case TicketStatus.CLOSED:
      return 'bg-gray-100 text-gray-700'
    default:
      return 'bg-gray-100 text-gray-700'
  }
}

const getStatusIcon = (status: TicketStatus) => {
  switch (status) {
    case TicketStatus.OPEN:
      return <AlertCircle className="h-4 w-4" />
    case TicketStatus.IN_PROGRESS:
      return <Clock className="h-4 w-4" />
    case TicketStatus.RESOLVED:
      return <CheckCircle className="h-4 w-4" />
    case TicketStatus.CLOSED:
      return <XCircle className="h-4 w-4" />
    default:
      return <MessageSquare className="h-4 w-4" />
  }
}

const getStatusLabel = (status: TicketStatus) => {
  switch (status) {
    case TicketStatus.OPEN:
      return 'Открыт'
    case TicketStatus.IN_PROGRESS:
      return 'В работе'
    case TicketStatus.RESOLVED:
      return 'Решен'
    case TicketStatus.CLOSED:
      return 'Закрыт'
    default:
      return status
  }
}

export const SupportPage = () => {
  const [showCreateForm, setShowCreateForm] = useState(false)
  const queryClient = useQueryClient()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<CreateTicketFormData>({
    resolver: zodResolver(createTicketSchema),
  })

  // Получение тикетов
  const { data: ticketsData, isLoading } = useQuery(
    ['my-tickets'],
    () => supportApi.getMyTickets(1, 20),
    {
      refetchInterval: 30000, // Обновляем каждые 30 секунд
    }
  )

  // Создание тикета
  const createTicketMutation = useMutation(
    (data: CreateTicketFormData) =>
      supportApi.createTicket({
        subject: data.subject,
        body: data.body,
      }),
    {
      onSuccess: () => {
        toast.success('Тикет создан успешно!')
        queryClient.invalidateQueries('my-tickets')
        reset()
        setShowCreateForm(false)
      },
      onError: (error: any) => {
        toast.error(error?.detail || 'Ошибка при создании тикета')
      },
    }
  )

  const onSubmit = (data: CreateTicketFormData) => {
    createTicketMutation.mutate(data)
  }

  return (
    <>
      <Helmet>
        <title>Поддержка - MasterConnect</title>
        <meta name="description" content="Служба поддержки MasterConnect" />
      </Helmet>

      <div className="container-wide py-8">
        {/* Заголовок */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold flex items-center">
              <HelpCircle className="h-8 w-8 mr-3" />
              Служба поддержки
            </h1>
            <p className="text-muted-foreground mt-2">
              Создавайте тикеты для решения вопросов и проблем
            </p>
          </div>
          <Button onClick={() => setShowCreateForm(!showCreateForm)}>
            <Plus className="h-4 w-4 mr-2" />
            Создать тикет
          </Button>
        </div>

        {/* Форма создания тикета */}
        {showCreateForm && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Новый тикет</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div>
                  <Label htmlFor="subject">Тема *</Label>
                  <Input
                    id="subject"
                    placeholder="Кратко опишите проблему"
                    error={errors.subject?.message}
                    {...register('subject')}
                  />
                  {errors.subject && (
                    <p className="text-sm text-red-500 mt-1">{errors.subject.message}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="body">Описание *</Label>
                  <Textarea
                    id="body"
                    rows={6}
                    placeholder="Подробно опишите вашу проблему или вопрос..."
                    {...register('body')}
                  />
                  {errors.body && (
                    <p className="text-sm text-red-500 mt-1">{errors.body.message}</p>
                  )}
                </div>

                <div className="flex justify-end space-x-3">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowCreateForm(false)
                      reset()
                    }}
                  >
                    Отмена
                  </Button>
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Создание...' : 'Создать тикет'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Список тикетов */}
        <Card>
          <CardHeader>
            <CardTitle>Мои тикеты</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                <p className="mt-4 text-muted-foreground">Загрузка...</p>
              </div>
            ) : ticketsData && ticketsData.tickets.length > 0 ? (
              <div className="space-y-3">
                {ticketsData.tickets.map((ticket) => (
                  <div
                    key={ticket.id}
                    className="border rounded-lg p-4 hover:bg-accent transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <span
                            className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                              ticket.status
                            )}`}
                          >
                            {getStatusIcon(ticket.status)}
                            <span>{getStatusLabel(ticket.status)}</span>
                          </span>
                          <span className="text-sm text-muted-foreground">
                            {dayjs(ticket.created_at).format('DD.MM.YYYY в HH:mm')}
                          </span>
                        </div>
                        <h3 className="font-semibold text-lg mb-2">{ticket.subject}</h3>
                        <p className="text-muted-foreground line-clamp-2">{ticket.body}</p>
                      </div>
                      <Button variant="ghost" size="sm" asChild>
                        <a href={`/support/${ticket.id}`}>Открыть</a>
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <MessageSquare className="h-16 w-16 mx-auto text-muted-foreground opacity-50 mb-4" />
                <h3 className="text-lg font-semibold mb-2">Нет тикетов</h3>
                <p className="text-muted-foreground mb-4">
                  У вас пока нет обращений в поддержку
                </p>
                <Button onClick={() => setShowCreateForm(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Создать первый тикет
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </>
  )
}

