import { useState, useEffect } from 'react'
import { Helmet } from 'react-helmet-async'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import {
  Calendar,
  Clock,
  Settings,
  Plus,
  Trash2,
  Save,
  RefreshCw,
  AlertCircle,
  Info,
  Zap,
  Globe,
  X,
  CheckCircle,
} from 'lucide-react'
import { dayjsTz } from '@/shared/lib/dayjs'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { availabilityApi } from '@/shared/api/availability'
import { TIMEZONES } from '@/shared/types/profiles'
import {
  DAY_NAMES,
  generateTimeSlots,
  isTimeSlotValid,
  DEFAULT_BUFFER_TIME,
  DEFAULT_MAX_BOOKINGS,
  DEFAULT_ADVANCE_DAYS,
} from '@/shared/types/availability'
import type {
  WeeklySchedule,
  AvailabilitySettings,
  TimeSlot,
  DayOfWeek,
} from '@/shared/types/availability'

// Схема валидации настроек
const settingsSchema = z.object({
  timezone: z.string().min(1, 'Выберите часовой пояс'),
  buffer_time_minutes: z.number().min(5, 'Минимум 5 минут').max(60, 'Максимум 60 минут'),
  max_bookings_per_day: z.number().min(1, 'Минимум 1 бронирование').max(20, 'Максимум 20 бронирований'),
  advance_booking_days: z.number().min(1, 'Минимум 1 день').max(90, 'Максимум 90 дней'),
})

type SettingsFormData = z.infer<typeof settingsSchema>

// Компонент для редактирования временного слота
interface TimeSlotEditorProps {
  slot: TimeSlot
  onUpdate: (slot: TimeSlot) => void
  onRemove: () => void
}

const TimeSlotEditor = ({ slot, onUpdate, onRemove }: TimeSlotEditorProps) => {
  return (
    <div className="flex items-center gap-2 p-3 border rounded-lg bg-muted/30">
      <div className="flex items-center gap-2 flex-1">
        <Input
          type="time"
          value={slot.start_time}
          onChange={(e) => onUpdate({ ...slot, start_time: e.target.value })}
          className="w-32"
        />
        <span className="text-muted-foreground">—</span>
        <Input
          type="time"
          value={slot.end_time}
          onChange={(e) => onUpdate({ ...slot, end_time: e.target.value })}
          className="w-32"
        />
      </div>
      <Button
        variant="ghost"
        size="sm"
        onClick={onRemove}
        className="text-red-600 hover:text-red-700"
      >
        <Trash2 className="h-4 w-4" />
      </Button>
    </div>
  )
}

// Компонент для редактирования расписания дня
interface DayScheduleEditorProps {
  day: DayOfWeek
  slots: TimeSlot[]
  onUpdate: (slots: TimeSlot[]) => void
}

