import { useState } from 'react'
import { Helmet } from 'react-helmet-async'
import { useSearchParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { toast } from 'sonner'
import {
  Calendar,
  Search,
  Filter,
  MoreHorizontal,
  Eye,
  Check,
  X,
  Clock,
  DollarSign,
  User,
  UserCheck,
  Download,
  RefreshCw,
  ChevronDown,
  AlertCircle,
  CheckCircle,
  XCircle,
  Timer,
} from 'lucide-react'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'

import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { PaymentEvidenceViewer } from '@/shared/components/PaymentEvidenceViewer'
import { adminApi } from '@/shared/api/admin'
import { bookingsApi } from '@/shared/api/bookings'
import { BookingStatusLabels, BookingStatusColors } from '@/shared/types/bookings'
import type { AdminBooking, AdminBookingSearchParams, AdminBookingAction } from '@/shared/types/admin'

dayjs.locale('ru')

// Безопасные геттеры для разных форматов API
const getScheduledAt = (b: any) => b?.starts_at
const getPrice = (b: any) => b?.price_usd ?? b?.price_amount ?? 0

// Компонент фильтров
interface FiltersProps {
  onFilterChange: (filters: Partial<AdminBookingSearchParams>) => void
  currentFilters: AdminBookingSearchParams
}

const Filters = ({ onFilterChange, currentFilters }: FiltersProps) => {
  const [showFilters, setShowFilters] = useState(false)

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <Button
          variant="outline"
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-2"
        >
          <Filter className="h-4 w-4" />
          Фильтры
          <ChevronDown className={`h-4 w-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
        </Button>
        
        {Object.keys(currentFilters).filter(key => 
          currentFilters[key as keyof AdminBookingSearchParams] !== undefined &&
          currentFilters[key as keyof AdminBookingSearchParams] !== null &&
          currentFilters[key as keyof AdminBookingSearchParams] !== ''
        ).length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onFilterChange({})}
            className="text-muted-foreground"
          >
            <X className="h-4 w-4 mr-1" />
            Сбросить
          </Button>
        )}
      </div>

      {showFilters && (
        <Card>
          <CardContent className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Статус</label>
                <select
                  value={currentFilters.status?.join(',') || ''}
                  onChange={(e) => onFilterChange({ 
                    status: e.target.value ? e.target.value.split(',') : undefined 
                  })}
                  className="w-full px-3 py-2 border border-input rounded-md bg-background"
                >
                  <option value="">Все статусы</option>
                  <option value="HOLD">Ожидает оплаты</option>
                  <option value="AWAITING_VERIFICATION">Ожидает подтверждения</option>
                  <option value="CONFIRMED">Подтверждено</option>
                  <option value="COMPLETED">Завершено</option>
                  <option value="CANCELLED">Отменено</option>
                  <option value="NO_SHOW_STUDENT">Неявка студента</option>
                  <option value="NO_SHOW_MENTOR">Неявка ментора</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Дата от</label>
                <Input
                  type="date"
                  value={currentFilters.date_from || ''}
                  onChange={(e) => onFilterChange({ date_from: e.target.value || undefined })}
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Дата до</label>
                <Input
                  type="date"
                  value={currentFilters.date_to || ''}
                  onChange={(e) => onFilterChange({ date_to: e.target.value || undefined })}
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Сортировка</label>
                <select
                  value={currentFilters.sort || 'created_desc'}
                  onChange={(e) => onFilterChange({ sort: e.target.value as any })}
                  className="w-full px-3 py-2 border border-input rounded-md bg-background"
                >
                  <option value="created_desc">Сначала новые</option>
                  <option value="created_asc">Сначала старые</option>
                  <option value="scheduled_desc">По дате (убыв.)</option>
                  <option value="scheduled_asc">По дате (возр.)</option>
                  <option value="price_desc">По цене (убыв.)</option>
                  <option value="price_asc">По цене (возр.)</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// Компонент действий с бронированием
interface BookingActionsProps {
  booking: AdminBooking
  onAction: (action: AdminBookingAction) => void
  onVerifyPayment: (bookingId: string) => void
}

const BookingActions = ({ booking, onAction, onVerifyPayment }: BookingActionsProps) => {
  const [showMenu, setShowMenu] = useState(false)

  const canConfirm = booking.status === 'AWAITING_VERIFICATION'
  const canCancel = ['HOLD', 'AWAITING_VERIFICATION', 'CONFIRMED'].includes(booking.status)
  const canComplete = booking.status === 'CONFIRMED' && dayjs(getScheduledAt(booking)).isBefore(dayjs())
  const canMarkNoShow = booking.status === 'CONFIRMED' && dayjs(getScheduledAt(booking)).add(1, 'hour').isBefore(dayjs())

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setShowMenu(!showMenu)}
      >
        <MoreHorizontal className="h-4 w-4" />
      </Button>

      {showMenu && (
        <div className="absolute right-0 top-full mt-1 w-56 bg-background border rounded-lg shadow-lg z-10">
          <div className="py-1">
            <Link
              to={`/admin/bookings/${booking.id}`}
              className="w-full px-4 py-2 text-left text-sm hover:bg-muted flex items-center"
              onClick={() => setShowMenu(false)}
            >
              <Eye className="h-4 w-4 mr-2" />
              Просмотреть детали
            </Link>

            {canConfirm && (
              <button
                className="w-full px-4 py-2 text-left text-sm hover:bg-muted flex items-center text-green-600"
                onClick={() => {
                  onVerifyPayment(booking.id)
                  setShowMenu(false)
                }}
              >
                <CheckCircle className="h-4 w-4 mr-2" />
                Проверить оплату
              </button>
            )}


            {canComplete && (
              <button
                className="w-full px-4 py-2 text-left text-sm hover:bg-muted flex items-center text-blue-600"
                onClick={() => {
                  onAction({ action: 'mark_completed', booking_id: booking.id })
                  setShowMenu(false)
                }}
              >
                <Check className="h-4 w-4 mr-2" />
                Отметить как завершенное
              </button>
            )}

            {canMarkNoShow && (
              <button
                className="w-full px-4 py-2 text-left text-sm hover:bg-muted flex items-center text-orange-600"
                onClick={() => {
                  onAction({ action: 'mark_no_show', booking_id: booking.id })
                  setShowMenu(false)
                }}
              >
                <Timer className="h-4 w-4 mr-2" />
                Отметить неявку
              </button>
            )}

            {canCancel && (
              <>
                <div className="border-t my-1" />
                <button
                  className="w-full px-4 py-2 text-left text-sm hover:bg-muted flex items-center text-red-600"
                  onClick={() => {
                    onAction({ action: 'cancel', booking_id: booking.id })
                    setShowMenu(false)
                  }}
                >
                  <XCircle className="h-4 w-4 mr-2" />
                  Отменить бронирование
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// Компонент статусного бейджа
const StatusBadge = ({ status }: { status: string }) => {
  const color = BookingStatusColors[status as keyof typeof BookingStatusColors] || 'bg-gray-100 text-gray-700'
  const label = BookingStatusLabels[status as keyof typeof BookingStatusLabels] || status

  const getIcon = () => {
    switch (status) {
      case 'HOLD':
        return <Clock className="h-3 w-3 mr-1" />
      case 'AWAITING_VERIFICATION':
        return <AlertCircle className="h-3 w-3 mr-1" />
      case 'CONFIRMED':
        return <CheckCircle className="h-3 w-3 mr-1" />
      case 'COMPLETED':
        return <Check className="h-3 w-3 mr-1" />
      case 'CANCELLED':
        return <XCircle className="h-3 w-3 mr-1" />
      case 'NO_SHOW_STUDENT':
      case 'NO_SHOW_MENTOR':
        return <Timer className="h-3 w-3 mr-1" />
      default:
        return null
    }
  }

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium flex items-center w-fit ${color}`}>
      {getIcon()}
      {label}
    </span>
  )
}

