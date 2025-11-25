import { useState } from 'react'
import { useSearchParams, Link, useNavigate } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { Calendar, Clock, Filter, X, AlertCircle, CheckCircle, XCircle, MessageSquare } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Card, CardContent } from '@/shared/ui/card'
import { bookingsApi } from '@/shared/api/bookings'
import { BookingStatusLabels, BookingStatusColors } from '@/shared/types/bookings'
import type { BookingSearchParams, BookingStatus } from '@/shared/types/bookings'
import { getImageUrl } from '@/shared/utils/imageUtils'

export const MentorBookingsPage = () => {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const [showFilters, setShowFilters] = useState(false)
  const [loadingBookingId, setLoadingBookingId] = useState<string | null>(null)

  // Извлекаем параметры из URL
  const currentPage = parseInt(searchParams.get('page') || '1')
  const selectedStatuses = searchParams.get('status')?.split(',').filter(Boolean) as BookingStatus[] || []
  const sortBy = searchParams.get('sort') || 'created_desc'

  // Подготавливаем параметры поиска
  const searchFilters: BookingSearchParams = {
    page: currentPage,
    page_size: 12,
    sort: sortBy as any,
    status: selectedStatuses.length > 0 ? selectedStatuses : undefined
  }

  // Запрос бронирований
  const { 
    data: bookingsData, 
    isLoading, 
    error 
  } = useQuery(
    ['my-bookings', 'mentor-list', searchFilters],
    () => bookingsApi.getMyBookings(searchFilters),
    {
      keepPreviousData: true,
      onError: (error: any) => {
        toast.error('Ошибка при загрузке бронирований: ' + (error?.detail || error?.message))
      }
    }
  )

  // Запрос статистики
  const { data: stats } = useQuery(
    ['booking-stats', 'mentor'],
    () => bookingsApi.getMyBookingStats()
  )

  const queryClient = useQueryClient()

  const markCompletedMutation = useMutation(
    (bookingId: string) => bookingsApi.markCompletedByMentor(bookingId),
    {
      onMutate: (bookingId) => {
        setLoadingBookingId(bookingId)
      },
      onSuccess: () => {
        toast.success('Консультация отмечена как завершенная')
        queryClient.invalidateQueries(['my-bookings', 'mentor-list'])
        queryClient.invalidateQueries(['booking-stats', 'mentor'])
        setLoadingBookingId(null)
      },
      onError: (error: any) => {
        toast.error('Ошибка: ' + (error?.detail || error?.message))
        setLoadingBookingId(null)
      }
    }
  )

  // Обновление URL параметров
  const updateSearchParams = (newParams: Record<string, string | undefined>) => {
    const params = new URLSearchParams(searchParams)
    
    Object.entries(newParams).forEach(([key, value]) => {
      if (value) {
        params.set(key, value)
      } else {
        params.delete(key)
      }
    })
    
    // Сбрасываем страницу при изменении фильтров
    if (!newParams.page) {
      params.delete('page')
    }
    
    setSearchParams(params)
  }

  const handlePageChange = (page: number) => {
    updateSearchParams({ page: page.toString() })
  }

  const handleStatusFilter = (status: BookingStatus) => {
    const newStatuses = selectedStatuses.includes(status)
      ? selectedStatuses.filter(s => s !== status)
      : [...selectedStatuses, status]
    
    updateSearchParams({ 
      status: newStatuses.length > 0 ? newStatuses.join(',') : undefined 
    })
  }

  const clearFilters = () => {
    setSearchParams(new URLSearchParams())
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
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

  const getStatusIcon = (status: BookingStatus) => {
    switch (status) {
      case 'HOLD':
        return <Clock className="h-4 w-4" />
      case 'AWAITING_VERIFICATION':
        return <AlertCircle className="h-4 w-4" />
      case 'CONFIRMED':
        return <CheckCircle className="h-4 w-4" />
      case 'COMPLETED':
        return <CheckCircle className="h-4 w-4" />
      case 'CANCELLED':
        return <XCircle className="h-4 w-4" />
      case 'NO_SHOW_STUDENT':
      case 'NO_SHOW_MENTOR':
        return <XCircle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getActionButton = (booking: any) => {
    switch (booking.status) {
      case 'HOLD':
        return (
          <div className="text-sm text-orange-600">
            Ожидает оплаты студентом
          </div>
        )
      
      case 'AWAITING_VERIFICATION':
        return (
          <div className="text-sm text-blue-600">
            Ожидает подтверждения админа
          </div>
        )
      
      case 'CONFIRMED':
        const isUpcoming = new Date(getScheduledAt(booking)) > new Date()
        return (
          <div className="flex flex-col gap-2">
            <Button 
              variant="default" 
              size="sm"
              onClick={() => {
                if (!loadingBookingId || loadingBookingId !== booking.id) {
                  markCompletedMutation.mutate(booking.id)
                }
              }}
              disabled={loadingBookingId === booking.id}
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              {loadingBookingId === booking.id ? 'Завершение...' : 'Консультация проведена'}
            </Button>
            {isUpcoming && (
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => navigate(`/mentor/chat?booking=${booking.id}`)}
              >
                <MessageSquare className="h-4 w-4 mr-2" />
                Связаться со студентом
              </Button>
            )}
          </div>
        )
      
      case 'COMPLETED':
        return (
          <div className="text-sm text-green-600 font-medium">
            +{formatPrice(getPrice(booking))}
          </div>
        )
      
      default:
        return null
    }
  }

  return (
    <>
      <Helmet>
        <title>Мои консультации - MasterConnect</title>
      </Helmet>

      <div className="space-y-8">
        {/* Заголовок */}
        <div>
          <h1 className="text-3xl font-bold mb-4">Мои консультации</h1>
          <p className="text-muted-foreground">
            Управляйте консультациями со студентами и отслеживайте доходы
          </p>
        </div>

        {/* Статистика */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="text-2xl font-bold">{stats.total_bookings}</div>
                <p className="text-sm text-muted-foreground">Всего консультаций</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
                <p className="text-sm text-muted-foreground">Завершено</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="text-2xl font-bold text-blue-600">{stats.confirmed}</div>
                <p className="text-sm text-muted-foreground">Подтверждено</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="text-2xl font-bold text-green-600">
                  {formatPrice(Number(stats.total_revenue) || 0)}
                </div>
                <p className="text-sm text-muted-foreground">Заработано</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Фильтры */}
        <div className="flex flex-col sm:flex-row gap-4">
          <Button
            variant="outline"
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2"
          >
            <Filter className="h-4 w-4" />
            Фильтры
            {selectedStatuses.length > 0 && (
              <span className="bg-primary text-primary-foreground text-xs px-1.5 py-0.5 rounded-full">
                {selectedStatuses.length}
              </span>
            )}
          </Button>

          <select
            value={sortBy}
            onChange={(e) => updateSearchParams({ sort: e.target.value })}
            className="px-3 py-2 border rounded-md bg-background"
          >
            <option value="created_desc">Сначала новые</option>
            <option value="created_asc">Сначала старые</option>
            <option value="scheduled_desc">По дате консультации (убыв.)</option>
            <option value="scheduled_asc">По дате консультации (возр.)</option>
          </select>

          <Button asChild variant="outline">
            <Link to="/mentor/availability">
              <Clock className="h-4 w-4 mr-2" />
              Настроить расписание
            </Link>
          </Button>
        </div>

        {/* Панель фильтров */}
        {showFilters && (
          <Card>
            <CardContent className="p-6">
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-3">Статус консультации</h4>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(BookingStatusLabels).map(([status, label]) => (
                      <Button
                        key={status}
                        variant={selectedStatuses.includes(status as BookingStatus) ? "default" : "outline"}
                        size="sm"
                        onClick={() => handleStatusFilter(status as BookingStatus)}
                      >
                        {getStatusIcon(status as BookingStatus)}
                        <span className="ml-2">{label}</span>
                      </Button>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={clearFilters}
                    disabled={selectedStatuses.length === 0}
                  >
                    <X className="h-4 w-4 mr-2" />
                    Очистить фильтры
                  </Button>
                  
                  <div className="text-sm text-muted-foreground">
                    {bookingsData ? `Найдено ${bookingsData.total} консультаций` : ''}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Список бронирований */}
        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 bg-muted rounded-full" />
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-muted rounded w-3/4" />
                      <div className="h-3 bg-muted rounded w-1/2" />
                    </div>
                    <div className="h-8 w-20 bg-muted rounded" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-destructive">Ошибка при загрузке консультаций</p>
            <Button className="mt-4" onClick={() => window.location.reload()}>
              Попробовать снова
            </Button>
          </div>
        ) : !bookingsData?.bookings.length ? (
          <div className="text-center py-12">
            <Calendar className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <p className="text-xl font-medium mb-2">Консультаций не найдено</p>
            <p className="text-muted-foreground mb-6">
              Заполните профиль и настройте расписание, чтобы студенты могли вас найти
            </p>
            <div className="flex justify-center gap-4">
              <Button asChild>
                <Link to="/mentor/profile">
                  Заполнить профиль
                </Link>
              </Button>
              <Button variant="outline" asChild>
                <Link to="/mentor/availability">
                  Настроить расписание
                </Link>
              </Button>
            </div>
          </div>
        ) : (
          <>
            <div className="space-y-4">
              {bookingsData.bookings.map((booking) => (
                <Card key={booking.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-4">
                      {/* Аватар студента */}
                      <div className="flex-shrink-0">
                        <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
                          {getStudentAvatar(booking) ? (
                            <img 
                              src={getStudentAvatar(booking) as string} 
                              alt={getStudentName(booking)} 
                              className="w-full h-full rounded-full object-cover"
                            />
                          ) : (
                            <span className="text-xl font-semibold text-primary">
                              {(getStudentName(booking) || 'С')[0].toUpperCase()}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Информация о бронировании */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="text-lg font-semibold mb-1">
                              {getStudentName(booking)}
                            </h3>
                            
                            <div className="flex items-center text-sm text-muted-foreground mb-2">
                              <Calendar className="h-4 w-4 mr-1" />
                              {formatDate(getScheduledAt(booking))}
                              <Clock className="h-4 w-4 ml-4 mr-1" />
                              {booking.duration_minutes} мин
                            </div>

                            <div className="flex items-center space-x-4">
                              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${BookingStatusColors[booking.status]}`}>
                                {getStatusIcon(booking.status)}
                                <span className="ml-2">{BookingStatusLabels[booking.status]}</span>
                              </span>
                              
                              <span className={`text-lg font-semibold ${
                                booking.status === 'COMPLETED' ? 'text-green-600' : ''
                              }`}>
                                {booking.status === 'COMPLETED' ? '+' : ''}{formatPrice(getPrice(booking))}
                              </span>
                            </div>
                          </div>

                          {/* Действия */}
                          <div className="flex flex-col items-end space-y-2">
                            <Link to={`/mentor/bookings/${booking.id}`}>
                              <Button variant="ghost" size="sm">
                                Подробнее
                              </Button>
                            </Link>
                            
                            {getActionButton(booking)}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Информация из анкеты студента */}
                    {booking.intake_form && (
                      <div className="mt-4 pt-4 border-t">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                          {booking.intake_form.goals && (
                            <div>
                              <strong className="text-muted-foreground">Цели:</strong>
                              <p className="mt-1 line-clamp-2">{booking.intake_form.goals}</p>
                            </div>
                          )}
                          {booking.intake_form.current_situation && (
                            <div>
                              <strong className="text-muted-foreground">Текущая ситуация:</strong>
                              <p className="mt-1 line-clamp-2">{booking.intake_form.current_situation}</p>
                            </div>
                          )}
                          {(booking.intake_form.experience || booking.intake_form.previous_experience) && (
                            <div>
                              <strong className="text-muted-foreground">Опыт:</strong>
                              <p className="mt-1 line-clamp-2">
                                {booking.intake_form.previous_experience || booking.intake_form.experience}
                              </p>
                            </div>
                          )}
                        </div>
                        
                        {(booking.intake_form.specific_questions || booking.intake_form.questions || booking.notes) && (
                          <div className="mt-3">
                            <strong className="text-muted-foreground text-sm">Вопросы:</strong>
                            <div className="text-sm mt-1">
                              {Array.isArray(booking.intake_form.specific_questions) ? (
                                <ul className="list-disc list-inside space-y-1">
                                  {booking.intake_form.specific_questions.map((q: string, idx: number) => (
                                    <li key={idx}>{q}</li>
                                  ))}
                                </ul>
                              ) : (
                                <p>{booking.intake_form.questions || booking.notes}</p>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Пагинация */}
            {bookingsData.total_pages > 1 && (
              <div className="flex justify-center mt-8">
                <div className="flex items-center space-x-2">
                  {/* Предыдущая */}
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={currentPage <= 1}
                    onClick={() => handlePageChange(currentPage - 1)}
                  >
                    Назад
                  </Button>

                  {/* Номера страниц */}
                  {Array.from({ length: Math.min(bookingsData.total_pages, 5) }, (_, i) => {
                    const page = i + 1
                    return (
                      <Button
                        key={page}
                        variant={currentPage === page ? "default" : "outline"}
                        size="sm"
                        onClick={() => handlePageChange(page)}
                      >
                        {page}
                      </Button>
                    )
                  })}

                  {/* Следующая */}
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={currentPage >= bookingsData.total_pages}
                    onClick={() => handlePageChange(currentPage + 1)}
                  >
                    Далее
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </>
  )
}
