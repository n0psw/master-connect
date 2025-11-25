import { useState } from 'react'
import { Helmet } from 'react-helmet-async'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { toast } from 'sonner'
import {
  Calendar,
  Clock,
  User,
  UserCheck,
  DollarSign,
  MapPin,
  MessageCircle,
  Star,
  ChevronLeft,
  AlertTriangle,
  CheckCircle,
  XCircle,
  CreditCard,
  CalendarDays,
  Phone,
  Mail,
  Target,
  BookOpen,
  Languages,
  Edit,
  X,
  Send,
  Video,
  ExternalLink,
} from 'lucide-react'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Textarea } from '@/shared/ui/textarea'
import { Input } from '@/shared/ui/input'
import { ReviewForm } from '@/shared/components/ReviewForm'
import { bookingsApi } from '@/shared/api/bookings'
import { useAuthStore } from '@/shared/store/auth'
import { BookingStatusLabels, BookingStatusColors } from '@/shared/types/bookings'
import type { BookingDetail } from '@/shared/types/bookings'

dayjs.extend(utc)
dayjs.extend(timezone)
dayjs.locale('ru')

// Компонент статусного бейджа
interface StatusBadgeProps {
  status: string
  size?: 'sm' | 'md'
}

const StatusBadge = ({ status, size = 'md' }: StatusBadgeProps) => {
  const color = BookingStatusColors[status as keyof typeof BookingStatusColors] || 'bg-gray-100 text-gray-700'
  const label = BookingStatusLabels[status as keyof typeof BookingStatusLabels] || status
  
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1 text-sm'
  }

  const getIcon = () => {
    switch (status) {
      case 'HOLD':
        return <Clock className="h-3 w-3 mr-1" />
      case 'AWAITING_VERIFICATION':
        return <AlertTriangle className="h-3 w-3 mr-1" />
      case 'CONFIRMED':
        return <CheckCircle className="h-3 w-3 mr-1" />
      case 'COMPLETED':
        return <CheckCircle className="h-3 w-3 mr-1" />
      case 'CANCELLED':
        return <XCircle className="h-3 w-3 mr-1" />
      case 'NO_SHOW_STUDENT':
      case 'NO_SHOW_MENTOR':
        return <XCircle className="h-3 w-3 mr-1" />
      default:
        return null
    }
  }

  return (
    <span className={`inline-flex items-center rounded-full font-medium ${sizeClasses[size]} ${color}`}>
      {getIcon()}
      {label}
    </span>
  )
}

// Компонент действий с бронированием
interface BookingActionsProps {
  booking: Booking
  userRole: 'student' | 'mentor' | 'admin'
}

