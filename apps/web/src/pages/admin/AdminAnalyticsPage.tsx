import { useState } from 'react'
import { Helmet } from 'react-helmet-async'
import { useQuery } from 'react-query'
import {
  BarChart3,
  TrendingUp,
  DollarSign,
  Users,
  Calendar,
  Clock,
  Star,
  Download,
  RefreshCw,
  Filter,
  ChevronDown,
} from 'lucide-react'

import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { adminApi } from '@/shared/api/admin'

// Компонент выбора периода (placeholder UI)
interface PeriodSelectorProps {
  period: 'daily' | 'weekly' | 'monthly'
  days: number
  onPeriodChange: (period: 'daily' | 'weekly' | 'monthly') => void
  onDaysChange: (days: number) => void
}

const PeriodSelector = ({ period, days, onPeriodChange, onDaysChange }: PeriodSelectorProps) => {
  return (
    <div className="flex items-center gap-4">
      <div>
        <label className="text-sm font-medium mr-2">Период:</label>
        <select
          value={period}
          onChange={(e) => onPeriodChange(e.target.value as any)}
          className="px-3 py-2 border border-input rounded-md bg-background"
        >
          <option value="daily">По дням</option>
          <option value="weekly">По неделям</option>
          <option value="monthly">По месяцам</option>
        </select>
      </div>
      <div>
        <label className="text-sm font-medium mr-2">За последние:</label>
        <select
          value={days}
          onChange={(e) => onDaysChange(Number(e.target.value))}
          className="px-3 py-2 border border-input rounded-md bg-background"
        >
          <option value={7}>7 дней</option>
          <option value={14}>14 дней</option>
          <option value={30}>30 дней</option>
          <option value={60}>60 дней</option>
          <option value={90}>90 дней</option>
        </select>
      </div>
    </div>
  )
}

// Компонент метрики
interface MetricCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  loading?: boolean
}

const MetricCard = ({ title, value, icon, loading }: MetricCardProps) => {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="h-8 w-20 bg-muted animate-pulse rounded" />
        ) : (
          <div className="text-2xl font-bold">{value}</div>
        )}
      </CardContent>
    </Card>
  )
}

export const AdminAnalyticsPage = () => {
  const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly'>('monthly')
  const [days, setDays] = useState(30)

  // Загружаем данные дашборда для основных метрик
  const { 
    data: dashboardStats, 
    isLoading: isLoadingDashboard,
    refetch: refetchDashboard 
  } = useQuery(
    ['admin-dashboard-stats'],
    () => adminApi.getDashboard(),
    {
      onError: (error: any) => {
        console.error('Ошибка при загрузке статистики дашборда:', error)
      }
    }
  )

  // Загружаем детальную аналитику из /admin/analytics
  const { 
    data: analytics, 
    isLoading: isLoadingAnalytics,
    refetch: refetchAnalytics 
  } = useQuery(
    ['admin-analytics'],
    () => adminApi.getAnalytics(),
    {
      onError: (error: any) => {
        console.error('Ошибка при загрузке аналитики:', error)
      }
    }
  )

  // Функция обновления всех данных
  const handleRefresh = () => {
    refetchDashboard()
    refetchAnalytics()
  }

  const isLoading = isLoadingDashboard || isLoadingAnalytics

  // Используем данные из дашборда для основных метрик
  const totalRevenue = dashboardStats?.total_revenue 
    ? parseFloat(dashboardStats.total_revenue.toString()) 
    : 0
  const totalBookings = dashboardStats?.total_bookings ?? 0
  
  // Вычисляем среднюю цену из аналитики или рассчитываем
  const avgBookingPrice = analytics?.average_session_price
    ? parseFloat(analytics.average_session_price.toString())
    : (totalBookings > 0 && totalRevenue > 0 ? totalRevenue / totalBookings : 0)
  
  // Количество активных менторов из распределения пользователей или дашборда
  const activeMentors = analytics?.user_distribution?.['MENTOR'] ?? dashboardStats?.total_mentors ?? 0

  // Форматирование валюты (KZT - казахстанский тенге)
  const formatCurrency = (amount: number) => {
    return `${Math.round(amount).toLocaleString('ru-RU')} ₸`
  }

  return (
    <>
      <Helmet>
        <title>Аналитика и отчеты - MasterConnect Admin</title>
      </Helmet>

      <div className="space-y-8">
        {/* Заголовок */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Аналитика и отчеты</h1>
            <p className="text-muted-foreground">
              Детальная аналитика работы платформы
            </p>
          </div>
          <Button 
            variant="outline" 
            onClick={handleRefresh}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Обновить данные
          </Button>
        </div>

        {/* Селектор периода (пока влияет только на отображение) */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Filter className="h-5 w-5 mr-2" />
              Настройки отчета
            </CardTitle>
          </CardHeader>
          <CardContent>
            <PeriodSelector
              period={period}
              days={days}
              onPeriodChange={setPeriod}
              onDaysChange={setDays}
            />
          </CardContent>
        </Card>

        {/* Основные метрики */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Общий доход"
            value={formatCurrency(totalRevenue)}
            icon={<DollarSign className="h-4 w-4 text-muted-foreground" />}
            loading={isLoading}
          />
          <MetricCard
            title="Всего бронирований"
            value={totalBookings.toLocaleString('ru-RU')}
            icon={<Calendar className="h-4 w-4 text-muted-foreground" />}
            loading={isLoading}
          />
          <MetricCard
            title="Средняя цена"
            value={formatCurrency(avgBookingPrice)}
            icon={<TrendingUp className="h-4 w-4 text-muted-foreground" />}
            loading={isLoading}
          />
          <MetricCard
            title="Активных менторов"
            value={activeMentors}
            icon={<Users className="h-4 w-4 text-muted-foreground" />}
            loading={isLoading}
          />
        </div>

        {/* Дополнительные блоки (заглушки под будущие графики) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center">
                <BarChart3 className="h-5 w-5 mr-2" />
                Динамика показателей
              </CardTitle>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Экспорт
              </Button>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground">
                Графики будут добавлены после уточнения контрактов отчетов.
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Clock className="h-5 w-5 mr-2" />
                Популярные временные слоты
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground">
                Детализация популярных слотов появится после добавления соответствующих эндпоинтов.
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  )
}
