import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
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
const registerSchema = z.object({
  email: z
    .string()
    .min(1, 'Email обязателен')
    .email('Некорректный email адрес'),
  password: z
    .string()
    .min(8, 'Пароль должен содержать минимум 8 символов')
    .regex(
      /^(?=.*[a-zA-Z])(?=.*\d)/,
      'Пароль должен содержать как минимум одну букву и одну цифру'
    ),
  confirmPassword: z.string().min(1, 'Подтвердите пароль'),
  name: z
    .string()
    .min(1, 'Имя обязательно')
    .min(2, 'Имя должно содержать минимум 2 символа')
    .max(255, 'Имя слишком длинное'),
  phone: z
    .string()
    .optional()
    .refine((value) => {
      if (!value) return true
      return /^[\+]?[\d\s\-\(\)]{10,}$/.test(value.replace(/\s/g, ''))
    }, 'Некорректный формат телефона'),
  timezone: z.string().default('Etc/GMT-5'),
  locale: z.string().default('ru')
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Пароли не совпадают',
  path: ['confirmPassword']
})

type RegisterFormData = z.infer<typeof registerSchema>

export const RegisterPage = () => {
  const navigate = useNavigate()
  const { register: registerUser, isLoading } = useAuthStore()
  
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      timezone: 'Etc/GMT-5',
      locale: 'ru'
    }
  })

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setServerError(null)
      
      // Убираем confirmPassword из данных для отправки и добавляем роль 'student'
      const { confirmPassword, ...registerData } = data
      
      await registerUser({ ...registerData, role: 'student' })
      
      // Показываем уведомление об успехе
      toast.success('Регистрация прошла успешно! Добро пожаловать!')
      
      // Перенаправляем на dashboard студента
      navigate('/student/dashboard', { replace: true })
      
    } catch (error: any) {
      console.error('Registration error:', error)
      
      // Показываем ошибку пользователю
      const errorMessage = error?.detail || error?.message || 'Произошла ошибка при регистрации'
      setServerError(errorMessage)
      toast.error(errorMessage)
    }
  }

  return (
    <>
      <Helmet>
        <title>Регистрация - MasterConnect</title>
        <meta name="description" content="Создайте аккаунт MasterConnect и получите доступ к персональным консультациям с менторами или начните помогать студентам." />
      </Helmet>

      <div className="min-h-screen gradient-bg flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full space-y-8">
          {/* Заголовок */}
          <div className="text-center">
            <div className="flex items-center justify-center mb-6">
              <img src="/masteredlogo-ico.ico" alt="MasterConnect" className="h-16 w-16" />
            </div>
            <h2 className="text-4xl font-bold tracking-tight">Регистрация студента</h2>
            <p className="mt-3 text-lg text-muted-foreground">
              Создайте аккаунт, чтобы найти ментора и начать обучение
            </p>
            <p className="mt-3 text-base text-muted-foreground">
              Уже есть аккаунт?{' '}
              <Link to="/login" className="text-primary hover:underline font-medium">
                Войти
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

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
              {/* Имя */}
              <div className="space-y-2">
                <Label htmlFor="name" className="text-base font-medium">Имя</Label>
                <Input
                  id="name"
                  placeholder="Ваше имя"
                  className="h-12"
                  error={errors.name?.message}
                  {...register('name')}
                />
              </div>

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

              {/* Телефон (опционально) */}
              <div className="space-y-2">
                <Label htmlFor="phone" className="text-base font-medium">Телефон (опционально)</Label>
                <Input
                  id="phone"
                  type="tel"
                  placeholder="+7 (777) 123-45-67"
                  className="h-12"
                  error={errors.phone?.message}
                  {...register('phone')}
                />
              </div>

              {/* Пароль */}
              <div className="space-y-2">
                <Label htmlFor="password" className="text-base font-medium">Пароль</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Создайте пароль"
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

              {/* Подтверждение пароля */}
              <div className="space-y-2">
                <Label htmlFor="confirmPassword" className="text-base font-medium">Подтвердите пароль</Label>
                <div className="relative">
                  <Input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    placeholder="Повторите пароль"
                    className="h-12"
                    error={errors.confirmPassword?.message}
                    {...register('confirmPassword')}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0 h-12 w-12 hover:bg-transparent"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-4 w-4 text-muted-foreground" />
                    ) : (
                      <Eye className="h-4 w-4 text-muted-foreground" />
                    )}
                  </Button>
                </div>
              </div>

              {/* Кнопка регистрации */}
              <Button
                type="submit"
                className="w-full h-12 text-base font-medium"
                disabled={isSubmitting || isLoading}
                loading={isSubmitting || isLoading}
              >
                Создать аккаунт
              </Button>
            </form>

            {/* Соглашения */}
            <div className="mt-4 text-center">
              <p className="text-xs text-muted-foreground">
                Создавая аккаунт, вы соглашаетесь с{' '}
                <Link to="/terms" className="text-primary hover:underline">
                  Условиями использования
                </Link>{' '}
                и{' '}
                <Link to="/privacy" className="text-primary hover:underline">
                  Политикой конфиденциальности
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
