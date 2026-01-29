import { useState } from 'react'
import { Helmet } from 'react-helmet-async'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { 
  User, 
  GraduationCap, 
  MapPin, 
  Save, 
  Plus, 
  Trash2, 
  Edit3, 
  Mail, 
  Phone, 
  Clock, 
  Globe,
  Star,
  DollarSign,
  Languages,
  BookOpen,
  Lock
} from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Textarea } from '@/shared/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { profilesApi } from '@/shared/api/profiles'
import { mentorsApi } from '@/shared/api/mentors'
import { useAuthStore } from '@/shared/store/auth'
import { TIMEZONES, LOCALES, COUNTRIES } from '@/shared/types/profiles'
import type { UserUpdateData } from '@/shared/types/profiles'
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

const mentorProfileSchema = z.object({
  headline: z.string().optional(),
  bio: z.string().optional(),
  price_30: z.number().min(0, 'Цена не может быть отрицательной').optional().or(z.literal('')),
  price_60: z.number().min(0, 'Цена не может быть отрицательной').optional().or(z.literal('')),
  languages: z.string().optional(),
  subjects: z.string().optional(),
  country: z.string().optional(),
  city: z.string().optional(),
})

const universitySchema = z.object({
  university: z.string().min(1, 'Название университета обязательно'),
  degree: z.string().optional(),
  major: z.string().optional(),
  year_from: z.number().min(1900, 'Год поступления слишком ранний').max(new Date().getFullYear(), 'Год не может быть в будущем').optional().or(z.literal('')),
  year_to: z.number().min(1900, 'Год окончания слишком ранний').max(new Date().getFullYear() + 10, 'Год слишком поздний').optional().or(z.literal('')),
  country: z.string().optional(),
  city: z.string().optional(),
}).refine((data) => {
  if (data.year_from && data.year_to) {
    return data.year_from <= data.year_to
  }
  return true
}, {
  message: 'Год окончания должен быть больше года поступления',
  path: ['year_to']
})

type UserProfileData = z.infer<typeof userProfileSchema>
type MentorProfileData = z.infer<typeof mentorProfileSchema>
type UniversityData = z.infer<typeof universitySchema>

