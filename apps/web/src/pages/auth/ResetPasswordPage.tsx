import { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, Lock, CheckCircle, AlertCircle } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { authApi } from '@/shared/api/auth'

// Схема валидации
const resetPasswordSchema = z.object({
  password: z
    .string()
    .min(8, 'Пароль должен содержать минимум 8 символов')
    .regex(
      /^(?=.*[a-zA-Z])(?=.*\d)/,
      'Пароль должен содержать как минимум одну букву и одну цифру'
    ),
  confirmPassword: z.string().min(1, 'Подтвердите пароль'),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Пароли не совпадают',
  path: ['confirmPassword']
})

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>

export const ResetPasswordPage = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [tokenError, setTokenError] = useState(false)

  const token = searchParams.get('token')

  useEffect(() => {
    // Проверяем наличие токена
    if (!token) {
      setTokenError(true)
    }
  }, [token])

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema)
  })

  const onSubmit = async (data: ResetPasswordFormData) => {
    if (!token) {
      toast.error('Токен сброса пароля отсутствует')
      return
    }

    try {
      await authApi.confirmPasswordReset({
        token: token,
        new_password: data.password
      })
      
      setIsSuccess(true)
      toast.success('Пароль успешно изменен!')
      
      // Перенаправляем на страницу входа через 3 секунды
      setTimeout(() => {
        navigate('/login')
      }, 3000)
    } catch (error: any) {
      console.error('Password reset error:', error)
      
      const errorMessage = error?.response?.data?.detail || error?.message || 'Ошибка при сбросе пароля'
      toast.error(errorMessage)
      
      // Если токен невалидный, показываем ошибку
      if (errorMessage.includes('токен') || errorMessage.includes('token')) {
        setTokenError(true)
      }
    }
  }

  // Если токен отсутствует или невалиден
  if (tokenError) {
    return (
      <>
        <Helmet>
          <title>Ошибка - MasterConnect</title>
        </Helmet>

        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
          <div className="w-full max-w-md">
            <div className="bg-card border rounded-lg p-8 shadow-sm text-center">
              <div className="flex items-center justify-center mb-6">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
                  <AlertCircle className="h-8 w-8 text-red-600" />
                </div>
              </div>
              
              <h2 className="text-2xl font-bold mb-4">Недействительная ссылка</h2>
              
              <p className="text-muted-foreground mb-6">
                Ссылка для сброса пароля недействительна или истекла.
                <br />
                Пожалуйста, запросите новую ссылку.
              </p>
              
              <div className="space-y-3">
                <Link to="/forgot-password">
                  <Button className="w-full">
                    Запросить новую ссылку
                  </Button>
                </Link>
                
                <Link to="/login">
                  <Button variant="outline" className="w-full">
                    Вернуться к входу
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </>
    )
  }

  // Если пароль успешно изменен
  if (isSuccess) {
    return (
      <>
        <Helmet>
          <title>Пароль изменен - MasterConnect</title>
        </Helmet>

        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
          <div className="w-full max-w-md">
            <div className="bg-card border rounded-lg p-8 shadow-sm text-center">
              <div className="flex items-center justify-center mb-6">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
                  <CheckCircle className="h-8 w-8 text-green-600" />
                </div>
              </div>
              
              <h2 className="text-2xl font-bold mb-4">Пароль изменен!</h2>
              
              <p className="text-muted-foreground mb-6">
                Ваш пароль успешно изменен.
                <br />
                Сейчас вы будете перенаправлены на страницу входа...
              </p>
              
              <Link to="/login">
                <Button className="w-full">
                  Войти сейчас
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </>
    )
  }

  // Форма установки нового пароля
  return (
    <>
      <Helmet>
        <title>Установить новый пароль - MasterConnect</title>
      </Helmet>

      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="w-full max-w-md">
          {/* Header */}
          <div className="text-center mb-6">
            <div className="flex items-center justify-center mb-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-primary-foreground">
                <span className="text-lg font-bold">MC</span>
              </div>
            </div>
            <h2 className="text-3xl font-bold tracking-tight">Новый пароль</h2>
            <p className="mt-2 text-muted-foreground">
              Введите новый пароль для вашего аккаунта
            </p>
          </div>

          {/* Form */}
          <div className="bg-card border rounded-lg p-6 shadow-sm">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {/* Password */}
              <div className="space-y-2">
                <Label htmlFor="password">Новый пароль</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Минимум 8 символов"
                    className="pl-10 pr-10"
                    error={errors.password?.message}
                    {...register('password')}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Confirm Password */}
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Подтвердите пароль</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                  <Input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    placeholder="Повторите пароль"
                    className="pl-10 pr-10"
                    error={errors.confirmPassword?.message}
                    {...register('confirmPassword')}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Password requirements */}
              <div className="text-xs text-muted-foreground space-y-1">
                <p>Пароль должен содержать:</p>
                <ul className="list-disc list-inside ml-2">
                  <li>Минимум 8 символов</li>
                  <li>Как минимум одну букву</li>
                  <li>Как минимум одну цифру</li>
                </ul>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Сохранение...' : 'Сохранить новый пароль'}
              </Button>
            </form>
          </div>

          {/* Back to Login */}
          <div className="mt-4 text-center text-sm text-muted-foreground">
            <Link to="/login" className="text-primary hover:underline">
              Вернуться к входу
            </Link>
          </div>
        </div>
      </div>
    </>
  )
}

