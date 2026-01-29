import { useState, useEffect, useRef } from 'react'
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

const DAY_KEYS: Array<keyof WeeklySchedule> = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday',
]

const DAY_LABELS: Record<keyof WeeklySchedule, string> = {
  monday: DAY_NAMES[0],
  tuesday: DAY_NAMES[1],
  wednesday: DAY_NAMES[2],
  thursday: DAY_NAMES[3],
  friday: DAY_NAMES[4],
  saturday: DAY_NAMES[5],
  sunday: DAY_NAMES[6],
}

const parseTimeToMinutes = (time: string): number | null => {
  const match = /^(\d{1,2}):([0-5]\d)$/.exec(time)
  if (!match) {
    return null
  }

  const hours = Number(match[1])
  const minutes = Number(match[2])
  if (Number.isNaN(hours) || hours > 23) {
    return null
  }
  return hours * 60 + minutes
}

const formatMinutes = (minutes: number): string => {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`
}

const cloneSlots = (slots: TimeSlot[]): TimeSlot[] => slots.map((slot) => ({ ...slot }))

const validateWeeklySchedule = (schedule: WeeklySchedule): string | null => {
  for (const dayKey of DAY_KEYS) {
    const slots = schedule[dayKey]
    if (!slots || slots.length === 0) {
      continue
    }

    const parsedSlots: Array<{ start: number; end: number }> = []

    for (let index = 0; index < slots.length; index += 1) {
      const slot = slots[index]
      const start = parseTimeToMinutes(slot.start_time)
      const end = parseTimeToMinutes(slot.end_time)

      if (start === null || end === null) {
        return `РћС€РёР±РєР° РІ ${DAY_LABELS[dayKey]}: РїСЂРѕРІРµСЂСЊС‚Рµ С„РѕСЂРјР°С‚ РІСЂРµРјРµРЅРё РІ РёРЅС‚РµСЂРІР°Р»Рµ ${index + 1}.`
      }

      if (!isTimeSlotValid(slot)) {
        return `РћС€РёР±РєР° РІ ${DAY_LABELS[dayKey]}: РєРѕРЅРµС† РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ РїРѕР·Р¶Рµ РЅР°С‡Р°Р»Р° (РёРЅС‚РµСЂРІР°Р» ${index + 1}).`
      }

      parsedSlots.push({ start, end })
    }

    const sorted = [...parsedSlots].sort((a, b) => a.start - b.start)
    for (let index = 1; index < sorted.length; index += 1) {
      if (sorted[index].start < sorted[index - 1].end) {
        return `РћС€РёР±РєР° РІ ${DAY_LABELS[dayKey]}: РёРЅС‚РµСЂРІР°Р»С‹ РїРµСЂРµСЃРµРєР°СЋС‚СЃСЏ.`
      }
    }
  }

  return null
}

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
  const isEnabled = slots.length > 0

  const handleToggle = () => {
    if (isEnabled) {
      onUpdate([])
    } else {
      onUpdate([{ start_time: '09:00', end_time: '17:00' }])
    }
  }

  const handleAddSlot = () => {
    const lastSlot = slots[slots.length - 1]
    const newStart = lastSlot ? lastSlot.end_time : '09:00'
    const startMinutes = parseTimeToMinutes(newStart)
    if (startMinutes === null) {
      toast.error('РќРµСѓРґР°С‡РЅРѕРµ РІСЂРµРјСЏ РЅР°С‡Р°Р»Р°. РСЃРїСЂР°РІСЊС‚Рµ РїСЂРµРґС‹РґСѓС‰РёР№ РёРЅС‚РµСЂРІР°Р».')
      return
    }

    const endMinutes = startMinutes + 60
    if (endMinutes >= 24 * 60) {
      toast.error('РќРµР»СЊР·СЏ РґРѕР±Р°РІРёС‚СЊ РёРЅС‚РµСЂРІР°Р» РїРѕСЃР»Рµ 24:00.')
      return
    }

    const newEnd = formatMinutes(endMinutes)
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
  const [isScheduleDirty, setIsScheduleDirty] = useState(false)
  const scheduleDirtyRef = useRef(false)
  const settingsDirtyRef = useRef(false)
  const hasLoadedRef = useRef(false)

  const { data: availability, isLoading, error } = useQuery(
    ['mentor-availability'],
    availabilityApi.getMyAvailability,
    {
      onError: (error: any) => {
        toast.error('Ошибка при загрузке расписания: ' + (error?.detail || error?.message))
      }
    }
  )

  // Форма настроек
  const {
    register,
    handleSubmit,
    formState: { errors, isDirty: isSettingsDirty },
    reset,
    getValues,
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
  useEffect(() => {
    if (!availability) {
      return
    }

    const isInitialLoad = !hasLoadedRef.current
    if (availability.weekly_schedule && (isInitialLoad || !scheduleDirtyRef.current)) {
      setWeeklySchedule(availability.weekly_schedule)
      scheduleDirtyRef.current = false
      setIsScheduleDirty(false)
    }
    if (availability.settings && (isInitialLoad || !settingsDirtyRef.current)) {
      reset({
        timezone: availability.settings.timezone,
        buffer_time_minutes: availability.settings.buffer_time_minutes,
        max_bookings_per_day: availability.settings.max_bookings_per_day,
        advance_booking_days: availability.settings.advance_booking_days,
      })
      settingsDirtyRef.current = false
    }
    hasLoadedRef.current = true
  }, [availability, reset])

  useEffect(() => {
    settingsDirtyRef.current = isSettingsDirty
  }, [isSettingsDirty])

  const markScheduleDirty = () => {
    if (!scheduleDirtyRef.current) {
      scheduleDirtyRef.current = true
      setIsScheduleDirty(true)
    }
  }

  const setWeeklyScheduleFromUser = (nextSchedule: WeeklySchedule) => {
    markScheduleDirty()
    setWeeklySchedule(nextSchedule)
  }

  const updateScheduleDay = (dayKey: keyof WeeklySchedule, slots: TimeSlot[]) => {
    markScheduleDirty()
    setWeeklySchedule((prev) => ({
      ...prev,
      [dayKey]: slots,
    }))
  }

  const updateSettingsMutation = useMutation(
    (data: AvailabilitySettings) => availabilityApi.updateSettings(data),
    {
      onSuccess: (data) => {
        toast.success('Настройки сохранены!')
        const nextValues = data
          ? {
              timezone: data.timezone,
              buffer_time_minutes: data.buffer_time_minutes,
              max_bookings_per_day: data.max_bookings_per_day,
              advance_booking_days: data.advance_booking_days,
            }
          : getValues()
        reset(nextValues)
        settingsDirtyRef.current = false
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
      onSuccess: (data) => {
        toast.success('Расписание сохранено!')
        if (data) {
          setWeeklySchedule(data)
        }
        scheduleDirtyRef.current = false
        setIsScheduleDirty(false)
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
    const validationError = validateWeeklySchedule(weeklySchedule)
    if (validationError) {
      toast.error(validationError)
      return
    }
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
          monday: cloneSlots(everydaySlot),
          tuesday: cloneSlots(everydaySlot),
          wednesday: cloneSlots(everydaySlot),
          thursday: cloneSlots(everydaySlot),
          friday: cloneSlots(everydaySlot),
          saturday: cloneSlots(everydaySlot),
          sunday: cloneSlots(everydaySlot),
        }
        break
      case 'flexible':
        // Гибкий график: утро и вечер
        const flexibleSlots = [
          { start_time: '08:00', end_time: '12:00' },
          { start_time: '18:00', end_time: '22:00' }
        ]
        newSchedule = {
          monday: cloneSlots(flexibleSlots),
          tuesday: cloneSlots(flexibleSlots),
          wednesday: cloneSlots(flexibleSlots),
          thursday: cloneSlots(flexibleSlots),
          friday: cloneSlots(flexibleSlots),
          saturday: [{ start_time: '10:00', end_time: '16:00' }],
          sunday: [],
        }
        break
    }

    setWeeklyScheduleFromUser(newSchedule)
    setShowQuickSetup(false)
    toast.success('Шаблон применен! Не забудьте сохранить изменения.')
  }

  const hasUnsavedChanges = isScheduleDirty || isSettingsDirty

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
            <div className="flex items-center gap-2 text-sm mt-2">
              {hasUnsavedChanges ? (
                <>
                  <AlertCircle className="h-4 w-4 text-amber-600" />
                  <span className="text-amber-700">Есть несохраненные изменения</span>
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="text-green-700">Все изменения сохранены</span>
                </>
              )}
            </div>
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
                  onUpdate={(slots) => updateScheduleDay(key as keyof WeeklySchedule, slots)}
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


