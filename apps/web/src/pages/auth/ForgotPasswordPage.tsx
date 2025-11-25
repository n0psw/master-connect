import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { authApi } from '@/shared/api/auth'

// Схема валидации
const forgotPasswordSchema = z.object({
  email: z
    .string()
    .min(1, 'Email обязателен')
    .email('Некорректный email адрес'),
})

type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>

export const ForgotPasswordPage = () => {
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [submittedEmail, setSubmittedEmail] = useState('')

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema)
  })

  const onSubmit = async (data: ForgotPasswordFormData) => {
    try {
      await authApi.requestPasswordReset({ email: data.email })
      
      setSubmittedEmail(data.email)
      setIsSubmitted(true)
      
      toast.success('Инструкции отправлены на ваш email')
    } catch (error: any) {
      console.error('Password reset error:', error)
      
      // В целях безопасности всегда показываем успех
      // даже если email не существует
      setSubmittedEmail(data.email)
      setIsSubmitted(true)
    }
  }

  if (isSubmitted) {
    return (
      <>
        <Helmet>
          <title>Письмо отправлено - MasterConnect</title>
        </Helmet>

        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
          <div className="w-full max-w-md">
            <div className="bg-card border rounded-lg p-8 shadow-sm text-center">
              <div className="flex items-center justify-center mb-6">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
                  <CheckCircle className="h-8 w-8 text-green-600" />
                </div>
              </div>
              
              <h2 className="text-2xl font-bold mb-4">Проверьте вашу почту</h2>
              
              <p className="text-muted-foreground mb-6">
                Мы отправили инструкции по сбросу пароля на адрес:
                <br />
                <span className="font-medium text-foreground">{submittedEmail}</span>
              </p>
              
              <p className="text-sm text-muted-foreground mb-6">
                Если письмо не пришло в течение нескольких минут, проверьте папку "Спам"
              </p>
              
              <div className="space-y-3">
                <Link to="/login">
                  <Button className="w-full">
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Вернуться к входу
                  </Button>
                </Link>
                
                <Button 
                  variant="ghost" 
                  className="w-full"
                  onClick={() => setIsSubmitted(false)}
                >
                  Отправить повторно
                </Button>
              </div>
            </div>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <Helmet>
        <title>Забыли пароль? - MasterConnect</title>
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
            <h2 className="text-3xl font-bold tracking-tight">Забыли пароль?</h2>
            <p className="mt-2 text-muted-foreground">
              Введите ваш email и мы отправим инструкции по восстановлению
            </p>
          </div>

          {/* Form */}
          <div className="bg-card border rounded-lg p-6 shadow-sm">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {/* Email */}
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="your@email.com"
                    className="pl-10"
                    error={errors.email?.message}
                    {...register('email')}
                  />
                </div>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Отправка...' : 'Отправить инструкции'}
              </Button>
            </form>

            {/* Back to Login */}
            <div className="mt-6 text-center">
              <Link
                to="/login"
                className="inline-flex items-center text-sm text-primary hover:underline"
              >
                <ArrowLeft className="h-4 w-4 mr-1" />
                Вернуться к входу
              </Link>
            </div>
          </div>

          {/* Help text */}
          <div className="mt-4 text-center text-sm text-muted-foreground">
            <p>
              Нет аккаунта?{' '}
              <Link to="/register" className="text-primary hover:underline">
                Зарегистрироваться
              </Link>
            </p>
          </div>
        </div>
      </div>
    </>
  )
}

