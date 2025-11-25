import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, Lock, CheckCircle } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Card, CardHeader, CardTitle, CardContent } from '@/shared/ui/card'
import { authApi } from '@/shared/api/auth'

// Схема валидации
const changePasswordSchema = z.object({
  currentPassword: z.string().min(1, 'Введите текущий пароль'),
  newPassword: z
    .string()
    .min(8, 'Пароль должен содержать минимум 8 символов')
    .regex(
      /^(?=.*[a-zA-Z])(?=.*\d)/,
      'Пароль должен содержать как минимум одну букву и одну цифру'
    ),
  confirmPassword: z.string().min(1, 'Подтвердите новый пароль'),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: 'Пароли не совпадают',
  path: ['confirmPassword']
})

type ChangePasswordFormData = z.infer<typeof changePasswordSchema>

export const ChangePasswordSection = () => {
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm<ChangePasswordFormData>({
    resolver: zodResolver(changePasswordSchema)
  })

  const onSubmit = async (data: ChangePasswordFormData) => {
    try {
      await authApi.changePassword({
        current_password: data.currentPassword,
        new_password: data.newPassword
      })
      
      setIsSuccess(true)
      toast.success('Пароль успешно изменен!')
      
      // Сбрасываем форму
      reset()
      
      // Убираем сообщение об успехе через 5 секунд
      setTimeout(() => {
        setIsSuccess(false)
      }, 5000)
    } catch (error: any) {
      console.error('Password change error:', error)
      
      const errorMessage = error?.response?.data?.detail || error?.message || 'Ошибка при смене пароля'
      toast.error(errorMessage)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lock className="h-5 w-5" />
          Безопасность
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isSuccess && (
          <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <p className="text-sm text-green-800">
              Пароль успешно изменен. Все активные сессии были завершены.
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Current Password */}
          <div className="space-y-2">
            <Label htmlFor="currentPassword">Текущий пароль</Label>
            <div className="relative">
              <Input
                id="currentPassword"
                type={showCurrentPassword ? 'text' : 'password'}
                placeholder="Введите текущий пароль"
                error={errors.currentPassword?.message}
                {...register('currentPassword')}
              />
              <button
                type="button"
                onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showCurrentPassword ? (
                  <EyeOff className="h-5 w-5" />
                ) : (
                  <Eye className="h-5 w-5" />
                )}
              </button>
            </div>
          </div>

          {/* New Password */}
          <div className="space-y-2">
            <Label htmlFor="newPassword">Новый пароль</Label>
            <div className="relative">
              <Input
                id="newPassword"
                type={showNewPassword ? 'text' : 'password'}
                placeholder="Минимум 8 символов"
                error={errors.newPassword?.message}
                {...register('newPassword')}
              />
              <button
                type="button"
                onClick={() => setShowNewPassword(!showNewPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showNewPassword ? (
                  <EyeOff className="h-5 w-5" />
                ) : (
                  <Eye className="h-5 w-5" />
                )}
              </button>
            </div>
          </div>

          {/* Confirm Password */}
          <div className="space-y-2">
            <Label htmlFor="confirmPassword">Подтвердите новый пароль</Label>
            <div className="relative">
              <Input
                id="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                placeholder="Повторите новый пароль"
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
          <div className="text-xs text-muted-foreground bg-muted p-3 rounded-md">
            <p className="font-medium mb-1">Требования к паролю:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Минимум 8 символов</li>
              <li>Как минимум одна буква</li>
              <li>Как минимум одна цифра</li>
            </ul>
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Сохранение...' : 'Изменить пароль'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}

