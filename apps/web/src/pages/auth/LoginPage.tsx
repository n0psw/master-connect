import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, AlertCircle } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { useAuthStore } from '@/shared/store/auth'

// Схема валидации
const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email обязателен')
    .email('Некорректный email адрес'),
  password: z
    .string()
    .min(1, 'Пароль обязателен')
    .min(8, 'Пароль должен содержать минимум 8 символов')
})

type LoginFormData = z.infer<typeof loginSchema>

export const LoginPage = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, isLoading } = useAuthStore()
  
  const [showPassword, setShowPassword] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema)
  })

  const onSubmit = async (data: LoginFormData) => {
    try {
      setServerError(null)
      
      await login(data.email, data.password)
      
      // Показываем уведомление об успехе
      toast.success('Вход выполнен успешно!')
      
      // Получаем текущего пользователя для определения роли
      const currentUser = useAuthStore.getState().user
      
      // Определяем куда перенаправить пользователя
      let redirectPath = '/student/dashboard' // По умолчанию
      
      if (currentUser) {
        switch (currentUser.role) {
          case 'student':
            redirectPath = '/student/dashboard'
            break
          case 'mentor':
            redirectPath = '/mentor/dashboard'
            break
          case 'admin':
            redirectPath = '/admin/dashboard'
            break
        }
      }
      
      // Перенаправляем на изначальную страницу или соответствующий dashboard
      const from = location.state?.from || redirectPath
      navigate(from, { replace: true })
      
    } catch (error: any) {
      console.error('Login error:', error)
      
      // Показываем ошибку пользователю
      const errorMessage = error?.detail || error?.message || 'Произошла ошибка при входе'
      setServerError(errorMessage)
      toast.error(errorMessage)
    }
  }

  return (
    <>
      <Helmet>
        <title>Вход - MasterConnect</title>
        <meta name="description" content="Войдите в свой аккаунт MasterConnect для доступа к персональным консультациям с менторами." />
      </Helmet>

      <div className="min-h-screen gradient-bg flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full space-y-8">
          {/* Заголовок */}
          <div className="text-center">
            <div className="flex items-center justify-center mb-6">
              <img src="/masteredlogo-ico.ico" alt="MasterConnect" className="h-16 w-16" />
            </div>
            <h2 className="text-4xl font-bold tracking-tight">Войдите в аккаунт</h2>
            <p className="mt-3 text-lg text-muted-foreground">
              Нет аккаунта?{' '}
              <Link to="/register" className="text-primary hover:underline font-medium">
                Зарегистрироваться
              </Link>
            </p>
          </div>
          
          {/* Форма */}
          <div className="bg-card border-2 rounded-2xl p-8 shadow-xl">
            {serverError && (
              <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-destructive" />
                <p className="text-sm text-destructive">{serverError}</p>
              </div>
            )}

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Email */}
              <div className="space-y-2">
                <Label htmlFor="email" className="text-base font-medium">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  className="h-12"
                  error={errors.email?.message}
                  {...register('email')}
                />
              </div>

              {/* Пароль */}
              <div className="space-y-2">
                <Label htmlFor="password" className="text-base font-medium">Пароль</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Введите пароль"
                    className="h-12"
                    error={errors.password?.message}
                    {...register('password')}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0 h-12 w-12 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-muted-foreground" />
                    ) : (
                      <Eye className="h-4 w-4 text-muted-foreground" />
                    )}
                  </Button>
                </div>
              </div>

              {/* Кнопка входа */}
              <Button
                type="submit"
                className="w-full h-12 text-base font-medium"
                disabled={isSubmitting || isLoading}
                loading={isSubmitting || isLoading}
              >
                Войти
              </Button>
            </form>

            {/* Дополнительные ссылки */}
            <div className="mt-6 text-center">
              <Link
                to="/forgot-password"
                className="text-sm text-muted-foreground hover:text-primary"
              >
                Забыли пароль?
              </Link>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
