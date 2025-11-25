import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  GraduationCap,
  Calendar,
  BarChart3,
  Settings,
  Shield,
  FileText,
  AlertTriangle,
  MessageSquare,
} from 'lucide-react'

import { cn } from '@/shared/utils/cn'

interface SidebarItem {
  to: string
  icon: React.ComponentType<{ className?: string }>
  label: string
  badge?: number
}

const sidebarItems: SidebarItem[] = [
  {
    to: '/admin/dashboard',
    icon: LayoutDashboard,
    label: 'Дашборд',
  },
  {
    to: '/admin/users',
    icon: Users,
    label: 'Пользователи',
  },
  {
    to: '/admin/mentors',
    icon: GraduationCap,
    label: 'Менторы',
    badge: 3, // Ожидают верификации
  },
  {
    to: '/admin/bookings',
    icon: Calendar,
    label: 'Бронирования',
    badge: 12, // Ожидают подтверждения оплаты
  },
  {
    to: '/admin/chat',
    icon: MessageSquare,
    label: 'Чаты',
  },
  {
    to: '/admin/analytics',
    icon: BarChart3,
    label: 'Аналитика',
  },
]

const systemItems: SidebarItem[] = [
  {
    to: '/admin/audit',
    icon: FileText,
    label: 'Аудит лог',
  },
  {
    to: '/admin/reports',
    icon: AlertTriangle,
    label: 'Отчеты',
  },
  {
    to: '/admin/settings',
    icon: Settings,
    label: 'Настройки',
  },
]

export const AdminSidebar = () => {
  const location = useLocation()

  const renderNavItem = (item: SidebarItem) => {
    const Icon = item.icon
    const isActive = location.pathname === item.to

    return (
      <NavLink
        key={item.to}
        to={item.to}
        className={cn(
          'flex items-center justify-between rounded-md px-3 py-2 text-sm font-medium transition-colors',
          isActive
            ? 'bg-red-600 text-white'
            : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
        )}
      >
        <div className="flex items-center space-x-3">
          <Icon className="h-4 w-4" />
          <span>{item.label}</span>
        </div>
        
        {item.badge && item.badge > 0 && (
          <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full">
            {item.badge}
          </span>
        )}
      </NavLink>
    )
  }

  return (
    <div className="w-64 border-r bg-background">
      {/* Админ логотип */}
      <div className="p-6 border-b bg-gradient-to-br from-red-50 to-pink-50">
        <div className="flex items-center space-x-3">
          <img src="/masteredlogo-ico.ico" alt="MasterConnect" className="h-10 w-10" />
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-lg font-bold">MasterConnect</span>
              <div className="flex h-5 w-5 items-center justify-center rounded-full bg-red-600 text-white">
                <Shield className="h-3 w-3" />
              </div>
            </div>
            <p className="text-xs text-red-600 font-medium">Admin Panel</p>
          </div>
        </div>
      </div>

      {/* Основная навигация */}
      <div className="p-4">
        <div className="space-y-2">
          <h3 className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Управление
          </h3>
          {sidebarItems.map(renderNavItem)}
        </div>

        {/* Системные настройки */}
        <div className="space-y-2 mt-8">
          <h3 className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Система
          </h3>
          {systemItems.map(renderNavItem)}
        </div>
      </div>

      {/* Статус системы */}
      <div className="p-4 mt-auto border-t">
        <div className="rounded-md bg-green-50 p-3">
          <div className="flex items-center space-x-2">
            <div className="h-2 w-2 rounded-full bg-green-500"></div>
            <span className="text-sm text-green-700">Система работает</span>
          </div>
          <p className="text-xs text-green-600 mt-1">
            Все сервисы доступны
          </p>
        </div>
      </div>
    </div>
  )
}