const BookingActions = ({ booking, userRole }: BookingActionsProps) => {
  const [showReschedule, setShowReschedule] = useState(false)
  const [showCancel, setShowCancel] = useState(false)
  const [showReview, setShowReview] = useState(false)
  const [newDateTime, setNewDateTime] = useState('')
  const [cancelReason, setCancelReason] = useState('')
  
  const queryClient = useQueryClient()

  // Мутации для различных действий
  const markPaymentMutation = useMutation(bookingsApi.markPayment, {
    onSuccess: () => {
      queryClient.invalidateQueries(['booking', booking.id])
      toast.success('Отметка об оплате отправлена!')
    },
    onError: (error: any) => {
      toast.error(error?.detail || 'Ошибка при отправке отметки об оплате')
    }
  })

  const cancelMutation = useMutation(
    (data: { reason: string }) => bookingsApi.cancelBooking(booking.id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['booking', booking.id])
        toast.success('Бронирование отменено')
        setShowCancel(false)
      },
      onError: (error: any) => {
        toast.error(error?.detail || 'Ошибка при отмене бронирования')
      }
    }
  )

  const rescheduleMutation = useMutation(
    (data: { new_starts_at: string }) => bookingsApi.rescheduleBooking(booking.id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['booking', booking.id])
        toast.success('Запрос на перенос отправлен')
        setShowReschedule(false)
      },
      onError: (error: any) => {
        toast.error(error?.detail || 'Ошибка при переносе бронирования')
      }
    }
  )

  const markCompletedMutation = useMutation(
    (bookingId: string) => bookingsApi.markCompletedByMentor(bookingId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['booking', booking.id])
        toast.success('Консультация отмечена как завершенная')
        setShowReview(false)
      },
      onError: (error: any) => {
        toast.error('Ошибка: ' + (error?.detail || error?.message))
      }
    }
  )

  const markCompletedByAdminMutation = useMutation(
    (bookingId: string) => bookingsApi.markCompleted(bookingId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['booking', booking.id])
        toast.success('Консультация отмечена как завершенная')
        setShowReview(false)
      },
      onError: (error: any) => {
        toast.error('Ошибка: ' + (error?.detail || error?.message))
      }
    }
  )

  const now = dayjs()
  const scheduledTime = dayjs((booking as any).starts_at)
  const isPast = scheduledTime.isBefore(now)
  const isUpcoming = scheduledTime.isAfter(now)
  const canCancel = ['HOLD', 'AWAITING_VERIFICATION', 'CONFIRMED'].includes(booking.status) && isUpcoming
  const canReschedule = ['CONFIRMED'].includes(booking.status) && isUpcoming
  const canPayment = booking.status === 'HOLD' && userRole === 'student'
  const canReview = booking.status === 'COMPLETED' && userRole === 'student' && !booking.has_review
  const canMarkCompleted = booking.status === 'CONFIRMED' && (userRole === 'mentor' || userRole === 'admin')

  const chatBasePath =
    userRole === 'mentor' ? '/mentor/chat' : userRole === 'student' ? '/student/chat' : '/admin/chat'

  const handleMarkPayment = () => {
    markPaymentMutation.mutate(booking.id)
  }

  const handleMarkCompleted = () => {
    if (userRole === 'admin') {
      markCompletedByAdminMutation.mutate(booking.id)
    } else {
      markCompletedMutation.mutate(booking.id)
    }
  }

  const handleCancel = () => {
    if (!cancelReason.trim()) {
      toast.error('Укажите причину отмены')
      return
    }
    cancelMutation.mutate({ reason: cancelReason })
  }

  const handleReschedule = () => {
    if (!newDateTime) {
      toast.error('Выберите новые дату и время')
      return
    }
    rescheduleMutation.mutate({ new_starts_at: newDateTime })
  }

  return (
    <div className="space-y-4">
      {/* Основные действия */}
      <div className="flex flex-wrap gap-2">
        <Button asChild variant="outline">
          <Link to={`${chatBasePath}?booking=${booking.id}`}>
            <MessageCircle className="h-4 w-4 mr-2" />
            Открыть чат
          </Link>
        </Button>

        {canPayment && (
          <Button
            onClick={handleMarkPayment}
            disabled={markPaymentMutation.isLoading}
            className="bg-green-600 hover:bg-green-700"
          >
            <CreditCard className="h-4 w-4 mr-2" />
            {markPaymentMutation.isLoading ? 'Отправка...' : 'Я оплатил'}
          </Button>
        )}

        {canReschedule && (
          <Button
            variant="outline"
            onClick={() => setShowReschedule(true)}
          >
            <CalendarDays className="h-4 w-4 mr-2" />
            Перенести
          </Button>
        )}

        {canCancel && (
          <Button
            variant="outline"
            onClick={() => setShowCancel(true)}
            className="text-red-600 border-red-200 hover:bg-red-50"
          >
            <XCircle className="h-4 w-4 mr-2" />
            Отменить
          </Button>
        )}

        {canReview && (
          <Button
            variant="outline"
            onClick={() => setShowReview(true)}
          >
            <Star className="h-4 w-4 mr-2" />
            Оставить отзыв
          </Button>
        )}

        {canMarkCompleted && (
          <Button
            variant="default"
            onClick={handleMarkCompleted}
            disabled={
              (userRole === 'admin' && markCompletedByAdminMutation.isLoading) ||
              (userRole === 'mentor' && markCompletedMutation.isLoading)
            }
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            {userRole === 'admin' 
              ? (markCompletedByAdminMutation.isLoading ? 'Завершение...' : 'Консультация проведена')
              : (markCompletedMutation.isLoading ? 'Завершение...' : 'Консультация проведена')
            }
          </Button>
        )}
      </div>

      {/* Форма переноса */}
      {showReschedule && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Перенос консультации
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowReschedule(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">
                Новые дата и время
              </label>
              <Input
                type="datetime-local"
                value={newDateTime}
                onChange={(e) => setNewDateTime(e.target.value)}
                min={dayjs().add(1, 'day').format('YYYY-MM-DDTHH:mm')}
              />
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handleReschedule}
                disabled={rescheduleMutation.isLoading}
                size="sm"
              >
                <Send className="h-4 w-4 mr-2" />
                {rescheduleMutation.isLoading ? 'Отправка...' : 'Отправить запрос'}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowReschedule(false)}
              >
                Отмена
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Форма отмены */}
      {showCancel && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Отмена бронирования
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowCancel(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">
                Причина отмены
              </label>
              <Textarea
                placeholder="Укажите причину отмены..."
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                rows={3}
              />
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handleCancel}
                disabled={cancelMutation.isLoading}
                variant="destructive"
                size="sm"
              >
                <XCircle className="h-4 w-4 mr-2" />
                {cancelMutation.isLoading ? 'Отмена...' : 'Отменить бронирование'}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowCancel(false)}
              >
                Назад
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Модальное окно формы отзыва */}
      {showReview && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <ReviewForm
            bookingId={booking.id}
            mentorName={(booking as any).mentor?.name || 'ментором'}
            onClose={() => setShowReview(false)}
            onSuccess={() => {
              queryClient.invalidateQueries(['booking', booking.id])
            }}
          />
        </div>
      )}
    </div>
  )
}