const DayScheduleEditor = ({ day, slots, onUpdate }: DayScheduleEditorProps) => {
  const [isEnabled, setIsEnabled] = useState(slots.length > 0)

  useEffect(() => {
    setIsEnabled(slots.length > 0)
  }, [slots])

  const handleToggle = () => {
    if (isEnabled) {
      onUpdate([])
      setIsEnabled(false)
    } else {
      onUpdate([{ start_time: '09:00', end_time: '17:00' }])
      setIsEnabled(true)
    }
  }

  const handleAddSlot = () => {
    const lastSlot = slots[slots.length - 1]
    const newStart = lastSlot ? lastSlot.end_time : '09:00'
    const newEnd = dayjsTz(`2000-01-01 ${newStart}`).add(1, 'hour').format('HH:mm')
    
    onUpdate([...slots, { start_time: newStart, end_time: newEnd }])
  }

  const handleUpdateSlot = (index: number, updatedSlot: TimeSlot) => {
    const newSlots = [...slots]
    newSlots[index] = updatedSlot
    onUpdate(newSlots)
  }

  const handleRemoveSlot = (index: number) => {
    const newSlots = slots.filter((_, i) => i !== index)
    onUpdate(newSlots)
    if (newSlots.length === 0) {
      setIsEnabled(false)
    }
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">{DAY_NAMES[day]}</CardTitle>
          <Button
            variant={isEnabled ? "default" : "outline"}
            size="sm"
            onClick={handleToggle}
          >
            {isEnabled ? 'Отключить' : 'Включить'}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isEnabled ? (
          <div className="space-y-2">
            {slots.map((slot, index) => (
              <TimeSlotEditor
                key={index}
                slot={slot}
                onUpdate={(updatedSlot) => handleUpdateSlot(index, updatedSlot)}
                onRemove={() => handleRemoveSlot(index)}
              />
            ))}
            <Button
              variant="outline"
              size="sm"
              onClick={handleAddSlot}
              className="w-full"
            >
              <Plus className="h-4 w-4 mr-2" />
              Добавить интервал
            </Button>
          </div>
        ) : (
          <div className="text-center py-4 text-muted-foreground text-sm">
            Выходной
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export const MentorAvailabilityPage = () => {
  const queryClient = useQueryClient()
  const [showQuickSetup, setShowQuickSetup] = useState(false)
  const [weeklySchedule, setWeeklySchedule] = useState<WeeklySchedule>({
    monday: [],
    tuesday: [],
    wednesday: [],
    thursday: [],
    friday: [],
    saturday: [],
    sunday: [],
  })

  // Загрузка данных
  const { data: availability, isLoading, error } = useQuery(
    ['mentor-availability'],
    availabilityApi.getMyAvailability,
    {
      onSuccess: (data) => {
        if (data.weekly_schedule) {
          setWeeklySchedule(data.weekly_schedule)
        }
        if (data.settings) {
          reset({
            timezone: data.settings.timezone,
            buffer_time_minutes: data.settings.buffer_time_minutes,
            max_bookings_per_day: data.settings.max_bookings_per_day,
            advance_booking_days: data.settings.advance_booking_days,
          })
        }
      },
      onError: (error: any) => {
        toast.error('Ошибка при загрузке расписания: ' + (error?.detail || error?.message))
      }
    }
  )

  // Форма настроек
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<SettingsFormData>({
    resolver: zodResolver(settingsSchema),
    defaultValues: {
      timezone: 'Etc/GMT-5',
      buffer_time_minutes: DEFAULT_BUFFER_TIME,
      max_bookings_per_day: DEFAULT_MAX_BOOKINGS,
      advance_booking_days: DEFAULT_ADVANCE_DAYS,
    },
  })

  // Мутация для обновления настроек
  const updateSettingsMutation = useMutation(
    (data: AvailabilitySettings) => availabilityApi.updateSettings(data),
    {
      onSuccess: () => {
        toast.success('Настройки сохранены!')
        queryClient.invalidateQueries(['mentor-availability'])
      },
      onError: (error: any) => {
        toast.error('Ошибка при сохранении настроек: ' + (error?.detail || error?.message))
      }
    }
  )

  // Мутация для обновления расписания
  const updateScheduleMutation = useMutation(
    (schedule: WeeklySchedule) => availabilityApi.updateSchedule(schedule),
    {
      onSuccess: () => {
        toast.success('Расписание сохранено!')
        queryClient.invalidateQueries(['mentor-availability'])
      },
      onError: (error: any) => {
        toast.error('Ошибка при сохранении расписания: ' + (error?.detail || error?.message))
      }
    }
  )

  const onSubmitSettings = (data: SettingsFormData) => {
    updateSettingsMutation.mutate(data)
  }

  const handleSaveSchedule = () => {
    updateScheduleMutation.mutate(weeklySchedule)
  }

  const handleQuickSetup = (template: 'weekdays' | 'everyday' | 'flexible') => {
    let newSchedule: WeeklySchedule = {
      monday: [],
      tuesday: [],
      wednesday: [],
      thursday: [],
      friday: [],
      saturday: [],
      sunday: [],
    }

    switch (template) {
      case 'weekdays':
        // Пн-Пт 9:00-18:00
        newSchedule = {
          monday: [{ start_time: '09:00', end_time: '18:00' }],
          tuesday: [{ start_time: '09:00', end_time: '18:00' }],
          wednesday: [{ start_time: '09:00', end_time: '18:00' }],
          thursday: [{ start_time: '09:00', end_time: '18:00' }],
          friday: [{ start_time: '09:00', end_time: '18:00' }],
          saturday: [],
          sunday: [],
        }
        break
      case 'everyday':
        // Каждый день 10:00-20:00
        const everydaySlot = [{ start_time: '10:00', end_time: '20:00' }]
        newSchedule = {
          monday: everydaySlot,
          tuesday: everydaySlot,
          wednesday: everydaySlot,
          thursday: everydaySlot,
          friday: everydaySlot,
          saturday: everydaySlot,
          sunday: everydaySlot,
        }
        break
      case 'flexible':
        // Гибкий график: утро и вечер
        const flexibleSlots = [
          { start_time: '08:00', end_time: '12:00' },
          { start_time: '18:00', end_time: '22:00' }
        ]
        newSchedule = {
          monday: flexibleSlots,
          tuesday: flexibleSlots,
          wednesday: flexibleSlots,
          thursday: flexibleSlots,
          friday: flexibleSlots,
          saturday: [{ start_time: '10:00', end_time: '16:00' }],
          sunday: [],
        }
        break
    }

    setWeeklySchedule(newSchedule)
    setShowQuickSetup(false)
    toast.success('Шаблон применен! Не забудьте сохранить изменения.')
  }

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded mb-4" />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-64 bg-muted rounded" />
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-xl font-semibold mb-2">Ошибка загрузки</h2>
        <p className="text-muted-foreground mb-4">
          Не удалось загрузить данные о расписании
        </p>
        <Button onClick={() => queryClient.invalidateQueries(['mentor-availability'])}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Попробовать снова
        </Button>
      </div>
    )
  }

  return (
    <>
      <Helmet>
        <title>Управление расписанием - MasterConnect</title>
      </Helmet>

      <div className="space-y-8">
        {/* Заголовок */}
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold mb-4">Управление расписанием</h1>
            <p className="text-muted-foreground">
              Настройте свою доступность для консультаций
            </p>
          </div>
          
          <Button onClick={() => setShowQuickSetup(!showQuickSetup)}>
            <Zap className="h-4 w-4 mr-2" />
            Быстрая настройка
          </Button>
        </div>

        {/* Модальное окно быстрой настройки */}
        {showQuickSetup && (
          <Card className="border-blue-200 bg-blue-50/50">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-blue-600" />
                  Выберите шаблон расписания
                </CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowQuickSetup(false)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button
                  variant="outline"
                  className="h-auto flex-col items-start p-4"
                  onClick={() => handleQuickSetup('weekdays')}
                >
                  <div className="font-semibold mb-2">Рабочие дни</div>
                  <div className="text-sm text-muted-foreground text-left">
                    Пн-Пт: 9:00-18:00<br />
                    Сб-Вс: Выходной
                  </div>
                </Button>
                <Button
                  variant="outline"
                  className="h-auto flex-col items-start p-4"
                  onClick={() => handleQuickSetup('everyday')}
                >
                  <div className="font-semibold mb-2">Каждый день</div>
                  <div className="text-sm text-muted-foreground text-left">
                    Пн-Вс: 10:00-20:00
                  </div>
                </Button>
                <Button
                  variant="outline"
                  className="h-auto flex-col items-start p-4"
                  onClick={() => handleQuickSetup('flexible')}
                >
                  <div className="font-semibold mb-2">Гибкий график</div>
                  <div className="text-sm text-muted-foreground text-left">
                    Пн-Пт: 8:00-12:00, 18:00-22:00<br />
                    Сб: 10:00-16:00<br />
                    Вс: Выходной
                  </div>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Настройки доступности */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Настройки доступности
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmitSettings)} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="timezone" className="flex items-center gap-2">
                    <Globe className="h-4 w-4" />
                    Часовой пояс
                  </Label>
                  <select
                    id="timezone"
                    {...register('timezone')}
                    className="w-full mt-2 px-3 py-2 border border-input rounded-md bg-background"
                  >
                    {TIMEZONES.map((tz) => (
                      <option key={tz.value} value={tz.value}>
                        {tz.label}
                      </option>
                    ))}
                  </select>
                  {errors.timezone && (
                    <p className="text-sm text-red-600 mt-1">{errors.timezone.message}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="buffer_time" className="flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    Буферное время (минуты)
                  </Label>
                  <Input
                    id="buffer_time"
                    type="number"
                    {...register('buffer_time_minutes', { valueAsNumber: true })}
                    className="mt-2"
                  />
                  {errors.buffer_time_minutes && (
                    <p className="text-sm text-red-600 mt-1">{errors.buffer_time_minutes.message}</p>
                  )}
                  <p className="text-xs text-muted-foreground mt-1">
                    Перерыв между консультациями
                  </p>
                </div>

                <div>
                  <Label htmlFor="max_bookings">
                    Макс. бронирований в день
                  </Label>
                  <Input
                    id="max_bookings"
                    type="number"
                    {...register('max_bookings_per_day', { valueAsNumber: true })}
                    className="mt-2"
                  />
                  {errors.max_bookings_per_day && (
                    <p className="text-sm text-red-600 mt-1">{errors.max_bookings_per_day.message}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="advance_days">
                    Бронирование заранее (дни)
                  </Label>
                  <Input
                    id="advance_days"
                    type="number"
                    {...register('advance_booking_days', { valueAsNumber: true })}
                    className="mt-2"
                  />
                  {errors.advance_booking_days && (
                    <p className="text-sm text-red-600 mt-1">{errors.advance_booking_days.message}</p>
                  )}
                  <p className="text-xs text-muted-foreground mt-1">
                    На сколько дней вперед можно бронировать
                  </p>
                </div>
              </div>

              <div className="flex justify-end">
                <Button
                  type="submit"
                  disabled={updateSettingsMutation.isLoading}
                >
                  {updateSettingsMutation.isLoading ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Сохранение...
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Сохранить настройки
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Недельное расписание */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Недельное расписание
              </CardTitle>
              <Button
                onClick={handleSaveSchedule}
                disabled={updateScheduleMutation.isLoading}
              >
                {updateScheduleMutation.isLoading ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Сохранение...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Сохранить расписание
                  </>
                )}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { key: 'monday', day: 0 },
                { key: 'tuesday', day: 1 },
                { key: 'wednesday', day: 2 },
                { key: 'thursday', day: 3 },
                { key: 'friday', day: 4 },
                { key: 'saturday', day: 5 },
                { key: 'sunday', day: 6 },
              ].map(({ key, day }) => (
                <DayScheduleEditor
                  key={key}
                  day={day as DayOfWeek}
                  slots={weeklySchedule[key as keyof WeeklySchedule]}
                  onUpdate={(slots) =>
                    setWeeklySchedule({
                      ...weeklySchedule,
                      [key]: slots,
                    })
                  }
                />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Информация */}
        <Card className="border-blue-200 bg-blue-50/50">
          <CardContent className="p-6">
            <div className="flex items-start gap-3">
              <Info className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="text-sm">
                <p className="font-medium text-blue-800 mb-2">
                  Советы по настройке расписания:
                </p>
                <ul className="text-blue-700 space-y-1">
                  <li>• Установите реалистичные временные рамки для консультаций</li>
                  <li>• Добавьте буферное время между встречами для отдыха</li>
                  <li>• Используйте несколько временных интервалов в день для гибкости</li>
                  <li>• Не забудьте учесть свой часовой пояс</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  )
}
