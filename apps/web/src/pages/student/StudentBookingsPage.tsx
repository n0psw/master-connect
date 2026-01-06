import { useState, useMemo } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { Calendar, Clock, Filter, Search, CreditCard, X, AlertCircle, CheckCircle, XCircle } from 'lucide-react'
import { useQuery, useQueryClient } from 'react-query'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Card, CardContent } from '@/shared/ui/card'
import { bookingsApi } from '@/shared/api/bookings'
import { PaymentEvidenceUpload } from '@/shared/components/PaymentEvidenceUpload'
import { ReviewForm } from '@/shared/components/ReviewForm'
import { BookingStatusLabels, BookingStatusColors } from '@/shared/types/bookings'
import type { BookingSearchParams, BookingStatus } from '@/shared/types/bookings'

const StudentBookingStatusFilters: Partial<Record<BookingStatus, string>> = {
  'HOLD': 'Ожидает оплаты',
  'AWAITING_VERIFICATION': 'На проверке',
  'CONFIRMED': 'Подтверждено',
  'COMPLETED': 'Завершено',
  'CANCELLED': 'Отменено',
  'EXPIRED': 'Истекло'
}
import { getImageUrl } from '@/shared/utils/imageUtils'
import { formatDateTime, getClientTimezone } from '@/shared/lib/dayjs'

