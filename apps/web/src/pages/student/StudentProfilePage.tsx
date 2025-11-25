import { useState } from 'react'
import { Helmet } from 'react-helmet-async'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { User, MapPin, Target, Save, Mail, Phone, Clock, Globe, Lock } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Textarea } from '@/shared/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { profilesApi } from '@/shared/api/profiles'
import { useAuthStore } from '@/shared/store/auth'
import { TIMEZONES, LOCALES, COUNTRIES } from '@/shared/types/profiles'
import type { UserUpdateData, StudentProfileUpdateData } from '@/shared/types/profiles'
import { ChangePasswordSection } from '@/shared/components/ChangePasswordSection'
import { AvatarUpload } from '@/shared/components/AvatarUpload'

// Схемы валидации
const userProfileSchema = z.object({
  name: z.string().min(1, 'Имя обязательно').min(2, 'Минимум 2 символа'),
  phone: z.string().optional().refine((value) => {
    if (!value) return true
    return /^[\+]?[\d\s\-\(\)]{10,}$/.test(value.replace(/\s/g, ''))
  }, 'Некорректный формат телефона'),
  timezone: z.string().min(1, 'Выберите часовой пояс'),
  locale: z.string().min(1, 'Выберите язык'),
})

const studentProfileSchema = z.object({
  goals: z.string().optional(),
  country: z.string().optional(),
  city: z.string().optional(),
})

type UserProfileData = z.infer<typeof userProfileSchema>
type StudentProfileData = z.infer<typeof studentProfileSchema>

