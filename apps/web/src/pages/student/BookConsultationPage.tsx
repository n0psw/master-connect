import { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Calendar, Clock, ArrowLeft, User, CreditCard, AlertCircle, Check } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Textarea } from '@/shared/ui/textarea'
import { mentorsApi } from '@/shared/api/mentors'
import { bookingsApi } from '@/shared/api/bookings'
import { availabilityApi } from '@/shared/api/availability'
import { useAuthStore } from '@/shared/store/auth'
import { getClientTimezone } from '@/shared/lib/dayjs'
import { getImageUrl } from '@/shared/utils/imageUtils'
import type { MentorDetail } from '@/shared/types/mentors'
import type { BookingCreate } from '@/shared/types/bookings'

// Схема валидации формы бронирования
const bookingSchema = z.object({
  duration: z.enum(['30', '45', '60'], {
    required_error: 'Выберите длительность консультации'
  }),
  date: z.string().min(1, 'Выберите дату'),
  time: z.string().min(1, 'Выберите время'),
  goals: z.string().min(10, 'Опишите ваши цели (минимум 10 символов)'),
  experience: z.string().min(10, 'Расскажите о своем опыте (минимум 10 символов)'),
  questions: z.string().min(5, 'Укажите хотя бы один вопрос (минимум 5 символов)'),
  additionalInfo: z.string().optional()
})

type BookingFormData = z.infer<typeof bookingSchema>

