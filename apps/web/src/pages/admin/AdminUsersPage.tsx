import { useState, useEffect } from 'react'
import { Helmet } from 'react-helmet-async'
import { useSearchParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { toast } from 'sonner'
import {
  Users,
  Search,
  Filter,
  MoreHorizontal,
  Edit,
  Shield,
  UserX,
  UserCheck,
  Mail,
  Phone,
  Calendar,
  Star,
  Download,
  RefreshCw,
  ChevronDown,
  X,
  UserPlus,
} from 'lucide-react'

import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { usersApi } from '@/shared/api/users'
import { adminApi } from '@/shared/api/admin'
// Fallback простого модального окна без общей библиотеки
import type { AdminUser, AdminUserSearchParams, AdminUserAction, CreateMentorRequest } from '@/shared/types/admin'

// Компонент фильтров
interface FiltersProps {
  onFilterChange: (filters: Partial<AdminUserSearchParams>) => void
  currentFilters: AdminUserSearchParams
}

const Filters = ({ onFilterChange, currentFilters }: FiltersProps) => {
  const [showFilters, setShowFilters] = useState(false)

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <Button
          variant="outline"
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-2"
        >
          <Filter className="h-4 w-4" />
          Фильтры
          <ChevronDown className={`h-4 w-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
        </Button>
        
        {Object.keys(currentFilters).filter(key => currentFilters[key as keyof AdminUserSearchParams]).length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onFilterChange({})}
            className="text-muted-foreground"
          >
            <X className="h-4 w-4 mr-1" />
            Сбросить
          </Button>
        )}
      </div>

      {showFilters && (
        <Card>
          <CardContent className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Роль</label>
                <select
                  value={currentFilters.role || ''}
                  onChange={(e) => onFilterChange({ role: e.target.value as any || undefined })}
                  className="w-full px-3 py-2 border border-input rounded-md bg-background"
                >
                  <option value="">Все роли</option>
                  <option value="student">Студенты</option>
                  <option value="mentor">Менторы</option>
                  <option value="admin">Администраторы</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Статус</label>
                <select
                  value={currentFilters.is_active === undefined ? '' : currentFilters.is_active.toString()}
                  onChange={(e) => onFilterChange({ 
                    is_active: e.target.value === '' ? undefined : e.target.value === 'true' 
                  })}
                  className="w-full px-3 py-2 border border-input rounded-md bg-background"
                >
                  <option value="">Все пользователи</option>
                  <option value="true">Активные</option>
                  <option value="false">Заблокированные</option>
                </select>
              </div>

            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// Компонент действий с пользователем
interface UserActionsProps {
  user: AdminUser
  onActivate: (userId: string, active: boolean) => void
}

const UserActions = ({ user, onActivate }: UserActionsProps) => {
  const [showMenu, setShowMenu] = useState(false)

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setShowMenu(!showMenu)}
      >
        <MoreHorizontal className="h-4 w-4" />
      </Button>

      {showMenu && (
        <div className="absolute right-0 top-full mt-1 w-48 bg-background border rounded-lg shadow-lg z-10">
          <div className="py-1">
            <button
              className="w-full px-4 py-2 text-left text-sm hover:bg-muted flex items-center"
              onClick={() => {
                // TODO: Открыть детальную информацию о пользователе
                setShowMenu(false)
              }}
            >
              <Edit className="h-4 w-4 mr-2" />
              Просмотреть детали
            </button>

            {user.is_active ? (
              <button
                className="w-full px-4 py-2 text-left text-sm hover:bg-muted flex items-center text-red-600"
                onClick={() => {
                  onActivate(user.id, false)
                  setShowMenu(false)
                }}
              >
                <UserX className="h-4 w-4 mr-2" />
                Заблокировать
              </button>
            ) : (
              <button
                className="w-full px-4 py-2 text-left text-sm hover:bg-muted flex items-center text-green-600"
                onClick={() => {
                  onActivate(user.id, true)
                  setShowMenu(false)
                }}
              >
                <UserCheck className="h-4 w-4 mr-2" />
                Разблокировать
              </button>
            )}

            {/* Кнопки верификации временно скрыты до реализации эндпоинтов */}
          </div>
        </div>
      )}
    </div>
  )
}

// Модальное окно создания ментора
interface CreateMentorModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

const CreateMentorModal = ({ isOpen, onClose, onSuccess }: CreateMentorModalProps) => {
  const [formData, setFormData] = useState<CreateMentorRequest>({
    email: '',
    password: '',
    name: '',
    phone: '',
    headline: '',
    bio: '',
    price_30: undefined,
    price_45: undefined,
    price_60: undefined,
    languages: [],
    avatar_url: '',
    send_welcome_email: true
  })
  const [errors, setErrors] = useState<Partial<Record<keyof CreateMentorRequest, string>>>({})

  const createMutation = useMutation(
    (data: CreateMentorRequest) => adminApi.createMentor(data),
    {
      onSuccess: () => {
        toast.success('Ментор успешно создан')
        onSuccess()
        onClose()
        // Сбрасываем форму
        setFormData({
          email: '',
          password: '',
          name: '',
          phone: '',
          headline: '',
          bio: '',
          price_30: undefined,
          price_45: undefined,
          price_60: undefined,
          languages: [],
          avatar_url: '',
          send_welcome_email: true
        })
        setErrors({})
      },
      onError: (error: any) => {
        toast.error('Ошибка при создании ментора: ' + (error?.detail || error?.message))
      }
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Простая валидация
    const newErrors: Partial<Record<keyof CreateMentorRequest, string>> = {}
    if (!formData.email) newErrors.email = 'Email обязателен'
    if (!formData.password || formData.password.length < 8) newErrors.password = 'Пароль должен быть минимум 8 символов'
    if (!formData.name) newErrors.name = 'Имя обязательно'
    if (!formData.price_30 && !formData.price_60) {
      newErrors.price_30 = 'Укажите хотя бы одну цену'
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }
    
    createMutation.mutate(formData)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b">
          <h2 className="text-2xl font-bold">Создать ментора</h2>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Email */}
          <div>
            <label className="block text-sm font-medium mb-1">Email *</label>
            <Input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className={errors.email ? 'border-red-500' : ''}
            />
            {errors.email && <p className="text-sm text-red-500 mt-1">{errors.email}</p>}
          </div>

          {/* Пароль */}
          <div>
            <label className="block text-sm font-medium mb-1">Пароль *</label>
            <Input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className={errors.password ? 'border-red-500' : ''}
              placeholder="Минимум 8 символов"
            />
            {errors.password && <p className="text-sm text-red-500 mt-1">{errors.password}</p>}
          </div>

          {/* Имя */}
          <div>
            <label className="block text-sm font-medium mb-1">Имя *</label>
            <Input
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className={errors.name ? 'border-red-500' : ''}
            />
            {errors.name && <p className="text-sm text-red-500 mt-1">{errors.name}</p>}
          </div>

          {/* Телефон */}
          <div>
            <label className="block text-sm font-medium mb-1">Телефон</label>
            <Input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              placeholder="+7 (777) 123-45-67"
            />
          </div>

          {/* Заголовок профиля */}
          <div>
            <label className="block text-sm font-medium mb-1">Заголовок профиля</label>
            <Input
              value={formData.headline || ''}
              onChange={(e) => setFormData({ ...formData, headline: e.target.value })}
              placeholder="Эксперт по поступлению в MIT"
            />
          </div>

          {/* Цены за консультации */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Цена 30 мин (₸)</label>
              <Input
                type="number"
                value={formData.price_30 || ''}
                onChange={(e) => setFormData({ ...formData, price_30: e.target.value ? Number(e.target.value) : undefined })}
                placeholder="15000"
                className={errors.price_30 ? 'border-red-500' : ''}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Цена 60 мин (₸)</label>
              <Input
                type="number"
                value={formData.price_60 || ''}
                onChange={(e) => setFormData({ ...formData, price_60: e.target.value ? Number(e.target.value) : undefined })}
                placeholder="30000"
              />
            </div>
          </div>
          {errors.price_30 && <p className="text-sm text-red-500 mt-1">{errors.price_30}</p>}

          {/* Биография */}
          <div>
            <label className="block text-sm font-medium mb-1">Биография</label>
            <textarea
              value={formData.bio || ''}
              onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              rows={4}
              placeholder="О менторе..."
            />
          </div>

          {/* Языки */}
          <div>
            <label className="block text-sm font-medium mb-1">Языки (через запятую)</label>
            <Input
              value={formData.languages?.join(', ') || ''}
              onChange={(e) => setFormData({ 
                ...formData, 
                languages: e.target.value.split(',').map(s => s.trim()).filter(Boolean) 
              })}
              placeholder="Русский, Английский, Казахский"
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="send_welcome_email"
              checked={formData.send_welcome_email}
              onChange={(e) => setFormData({ ...formData, send_welcome_email: e.target.checked })}
              className="rounded"
            />
            <label htmlFor="send_welcome_email" className="text-sm">
              Отправить приветственное письмо
            </label>
          </div>

          <div className="flex gap-2 pt-4">
            <Button type="submit" disabled={createMutation.isLoading}>
              {createMutation.isLoading ? 'Создание...' : 'Создать ментора'}
            </Button>
            <Button type="button" variant="outline" onClick={onClose}>
              Отмена
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

// Основной компонент
export const AdminUsersPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const queryClient = useQueryClient()
  const [selectedUsers, setSelectedUsers] = useState<string[]>([])
  const [detailsUserId, setDetailsUserId] = useState<string | null>(null)
  const [showCreateMentorModal, setShowCreateMentorModal] = useState(false)

  // Извлечение параметров из URL
  const searchFilters: AdminUserSearchParams = {
    page: parseInt(searchParams.get('page') || '1'),
    page_size: parseInt(searchParams.get('page_size') || '20'),
    search: searchParams.get('search') || undefined,
    role: (searchParams.get('role') as any) || undefined,
    is_active: searchParams.get('is_active') ? searchParams.get('is_active') === 'true' : undefined,
    sort: (searchParams.get('sort') as any) || 'created_desc',
  }

  // Загрузка пользователей
  const { data: usersData, isLoading, error } = useQuery(
    ['admin-users', searchFilters],
    () => usersApi.list(searchFilters as any),
    {
      keepPreviousData: true,
      refetchOnMount: true,
      refetchOnWindowFocus: true,
      staleTime: 30 * 1000,
      cacheTime: 60 * 1000,
      onError: (error: any) => {
        toast.error('Ошибка при загрузке пользователей: ' + (error?.detail || error?.message))
      }
    }
  )

  const { data: detailsUser, isLoading: detailsLoading } = useQuery(
    ['admin-user', detailsUserId],
    () => usersApi.getById(detailsUserId as string),
    { enabled: !!detailsUserId }
  )

  // Мутация активации/деактивации
  const activationMutation = useMutation(({ userId, active }: { userId: string; active: boolean }) => usersApi.setActivation(userId, { is_active: active }), {
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-users'])
      toast.success('Статус пользователя обновлен')
    },
    onError: (error: any) => {
      toast.error('Ошибка при обновлении статуса: ' + (error?.detail || error?.message))
    }
  })

  // Мутация для экспорта (временно отключена до выравнивания роутов экспорта)
  const handleExport = () => {
    toast.info('Экспорт будет доступен после выравнивания эндпоинтов экспорта')
  }

  // Обновление URL при изменении фильтров
  const updateFilters = (newFilters: Partial<AdminUserSearchParams>) => {
    const updatedParams = new URLSearchParams(searchParams)
    
    Object.entries({ ...searchFilters, ...newFilters }).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        updatedParams.set(key, value.toString())
      } else {
        updatedParams.delete(key)
      }
    })
    
    // Сбрасываем страницу при изменении фильтров
    if (Object.keys(newFilters).some(key => key !== 'page')) {
      updatedParams.set('page', '1')
    }
    
    setSearchParams(updatedParams)
  }

  const handleActivate = (userId: string, active: boolean) => {
    activationMutation.mutate({ userId, active })
  }

  const getRoleBadge = (role: string) => {
    const colors = {
      student: 'bg-blue-100 text-blue-700',
      mentor: 'bg-green-100 text-green-700',
      admin: 'bg-purple-100 text-purple-700'
    }
    const labels = {
      student: 'Студент',
      mentor: 'Ментор',
      admin: 'Админ'
    }
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[role as keyof typeof colors]}`}>
        {labels[role as keyof typeof labels]}
      </span>
    )
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <>
      <Helmet>
        <title>Управление пользователями - MasterConnect Admin</title>
      </Helmet>

      <div className="space-y-6">
        {/* Заголовок */}
        <div className="flex justify-between items-center">
      <div>
            <h1 className="text-3xl font-bold">Управление пользователями</h1>
            <p className="text-muted-foreground">
              {usersData?.total || 0} пользователей в системе
          </p>
        </div>
          <div className="flex gap-2">
            <Button
              onClick={() => setShowCreateMentorModal(true)}
            >
              <UserPlus className="h-4 w-4 mr-2" />
              Создать ментора
            </Button>
            <Button
              variant="outline"
              onClick={handleExport}
            >
              <Download className="h-4 w-4 mr-2" />
              Экспорт CSV
            </Button>
            <Button
              variant="outline"
              onClick={() => queryClient.invalidateQueries(['admin-users'])}
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Обновить
            </Button>
          </div>
        </div>

        {/* Поиск и фильтры */}
        <div className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Поиск по имени или email..."
              value={searchFilters.search || ''}
              onChange={(e) => updateFilters({ search: e.target.value || undefined })}
              className="pl-10"
            />
          </div>

          <Filters
            currentFilters={searchFilters}
            onFilterChange={updateFilters}
          />
        </div>

        {/* Статистика */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">{usersData?.total || 0}</div>
              <div className="text-sm text-muted-foreground">Всего пользователей</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-blue-600">
                {usersData?.users?.filter((u: any) => u.role === 'student').length || 0}
              </div>
              <div className="text-sm text-muted-foreground">Студентов</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-green-600">
                {usersData?.users?.filter((u: any) => u.role === 'mentor').length || 0}
              </div>
              <div className="text-sm text-muted-foreground">Менторов</div>
            </CardContent>
          </Card>
        </div>

        {/* Таблица пользователей */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Users className="h-5 w-5 mr-2" />
              Пользователи
            </CardTitle>
          </CardHeader>
          <CardContent>
            {error ? (
              <div className="text-center py-8">
                <div className="text-red-600 mb-2">Ошибка при загрузке данных</div>
                <Button onClick={() => queryClient.invalidateQueries(['admin-users'])}>
                  Попробовать снова
                </Button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4">Пользователь</th>
                      <th className="text-left py-3 px-4">Роль</th>
                      <th className="text-left py-3 px-4">Статус</th>
                      <th className="text-left py-3 px-4">Регистрация</th>
                      <th className="text-left py-3 px-4">Статистика</th>
                      <th className="text-right py-3 px-4">Действия</th>
                    </tr>
                  </thead>
                  <tbody>
                    {isLoading ? (
                      // Скелетоны загрузки
                      Array.from({ length: 5 }).map((_, i) => (
                        <tr key={i} className="border-b">
                          <td className="py-4 px-4">
                            <div className="flex items-center space-x-3">
                              <div className="w-8 h-8 bg-muted rounded-full animate-pulse" />
                              <div className="space-y-2">
                                <div className="h-4 w-32 bg-muted rounded animate-pulse" />
                                <div className="h-3 w-48 bg-muted rounded animate-pulse" />
                              </div>
                            </div>
                          </td>
                          <td className="py-4 px-4">
                            <div className="h-6 w-16 bg-muted rounded animate-pulse" />
                          </td>
                          <td className="py-4 px-4">
                            <div className="h-6 w-20 bg-muted rounded animate-pulse" />
                          </td>
                          <td className="py-4 px-4">
                            <div className="h-4 w-24 bg-muted rounded animate-pulse" />
                          </td>
                          <td className="py-4 px-4">
                            <div className="h-4 w-16 bg-muted rounded animate-pulse" />
                          </td>
                          <td className="py-4 px-4">
                            <div className="h-8 w-8 bg-muted rounded animate-pulse ml-auto" />
                          </td>
                        </tr>
                      ))
                    ) : usersData?.users?.length ? (
                      usersData.users.map((user: any) => (
                        <tr key={user.id} className="border-b hover:bg-muted/50">
                          <td className="py-4 px-4">
                            <div className="flex items-center space-x-3">
                              <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                                <Users className="h-4 w-4 text-primary" />
                              </div>
                              <div>
                                <div className="font-medium">{user.name || 'Без имени'}</div>
                                <div className="text-sm text-muted-foreground flex items-center">
                                  <Mail className="h-3 w-3 mr-1" />
                                  {user.email}
                                </div>
                                {user.phone && (
                                  <div className="text-sm text-muted-foreground flex items-center">
                                    <Phone className="h-3 w-3 mr-1" />
                                    {user.phone}
                                  </div>
                                )}
                              </div>
                            </div>
                          </td>
                          <td className="py-4 px-4">
                            {getRoleBadge(user.role)}
                          </td>
                          <td className="py-4 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              user.is_active 
                                ? 'bg-green-100 text-green-700' 
                                : 'bg-red-100 text-red-700'
                            }`}>
                              {user.is_active ? 'Активен' : 'Заблокирован'}
                            </span>
                          </td>
                          <td className="py-4 px-4">
                            <div className="text-sm">
                              <div className="flex items-center text-muted-foreground">
                                <Calendar className="h-3 w-3 mr-1" />
                                {formatDate(user.created_at)}
                              </div>
                              {user.last_login_at && (
                                <div className="text-xs text-muted-foreground mt-1">
                                  Вход: {formatDate(user.last_login_at)}
                                </div>
                              )}
                            </div>
                          </td>
                          <td className="py-4 px-4">
                            <div className="text-sm">
                              {user.total_bookings !== undefined && (
                                <div>Бронирований: {user.total_bookings}</div>
                              )}
                              {user.mentor_rating && (
                                <div className="flex items-center text-yellow-600">
                                  <Star className="h-3 w-3 mr-1" />
                                  {user.mentor_rating.toFixed(1)}
                                </div>
                              )}
                            </div>
                          </td>
                          <td className="py-4 px-4">
                            <div className="flex justify-end gap-2">
                              <Button variant="ghost" size="sm" onClick={() => setDetailsUserId(user.id)}>
                                Просмотреть детали
                              </Button>
                              <UserActions user={user} onActivate={handleActivate} />
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={6} className="text-center py-8 text-muted-foreground">
                          Пользователи не найдены
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {/* Пагинация */}
            {usersData && Math.ceil((usersData.total || 0) / (usersData.page_size || 1)) > 1 && (
              <div className="flex items-center justify-between mt-6">
                <div className="text-sm text-muted-foreground">
                  Показано {((usersData.page - 1) * usersData.page_size) + 1} - {Math.min(usersData.page * usersData.page_size, usersData.total)} из {usersData.total} пользователей
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => updateFilters({ page: Math.max(1, usersData.page - 1) })}
                    disabled={usersData.page <= 1 || isLoading}
                  >
                    Предыдущая
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      const totalPages = Math.ceil(usersData.total / usersData.page_size)
                      updateFilters({ page: Math.min(totalPages, usersData.page + 1) })
                    }}
                    disabled={usersData.page >= Math.ceil(usersData.total / usersData.page_size) || isLoading}
                  >
                    Следующая
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {detailsUserId && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={() => setDetailsUserId(null)}>
            <div className="bg-background rounded-lg shadow-lg w-[420px] max-w-[90vw]" onClick={(e) => e.stopPropagation()}>
              <div className="border-b px-4 py-3 font-semibold">Детали пользователя</div>
              <div className="p-4">
                {detailsLoading ? (
                  <div>Загрузка...</div>
                ) : detailsUser ? (
                  <div className="space-y-2 text-sm">
                    <div className="font-medium text-base">{detailsUser.name || 'Без имени'}</div>
                    <div>Email: {detailsUser.email}</div>
                    <div>Роль: {detailsUser.role}</div>
                    <div>Статус: {detailsUser.is_active ? 'Активен' : 'Заблокирован'}</div>
                    <div>Регистрация: {new Date(detailsUser.created_at).toLocaleDateString('ru-RU')}</div>
                  </div>
                ) : (
                  <div>Не удалось загрузить данные</div>
                )}
              </div>
              <div className="border-t px-4 py-3 flex justify-end">
                <Button variant="outline" onClick={() => setDetailsUserId(null)}>Закрыть</Button>
              </div>
            </div>
          </div>
        )}

        {/* Модальное окно создания ментора */}
        <CreateMentorModal
          isOpen={showCreateMentorModal}
          onClose={() => setShowCreateMentorModal(false)}
          onSuccess={() => queryClient.invalidateQueries(['admin-users'])}
        />
      </div>
    </>
  )
}