export const MentorProfilePage = () => {
  const { user, setUser } = useAuthStore()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'general' | 'mentor' | 'education' | 'security'>('general')
  const [editingUniversity, setEditingUniversity] = useState<string | null>(null)
  const [showAddUniversity, setShowAddUniversity] = useState(false)

  // Загрузка профиля
  const { data: profile, isLoading } = useQuery(
    ['my-profile'],
    () => profilesApi.getMyProfile(),
    {
      onError: (error: any) => {
        toast.error('Ошибка при загрузке профиля: ' + (error?.detail || error?.message))
      }
    }
  )

  // Загрузка профиля ментора
  const { data: mentorProfile, isLoading: mentorLoading } = useQuery(
    ['my-mentor-profile'],
    () => mentorsApi.getMyMentorProfile(),
    {
      enabled: !!profile,
      onError: (error: any) => {
        // Если профиль ментора не найден, это нормально
        if (!error?.detail?.includes('не найден')) {
          console.error('Ошибка при загрузке профиля ментора:', error)
        }
      }
    }
  )

  // Форма основного профиля
  const {
    register: registerUser,
    handleSubmit: handleUserSubmit,
    formState: { errors: userErrors },
  } = useForm<UserProfileData>({
    resolver: zodResolver(userProfileSchema),
    values: profile ? {
      name: profile.name || '',
      phone: profile.phone || '',
      timezone: profile.timezone || 'Etc/GMT-5',
      locale: profile.locale || 'ru',
    } : undefined
  })

  // Форма профиля ментора
  const {
    register: registerMentor,
    handleSubmit: handleMentorSubmit,
    formState: { errors: mentorErrors },
  } = useForm<MentorProfileData>({
    resolver: zodResolver(mentorProfileSchema),
    values: mentorProfile ? {
      headline: mentorProfile.headline || '',
      bio: mentorProfile.bio || '',
      price_30: mentorProfile.price_30 || '',
      price_60: mentorProfile.price_60 || '',
      languages: mentorProfile.languages?.join(', ') || '',
      subjects: mentorProfile.subjects?.join(', ') || '',
      country: mentorProfile.country || '',
      city: mentorProfile.city || '',
    } : undefined
  })

  // Форма добавления/редактирования университета
  const {
    register: registerUniversity,
    handleSubmit: handleUniversitySubmit,
    formState: { errors: universityErrors },
    reset: resetUniversity
  } = useForm<UniversityData>({
    resolver: zodResolver(universitySchema),
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

  const updateMentorMutation = useMutation(
    mentorProfile 
      ? mentorsApi.updateMentorProfile
      : mentorsApi.createMentorProfile,
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['my-mentor-profile'])
        toast.success('Профиль ментора обновлен!')
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

  const onMentorSubmit = (data: MentorProfileData) => {
    const mentorData = {
      headline: data.headline,
      bio: data.bio,
      price_30: data.price_30 === '' ? null : Number(data.price_30),
      price_60: data.price_60 === '' ? null : Number(data.price_60),
      languages: data.languages ? data.languages.split(',').map(lang => lang.trim()).filter(Boolean) : [],
      subjects: data.subjects ? data.subjects.split(',').map(subj => subj.trim()).filter(Boolean) : [],
      country: data.country,
      city: data.city,
    }
    updateMentorMutation.mutate(mentorData)
  }

  if (isLoading || mentorLoading) {
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
        <title>Профиль ментора - MasterConnect</title>
      </Helmet>

      <div className="space-y-8">
        {/* Заголовок */}
        <div>
          <h1 className="text-3xl font-bold mb-4">Мой профиль</h1>
          <p className="text-muted-foreground">
            Управляйте своей информацией и настройками ментора
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
            onClick={() => setActiveTab('mentor')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'mentor'
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Star className="h-4 w-4 inline mr-2" />
            Профиль ментора
          </button>
          <button
            onClick={() => setActiveTab('education')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'education'
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <GraduationCap className="h-4 w-4 inline mr-2" />
            Образование
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
                  currentAvatarUrl={mentorProfile?.avatar_url}
                  userName={profile?.name || profile?.email}
                  onSuccess={() => {
                    queryClient.invalidateQueries(['my-profile'])
                    queryClient.invalidateQueries(['my-mentor-profile'])
                    queryClient.invalidateQueries(['mentor-detail'])
                    queryClient.invalidateQueries(['mentors-catalog'])
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

        {/* Профиль ментора */}
        {activeTab === 'mentor' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Star className="h-5 w-5 mr-2" />
                Профиль ментора
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleMentorSubmit(onMentorSubmit)} className="space-y-6">
                {/* Заголовок */}
                <div>
                  <Label htmlFor="headline">Заголовок профиля</Label>
                  <Input
                    id="headline"
                    placeholder="Например: Senior Software Engineer в Google, специалист по Computer Science"
                    error={mentorErrors.headline?.message}
                    {...registerMentor('headline')}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Краткое описание вашей профессии и специализации
                  </p>
                </div>

                {/* Биография */}
                <div>
                  <Label htmlFor="bio">О себе</Label>
                  <Textarea
                    id="bio"
                    placeholder="Расскажите о своем опыте, достижениях, интересах и том, чем можете помочь студентам..."
                    rows={5}
                    error={mentorErrors.bio?.message}
                    {...registerMentor('bio')}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Подробное описание поможет студентам лучше понять ваш профиль
                  </p>
                </div>

                {/* Стоимость консультаций */}
                <div>
                  <Label className="text-base font-medium flex items-center mb-4">
                    <DollarSign className="h-4 w-4 mr-2" />
                    Стоимость консультаций (в тенге)
                  </Label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="price_30">30 минут</Label>
                      <Input
                        id="price_30"
                        type="number"
                        placeholder="0"
                        min="0"
                        step="1"
                        error={mentorErrors.price_30?.message}
                        {...registerMentor('price_30', { valueAsNumber: true })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="price_60">60 минут</Label>
                      <Input
                        id="price_60"
                        type="number"
                        placeholder="0"
                        min="0"
                        step="1"
                        error={mentorErrors.price_60?.message}
                        {...registerMentor('price_60', { valueAsNumber: true })}
                      />
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    Оставьте поле пустым, если не предоставляете консультации данной продолжительности
                  </p>
                </div>

                {/* Языки и предметы */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <Label htmlFor="languages" className="flex items-center">
                      <Languages className="h-4 w-4 mr-2" />
                      Языки консультаций
                    </Label>
                    <Input
                      id="languages"
                      placeholder="Русский, Английский, Казахский"
                      error={mentorErrors.languages?.message}
                      {...registerMentor('languages')}
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Перечислите через запятую
                    </p>
                  </div>

                  <div>
                    <Label htmlFor="subjects" className="flex items-center">
                      <BookOpen className="h-4 w-4 mr-2" />
                      Предметы и специализации
                    </Label>
                    <Input
                      id="subjects"
                      placeholder="Computer Science, Mathematics, Physics"
                      error={mentorErrors.subjects?.message}
                      {...registerMentor('subjects')}
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Перечислите через запятую
                    </p>
                  </div>
                </div>

                {/* Местоположение */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <Label htmlFor="country">Страна</Label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <select
                        id="country"
                        {...registerMentor('country')}
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

                  <div>
                    <Label htmlFor="city">Город</Label>
                    <Input
                      id="city"
                      placeholder="Ваш город"
                      {...registerMentor('city')}
                    />
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button
                    type="submit"
                    disabled={updateMentorMutation.isLoading}
                    loading={updateMentorMutation.isLoading}
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Сохранить изменения
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Образование */}
        {activeTab === 'education' && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center">
                    <GraduationCap className="h-5 w-5 mr-2" />
                    Образование
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setShowAddUniversity(true)}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Добавить
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mentorProfile?.universities?.length ? (
                    mentorProfile.universities.map((university) => (
                      <div key={university.id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h3 className="font-semibold">{university.university}</h3>
                            {university.degree && (
                              <p className="text-sm text-muted-foreground">{university.degree}</p>
                            )}
                            {university.major && (
                              <p className="text-sm">{university.major}</p>
                            )}
                            <div className="flex items-center text-sm text-muted-foreground mt-2">
                              {university.year_from && university.year_to && (
                                <span>{university.year_from} - {university.year_to}</span>
                              )}
                              {university.country && university.city && (
                                <span className="ml-4">
                                  <MapPin className="h-4 w-4 inline mr-1" />
                                  {university.city}, {university.country}
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="flex gap-2 ml-4">
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => setEditingUniversity(university.id)}
                            >
                              <Edit3 className="h-4 w-4" />
                            </Button>
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              className="text-destructive hover:text-destructive"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <GraduationCap className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <p className="text-muted-foreground">Информация об образовании не добавлена</p>
                      <p className="text-sm text-muted-foreground mt-1">
                        Добавьте информацию о своем образовании, чтобы студенты могли лучше оценить ваш профиль
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Форма добавления/редактирования университета */}
            {(showAddUniversity || editingUniversity) && (
              <Card>
                <CardHeader>
                  <CardTitle>
                    {editingUniversity ? 'Редактировать образование' : 'Добавить образование'}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="md:col-span-2">
                        <Label htmlFor="university">Название университета *</Label>
                        <Input
                          id="university"
                          placeholder="MIT, Stanford University, МГУ..."
                          error={universityErrors.university?.message}
                          {...registerUniversity('university')}
                        />
                      </div>

                      <div>
                        <Label htmlFor="degree">Степень</Label>
                        <Input
                          id="degree"
                          placeholder="Bachelor's, Master's, PhD..."
                          {...registerUniversity('degree')}
                        />
                      </div>

                      <div>
                        <Label htmlFor="major">Специальность</Label>
                        <Input
                          id="major"
                          placeholder="Computer Science, Mathematics..."
                          {...registerUniversity('major')}
                        />
                      </div>

                      <div>
                        <Label htmlFor="year_from">Год поступления</Label>
                        <Input
                          id="year_from"
                          type="number"
                          min="1900"
                          max={new Date().getFullYear()}
                          placeholder="2018"
                          error={universityErrors.year_from?.message}
                          {...registerUniversity('year_from', { valueAsNumber: true })}
                        />
                      </div>

                      <div>
                        <Label htmlFor="year_to">Год окончания</Label>
                        <Input
                          id="year_to"
                          type="number"
                          min="1900"
                          max={new Date().getFullYear() + 10}
                          placeholder="2022"
                          error={universityErrors.year_to?.message}
                          {...registerUniversity('year_to', { valueAsNumber: true })}
                        />
                      </div>

                      <div>
                        <Label htmlFor="uni_country">Страна</Label>
                        <select
                          id="uni_country"
                          {...registerUniversity('country')}
                          className="w-full px-3 py-2 border border-input rounded-md bg-background"
                        >
                          <option value="">Выберите страну</option>
                          {COUNTRIES.map((country) => (
                            <option key={country} value={country}>
                              {country}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <Label htmlFor="uni_city">Город</Label>
                        <Input
                          id="uni_city"
                          placeholder="Город университета"
                          {...registerUniversity('city')}
                        />
                      </div>
                    </div>

                    <div className="flex justify-end gap-2">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
                          setShowAddUniversity(false)
                          setEditingUniversity(null)
                          resetUniversity()
                        }}
                      >
                        Отмена
                      </Button>
                      <Button type="submit">
                        <Save className="h-4 w-4 mr-2" />
                        Сохранить
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            )}
          </div>
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
                Полностью заполненный профиль увеличивает доверие студентов и количество бронирований. 
                Обязательно добавьте информацию об образовании и опыте работы.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold mb-2">⭐ Рейтинг</h3>
              <p className="text-sm text-muted-foreground">
                Ваш рейтинг: {(mentorProfile?.rating_avg ? Number(mentorProfile.rating_avg).toFixed(1) : 'Нет оценок')} 
                {mentorProfile?.rating_count ? ` (${mentorProfile.rating_count} отзывов)` : ''}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Рейтинг формируется на основе отзывов студентов после консультаций
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  )
}