export const BookingDetailPage = () => {
  const { bookingId } = useParams<{ bookingId: string }>()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [showReviewForm, setShowReviewForm] = useState(false)

  // Загрузка данных бронирования
  const { data: booking, isLoading, error } = useQuery(
    ['booking', bookingId],
    () => bookingsApi.getBooking(bookingId!),
    {
      enabled: !!bookingId,
      onError: (error: any) => {
        toast.error('Ошибка при загрузке бронирования: ' + (error?.detail || error?.message))
      }
    }
  )

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded mb-4" />
          <div className="h-64 bg-muted rounded" />
        </div>
      </div>
    )
  }

  if (error || !booking) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-xl font-semibold mb-2">Бронирование не найдено</h2>
        <p className="text-muted-foreground mb-4">
          Возможно, бронирование было удалено или у вас нет прав для его просмотра.
        </p>
        <Button onClick={() => navigate(-1)}>
          <ChevronLeft className="h-4 w-4 mr-2" />
          Назад
        </Button>
      </div>
    )
  }

  const userRole = user?.role as 'student' | 'mentor' | 'admin'
  const isStudent = userRole === 'student'
  const isMentor = userRole === 'mentor'
  const isAdmin = userRole === 'admin'

  const bookingData = booking.booking
  const scheduledTime = dayjs(bookingData.starts_at)
  const isPast = scheduledTime.isBefore(dayjs())

  const formatPrice = (amount: number) => {
    return amount.toLocaleString('ru-RU') + ' ₸'
  }

  return (
    <>
      <Helmet>
        <title>Консультация #{(bookingData?.id ? String(bookingData.id).slice(0, 8) : '')} - MasterConnect</title>
      </Helmet>

      <div className="space-y-6">
        {/* Заголовок и навигация */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate(-1)}
            >
              <ChevronLeft className="h-4 w-4 mr-2" />
              Назад
            </Button>
            <div>
              <h1 className="text-2xl font-bold">
                Консультация #{bookingData?.id ? String(bookingData.id).slice(0, 8) : ''}
              </h1>
              <div className="flex items-center space-x-2 mt-1">
                <StatusBadge status={bookingData.status} />
                {isPast && <span className="text-sm text-muted-foreground">• Прошедшая</span>}
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Основная информация */}
          <div className="lg:col-span-2 space-y-6">
            {/* Детали консультации */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calendar className="h-5 w-5 mr-2" />
                  Детали консультации
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div className="flex items-center text-sm">
                      <Calendar className="h-4 w-4 mr-2 text-muted-foreground" />
                      <span>{scheduledTime.format('DD MMMM YYYY')}</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <Clock className="h-4 w-4 mr-2 text-muted-foreground" />
                      <span>{scheduledTime.format('HH:mm')} ({bookingData.duration_minutes} мин)</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <DollarSign className="h-4 w-4 mr-2 text-muted-foreground" />
                      <span>{formatPrice(bookingData.price_amount)}</span>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="text-sm">
                      <span className="text-muted-foreground">Создано:</span>
                      <br />
                      {dayjs(bookingData.created_at).format('DD.MM.YYYY в HH:mm')}
                    </div>
                    {bookingData.updated_at !== bookingData.created_at && (
                      <div className="text-sm">
                        <span className="text-muted-foreground">Обновлено:</span>
                        <br />
                        {dayjs(bookingData.updated_at).format('DD.MM.YYYY в HH:mm')}
                      </div>
                    )}
                  </div>
                </div>

                {/* Google Meet Link */}
                {bookingData.google_meet_link && bookingData.status === 'CONFIRMED' && (
                  <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-green-100 rounded-lg">
                          <Video className="h-6 w-6 text-green-600" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-green-900">Ссылка на консультацию</h4>
                          <p className="text-sm text-green-700">Google Meet готов к использованию</p>
                        </div>
                      </div>
                      <a
                        href={bookingData.google_meet_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                      >
                        Присоединиться
                        <ExternalLink className="h-4 w-4 ml-2" />
                      </a>
                    </div>
                    <div className="mt-3 text-sm text-green-700">
                      <p className="font-mono bg-white p-2 rounded border border-green-200 break-all">
                        {bookingData.google_meet_link}
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Участники */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <User className="h-5 w-5 mr-2" />
                  Участники
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Студент */}
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <User className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold">{bookingData.student_name ?? 'Студент'}</h3>
                        <p className="text-sm text-muted-foreground">Студент</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Ментор */}
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <UserCheck className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold">{bookingData.mentor_name ?? 'Ментор'}</h3>
                        <p className="text-sm text-muted-foreground">Ментор</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4 mt-2 text-sm">
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Анкета консультации */}
            {bookingData.intake_form && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <MessageCircle className="h-5 w-5 mr-2" />
                    Анкета консультации
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {bookingData.intake_form.goals && (
                    <div>
                      <h4 className="font-medium flex items-center mb-2">
                        <Target className="h-4 w-4 mr-2" />
                        Цели консультации
                      </h4>
                      <p className="text-sm text-muted-foreground pl-6">
                        {bookingData.intake_form.goals}
                      </p>
                    </div>
                  )}
                  
                  {bookingData.intake_form.specific_questions && (
                    <div>
                      <h4 className="font-medium flex items-center mb-2">
                        <MessageCircle className="h-4 w-4 mr-2" />
                        Конкретные вопросы
                      </h4>
                      <p className="text-sm text-muted-foreground pl-6">
                        {Array.isArray(bookingData.intake_form.specific_questions) 
                          ? bookingData.intake_form.specific_questions.join(', ')
                          : bookingData.intake_form.specific_questions}
                      </p>
                    </div>
                  )}
                  
                  {bookingData.intake_form.preferred_language && (
                    <div>
                      <h4 className="font-medium flex items-center mb-2">
                        <Languages className="h-4 w-4 mr-2" />
                        Предпочтительный язык
                      </h4>
                      <p className="text-sm text-muted-foreground pl-6">
                        {bookingData.intake_form.preferred_language}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Боковая панель */}
          <div className="space-y-6">
            {/* Действия */}
            <Card>
              <CardHeader>
                <CardTitle>Действия</CardTitle>
              </CardHeader>
              <CardContent>
                <BookingActions booking={bookingData} userRole={userRole} />
              </CardContent>
            </Card>

            {/* Статус и история */}
            <Card>
              <CardHeader>
                <CardTitle>Информация</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Текущий статус</h4>
                  <StatusBadge status={bookingData.status} />
                </div>

                {bookingData.notes && (
                  <div>
                    <h4 className="font-medium mb-2">Заметки</h4>
                    <p className="text-sm text-muted-foreground">
                      {bookingData.notes}
                    </p>
                  </div>
                )}

                <div className="pt-4 border-t">
                  <div className="text-xs text-muted-foreground space-y-1">
                    <p>ID: {bookingData.id}</p>
                    <p>Создано: {dayjs(bookingData.created_at).format('DD.MM.YYYY HH:mm')}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Контактная информация (только для подтвержденных консультаций) */}
            {bookingData.status === 'CONFIRMED' && (
              <Card>
                <CardHeader>
                  <CardTitle>Как подключиться</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm font-medium text-blue-900">
                        Ссылка на встречу доступна во вкладке "Детали консультации"
                      </p>
                    </div>
                    
                    <div className="text-xs text-muted-foreground">
                      <p>• Убедитесь, что у вас стабильное интернет-соединение</p>
                      <p>• Подготовьте вопросы заранее</p>
                      <p>• Найдите тихое место для разговора</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </>
  )
}
