import { useMemo, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { User, Menu, LogOut, X, ArrowRight } from 'lucide-react'

import { Button } from '@/shared/ui/button'
import { useAuthStore } from '@/shared/store/auth'
import { NotificationBell } from '@/shared/components/NotificationBell'

export const PublicHeader = () => {
  const location = useLocation()
  const { isAuthenticated, user, logout } = useAuthStore()
  const [isMobileOpen, setIsMobileOpen] = useState(false)

  const navItems = useMemo(
    () => [
      { label: 'Менторы', href: '/mentors' },
      { label: 'О платформе', href: '/about' },
      { label: 'FAQ', href: '/faq' }
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
      <div className="container-wide flex items-center justify-between gap-6 py-3">
        <Link to="/" className="flex items-center gap-3 rounded-full px-3 py-2 transition hover:bg-white/70">
          <img src="/masteredlogo-ico.ico" alt="MasterConnect" className="h-10 w-10 rounded-full shadow-lg" />
        </Link>

        <nav className="hidden items-center gap-2 md:flex">
            {navItems.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                  isActive(item.href)
                    ? 'bg-gradient-to-r from-[#1c3fe3] to-[#7a5cff] text-white shadow-[0_12px_30px_-20px_rgba(28,63,227,0.6)]'
                    : 'text-[#475467] hover:bg-[rgba(28,63,227,0.08)]'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>

        <div className="flex items-center gap-3">
            <Button variant="gradient" className="hidden h-11 rounded-full px-6 text-sm font-semibold lg:flex" asChild>
              <Link to="/mentors">
                Подобрать наставника
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            {isAuthenticated ? (
              <div className="hidden items-center gap-3 rounded-full border border-[rgba(16,24,40,0.08)] bg-white/80 px-3 py-2 shadow-sm md:flex">
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-primary" />
                  <span className="text-sm font-medium text-[#101828]">{user?.name || 'Профиль'}</span>
                </div>
                <NotificationBell />
                <Button variant="outline" size="sm" className="rounded-full border-none bg-[rgba(28,63,227,0.08)] px-4 py-2 text-xs font-semibold text-primary" asChild>
                  <Link to={getDashboardPath(user?.role)}>Личный кабинет</Link>
                </Button>
                <Button variant="ghost" size="icon" className="text-[#475467] hover:text-primary" onClick={handleLogout} title="Выйти">
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
            <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setIsMobileOpen(true)}>
              <Menu className="h-5 w-5" />
            </Button>
        </div>
      </div>
      {isMobileOpen && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm md:hidden" onClick={() => setIsMobileOpen(false)}>
          <div className="absolute right-0 top-0 h-full w-80 max-w-[85vw] border-l border-white/20 bg-white shadow-2xl" onClick={(event) => event.stopPropagation()}>
            <div className="flex items-center justify-between border-b border-[rgba(16,24,40,0.08)] px-6 py-4">
              <span className="text-lg font-semibold text-[#101828]">Меню</span>
              <Button variant="ghost" size="icon" onClick={() => setIsMobileOpen(false)}>
                <X className="h-5 w-5" />
              </Button>
            </div>
            <div className="flex flex-col gap-3 px-6 py-6">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  to={item.href}
                  onClick={() => setIsMobileOpen(false)}
                  className={`rounded-2xl px-4 py-3 text-sm font-semibold ${
                    isActive(item.href) ? 'bg-gradient-to-r from-[#1c3fe3] to-[#7a5cff] text-white' : 'bg-[rgba(28,63,227,0.08)] text-primary'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
            <div className="px-6 pb-6">
              {isAuthenticated ? (
                <div className="space-y-3">
                  <div className="rounded-2xl border border-[rgba(16,24,40,0.08)] bg-white px-4 py-3 text-sm text-[#475467]">
                    <div className="font-semibold text-[#101828]">{user?.name || 'Профиль'}</div>
                    <Link to={getDashboardPath(user?.role)} onClick={() => setIsMobileOpen(false)} className="mt-2 inline-flex items-center gap-2 text-primary">
                      Личный кабинет
                      <ArrowRight className="h-3 w-3" />
                    </Link>
                  </div>
                  <Button variant="outline" className="w-full rounded-2xl border-[rgba(16,24,40,0.12)]" onClick={handleLogout}>
                    Выйти
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  <Button variant="gradient" className="w-full rounded-2xl h-12" asChild>
                    <Link to="/mentors" onClick={() => setIsMobileOpen(false)}>
                      Подобрать наставника
                    </Link>
                  </Button>
                  <div className="flex items-center justify-between">
                    <Button variant="ghost" className="text-sm text-[#475467]" asChild>
                      <Link to="/login" onClick={() => setIsMobileOpen(false)}>
                        Войти
                      </Link>
                    </Button>
                    <Button variant="outline" className="text-sm font-semibold border-[rgba(16,24,40,0.12)]" asChild>
                      <Link to="/register" onClick={() => setIsMobileOpen(false)}>
                        Регистрация
                      </Link>
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
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