export const BookConsultationPage = () => {
  const { mentorId } = useParams<{ mentorId: string }>()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const queryClient = useQueryClient()

  const [step, setStep] = useState<'mentor' | 'datetime' | 'form' | 'confirmation'>('mentor')
  const [selectedPrice, setSelectedPrice] = useState<number | null>(null)

  // Загрузка данных ментора
  const { data: mentor, isLoading, error } = useQuery(
    ['mentor', mentorId],
    () => mentorsApi.getMentor(mentorId!),
    {
      enabled: !!mentorId,
      onError: (error: any) => {
        toast.error('Ошибка при загрузке ментора: ' + (error?.detail || error?.message))
      }
    }
  )

  const {
    control,
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting }
  } = useForm<BookingFormData>({
    resolver: zodResolver(bookingSchema)
  })

  const selectedDuration = watch('duration')
  const selectedDate = watch('date')
  const selectedTime = watch('time')

  // Подгружаем реальный календарь слотов (следующие 14 дней)
  const dateFrom = useMemo(() => {
    const d = new Date()
    d.setDate(d.getDate() + 1)
    return d
  }, [])

  const dateTo = useMemo(() => {
    const d = new Date(dateFrom)
    d.setDate(dateFrom.getDate() + 14)
    return d
  }, [dateFrom])
  const availabilityKey = useMemo(
    () => `${dateFrom.toISOString().split('T')[0]}_${dateTo.toISOString().split('T')[0]}`,
    [dateFrom, dateTo]
  )

  const clientTimezone = useMemo(() => getClientTimezone(user?.timezone), [user?.timezone])

  const { data: availabilityCalendar, isLoading: isLoadingCalendar } = useQuery(
    ['mentor-availability-calendar', mentorId, selectedDuration, availabilityKey],
    () =>
      availabilityApi.getMentorAvailableCalendar(
        mentorId!,
        dateFrom.toISOString().split('T')[0],
        dateTo.toISOString().split('T')[0],
        selectedDuration ? parseInt(selectedDuration) : undefined,
        clientTimezone
      ),
    {
      enabled: !!mentorId && !!selectedDuration,
      staleTime: 2 * 60 * 1000,  // 2 минуты - данные свежие
      cacheTime: 5 * 60 * 1000,  // 5 минут - хранить в кэше
      refetchOnWindowFocus: true,
      refetchInterval: false,  // Убрать автоматический polling
    }
  )

  // Обновляем цену при изменении длительности
  useEffect(() => {
    if (selectedDuration && mentor) {
      const priceKey = `price_${selectedDuration}` as 'price_30' | 'price_45' | 'price_60'
      const price = mentor.mentor[priceKey]
      setSelectedPrice(price || null)
    }
  }, [selectedDuration, mentor])

  // Мутация для создания бронирования
  const bookingMutation = useMutation(bookingsApi.createBooking, {
    onSuccess: () => {
      queryClient.invalidateQueries(['my-bookings'])
      queryClient.invalidateQueries(['booking-stats'])
      queryClient.invalidateQueries(['mentor-availability-calendar', mentorId, selectedDuration, availabilityKey])
      setStep('confirmation')
      toast.success('Консультация забронирована!')
    },
    onError: (error: any) => {
      queryClient.invalidateQueries(['mentor-availability-calendar', mentorId, selectedDuration, availabilityKey])
      toast.error('Ошибка при бронировании: ' + (error?.detail || error?.message))
    }
  })

  const onSubmit = async (data: BookingFormData) => {
    if (!mentor || !selectedPrice) {
      toast.error('Данные ментора не загружены')
      return
    }

    const slots = availabilityCalendar?.slots || []
    const selectedSlot = slots.find((s: any) => {
      if (!s.is_available) return false
      const utcDate = new Date(s.start)
      const localDateKey = utcDate.toISOString().split('T')[0]
      const hours = utcDate.getHours().toString().padStart(2, '0')
      const minutes = utcDate.getMinutes().toString().padStart(2, '0')
      const timeKey = `${hours}:${minutes}`
      return localDateKey === data.date && timeKey === data.time
    })

    if (!selectedSlot) {
      toast.error('Выбранный слот не найден. Пожалуйста, обновите календарь.')
      return
    }

    const scheduledAtIso = selectedSlot.start
    
    const specificQuestions = data.questions
      ? data.questions
          .split('\n')
          .map(q => q.trim())
          .filter(q => q.length >= 5)
      : []
    
    const finalQuestions = specificQuestions.length > 0 
      ? specificQuestions 
      : (data.questions?.trim() ? [data.questions.trim()] : [])
    
    if (finalQuestions.length === 0) {
      toast.error('Укажите хотя бы один вопрос (минимум 5 символов)')
      return
    }

    const bookingData: BookingCreate = {
      mentor_id: mentorId!,
      starts_at: scheduledAtIso,
      duration_minutes: parseInt(data.duration),
      intake_form: {
        goals: data.goals,
        current_situation: data.experience,
        specific_questions: finalQuestions,
        additional_info: data.additionalInfo || ''
      },
      notes: data.questions || undefined
    }

    bookingMutation.mutate(bookingData)
  }

  // Доступные даты на основе календаря (только даты с доступными слотами)
  const getDateOptions = () => {
    const dates: { value: string; label: string }[] = []
    const slots = availabilityCalendar?.slots || []
    const availableSlots = slots.filter((s: any) => s.is_available === true)
    
    // Конвертируем UTC слоты в локальное время студента для отображения дат
    const datesMap = new Map<string, Date>()
    availableSlots.forEach((s: any) => {
      const utcDate = new Date(s.start)
      const localDate = new Date(utcDate.getTime())
      const dateKey = localDate.toISOString().split('T')[0]
      if (!datesMap.has(dateKey)) {
        datesMap.set(dateKey, localDate)
      }
    })
    
    datesMap.forEach((localDate, dateKey) => {
      dates.push({
        value: dateKey,
        label: localDate.toLocaleDateString('ru-RU', { weekday: 'short', day: 'numeric', month: 'short' })
      })
    })
    
    return dates.sort((a, b) => a.value.localeCompare(b.value))
  }

  // Доступные времена для выбранной даты (только свободные слоты)
  const getTimeOptions = (): string[] => {
    if (!selectedDate) return []
    const slots = availabilityCalendar?.slots || []
    
    // Фильтруем слоты по дате в локальном времени студента и конвертируем время
    const times = slots
      .filter((s: any) => {
        if (!s.is_available) return false
        const utcDate = new Date(s.start)
        const localDateKey = utcDate.toISOString().split('T')[0]
        return localDateKey === selectedDate
      })
      .map((s: any) => {
        const utcDate = new Date(s.start)
        const hours = utcDate.getHours().toString().padStart(2, '0')
        const minutes = utcDate.getMinutes().toString().padStart(2, '0')
        return `${hours}:${minutes}`
      })
    
    return Array.from(new Set(times)).sort()
  }

  const formatPrice = (amount: number) => {
    return amount.toLocaleString('ru-RU') + ' ₸'
  }

  if (isLoading) {
    return (
      <div className="container-wide py-8">
        <div className="max-w-2xl mx-auto">
          <div className="animate-pulse space-y-8">
            <div className="h-8 bg-muted rounded" />
            <div className="h-64 bg-muted rounded" />
          </div>
        </div>
      </div>
    )
  }

  if (error || !mentor) {
    return (
      <div className="container-wide py-8">
        <div className="max-w-2xl mx-auto text-center">
          <p className="text-destructive text-lg mb-4">Ментор не найден</p>
          <Button onClick={() => navigate('/mentors')}>
            Вернуться к каталогу
          </Button>
        </div>
      </div>
    )
  }

  return (
    <>
      <Helmet>
        <title>Бронирование консультации - {mentor.user.name || 'Ментор'} - MasterConnect</title>
      </Helmet>

      <div className="container-wide py-8">
        <div className="max-w-4xl mx-auto">
          {/* Навигация */}
          <div className="mb-6">
            <Button 
              variant="ghost" 
              onClick={() => navigate(`/mentors/${mentorId}`)}
              className="flex items-center gap-2 mb-4"
            >
              <ArrowLeft className="h-4 w-4" />
              Назад к профилю ментора
            </Button>
          </div>

          {/* Прогресс */}
          <div className="mb-8">
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 ${
                ['mentor', 'datetime', 'form', 'confirmation'].includes(step) ? 'text-primary' : 'text-muted-foreground'
              }`}>
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                  <Check className="h-4 w-4" />
                </div>
                <span className="text-sm font-medium">Ментор</span>
              </div>
              
              <div className="flex-1 h-px bg-border" />
              
              <div className={`flex items-center space-x-2 ${
                ['datetime', 'form', 'confirmation'].includes(step) ? 'text-primary' : 'text-muted-foreground'
              }`}>
                <div className={`flex h-8 w-8 items-center justify-center rounded-full ${
                  ['datetime', 'form', 'confirmation'].includes(step) ? 'bg-primary text-primary-foreground' : 'bg-muted'
                }`}>
                  {['form', 'confirmation'].includes(step) ? <Check className="h-4 w-4" /> : '2'}
                </div>
                <span className="text-sm font-medium">Время</span>
              </div>
              
              <div className="flex-1 h-px bg-border" />
              
              <div className={`flex items-center space-x-2 ${
                ['form', 'confirmation'].includes(step) ? 'text-primary' : 'text-muted-foreground'
              }`}>
                <div className={`flex h-8 w-8 items-center justify-center rounded-full ${
                  ['form', 'confirmation'].includes(step) ? 'bg-primary text-primary-foreground' : 'bg-muted'
                }`}>
                  {step === 'confirmation' ? <Check className="h-4 w-4" /> : '3'}
                </div>
                <span className="text-sm font-medium">Форма</span>
              </div>
              
              <div className="flex-1 h-px bg-border" />
              
              <div className={`flex items-center space-x-2 ${
                step === 'confirmation' ? 'text-primary' : 'text-muted-foreground'
              }`}>
                <div className={`flex h-8 w-8 items-center justify-center rounded-full ${
                  step === 'confirmation' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                }`}>
                  4
                </div>
                <span className="text-sm font-medium">Готово</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Информация о менторе */}
            <div className="lg:col-span-1">
              <Card className="sticky top-8">
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4 mb-4">
                    <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden">
                      {mentor.mentor.avatar_url ? (
                        <img 
                          src={getImageUrl(mentor.mentor.avatar_url)} 
                          alt={mentor.user.name || 'Ментор'} 
                          className="w-16 h-16 rounded-full object-cover"
                        />
                      ) : (
                        <span className="text-2xl font-semibold text-primary">
                          {(mentor.user.name || 'М')[0].toUpperCase()}
                        </span>
                      )}
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">
                        {mentor.user.name || 'Ментор'}
                      </h3>
                      {mentor.mentor.headline && (
                        <p className="text-sm text-muted-foreground">
                          {mentor.mentor.headline}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <h4 className="font-medium text-sm mb-2">Варианты консультации:</h4>
                      <div className="space-y-2">
                        {mentor.mentor.price_30 && (
                          <div className="flex justify-between text-sm">
                            <span>30 минут</span>
                            <span className="font-medium">{formatPrice(mentor.mentor.price_30)}</span>
                          </div>
                        )}
                        {mentor.mentor.price_45 && (
                          <div className="flex justify-between text-sm">
                            <span>45 минут</span>
                            <span className="font-medium">{formatPrice(mentor.mentor.price_45)}</span>
                          </div>
                        )}
                        {mentor.mentor.price_60 && (
                          <div className="flex justify-between text-sm">
                            <span>60 минут</span>
                            <span className="font-medium">{formatPrice(mentor.mentor.price_60)}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {selectedPrice && (
                      <div className="border-t pt-3">
                        <div className="flex justify-between items-center">
                          <span className="font-medium">Итого:</span>
                          <span className="text-lg font-bold text-primary">
                            {formatPrice(selectedPrice)}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Основная форма */}
            <div className="lg:col-span-2">
              {step === 'confirmation' ? (
                <Card>
                  <CardContent className="p-8 text-center">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Check className="h-8 w-8 text-green-600" />
                    </div>
                    <h2 className="text-2xl font-bold mb-4">Консультация забронирована!</h2>
                    <p className="text-muted-foreground mb-6">
                      Ваша заявка отправлена ментору. Вы получите подтверждение на email.
                    </p>
                    <div className="space-y-3">
                      <Button asChild className="w-full">
                        <Link to="/student/bookings">
                          Мои бронирования
                        </Link>
                      </Button>
                      <Button variant="outline" asChild className="w-full">
                        <Link to="/student/dashboard">
                          Вернуться на главную
                        </Link>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <form onSubmit={handleSubmit(onSubmit)}>
                  <div className="space-y-6">
                    {/* Выбор длительности и времени */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center">
                          <Clock className="h-5 w-5 mr-2" />
                          Выберите время и длительность
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-6">
                        {/* Длительность */}
                        <div>
                          <Label className="text-base font-medium mb-4 block">
                            Длительность консультации
                          </Label>
                          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            {mentor.mentor.price_30 && (
                              <label className={`cursor-pointer border-2 rounded-lg p-4 text-center transition-colors ${
                                selectedDuration === '30' ? 'border-primary bg-primary/5' : 'border-input hover:bg-accent'
                              }`}>
                                <input
                                  type="radio"
                                  value="30"
                                  {...register('duration')}
                                  className="sr-only"
                                />
                                <div className="font-semibold">30 минут</div>
                                <div className="text-sm text-muted-foreground">
                                  {formatPrice(mentor.mentor.price_30)}
                                </div>
                                <div className="text-xs text-muted-foreground mt-1">
                                  Быстрая консультация
                                </div>
                              </label>
                            )}

                            {mentor.mentor.price_45 && (
                              <label className={`cursor-pointer border-2 rounded-lg p-4 text-center transition-colors ${
                                selectedDuration === '45' ? 'border-primary bg-primary/5' : 'border-input hover:bg-accent'
                              }`}>
                                <input
                                  type="radio"
                                  value="45"
                                  {...register('duration')}
                                  className="sr-only"
                                />
                                <div className="font-semibold">45 минут</div>
                                <div className="text-sm text-muted-foreground">
                                  {formatPrice(mentor.mentor.price_45)}
                                </div>
                                <div className="text-xs text-muted-foreground mt-1">
                                  Стандартная консультация
                                </div>
                              </label>
                            )}

                            {mentor.mentor.price_60 && (
                              <label className={`cursor-pointer border-2 rounded-lg p-4 text-center transition-colors ${
                                selectedDuration === '60' ? 'border-primary bg-primary/5' : 'border-input hover:bg-accent'
                              }`}>
                                <input
                                  type="radio"
                                  value="60"
                                  {...register('duration')}
                                  className="sr-only"
                                />
                                <div className="font-semibold">60 минут</div>
                                <div className="text-sm text-muted-foreground">
                                  {formatPrice(mentor.mentor.price_60)}
                                </div>
                                <div className="text-xs text-muted-foreground mt-1">
                                  Развернутая консультация
                                </div>
                              </label>
                            )}
                          </div>
                          {errors.duration && (
                            <p className="text-sm text-destructive mt-2">{errors.duration.message}</p>
                          )}
                        </div>

                        {/* Дата */}
                        <div>
                          <Label htmlFor="date" className="text-base font-medium">Дата</Label>
                          {isLoadingCalendar ? (
                            <div className="text-center py-8">
                              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                              <p className="mt-2 text-sm text-muted-foreground">Загрузка доступных дат...</p>
                            </div>
                          ) : (
                            <>
                              <select
                                id="date"
                                {...register('date')}
                                className="w-full mt-2 px-3 py-2 border border-input rounded-md bg-background"
                              >
                                <option value="">Выберите дату</option>
                                {getDateOptions().map((date) => (
                                  <option key={date.value} value={date.value}>
                                    {date.label}
                                  </option>
                                ))}
                              </select>
                              {errors.date && (
                                <p className="text-sm text-destructive mt-2">{errors.date.message}</p>
                              )}
                            </>
                          )}
                        </div>

                        {/* Время */}
                        {selectedDate && (
                          <div>
                            <Label htmlFor="time" className="text-base font-medium">Время</Label>
                            <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-6 gap-2 mt-2">
                              {getTimeOptions().map((timeSlot: string) => (
                                <label
                                  key={timeSlot}
                                  className={`cursor-pointer border rounded-md p-2 text-center text-sm transition-colors ${
                                    selectedTime === timeSlot ? 'border-primary bg-primary text-primary-foreground' : 'border-input hover:bg-accent'
                                  }`}
                                >
                                  <input
                                    type="radio"
                                    value={timeSlot}
                                    {...register('time')}
                                    className="sr-only"
                                  />
                                  {timeSlot}
                                </label>
                              ))}
                            </div>
                            {errors.time && (
                              <p className="text-sm text-destructive mt-2">{errors.time.message}</p>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>

                    {/* Анкета */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center">
                          <User className="h-5 w-5 mr-2" />
                          Расскажите о себе
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-6">
                        <div>
                          <Label htmlFor="goals" className="text-base font-medium">
                            Ваши цели и что хотите получить от консультации *
                          </Label>
                          <Textarea
                            id="goals"
                            placeholder="Например: Хочу поступить в MIT на Computer Science, нужна помощь с выбором предметов и подготовкой документов..."
                            className="mt-2"
                            rows={4}
                            {...register('goals')}
                          />
                          {errors.goals && (
                            <p className="text-sm text-destructive mt-2">{errors.goals.message}</p>
                          )}
                        </div>

                        <div>
                          <Label htmlFor="experience" className="text-base font-medium">
                            Ваш текущий опыт и достижения *
                          </Label>
                          <Textarea
                            id="experience"
                            placeholder="Например: Учусь в 11 классе, отличник по математике и физике, участвовал в олимпиадах..."
                            className="mt-2"
                            rows={4}
                            {...register('experience')}
                          />
                          {errors.experience && (
                            <p className="text-sm text-destructive mt-2">{errors.experience.message}</p>
                          )}
                        </div>

                        <div>
                          <Label htmlFor="questions" className="text-base font-medium">
                            Конкретные вопросы для ментора (необязательно)
                          </Label>
                          <Textarea
                            id="questions"
                            placeholder="Какие есть конкретные вопросы, которые хотите задать?"
                            className="mt-2"
                            rows={3}
                            {...register('questions')}
                          />
                        </div>

                        <div>
                          <Label htmlFor="additionalInfo" className="text-base font-medium">
                            Дополнительная информация (необязательно)
                          </Label>
                          <Textarea
                            id="additionalInfo"
                            placeholder="Любая дополнительная информация, которая может быть полезна ментору"
                            className="mt-2"
                            rows={3}
                            {...register('additionalInfo')}
                          />
                        </div>
                      </CardContent>
                    </Card>

                    {/* Оплата */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center">
                          <CreditCard className="h-5 w-5 mr-2" />
                          Оплата и подтверждение
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                          <div className="flex items-start">
                            <AlertCircle className="h-5 w-5 text-blue-600 mr-3 mt-0.5" />
                            <div>
                              <h4 className="font-medium text-blue-900 mb-1">Как проходит оплата</h4>
                              <p className="text-sm text-blue-800">
                                1. Нажмите "Забронировать" - консультация будет зарезервирована на 30 минут<br/>
                                2. Переведите деньги ментору через Kaspi или другие способы<br/>
                                3. Отметьте "Я оплатил" в личном кабинете<br/>
                                4. После проверки админом консультация будет подтверждена
                              </p>
                            </div>
                          </div>
                        </div>

                        <Button 
                          type="submit" 
                          className="w-full" 
                          size="lg"
                          disabled={isSubmitting || bookingMutation.isLoading}
                          loading={isSubmitting || bookingMutation.isLoading}
                        >
                          <Calendar className="h-5 w-5 mr-2" />
                          Забронировать консультацию
                          {selectedPrice && (
                            <span className="ml-2">- {formatPrice(selectedPrice)}</span>
                          )}
                        </Button>
                      </CardContent>
                    </Card>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
