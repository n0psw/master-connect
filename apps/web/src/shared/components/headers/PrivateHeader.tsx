import { Search, User, LogOut, Settings } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useQuery } from 'react-query'

import { Button } from '@/shared/ui/button'
import { useAuthStore } from '@/shared/store/auth'
import { profilesApi } from '@/shared/api/profiles'
import { mentorsApi } from '@/shared/api/mentors'
import { getImageUrl } from '@/shared/utils/imageUtils'
import { NotificationBell } from '@/shared/components/NotificationBell'

export const PrivateHeader = () => {
  const { user, logout } = useAuthStore()
  
  const { data: profile } = useQuery(
    ['my-profile'],
    () => profilesApi.getMyProfile(),
    {
      enabled: !!user,
      staleTime: 30 * 1000,
      refetchOnWindowFocus: true
    }
  )
  
  const { data: mentorProfile } = useQuery(
    ['my-mentor-profile'],
    () => mentorsApi.getMyMentorProfile(),
    {
      enabled: !!user && user.role === 'mentor',
      staleTime: 30 * 1000,
      refetchOnWindowFocus: true
    }
  )
  
  const avatarUrl = user?.role === 'mentor' 
    ? mentorProfile?.avatar_url 
    : profile?.student_profile?.avatar_url

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
        {/* Логотип */}
        <div className="flex items-center space-x-3">
          <img src="/masteredlogo-ico.ico" alt="MasterConnect" className="h-10 w-10" />
          <span className="text-lg font-bold hidden md:block">MasterConnect</span>
        </div>

        {/* Поиск */}
        <div className="flex items-center flex-1 max-w-md">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="search"
              placeholder="Поиск..."
              className="w-full rounded-md border border-input bg-background pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>

        {/* Действия */}
        <div className="flex items-center space-x-4">
          <NotificationBell />

          {/* Профиль пользователя */}
          <div className="flex items-center space-x-2">
            {getImageUrl(avatarUrl) ? (
              <img
                src={getImageUrl(avatarUrl)!}
                alt={user?.name || 'Пользователь'}
                className="h-8 w-8 rounded-full object-cover border border-border"
                onError={(e) => {
                  console.error('Failed to load avatar in header:', avatarUrl)
                  e.currentTarget.style.display = 'none'
                }}
              />
            ) : (
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                <User className="h-4 w-4 text-primary-foreground" />
              </div>
            )}
            
            <div className="hidden md:block">
              <p className="text-sm font-medium">{user?.name || 'Пользователь'}</p>
              <p className="text-xs text-muted-foreground">{user?.email}</p>
            </div>
          </div>

          {/* Настройки */}
          <Button variant="ghost" size="icon" asChild>
            <Link to="./profile">
              <Settings className="h-4 w-4" />
            </Link>
          </Button>

          {/* Выход */}
          <Button
            variant="ghost"
            size="icon"
            onClick={handleLogout}
            title="Выйти"
          >
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  )
}
