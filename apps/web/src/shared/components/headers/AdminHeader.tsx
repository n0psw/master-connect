import { Shield, LogOut } from 'lucide-react'

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
        {/* Админ индикатор */}
          <div className="flex items-center space-x-2 rounded-lg bg-gradient-to-r from-red-50 to-pink-50 px-4 py-2 border border-red-100">
            <Shield className="h-4 w-4 text-red-600" />
            <span className="text-sm font-semibold text-red-600">Административная панель</span>
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