// Основной компонент
export const AdminBookingsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [paymentVerificationModal, setPaymentVerificationModal] = useState<{ bookingId: string } | null>(null)
  const queryClient = useQueryClient()

  // Извлечение параметров из URL
  const searchFilters: AdminBookingSearchParams = {
    page: parseInt(searchParams.get('page') || '1'),
    page_size: parseInt(searchParams.get('page_size') || '20'),
    search: searchParams.get('search') || undefined,
    status: searchParams.get('status')?.split(',').filter(Boolean) || undefined,
    date_from: searchParams.get('date_from') || undefined,
    date_to: searchParams.get('date_to') || undefined,
    sort: (searchParams.get('sort') as any) || 'created_desc',
  }

  // Загрузка бронирований
  const { data: bookingsData, isLoading, error } = useQuery(
    ['admin-bookings', searchFilters],
    () => adminApi.getBookings(searchFilters),
    {
      keepPreviousData: true,
      onError: (error: any) => {
        toast.error('Ошибка при загрузке бронирований: ' + (error?.detail || error?.message))
      }
    }
  )

  const totalPages = bookingsData
    ? Math.max(
        1,
        Math.ceil(
          (bookingsData.total || 0) /
            (bookingsData.page_size || searchFilters.page_size || 20)
        )
      )
    : 1

  // Мутация для выполнения действий
  const bookingActionMutation = useMutation(adminApi.performBookingAction, {
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-bookings'])
      toast.success('Действие выполнено успешно!')
    },
    onError: (error: any) => {
      toast.error('Ошибка при выполнении действия: ' + (error?.detail || error?.message))
    }
  })


  // Мутация для экспорта
  const exportMutation = useMutation(
    () => adminApi.exportBookings(searchFilters, 'csv'),
    {
      onSuccess: (blob) => {
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `bookings-export-${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        toast.success('Файл экспорта загружен!')
      },
      onError: (error: any) => {
        toast.error('Ошибка при экспорте: ' + (error?.detail || error?.message))
      }
    }
  )

  // Обновление URL при изменении фильтров
  const updateFilters = (newFilters: Partial<AdminBookingSearchParams>) => {
    const updatedParams = new URLSearchParams(searchParams)
    
    Object.entries({ ...searchFilters, ...newFilters }).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        if (Array.isArray(value)) {
          updatedParams.set(key, value.join(','))
        } else {
          updatedParams.set(key, value.toString())
        }
      } else {
        updatedParams.delete(key)
      }
    })
    
    // Сбрасываем страницу при изменении фильтров
    if (Object.keys(newFilters).some(key => key !== 'page')) {
      updatedParams.set('page', '1')
    }
    
    setSearchParams(updatedParams)
  }

  const handleBookingAction = (action: AdminBookingAction) => {
    bookingActionMutation.mutate(action)
  }


  const handleExport = () => {
    exportMutation.mutate()
  }

  const formatDateTime = (dateString: string) => {
    return dayjs(dateString).format('DD.MM.YYYY в HH:mm')
  }

  const formatDuration = (minutes: number) => {
    return `${minutes} мин`
  }

  return (
    <>
      <Helmet>
        <title>Управление бронированиями - MasterConnect Admin</title>
      </Helmet>

      <div className="space-y-6">
        {/* Заголовок */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Управление бронированиями</h1>
            <p className="text-muted-foreground">
              {bookingsData?.total || 0} бронирований в системе
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleExport}
              disabled={exportMutation.isLoading}
            >
              <Download className="h-4 w-4 mr-2" />
              {exportMutation.isLoading ? 'Экспорт...' : 'Экспорт CSV'}
            </Button>
            <Button
              variant="outline"
              onClick={() => queryClient.invalidateQueries(['admin-bookings'])}
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Обновить
            </Button>
          </div>
        </div>

        {/* Поиск и фильтры */}
        <div className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Поиск по имени студента, ментора или email..."
              value={searchFilters.search || ''}
              onChange={(e) => updateFilters({ search: e.target.value || undefined })}
              className="pl-10"
            />
          </div>

          <Filters
            currentFilters={searchFilters}
            onFilterChange={updateFilters}
          />
        </div>

        {/* Статистика */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">{bookingsData?.total || 0}</div>
              <div className="text-sm text-muted-foreground">Всего</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-yellow-600">
                {bookingsData?.bookings?.filter(b => b.status === 'AWAITING_VERIFICATION').length || 0}
              </div>
              <div className="text-sm text-muted-foreground">Ожидают</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-green-600">
                {bookingsData?.bookings?.filter(b => b.status === 'CONFIRMED').length || 0}
              </div>
              <div className="text-sm text-muted-foreground">Подтверждены</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-blue-600">
                {bookingsData?.bookings?.filter(b => b.status === 'COMPLETED').length || 0}
              </div>
              <div className="text-sm text-muted-foreground">Завершены</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-red-600">
                {bookingsData?.bookings?.filter(b => b.status === 'CANCELLED').length || 0}
              </div>
              <div className="text-sm text-muted-foreground">Отменены</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-green-600">
                {((bookingsData?.bookings?.reduce((sum, b) => sum + (b.status === 'COMPLETED' ? (Number(getPrice(b)) || 0) : 0), 0) ?? 0)).toFixed(0)}
              </div>
              <div className="text-sm text-muted-foreground">Доход</div>
            </CardContent>
          </Card>
        </div>

        {/* Таблица бронирований */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Calendar className="h-5 w-5 mr-2" />
              Бронирования
            </CardTitle>
          </CardHeader>
          <CardContent>
            {error ? (
              <div className="text-center py-8">
                <div className="text-red-600 mb-2">Ошибка при загрузке данных</div>
                <Button onClick={() => queryClient.invalidateQueries(['admin-bookings'])}>
                  Попробовать снова
                </Button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4">Участники</th>
                      <th className="text-left py-3 px-4">Консультация</th>
                      <th className="text-left py-3 px-4">Статус</th>
                      <th className="text-left py-3 px-4">Стоимость</th>
                      <th className="text-left py-3 px-4">Создано</th>
                      <th className="text-right py-3 px-4">Действия</th>
                    </tr>
                  </thead>
                  <tbody>
                    {isLoading ? (
                      // Скелетоны загрузки
                      Array.from({ length: 5 }).map((_, i) => (
                        <tr key={i} className="border-b">
                          <td className="py-4 px-4">
                            <div className="space-y-2">
                              <div className="h-4 w-40 bg-muted rounded animate-pulse" />
                              <div className="h-3 w-32 bg-muted rounded animate-pulse" />
                            </div>
                          </td>
                          <td className="py-4 px-4">
                            <div className="space-y-2">
                              <div className="h-4 w-36 bg-muted rounded animate-pulse" />
                              <div className="h-3 w-24 bg-muted rounded animate-pulse" />
                            </div>
                          </td>
                          <td className="py-4 px-4">
                            <div className="h-6 w-28 bg-muted rounded animate-pulse" />
                          </td>
                          <td className="py-4 px-4">
                            <div className="h-4 w-16 bg-muted rounded animate-pulse" />
                          </td>
                          <td className="py-4 px-4">
                            <div className="h-4 w-20 bg-muted rounded animate-pulse" />
                          </td>
                          <td className="py-4 px-4">
                            <div className="h-8 w-8 bg-muted rounded animate-pulse ml-auto" />
                          </td>
                        </tr>
                      ))
                    ) : bookingsData?.bookings?.length ? (
                      bookingsData.bookings.map((booking) => (
                        <tr key={booking.id} className="border-b hover:bg-muted/50">
                          <td className="py-4 px-4">
                            <div className="space-y-2">
                              <div className="flex items-center text-sm">
                                <User className="h-3 w-3 mr-1 text-blue-600" />
                                <span className="font-medium">{booking.student_name}</span>
                              </div>
                              <div className="text-xs text-muted-foreground">
                                {booking.student_email}
                              </div>
                              <div className="flex items-center text-sm">
                                <UserCheck className="h-3 w-3 mr-1 text-green-600" />
                                <span className="font-medium">{booking.mentor_name}</span>
                              </div>
                              <div className="text-xs text-muted-foreground">
                                {booking.mentor_email}
                              </div>
                            </div>
                          </td>
                          <td className="py-4 px-4">
                            <div className="space-y-2">
                              <div className="flex items-center text-sm">
                                <Calendar className="h-3 w-3 mr-1 text-muted-foreground" />
                                {formatDateTime(getScheduledAt(booking) as string)}
                              </div>
                              <div className="flex items-center text-sm text-muted-foreground">
                                <Clock className="h-3 w-3 mr-1" />
                                {formatDuration(booking.duration_minutes)}
                              </div>
                            </div>
                          </td>
                          <td className="py-4 px-4">
                            <div className="space-y-2">
                              <StatusBadge status={booking.status} />
                              {booking.status === 'AWAITING_VERIFICATION' && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="text-xs"
                                  onClick={() => setPaymentVerificationModal({ bookingId: booking.id })}
                                >
                                  <CheckCircle className="h-3 w-3 mr-1" />
                                  Проверить
                                </Button>
                              )}
                            </div>
                          </td>
                          <td className="py-4 px-4">
                            <div className="flex items-center text-sm font-medium">
                              <DollarSign className="h-3 w-3 mr-1 text-green-600" />
                              {getPrice(booking)}
                            </div>
                          </td>
                          <td className="py-4 px-4">
                            <div className="text-sm text-muted-foreground">
                              {formatDateTime(booking.created_at)}
                            </div>
                          </td>
                          <td className="py-4 px-4">
                            <div className="flex justify-end">
                              <BookingActions 
                                booking={booking} 
                                onAction={handleBookingAction}
                                onVerifyPayment={(bookingId) => setPaymentVerificationModal({ bookingId })}
                              />
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={6} className="text-center py-8 text-muted-foreground">
                          Бронирования не найдены
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {/* Пагинация */}
            {bookingsData && totalPages > 1 && (
              <div className="flex items-center justify-between mt-6">
                <div className="text-sm text-muted-foreground">
                  Показано {((bookingsData.page - 1) * bookingsData.page_size) + 1} - {Math.min(bookingsData.page * bookingsData.page_size, bookingsData.total)} из {bookingsData.total} бронирований
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => updateFilters({ page: Math.max(1, bookingsData.page - 1) })}
                    disabled={bookingsData.page <= 1 || isLoading}
                  >
                    Предыдущая
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => updateFilters({ page: Math.min(totalPages, bookingsData.page + 1) })}
                    disabled={bookingsData.page >= totalPages || isLoading}
                  >
                    Следующая
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Модальное окно проверки доказательств оплаты */}
      {paymentVerificationModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <PaymentEvidenceViewer
              bookingId={paymentVerificationModal.bookingId}
              onClose={() => setPaymentVerificationModal(null)}
              onSuccess={() => {
                // Обновляем данные после успешной проверки
                queryClient.invalidateQueries(['admin-bookings'])
                queryClient.invalidateQueries(['moderation-queue'])
              }}
            />
          </div>
        </div>
      )}
    </>
  )
}
