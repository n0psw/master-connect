import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Calendar,
  User,
  MessageCircle,
  Star,
  Clock,
  BookOpen,
} from 'lucide-react'

import { cn } from '@/shared/utils/cn'
import { useAuthStore } from '@/shared/store/auth'

import type { UserRole } from '@/shared/types/auth'

interface SidebarItem {
  to: string
  icon: React.ComponentType<{ className?: string }>
  label: string
  roles: UserRole[]
}

const sidebarItems: SidebarItem[] = [
  {
    to: '/student/dashboard',
    icon: LayoutDashboard,
    label: 'Дашборд',
    roles: ['student'],
  },
  {
    to: '/student/bookings',
    icon: Calendar,
    label: 'Мои сессии',
    roles: ['student'],
  },
  {
    to: '/student/reviews',
    icon: Star,
    label: 'Мои отзывы',
    roles: ['student'],
  },
  {
    to: '/student/profile',
    icon: User,
    label: 'Профиль',
    roles: ['student'],
  },
  {
    to: '/mentor/dashboard',
    icon: LayoutDashboard,
    label: 'Дашборд',
    roles: ['mentor'],
  },
  {
    to: '/mentor/bookings',
    icon: Calendar,
    label: 'Сессии',
    roles: ['mentor'],
  },
  {
    to: '/mentor/availability',
    icon: Clock,
    label: 'Доступность',
    roles: ['mentor'],
  },
  {
    to: '/mentor/profile',
    icon: User,
    label: 'Профиль',
    roles: ['mentor'],
  },
]

export const PrivateSidebar = () => {
  const location = useLocation()
  const { user } = useAuthStore()
  const chatPath =
    user?.role === 'mentor' ? '/mentor/chat' : user?.role === 'student' ? '/student/chat' : '#'

  const filteredItems = sidebarItems.filter(item =>
    user?.role && item.roles.includes(user.role)
  )

  return (
    <div className="w-64 border-r bg-background">
      {/* Логотип */}
      <div className="p-6 border-b">
        <div className="flex items-center space-x-3">
          <img src="/masteredlogo-ico.ico" alt="MasterConnect" className="h-10 w-10" />
          <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">MasterConnect</span>
        </div>
      </div>

      {/* Навигация */}
      <nav className="p-4 space-y-2">
        {filteredItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.to || 
            (item.to !== '/dashboard' && location.pathname.startsWith(item.to))

          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={cn(
                'flex items-center space-x-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      {/* Дополнительные ссылки */}
      <div className="p-4 mt-auto border-t">
        <div className="space-y-2">
          <NavLink
            to={chatPath}
            onClick={(event) => {
              if (chatPath === '#') {
                event.preventDefault()
              }
            }}
            className="flex items-center space-x-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
          >
            <MessageCircle className="h-4 w-4" />
            <span>Чат</span>
          </NavLink>
          
          {user?.role === 'student' && (
            <NavLink
              to="/student/mentors"
              className="flex items-center space-x-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
            >
              <BookOpen className="h-4 w-4" />
              <span>Каталог менторов</span>
            </NavLink>
          )}
        </div>
      </div>
    </div>
  )
}