export const StudentProfilePage = () => {
  const { user, setUser } = useAuthStore()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'general' | 'education' | 'security'>('general')

  // Загрузка профиля (включая student_profile)
  const { data: profile, isLoading } = useQuery(
    ['my-profile'],
    () => profilesApi.getMyProfile(),
    {
      refetchOnWindowFocus: false,
      staleTime: 60_000,
      onError: (error: any) => {
        toast.error('Ошибка при загрузке профиля: ' + (error?.detail || error?.message))
      }
    }
  )
  const studentProfile = profile?.student_profile

  // Форма основного профиля
  const {
    register: registerUser,
    handleSubmit: handleUserSubmit,
    formState: { errors: userErrors },
    reset: resetUser
  } = useForm<UserProfileData>({
    resolver: zodResolver(userProfileSchema),
    values: profile ? {
      name: profile.name || '',
      phone: profile.phone || '',
      timezone: profile.timezone || 'Asia/Almaty',
      locale: profile.locale || 'ru',
    } : undefined
  })

  // Форма профиля студента
  const {
    register: registerStudent,
    handleSubmit: handleStudentSubmit,
    formState: { errors: studentErrors },
    reset: resetStudent
  } = useForm<StudentProfileData>({
    resolver: zodResolver(studentProfileSchema),
    values: studentProfile ? {
      goals: studentProfile.goals || '',
      country: studentProfile.country || '',
      city: studentProfile.city || '',
    } : undefined
  })

  // Мутации
  const updateUserMutation = useMutation(profilesApi.updateMyProfile, {
    onSuccess: (data) => {
      setUser(data)
      queryClient.invalidateQueries(['my-profile'])
      toast.success('Основная информация обновлена!')
    },
    onError: (error: any) => {
      toast.error('Ошибка при обновлении: ' + (error?.detail || error?.message))
    }
  })

  const updateStudentMutation = useMutation(
    (data: StudentProfileData) => (
      studentProfile
        ? profilesApi.updateMyStudentProfile(data)
        : profilesApi.createMyStudentProfile(data)
    ),
    {
      onSuccess: async () => {
        await queryClient.invalidateQueries(['my-profile'])
        toast.success('Информация об образовании обновлена!')
      },
      onError: (error: any) => {
        toast.error('Ошибка при обновлении: ' + (error?.detail || error?.message))
      }
    }
  )

  // Обработчики форм
  const onUserSubmit = (data: UserProfileData) => {
    updateUserMutation.mutate(data)
  }

  const onStudentSubmit = (data: StudentProfileData) => {
    updateStudentMutation.mutate(data)
  }

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded mb-4" />
          <div className="h-64 bg-muted rounded" />
        </div>
      </div>
    )
  }

  return (
    <>
      <Helmet>
        <title>Профиль студента - MasterConnect</title>
      </Helmet>

      <div className="space-y-8">
        {/* Заголовок */}
        <div>
          <h1 className="text-3xl font-bold mb-4">Мой профиль</h1>
          <p className="text-muted-foreground">
            Управляйте своей личной информацией и настройками
          </p>
        </div>

        {/* Вкладки */}
        <div className="flex space-x-1 bg-muted p-1 rounded-lg w-fit">
          <button
            onClick={() => setActiveTab('general')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'general'
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <User className="h-4 w-4 inline mr-2" />
            Основная информация
          </button>
          <button
            onClick={() => setActiveTab('education')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'education'
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Target className="h-4 w-4 inline mr-2" />
            Цели и образование
          </button>
          <button
            onClick={() => setActiveTab('security')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'security'
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Lock className="h-4 w-4 inline mr-2" />
            Безопасность
          </button>
        </div>

        {/* Основная информация */}
        {activeTab === 'general' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <User className="h-5 w-5 mr-2" />
                Основная информация
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUserSubmit(onUserSubmit)} className="space-y-6">
                <AvatarUpload
                  currentAvatarUrl={studentProfile?.avatar_url}
                  userName={profile?.name || profile?.email}
                  onSuccess={() => {
                    queryClient.invalidateQueries(['my-profile'])
                    queryClient.invalidateQueries(['my-student-profile'])
                  }}
                />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Имя */}
                  <div>
                    <Label htmlFor="name">Имя *</Label>
                    <Input
                      id="name"
                      placeholder="Ваше имя"
                      error={userErrors.name?.message}
                      {...registerUser('name')}
                    />
                  </div>

                  {/* Email (только для показа) */}
                  <div>
                    <Label>Email</Label>
                    <div className="flex items-center mt-2">
                      <Mail className="h-4 w-4 text-muted-foreground mr-2" />
                      <span className="text-sm">{profile?.email}</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Для изменения email обратитесь в поддержку
                    </p>
                  </div>

                  {/* Телефон */}
                  <div>
                    <Label htmlFor="phone">Телефон</Label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="phone"
                        type="tel"
                        placeholder="+7 (777) 123-45-67"
                        className="pl-10"
                        error={userErrors.phone?.message}
                        {...registerUser('phone')}
                      />
                    </div>
                  </div>

                  {/* Часовой пояс */}
                  <div>
                    <Label htmlFor="timezone">Часовой пояс *</Label>
                    <div className="relative">
                      <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <select
                        id="timezone"
                        {...registerUser('timezone')}
                        className="w-full pl-10 pr-3 py-2 border border-input rounded-md bg-background"
                      >
                        {TIMEZONES.map((tz) => (
                          <option key={tz.value} value={tz.value}>
                            {tz.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    {userErrors.timezone && (
                      <p className="text-sm text-destructive mt-2">{userErrors.timezone.message}</p>
                    )}
                  </div>

                  {/* Язык */}
                  <div>
                    <Label htmlFor="locale">Язык интерфейса *</Label>
                    <div className="relative">
                      <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <select
                        id="locale"
                        {...registerUser('locale')}
                        className="w-full pl-10 pr-3 py-2 border border-input rounded-md bg-background"
                      >
                        {LOCALES.map((locale) => (
                          <option key={locale.value} value={locale.value}>
                            {locale.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    {userErrors.locale && (
                      <p className="text-sm text-destructive mt-2">{userErrors.locale.message}</p>
                    )}
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button
                    type="submit"
                    disabled={updateUserMutation.isLoading}
                    loading={updateUserMutation.isLoading}
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Сохранить изменения
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Цели и образование */}
        {activeTab === 'education' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="h-5 w-5 mr-2" />
                Цели и образование
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleStudentSubmit(onStudentSubmit)} className="space-y-6">
                {/* Цели */}
                <div>
                  <Label htmlFor="goals">Ваши цели и интересы</Label>
                  <Textarea
                    id="goals"
                    placeholder="Расскажите о том, чего хотите достичь. Например: поступить в MIT, изучать Computer Science, получить стипендию..."
                    rows={5}
                    {...registerStudent('goals')}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Эта информация поможет менторам лучше понять ваши потребности
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Страна */}
                  <div>
                    <Label htmlFor="country">Страна</Label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <select
                        id="country"
                        {...registerStudent('country')}
                        className="w-full pl-10 pr-3 py-2 border border-input rounded-md bg-background"
                      >
                        <option value="">Выберите страну</option>
                        {COUNTRIES.map((country) => (
                          <option key={country} value={country}>
                            {country}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Город */}
                  <div>
                    <Label htmlFor="city">Город</Label>
                    <Input
                      id="city"
                      placeholder="Ваш город"
                      {...registerStudent('city')}
                    />
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button
                    type="submit"
                    disabled={updateStudentMutation.isLoading}
                    loading={updateStudentMutation.isLoading}
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Сохранить изменения
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Безопасность */}
        {activeTab === 'security' && (
          <ChangePasswordSection />
        )}

        {/* Информационные карточки */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold mb-2">💡 Совет</h3>
              <p className="text-sm text-muted-foreground">
                Заполнение профиля поможет менторам лучше понять ваши потребности и предоставить более точные рекомендации.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold mb-2">🔒 Приватность</h3>
              <p className="text-sm text-muted-foreground">
                Ваша контактная информация видна только менторам при бронировании консультаций. Email виден только администраторам.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  )
}
