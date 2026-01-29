import { Link } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { Calendar, Clock, DollarSign, Star, Users, TrendingUp, BookOpen, Settings, AlertTriangle } from 'lucide-react'
import { useQuery } from 'react-query'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { bookingsApi } from '@/shared/api/bookings'
import { mentorsApi } from '@/shared/api/mentors'
import { useAuthStore } from '@/shared/store/auth'
import { BookingStatusLabels, BookingStatusColors } from '@/shared/types/bookings'
import { getImageUrl } from '@/shared/utils/imageUtils'

export const MentorDashboardPage = () => {
  const { user } = useAuthStore()

  // Загружаем статистику
  const { data: stats, isLoading: statsLoading } = useQuery(
    ['booking-stats', 'mentor'],
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

  // Загружаем профиль ментора
  const { data: mentorProfile } = useQuery(
    ['mentor-profile', 'me'],
    () => mentorsApi.getMyMentorProfile(),
    {
      onError: (error: any) => {
        // Если ментор еще не создал профиль, не показываем ошибку
        if (!error?.detail?.includes('не найден')) {
          toast.error('Ошибка при загрузке профиля: ' + (error?.detail || error?.message))
        }
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
      onError: (error: any) => {
        toast.error('Ошибка при загрузке бронирований: ' + (error?.detail || error?.message))
      }
    }
  )

  // Загружаем предстоящие консультации
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
      onError: (error: any) => {
        toast.error('Ошибка при загрузке предстоящих консультаций: ' + (error?.detail || error?.message))
      }
    }
  )

  // Загружаем бронирования, ожидающие подтверждения
  const { data: pendingBookings } = useQuery(
    ['my-bookings', 'pending'],
    () => bookingsApi.getMyBookings({ 
      page: 1, 
      page_size: 5,
      status: ['AWAITING_VERIFICATION'],
      sort: 'created_desc'
    }),
    {
      refetchOnMount: true,
      refetchOnWindowFocus: true,
      staleTime: 30 * 1000,
      cacheTime: 60 * 1000
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

  const getStudentName = (b: any) => b?.student?.name ?? b?.student_name ?? 'Студент'
  const getStudentAvatar = (b: any) => {
    const url = b?.student?.avatar_url ?? b?.student_avatar_url ?? null
    return getImageUrl(url)
  }
  const getScheduledAt = (b: any) => b?.starts_at
  const getPrice = (b: any) => b?.price_amount ?? b?.price ?? 0

  // Проверяем, заполнен ли профиль ментора
  const isProfileIncomplete = !mentorProfile || 
    !mentorProfile.bio || 
    !mentorProfile.headline ||
    mentorProfile.languages.length === 0 ||
    (!mentorProfile.price_30 && !mentorProfile.price_60)

  return (
    <>
      <Helmet>
        <title>Дашборд ментора - MasterConnect</title>
      </Helmet>

      <div className="space-y-8">
        {/* Заголовок */}
        <div>
          <h1 className="text-3xl font-bold mb-2">
            Добро пожаловать, {user?.name || 'Ментор'}!
          </h1>
          <div className="flex items-center justify-between">
            <p className="text-muted-foreground">
              Управляйте своими консультациями и отслеживайте доходы
            </p>
            {mentorProfile && (
              <div className="flex items-center text-sm">
                <Star className="h-4 w-4 text-yellow-500 mr-1" />
                <span className="font-medium">{(Number(mentorProfile.rating_avg) || 0).toFixed(1)}</span>
                <span className="text-muted-foreground ml-1">
                  ({mentorProfile.rating_count} отзывов)
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Предупреждение о незаполненном профиле */}
        {isProfileIncomplete && (
          <Card className="border-orange-200 bg-orange-50">
            <CardContent className="p-4">
              <div className="flex items-center">
                <AlertTriangle className="h-5 w-5 text-orange-500 mr-3" />
                <div className="flex-1">
                  <p className="font-medium text-orange-800">Профиль не заполнен</p>
                  <p className="text-sm text-orange-600">
                    Заполните профиль, чтобы студенты могли вас найти и забронировать консультации.
                  </p>
                </div>
                <Button asChild size="sm">
                  <Link to="/mentor/profile">
                    Заполнить профиль
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Быстрые действия */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Button asChild className="h-20 flex-col">
            <Link to="/mentor/profile">
              <Settings className="h-6 w-6 mb-2" />
              Мой профиль
            </Link>
          </Button>
          
          <Button variant="outline" asChild className="h-20 flex-col">
            <Link to="/mentor/bookings">
              <Calendar className="h-6 w-6 mb-2" />
              Мои бронирования
            </Link>
          </Button>
          
          <Button variant="outline" asChild className="h-20 flex-col">
            <Link to="/mentor/availability">
              <Clock className="h-6 w-6 mb-2" />
              Расписание
            </Link>
          </Button>
          
          <Button variant="outline" asChild className="h-20 flex-col">
            <Link to={`/mentors/${user?.id}`}>
              <Users className="h-6 w-6 mb-2" />
              Моя страница
            </Link>
          </Button>
        </div>

        {/* Статистика */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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
                    {statsLoading ? '...' : stats?.completed_bookings || 0}
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
                    {statsLoading ? '...' : stats?.upcoming_bookings || 0}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <DollarSign className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">
                    Заработок
                  </p>
                  <div className="text-2xl font-bold">
                    {statsLoading ? '...' : formatPrice(stats?.total_earned || 0)}
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
                <Link to="/mentor/bookings?status=CONFIRMED">
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
                          {getStudentAvatar(booking) ? (
                            <img 
                              src={getStudentAvatar(booking) as string} 
                              alt={getStudentName(booking)} 
                              className="w-full h-full rounded-full object-cover"
                            />
                          ) : (
                            <span className="font-semibold text-primary">
                              {(getStudentName(booking) || 'С')[0].toUpperCase()}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium truncate">
                            {getStudentName(booking)}
                          </p>
                          <span className="text-sm font-medium text-green-600">
                            +{formatPrice(getPrice(booking))}
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
                  {isProfileIncomplete ? (
                    <Button asChild>
                      <Link to="/mentor/profile">
                        Заполнить профиль
                      </Link>
                    </Button>
                  ) : (
                    <Button asChild variant="outline">
                      <Link to="/mentor/availability">
                        Настроить расписание
                      </Link>
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Ожидающие подтверждения */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Ожидают подтверждения
                {pendingBookings?.bookings?.length ? (
                  <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                    {pendingBookings.bookings.length}
                  </span>
                ) : null}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {pendingBookings?.bookings?.length ? (
                <div className="space-y-4 max-h-80 overflow-y-auto pr-2">
                  {pendingBookings.bookings.map((booking) => (
                    <div key={booking.id} className="flex items-center space-x-4 p-4 border rounded-lg bg-blue-50 border-blue-200">
                      <div className="flex-shrink-0">
                        <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                          {getStudentAvatar(booking) ? (
                            <img 
                              src={getStudentAvatar(booking) as string} 
                              alt={getStudentName(booking)} 
                              className="w-full h-full rounded-full object-cover"
                            />
                          ) : (
                            <span className="font-semibold text-blue-600">
                              {(getStudentName(booking) || 'С')[0].toUpperCase()}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium truncate">
                            {booking.student?.name || getStudentName(booking)}
                          </p>
                          <span className="text-sm font-medium text-blue-600">
                            {formatPrice(booking.price_amount)}
                          </span>
                        </div>
                        
                        <div className="flex items-center text-sm text-muted-foreground mt-1">
                          <Calendar className="h-4 w-4 mr-1" />
                          {formatDate(booking.starts_at)}
                          <Clock className="h-4 w-4 ml-3 mr-1" />
                          {booking.duration_minutes} мин
                        </div>

                        <p className="text-xs text-blue-600 mt-2">
                          Студент отметил оплату, ожидается подтверждение админа
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Clock className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">
                    Нет бронирований, ожидающих подтверждения
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Последние бронирования */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Последние бронирования
              <Link to="/mentor/bookings">
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
                        {getStudentAvatar(booking) ? (
                          <img 
                            src={getStudentAvatar(booking) as string} 
                            alt={getStudentName(booking)} 
                            className="w-full h-full rounded-full object-cover"
                          />
                        ) : (
                          <span className="font-semibold text-primary">
                            {(getStudentName(booking) || 'С')[0].toUpperCase()}
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium truncate">
                          {getStudentName(booking)}
                        </p>
                        <span className={`text-xs px-2 py-1 rounded-full ${BookingStatusColors[booking.status]}`}>
                          {BookingStatusLabels[booking.status]}
                        </span>
                      </div>
                      
                      <div className="flex items-center justify-between text-sm text-muted-foreground mt-1">
                        <span>{formatDate(getScheduledAt(booking))}</span>
                        <span className={booking.status === 'COMPLETED' ? 'text-green-600 font-medium' : ''}>
                          {booking.status === 'COMPLETED' ? '+' : ''}{formatPrice(getPrice(booking))}
                        </span>
                      </div>
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
                {isProfileIncomplete ? (
                  <Button asChild>
                    <Link to="/mentor/profile">
                      Заполнить профиль для привлечения студентов
                    </Link>
                  </Button>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    Студенты скоро найдут вас через каталог менторов
                  </p>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Советы для менторов */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-5 w-5 mr-2 text-blue-500" />
              Советы для успешного менторинга
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <h4 className="font-medium">Качественный профиль</h4>
                <p className="text-sm text-muted-foreground">
                  Заполните детальную информацию о себе, добавьте фото, укажите свой опыт 
                  и университеты. Это поможет студентам лучше понять, подходите ли вы им.
                </p>
              </div>
              
              <div className="space-y-2">
                <h4 className="font-medium">Быстрые ответы</h4>
                <p className="text-sm text-muted-foreground">
                  Отвечайте на вопросы студентов быстро и подробно. Проводите консультации 
                  в назначенное время. Это повысит ваш рейтинг и привлечет больше студентов.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  )
}