export const StudentBookingsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [showFilters, setShowFilters] = useState(false)
  const [paymentModal, setPaymentModal] = useState<{ bookingId: string } | null>(null)
  const [reviewModal, setReviewModal] = useState<{ bookingId: string; mentorName: string } | null>(null)
  const queryClient = useQueryClient()
  const clientTz = useMemo(() => getClientTimezone(), [])

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
    ['my-bookings', 'list', searchFilters],
    () => bookingsApi.getMyBookings(searchFilters),
    {
      keepPreviousData: true,
      refetchOnMount: true,
      refetchOnWindowFocus: true,
      staleTime: 30 * 1000,
      cacheTime: 60 * 1000,
      onError: (error: any) => {
        toast.error('Ошибка при загрузке бронирований: ' + (error?.detail || error?.message))
      }
    }
  )

  // Запрос статистики
  const { data: stats } = useQuery(
    ['booking-stats', 'student'],
    () => bookingsApi.getMyBookingStats(),
    {
      refetchOnWindowFocus: true,
      staleTime: 30 * 1000
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

  const formatDate = (dateString: string) => formatDateTime(dateString, clientTz, 'DD MMM YYYY, HH:mm')

  const formatPrice = (amount: number) => {
    return amount.toLocaleString('ru-RU') + ' ₸'
  }

  // Совместимость с разными вариантами API
  const getMentorName = (booking: any) => booking?.mentor?.name ?? booking?.mentor_name ?? 'Ментор'
  const getMentorAvatar = (booking: any) => {
    const url = booking?.mentor?.avatar_url ?? booking?.mentor_avatar_url ?? null
    return getImageUrl(url)
  }
  const getScheduledAt = (booking: any) => booking?.starts_at

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
          <Button 
            size="sm"
            onClick={() => setPaymentModal({ bookingId: booking.id })}
          >
            <CreditCard className="h-4 w-4 mr-2" />
            Я оплатил
          </Button>
        )
      
      case 'AWAITING_VERIFICATION':
        return (
          <div className="text-sm text-blue-600">
            Ожидает подтверждения админа
          </div>
        )
      
      case 'CONFIRMED':
        const isUpcoming = new Date(booking.starts_at) > new Date()
        return isUpcoming ? (
          <div className="text-sm text-green-600">
            Скоро состоится
          </div>
        ) : (
          <div className="text-sm text-muted-foreground">
            Прошедшая консультация
          </div>
        )
      
      case 'COMPLETED':
        // Показываем кнопку только если отзыв еще не оставлен
        if (booking.has_review) {
          return (
            <div className="text-sm text-green-600">
              Отзыв оставлен
            </div>
          )
        }
        return (
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => {
              const mentorName = getMentorName(booking)
              setReviewModal({ bookingId: booking.id, mentorName })
            }}
          >
            Оставить отзыв
          </Button>
        )
      
      default:
        return null
    }
  }

  return (
    <>
      <Helmet>
        <title>Мои бронирования - MasterConnect</title>
      </Helmet>

      <div className="space-y-8">
        {/* Заголовок */}
        <div>
          <h1 className="text-3xl font-bold mb-4">Мои бронирования</h1>
          <p className="text-muted-foreground">
            Управляйте своими консультациями с менторами
          </p>
        </div>

        {/* Статистика */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="text-2xl font-bold">{stats.total_bookings}</div>
                <p className="text-sm text-muted-foreground">Всего бронирований</p>
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

          <Button asChild>
            <Link to="/student/mentors">
              <Search className="h-4 w-4 mr-2" />
              Найти ментора
            </Link>
          </Button>
        </div>

        {/* Панель фильтров */}
        {showFilters && (
          <Card>
            <CardContent className="p-6">
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-3">Статус бронирования</h4>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(StudentBookingStatusFilters).map(([status, label]) => (
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
                    {bookingsData ? `Найдено ${bookingsData.total} бронирований` : ''}
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
            <p className="text-destructive">Ошибка при загрузке бронирований</p>
            <Button className="mt-4" onClick={() => window.location.reload()}>
              Попробовать снова
            </Button>
          </div>
        ) : !bookingsData?.bookings.length ? (
          <div className="text-center py-12">
            <Calendar className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <p className="text-xl font-medium mb-2">Бронирований не найдено</p>
            <p className="text-muted-foreground mb-6">
              Начните с поиска подходящего ментора
            </p>
            <Button asChild>
              <Link to="/student/mentors">
                Найти ментора
              </Link>
            </Button>
          </div>
        ) : (
          <>
            <div className="space-y-4">
              {bookingsData.bookings.map((booking) => (
                <Card key={booking.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-4">
                      {/* Аватар ментора */}
                      <div className="flex-shrink-0">
                        <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
                          {getMentorAvatar(booking) ? (
                            <img 
                              src={getMentorAvatar(booking) as string} 
                              alt={getMentorName(booking)} 
                              className="w-full h-full rounded-full object-cover"
                            />
                          ) : (
                            <span className="text-xl font-semibold text-primary">
                              {(getMentorName(booking) || 'М')[0].toUpperCase()}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Информация о бронировании */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="text-lg font-semibold mb-1 flex items-center">
                              {getMentorName(booking)}
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
                              
                              <span className="text-lg font-semibold">
                                {formatPrice(booking.price_amount)}
                              </span>
                            </div>
                          </div>

                          {/* Действия */}
                          <div className="flex flex-col items-end space-y-2">
                            <Link to={`/student/bookings/${booking.id}`}>
                              <Button variant="ghost" size="sm">
                                Подробнее
                              </Button>
                            </Link>
                            
                            {getActionButton(booking)}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Заметки */}
                    {booking.notes && (
                      <div className="mt-4 pt-4 border-t">
                        <p className="text-sm text-muted-foreground">
                          <strong>Заметки:</strong> {booking.notes}
                        </p>
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
              }}
            />
          </div>
        </div>
      )}

      {/* Модальное окно формы отзыва */}
      {reviewModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <ReviewForm
            bookingId={reviewModal.bookingId}
            mentorName={reviewModal.mentorName}
            onClose={() => setReviewModal(null)}
            onSuccess={() => {
              // Обновляем данные после успешного создания отзыва
              queryClient.invalidateQueries(['my-bookings'])
              queryClient.invalidateQueries(['my-reviews'])
            }}
          />
        </div>
      )}
    </>
  )
}
