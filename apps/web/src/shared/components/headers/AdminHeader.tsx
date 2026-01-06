import { Search, Shield, LogOut } from 'lucide-react'

import { Button } from '@/shared/ui/button'
import { useAuthStore } from '@/shared/store/auth'
import { NotificationBell } from '@/shared/components/NotificationBell'

export const AdminHeader = () => {
  const { user, logout } = useAuthStore()

  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  return (
    <header className="border-b bg-background">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Логотип + Админ индикатор */}
        <div className="flex items-center space-x-4">
          <img src="/masteredlogo-ico.ico" alt="MasterConnect" className="h-10 w-10" />
          <div className="flex items-center space-x-2 rounded-lg bg-gradient-to-r from-red-50 to-pink-50 px-4 py-2 border border-red-100">
            <Shield className="h-4 w-4 text-red-600" />
            <span className="text-sm font-semibold text-red-600">Административная панель</span>
          </div>
        </div>

        {/* Поиск */}
        <div className="flex items-center flex-1 max-w-md mx-8">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="search"
              placeholder="Поиск пользователей, менторов, бронирований..."
              className="w-full rounded-md border border-input bg-background pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>

        {/* Действия */}
        <div className="flex items-center space-x-4">
          <NotificationBell />

          {/* Информация об админе */}
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-full bg-red-600 flex items-center justify-center">
              <Shield className="h-4 w-4 text-white" />
            </div>
            
            <div className="hidden md:block">
              <p className="text-sm font-medium">{user?.name || 'Администратор'}</p>
              <p className="text-xs text-red-600">Супер-администратор</p>
            </div>
          </div>

          {/* Выход */}
          <Button
            variant="destructive"
            size="icon"
            onClick={handleLogout}
            title="Выйти из админ панели"
          >
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  )
}
