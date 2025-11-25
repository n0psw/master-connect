import { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'

import { useAuthStore } from '@/shared/store/auth'
import { PageLoader } from '@/shared/ui/PageLoader'

import type { UserRole } from '@/shared/types/auth'

interface ProtectedRouteProps {
  children: ReactNode
  roles?: UserRole[]
}

export const ProtectedRoute = ({ children, roles }: ProtectedRouteProps) => {
  const location = useLocation()
  const { isAuthenticated, user, isLoading } = useAuthStore()

  // Показываем загрузку пока проверяем аутентификацию
  if (isLoading) {
    return <PageLoader />
  }

  // Если не аутентифицирован, перенаправляем на логин
  if (!isAuthenticated || !user) {
    return (
      <Navigate
        to="/login"
        state={{ from: location.pathname }}
        replace
      />
    )
  }

  // Если указаны роли, проверяем права доступа
  if (roles && roles.length > 0) {
    const hasRequiredRole = roles.some(role => user.role === role)
    
    if (!hasRequiredRole) {
      // Перенаправляем на подходящую страницу в зависимости от роли
      const redirectPath = getRedirectPathForRole(user.role)
      return <Navigate to={redirectPath} replace />
    }
  }

  return <>{children}</>
}

function getRedirectPathForRole(role: UserRole): string {
  switch (role) {
    case 'student':
      return '/student/dashboard'
    case 'mentor':
      return '/mentor/dashboard'
    case 'admin':
      return '/admin/dashboard'
    default:
      return '/'
  }
}
