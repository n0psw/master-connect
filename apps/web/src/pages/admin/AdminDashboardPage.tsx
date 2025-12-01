import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useQuery } from 'react-query'
import { toast } from 'sonner'
import { 
  Users, 
  Calendar, 
  DollarSign, 
  Star, 
  TrendingUp, 
  TrendingDown,
  Activity,
  Shield,
  Clock,
  AlertCircle,
  CheckCircle,
  XCircle,
  Loader,
} from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { adminApi } from '@/shared/api/admin'

// Компонент статистической карточки
interface StatCardProps {
  title: string
  value: string | number
  change?: number
  icon: React.ReactNode
  loading?: boolean
}

const StatCard = ({ title, value, change, icon, loading }: StatCardProps) => {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center">
            <Loader className="h-4 w-4 animate-spin mr-2" />
            <div className="h-7 w-16 bg-muted animate-pulse rounded" />
          </div>
        ) : (
          <>
            <div className="text-2xl font-bold">{value}</div>
            {change !== undefined && (
              <p className={`text-xs flex items-center mt-1 ${
                change > 0 ? 'text-green-600' : change < 0 ? 'text-red-600' : 'text-muted-foreground'
              }`}>
                {change > 0 ? (
                  <TrendingUp className="h-3 w-3 mr-1" />
                ) : change < 0 ? (
                  <TrendingDown className="h-3 w-3 mr-1" />
                ) : null}
                {change > 0 ? '+' : ''}{change.toFixed?.(1) ?? change}% за месяц
              </p>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}

// Компонент быстрых действий
interface QuickActionProps {
  title: string
  description: string
  icon: React.ReactNode
  onClick: () => void
  variant?: 'default' | 'warning' | 'destructive'
}

const QuickAction = ({ title, description, icon, onClick, variant = 'default' }: QuickActionProps) => {
  const bgColor = {
    default: 'hover:bg-muted',
    warning: 'hover:bg-yellow-50 border-yellow-200',
    destructive: 'hover:bg-red-50 border-red-200'
  }[variant]

  return (
    <Card 
      className={`cursor-pointer transition-colors ${bgColor}`}
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${
            variant === 'warning' ? 'bg-yellow-100 text-yellow-600' :
            variant === 'destructive' ? 'bg-red-100 text-red-600' :
            'bg-primary/10 text-primary'
          }`}>
            {icon}
          </div>
          <div className="flex-1">
            <h3 className="font-medium">{title}</h3>
            <p className="text-sm text-muted-foreground">{description}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export const AdminDashboardPage = () => {
  // Загрузка общей статистики с бэка
  const { data: stats, isLoading: statsLoading } = useQuery(
    ['admin-dashboard'],
    () => adminApi.getDashboard(),
    {
      refetchOnMount: true,
      refetchOnWindowFocus: true,
      staleTime: 30 * 1000,
      cacheTime: 60 * 1000,
      refetchInterval: 5 * 60 * 1000,
      onError: (error: any) => {
        console.error('Ошибка при загрузке статистики:', error)
      }
    }
  )

  const navigate = useNavigate()

  const handleQuickAction = (action: string) => {
    switch (action) {
      case 'users':
        navigate('/admin/users')
        break
      case 'bookings':
        navigate('/admin/bookings')
        break
      case 'mentors':
        navigate('/admin/mentors')
        break
      case 'analytics':
        navigate('/admin/analytics')
        break
      case 'settings':
        toast.info('Настройки системы будут доступны в следующей версии')
        break
      case 'export':
        toast.info('Экспорт данных будет доступен в следующей версии')
        break
      default:
        console.log('Unknown action:', action)
    }
  }

  return (
    <>
      <Helmet>
        <title>Административная панель - MasterConnect</title>
      </Helmet>

      <div className="space-y-8">
        {/* Заголовок */}
        <div>
          <h1 className="text-3xl font-bold mb-4">Административная панель</h1>
          <p className="text-muted-foreground">
            Обзор системы и управление платформой
          </p>
        </div>

        {/* Основная статистика */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Всего пользователей"
            value={stats?.total_users ?? 0}
            icon={<Users className="h-4 w-4 text-muted-foreground" />}
            loading={statsLoading}
          />
          
          <StatCard
            title="Активных менторов"
            value={stats?.total_mentors ?? 0}
            icon={<Shield className="h-4 w-4 text-muted-foreground" />}
            loading={statsLoading}
          />

          <StatCard
            title="Всего бронирований"
            value={stats?.total_bookings ?? 0}
            icon={<Calendar className="h-4 w-4 text-muted-foreground" />}
            loading={statsLoading}
          />

          <StatCard
            title="Доход за месяц"
            value={stats?.monthly_revenue ? `${Number(stats.monthly_revenue).toLocaleString()} ₸` : '0 ₸'}
            icon={<DollarSign className="h-4 w-4 text-muted-foreground" />}
            loading={statsLoading}
          />
        </div>

        {/* Детальная статистика */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Статистика пользователей */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="h-5 w-5 mr-2" />
                Пользователи
              </CardTitle>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="flex justify-between items-center">
                      <div className="h-4 bg-muted animate-pulse rounded w-24" />
                      <div className="h-4 bg-muted animate-pulse rounded w-16" />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Студенты</span>
                    <span className="font-medium">{stats?.total_students ?? 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Менторы</span>
                    <span className="font-medium">{stats?.total_mentors ?? 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Активные</span>
                    <span className="font-medium">{stats?.active_users ?? 0}</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Статистика бронирований */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="h-5 w-5 mr-2" />
                Бронирования
              </CardTitle>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="flex justify-between items-center">
                      <div className="h-4 bg-muted animate-pulse rounded w-32" />
                      <div className="h-4 bg-muted animate-pulse rounded w-16" />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm flex items-center">
                      <Clock className="h-3 w-3 mr-1" />
                      Ожидают подтверждения
                    </span>
                    <span className="font-medium text-yellow-600">{stats?.pending_bookings ?? 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm flex items-center">
                      <Activity className="h-3 w-3 mr-1" />
                      Завершены
                    </span>
                    <span className="font-medium text-green-600">{stats?.completed_bookings ?? 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm flex items-center">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      Всего
                    </span>
                    <span className="font-medium">{stats?.total_bookings ?? 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm flex items-center">
                      <DollarSign className="h-3 w-3 mr-1" />
                      Выручка
                    </span>
                    <span className="font-medium text-primary">{stats?.total_revenue ? `${Number(stats.total_revenue).toLocaleString()} ₸` : '0 ₸'}</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Статистика менторов */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Star className="h-5 w-5 mr-2" />
              Менторы
            </CardTitle>
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="text-center">
                    <div className="h-8 bg-muted animate-pulse rounded mb-2" />
                    <div className="h-4 bg-muted animate-pulse rounded" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold">{stats?.total_mentors ?? 0}</div>
                  <div className="text-sm text-muted-foreground">Всего менторов</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{stats?.total_students ?? 0}</div>
                  <div className="text-sm text-muted-foreground">Всего студентов</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{stats?.active_users ?? 0}</div>
                  <div className="text-sm text-muted-foreground">Активных пользователей</div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Быстрые действия */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Быстрые действия</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <QuickAction
              title="Управление пользователями"
              description="Просмотр, активация и управление пользователями"
              icon={<Users className="h-4 w-4" />}
              onClick={() => handleQuickAction('users')}
            />
            
            <QuickAction
              title="Управление бронированиями"
              description="Просмотр и управление бронированиями консультаций"
              icon={<Calendar className="h-4 w-4" />}
              onClick={() => handleQuickAction('bookings')}
            />

            <QuickAction
              title="Управление менторами"
              description="Просмотр и управление менторами платформы"
              icon={<Star className="h-4 w-4" />}
              onClick={() => handleQuickAction('mentors')}
            />

            <QuickAction
              title="Аналитика и отчеты"
              description="Детальная аналитика работы платформы"
              icon={<TrendingUp className="h-4 w-4" />}
              onClick={() => handleQuickAction('analytics')}
            />

            <QuickAction
              title="Настройки системы"
              description="Конфигурация платформы и настройки"
              icon={<Shield className="h-4 w-4" />}
              onClick={() => handleQuickAction('settings')}
            />

            <QuickAction
              title="Экспорт данных"
              description="Экспорт данных пользователей и бронирований"
              icon={<DollarSign className="h-4 w-4" />}
              onClick={() => handleQuickAction('export')}
            />
          </div>
        </div>

        {/* Системные предупреждения */}
        {stats && (stats.pending_bookings ?? 0) > 10 && (
          <Card className="border-yellow-200 bg-yellow-50">
            <CardHeader>
              <CardTitle className="flex items-center text-yellow-800">
                <AlertCircle className="h-5 w-5 mr-2" />
                Требуется внимание
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-sm text-yellow-700">
                  • {stats.pending_bookings} бронирований ожидают подтверждения оплаты
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </>
  )
}
