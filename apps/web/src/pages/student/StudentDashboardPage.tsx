import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { Calendar, Clock, User, Search, BookOpen, AlertCircle, TrendingUp } from 'lucide-react'
import { useQuery, useQueryClient } from 'react-query'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { bookingsApi } from '@/shared/api/bookings'
import { PaymentEvidenceUpload } from '@/shared/components/PaymentEvidenceUpload'
import { useAuthStore } from '@/shared/store/auth'
import { BookingStatusLabels, BookingStatusColors } from '@/shared/types/bookings'
import { getImageUrl } from '@/shared/utils/imageUtils'

export const StudentDashboardPage = () => {
  const { user } = useAuthStore()
  const [paymentModal, setPaymentModal] = useState<{ bookingId: string } | null>(null)
  const queryClient = useQueryClient()

  // Загружаем статистику
  const { data: stats, isLoading: statsLoading } = useQuery(
    ['booking-stats', 'student'],
    () => bookingsApi.getMyBookingStats(),
    {
      refetchOnMount: true,
      refetchOnWindowFocus: true,
      staleTime: 30 * 1000,
      onError: (error: any) => {
        toast.error('Ошибка при загрузке статистики: ' + (error?.detail || error?.message))
      }
    }
  )

  // Загружаем последние бронирования
  const { data: recentBookings, isLoading: bookingsLoading } = useQuery(
    ['my-bookings', 'recent'],
    () => bookingsApi.getMyBookings({ 
      page: 1, 
      page_size: 5,
      sort: 'created_desc'
    }),
    {
      refetchOnMount: true,
      refetchOnWindowFocus: true,
      staleTime: 30 * 1000,
      cacheTime: 60 * 1000,
      refetchInterval: 60 * 1000,
      onError: (error: any) => {
        toast.error('Ошибка при загрузке бронирований: ' + (error?.detail || error?.message))
      }
    }
  )

  // Загружаем предстоящие консультации (только будущие)
  const { data: upcomingBookings } = useQuery(
    ['my-bookings', 'upcoming'],
    () => bookingsApi.getMyBookings({ 
      page: 1, 
      page_size: 10,
      status: ['CONFIRMED'],
      upcoming: true,
      sort: 'scheduled_asc'
    }),
    {
      refetchOnMount: true,
      refetchOnWindowFocus: true,
      staleTime: 30 * 1000,
      cacheTime: 60 * 1000,
      refetchInterval: 60 * 1000,
      onError: (error: any) => {
        toast.error('Ошибка при загрузке предстоящих консультаций: ' + (error?.detail || error?.message))
      }
    }
  )

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatPrice = (amount: number) => {
    return amount.toLocaleString('ru-RU') + ' ₸'
  }

  // Совместимость с разными формами API
  const getMentorName = (booking: any) => booking?.mentor?.name ?? booking?.mentor_name ?? 'Ментор'
  const getMentorAvatar = (booking: any) => {
    const url = booking?.mentor?.avatar_url ?? booking?.mentor_avatar_url ?? null
    return getImageUrl(url)
  }
  const getScheduledAt = (booking: any) => booking?.starts_at

  return (
    <>
      <Helmet>
        <title>Дашборд студента - MasterConnect</title>
      </Helmet>

      <div className="space-y-8">
        {/* Заголовок */}
        <div>
          <h1 className="text-3xl font-bold mb-2">
            Добро пожаловать, {user?.name || 'Студент'}!
          </h1>
          <p className="text-muted-foreground">
            Управляйте своими консультациями и отслеживайте прогресс
          </p>
        </div>

        {/* Быстрые действия */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Button asChild className="h-20 flex-col">
            <Link to="/student/mentors">
              <Search className="h-6 w-6 mb-2" />
              Найти ментора
            </Link>
          </Button>
          
          <Button variant="outline" asChild className="h-20 flex-col">
            <Link to="/student/bookings">
              <Calendar className="h-6 w-6 mb-2" />
              Мои бронирования
            </Link>
          </Button>
          
          <Button variant="outline" asChild className="h-20 flex-col">
            <Link to="/student/profile">
              <User className="h-6 w-6 mb-2" />
              Мой профиль
            </Link>
          </Button>
          
          <Button variant="outline" asChild className="h-20 flex-col">
            <Link to="/student/mentors?rating_min=4.5">
              <TrendingUp className="h-6 w-6 mb-2" />
              Топ менторы
            </Link>
          </Button>
        </div>

        {/* Статистика */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <BookOpen className="h-8 w-8 text-primary" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">
                    Всего консультаций
                  </p>
                  <div className="text-2xl font-bold">
                    {statsLoading ? '...' : stats?.total_bookings || 0}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Calendar className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">
                    Завершено
                  </p>
                  <div className="text-2xl font-bold">
                    {statsLoading ? '...' : stats?.completed || 0}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Clock className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">
                    Предстоящих
                  </p>
                  <div className="text-2xl font-bold">
                    {statsLoading ? '...' : stats?.confirmed || 0}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Предстоящие консультации */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Предстоящие консультации
                <Link to="/student/bookings?status=CONFIRMED">
                  <Button variant="ghost" size="sm">
                    Смотреть все
                  </Button>
                </Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {upcomingBookings?.bookings?.length ? (
                <div className="space-y-4 max-h-80 overflow-y-auto pr-2">
                  {upcomingBookings.bookings.map((booking) => (
                    <div key={booking.id} className="flex items-center space-x-4 p-4 border rounded-lg">
                      <div className="flex-shrink-0">
                        <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                          {getMentorAvatar(booking) ? (
                            <img 
                              src={getMentorAvatar(booking) as string} 
                              alt={getMentorName(booking)} 
                              className="w-full h-full rounded-full object-cover"
                            />
                          ) : (
                            <span className="font-semibold text-primary">
                              {(getMentorName(booking) || 'М')[0].toUpperCase()}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium truncate">
                            {getMentorName(booking)}
                          </p>
                          <span className="text-sm font-medium text-primary">
                            {formatPrice(booking.price_amount)}
                          </span>
                        </div>
                        
                        <div className="flex items-center text-sm text-muted-foreground mt-1">
                          <Calendar className="h-4 w-4 mr-1" />
                          {formatDate(getScheduledAt(booking))}
                          <Clock className="h-4 w-4 ml-3 mr-1" />
                          {booking.duration_minutes} мин
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Calendar className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground mb-4">
                    У вас нет предстоящих консультаций
                  </p>
                  <Button asChild>
                    <Link to="/student/mentors">
                      Найти ментора
                    </Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Последние бронирования */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Последние бронирования
                <Link to="/student/bookings">
                  <Button variant="ghost" size="sm">
                    Смотреть все
                  </Button>
                </Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {bookingsLoading ? (
                <div className="space-y-4">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="animate-pulse">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-muted rounded-full" />
                        <div className="flex-1">
                          <div className="h-4 bg-muted rounded mb-2" />
                          <div className="h-3 bg-muted rounded" />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : recentBookings?.bookings?.length ? (
                <div className="space-y-4">
                  {recentBookings.bookings.map((booking) => (
                    <div key={booking.id} className="flex items-center space-x-4 p-4 border rounded-lg">
                      <div className="flex-shrink-0">
                        <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                          {getMentorAvatar(booking) ? (
                            <img 
                              src={getMentorAvatar(booking) as string} 
                              alt={getMentorName(booking)} 
                              className="w-full h-full rounded-full object-cover"
                            />
                          ) : (
                            <span className="font-semibold text-primary">
                              {(getMentorName(booking) || 'М')[0].toUpperCase()}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium truncate">
                            {getMentorName(booking)}
                          </p>
                          <span className={`text-xs px-2 py-1 rounded-full ${BookingStatusColors[booking.status]}`}>
                            {BookingStatusLabels[booking.status]}
                          </span>
                        </div>
                        
                        <div className="flex items-center justify-between text-sm text-muted-foreground mt-1">
                          <span>{formatDate(getScheduledAt(booking))}</span>
                          <span>{formatPrice(booking.price_amount)}</span>
                        </div>

                        {/* Действия для разных статусов */}
                        {booking.status === 'HOLD' && (
                          <div className="mt-2">
                            <Button 
                              size="sm" 
                              onClick={() => setPaymentModal({ bookingId: booking.id })}
                            >
                              Оплатить
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground mb-4">
                    У вас еще нет бронирований
                  </p>
                  <Button asChild>
                    <Link to="/student/mentors">
                      Забронировать первую консультацию
                    </Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Подсказки и рекомендации */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertCircle className="h-5 w-5 mr-2 text-blue-500" />
              Полезные советы
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <h4 className="font-medium">Как выбрать ментора?</h4>
                <p className="text-sm text-muted-foreground">
                  Обращайте внимание на рейтинг, отзывы, университет и специализацию ментора.
                  Лучше выбирать верифицированных менторов с опытом в вашей области.
                </p>
              </div>
              
              <div className="space-y-2">
                <h4 className="font-medium">Подготовка к консультации</h4>
                <p className="text-sm text-muted-foreground">
                  Подготовьте список вопросов заранее. Расскажите о ваших целях и планах.
                  Имейте при себе документы или портфолио, если они релевантны.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Модальное окно загрузки доказательства оплаты */}
      {paymentModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <PaymentEvidenceUpload
              bookingId={paymentModal.bookingId}
              onClose={() => setPaymentModal(null)}
              onSuccess={() => {
                // Обновляем данные после успешной загрузки
                queryClient.invalidateQueries(['my-bookings'])
                queryClient.invalidateQueries(['booking-stats'])
              }}
            />
          </div>
        </div>
      )}
    </>
  )
}
