import { useMemo, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { User, Menu, LogOut, X, ArrowRight, Users, Info, HelpCircle } from 'lucide-react'

import { Button } from '@/shared/ui/button'
import { useAuthStore } from '@/shared/store/auth'
import { NotificationBell } from '@/shared/components/NotificationBell'

export const PublicHeader = () => {
  const location = useLocation()
  const { isAuthenticated, user, logout } = useAuthStore()
  const [isMobileOpen, setIsMobileOpen] = useState(false)

  const navItems = useMemo(
    () => [
      { 
        label: 'Менторы', 
        href: '/mentors', 
        icon: Users,
        gradient: 'from-blue-500 to-cyan-500',
        bgGradient: 'from-blue-50 to-cyan-50',
        decoration: 'blue'
      },
      { 
        label: 'О платформе', 
        href: '/about', 
        icon: Info,
        gradient: 'from-indigo-500 to-purple-500',
        bgGradient: 'from-indigo-50 to-purple-50',
        decoration: 'purple'
      },
      { 
        label: 'FAQ', 
        href: '/faq', 
        icon: HelpCircle,
        gradient: 'from-violet-500 to-fuchsia-500',
        bgGradient: 'from-violet-50 to-fuchsia-50',
        decoration: 'pink'
      }
    ],
    []
  )

  const isActive = (href: string) => {
    if (href === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(href)
  }

  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-[rgba(16,24,40,0.08)] bg-white/85 backdrop-blur-xl supports-[backdrop-filter]:bg-white/75 shadow-[0_18px_44px_-28px_rgba(16,24,40,0.6)]">
      <div className="container-wide flex items-center justify-between gap-3 sm:gap-6 py-2.5 sm:py-3">
        <div className="flex items-center gap-3 sm:gap-6 min-w-0">
          <Link to="/" className="flex items-center gap-1.5 sm:gap-2 flex-shrink-0">
            <img src="/masteredlogo-ico.ico" alt="MasterConnect" className="h-7 w-7 sm:h-9 sm:w-9" />
            <span className="text-base sm:text-lg font-bold text-[#101828] hidden xs:inline">MasterConnect</span>
          </Link>
          <nav className="hidden items-center gap-3 md:flex">
            {navItems.map((item) => {
              const Icon = item.icon
              const isItemActive = isActive(item.href)
              
              const getHoverTextColor = () => {
                if (item.decoration === 'blue') return 'hover:text-blue-600'
                if (item.decoration === 'purple') return 'hover:text-indigo-600'
                if (item.decoration === 'pink') return 'hover:text-violet-600'
                return 'hover:text-primary'
              }
              
              return (
                <Link
                  key={item.href}
                  to={item.href}
                  className={`relative rounded-full px-4 sm:px-6 py-2 sm:py-3 text-xs sm:text-sm font-semibold transition-all duration-300 flex items-center gap-1.5 sm:gap-2.5 group overflow-hidden ${
                    isItemActive
                      ? `bg-gradient-to-r ${item.gradient} text-white shadow-lg`
                      : `text-[#475467] hover:bg-gradient-to-r ${item.bgGradient} ${getHoverTextColor()}`
                  }`}
                >
                  {!isItemActive && (
                    <>
                      <div className={`absolute -top-2 -right-2 w-8 h-8 rounded-full bg-gradient-to-br ${item.gradient} opacity-0 group-hover:opacity-20 blur-xl transition-opacity duration-500`} />
                      <div className={`absolute -bottom-2 -left-2 w-6 h-6 rounded-full bg-gradient-to-tr ${item.gradient} opacity-0 group-hover:opacity-15 blur-lg transition-opacity duration-500`} />
                    </>
                  )}
                  {isItemActive && (
                    <>
                      <div className={`absolute inset-0 bg-gradient-to-r ${item.gradient} opacity-100`} />
                      <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_30%_20%,rgba(255,255,255,0.3),transparent_50%)]" />
                      <div className="absolute -top-4 -right-4 w-16 h-16 rounded-full bg-white/10 blur-2xl" />
                      <div className="absolute -bottom-4 -left-4 w-12 h-12 rounded-full bg-white/10 blur-xl" />
                    </>
                  )}
                  <Icon className={`h-4 w-4 relative z-10 transition-all duration-300 ${
                    isItemActive ? 'scale-110 drop-shadow-sm' : 'group-hover:scale-110 group-hover:rotate-3'
                  }`} />
                  <span className="relative z-10">{item.label}</span>
                  {isItemActive && (
                    <>
                      <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-white animate-pulse shadow-lg" />
                      <div className="absolute inset-0 border-2 border-white/30 rounded-full animate-ping opacity-20" />
                    </>
                  )}
                </Link>
              )
            })}
          </nav>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          {!isAuthenticated && (
            <Button variant="gradient" className="hidden h-11 rounded-full px-6 text-sm font-semibold lg:flex" asChild>
              <Link to="/mentors">
                Подобрать наставника
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          )}
          {isAuthenticated ? (
            <div className="hidden items-center gap-2 rounded-full border border-[rgba(16,24,40,0.08)] bg-white/80 px-2.5 py-1.5 shadow-sm md:flex">
              <div className="flex items-center gap-1.5 min-w-0">
                <User className="h-4 w-4 text-primary flex-shrink-0" />
                <span className="text-sm font-medium text-[#101828] truncate max-w-[120px]">{user?.name || 'Профиль'}</span>
              </div>
              <NotificationBell />
              <Button variant="outline" size="sm" className="rounded-full border-none bg-[rgba(28,63,227,0.08)] px-3 py-1.5 text-xs font-semibold text-primary whitespace-nowrap" asChild>
                <Link to={getDashboardPath(user?.role)}>Кабинет</Link>
              </Button>
              <Button variant="ghost" size="icon" className="text-[#475467] hover:text-primary h-8 w-8 flex-shrink-0" onClick={handleLogout} title="Выйти">
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <div className="hidden items-center gap-2 md:flex">
              <Button variant="ghost" size="sm" className="rounded-full px-4 py-2 text-sm font-semibold text-[#475467]" asChild>
                <Link to="/login">Войти</Link>
              </Button>
              <Button variant="gradient" size="sm" className="rounded-full px-5 text-sm font-semibold" asChild>
                <Link to="/register">Регистрация</Link>
              </Button>
            </div>
          )}
          <button
            type="button"
            className="md:hidden p-2 hover:bg-gray-100 rounded-lg"
            onClick={() => setIsMobileOpen(true)}
          >
            <Menu className="h-5 w-5 text-gray-700" />
          </button>
        </div>
      </div>
      {isMobileOpen && (
        <>
          <div 
            className="fixed inset-0 bg-black/40 z-[100] md:hidden" 
            onClick={() => setIsMobileOpen(false)} 
          />
          <div 
            className="fixed right-0 top-0 h-full w-[280px] bg-white z-[101] md:hidden flex flex-col shadow-2xl"
          >
            <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200">
              <span className="text-lg font-semibold text-gray-900">Меню</span>
              <button
                type="button"
                onClick={() => setIsMobileOpen(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="h-5 w-5 text-gray-600" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto min-h-0 py-4">
              <div className="px-4 space-y-2">
                <Link
                  to="/mentors"
                  onClick={() => setIsMobileOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg text-base font-medium transition-colors ${
                    isActive('/mentors')
                      ? 'bg-primary text-white'
                      : 'text-gray-700 hover:bg-gray-100 bg-gray-50'
                  }`}
                >
                  <Users className="h-5 w-5 flex-shrink-0" />
                  <span>Менторы</span>
                </Link>
                <Link
                  to="/about"
                  onClick={() => setIsMobileOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg text-base font-medium transition-colors ${
                    isActive('/about')
                      ? 'bg-primary text-white'
                      : 'text-gray-700 hover:bg-gray-100 bg-gray-50'
                  }`}
                >
                  <Info className="h-5 w-5 flex-shrink-0" />
                  <span>О платформе</span>
                </Link>
                <Link
                  to="/faq"
                  onClick={() => setIsMobileOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg text-base font-medium transition-colors ${
                    isActive('/faq')
                      ? 'bg-primary text-white'
                      : 'text-gray-700 hover:bg-gray-100 bg-gray-50'
                  }`}
                >
                  <HelpCircle className="h-5 w-5 flex-shrink-0" />
                  <span>FAQ</span>
                </Link>
              </div>
            </div>
            
            <div className="border-t border-gray-200 px-4 py-4 space-y-3 bg-gray-50">
              {isAuthenticated ? (
                <>
                  <div className="p-4 bg-white rounded-lg border border-gray-200">
                    <div className="font-semibold text-gray-900 text-sm mb-2 truncate">
                      {user?.name || 'Профиль'}
                    </div>
                    <Link
                      to={getDashboardPath(user?.role)}
                      onClick={() => setIsMobileOpen(false)}
                      className="text-sm text-primary font-medium inline-flex items-center gap-1.5 hover:underline"
                    >
                      Личный кабинет
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setIsMobileOpen(false)
                      handleLogout()
                    }}
                    className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg font-medium text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    Выйти
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/mentors"
                    onClick={() => setIsMobileOpen(false)}
                    className="block w-full px-4 py-3 bg-primary text-white rounded-lg font-semibold text-sm text-center hover:bg-primary/90 transition-colors"
                  >
                    Подобрать наставника
                  </Link>
                  <div className="flex gap-2">
                    <Link
                      to="/login"
                      onClick={() => setIsMobileOpen(false)}
                      className="flex-1 px-4 py-3 bg-white border border-gray-300 rounded-lg font-medium text-sm text-center text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      Войти
                    </Link>
                    <Link
                      to="/register"
                      onClick={() => setIsMobileOpen(false)}
                      className="flex-1 px-4 py-3 bg-white border border-gray-300 rounded-lg font-medium text-sm text-center text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      Регистрация
                    </Link>
                  </div>
                </>
              )}
            </div>
          </div>
        </>
      )}
    </header>
  )
}

function getDashboardPath(role?: string): string {
  switch (role) {
    case 'student':
      return '/student/dashboard'
    case 'mentor':
      return '/mentor/dashboard'
    case 'admin':
      return '/admin/dashboard'
    default:
      return '/student/dashboard'
  }
}
