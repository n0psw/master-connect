import React, { useState, useEffect } from 'react'
import { Helmet } from 'react-helmet-async'
import { useSearchParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { toast } from 'sonner'
import {
  GraduationCap,
  Search,
  MoreHorizontal,
  Eye,
  UserX,
  UserCheck,
  Star,
  RefreshCw,
  X,
  XCircle,
  Clock,
  DollarSign,
  Globe,
  BookOpen,
} from 'lucide-react'

import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { mentorsApi } from '@/shared/api/mentors'
import { usersApi } from '@/shared/api/users'
import { adminApi } from '@/shared/api/admin'
import { AdminMentorCreateData, AdminMentorUpdateData, CreateMentorRequest } from '@/shared/types/admin'
import type { 
  Mentor, 
  MentorStats, 
  MentorListResponse,
  MentorDetail,
  MentorCard 
} from '@/shared/types/mentors'
import type { 
  AdminMentorSearchParams, 
  AdminMentorAction 
} from '@/shared/types/admin'



export const AdminMentorsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [detailsMentorId, setDetailsMentorId] = useState<string | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingMentorId, setEditingMentorId] = useState<string | null>(null)
  const [deletingMentorId, setDeletingMentorId] = useState<string | null>(null)
  const queryClient = useQueryClient()

  // Параметры поиска (упрощенные, фильтры удалены)
  const searchFilters: AdminMentorSearchParams = {
    page: Number(searchParams.get('page')) || 1,
    page_size: Number(searchParams.get('page_size')) || 20,
    search: searchParams.get('search') || undefined,
    sort: (searchParams.get('sort') as any) || 'created_desc'
  }

  // Загрузка данных
  const { data: mentorsData, isLoading: mentorsLoading, error: mentorsError } = useQuery(
    ['admin-mentors', searchFilters],
    () => mentorsApi.getMentors({
      page: searchFilters.page || 1,
      page_size: searchFilters.page_size || 20,
      search: searchFilters.search,
      sort: searchFilters.sort === 'name_asc' ? 'name_asc' : 
            searchFilters.sort === 'name_desc' ? 'name_desc' :
            searchFilters.sort === 'rating_asc' ? 'rating_asc' : 'rating_desc'
    }),
    { 
      staleTime: 30000,
      onError: (error: any) => {
        console.error('Error loading mentors:', error)
        toast.error('Ошибка при загрузке менторов: ' + (error?.detail || error?.message))
      }
    }
  )

  const { data: mentorStats, isLoading: statsLoading, error: statsError } = useQuery(
    'mentor-stats',
    () => mentorsApi.getMentorStats(),
    { 
      staleTime: 60000,
      retry: false, // Не повторять запрос при ошибке
      onError: (error: any) => {
        console.error('Error loading mentor stats:', error)
        // Не показываем toast для ошибок авторизации - это нормально
        if (error?.status !== 401 && error?.status !== 403) {
          toast.error('Ошибка при загрузке статистики: ' + (error?.detail || error?.message))
        }
      }
    }
  )

  const { data: detailsMentor, isLoading: detailsLoading } = useQuery(
    ['mentor-details', detailsMentorId],
    () => detailsMentorId ? mentorsApi.getMentorAdmin(detailsMentorId) : null,
    { enabled: !!detailsMentorId }
  )


  // Обработчики
  const handleFilterChange = (newFilters: Partial<AdminMentorSearchParams>) => {
    const updatedFilters = { ...searchFilters, ...newFilters, page: 1 }
    const params = new URLSearchParams()
    
    Object.entries(updatedFilters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        if (Array.isArray(value)) {
          params.set(key, value.join(','))
        } else {
          params.set(key, String(value))
        }
      }
    })
    
    setSearchParams(params)
  }

  const handleSearch = (search: string) => {
    handleFilterChange({ search: search || undefined })
  }


  const handleBlockUser = async (userId: string) => {
    try {
      await usersApi.activateUser(userId, false)
      queryClient.invalidateQueries(['admin-mentors'])
      toast.success('Пользователь заблокирован')
    } catch (error) {
      toast.error('Ошибка при блокировке пользователя')
    }
  }

  const handleUnblockUser = async (userId: string) => {
    try {
      await usersApi.activateUser(userId, true)
      queryClient.invalidateQueries(['admin-mentors'])
      toast.success('Пользователь разблокирован')
    } catch (error) {
      toast.error('Ошибка при разблокировке пользователя')
    }
  }

  const handleMentorAction = (mentor: MentorCard, action: string) => {
    switch (action) {
      case 'view':
        setDetailsMentorId(mentor.user_id)
        break
      case 'edit':
        setEditingMentorId(mentor.user_id)
        setShowEditModal(true)
        break
      case 'delete':
        if (confirm(`Вы уверены, что хотите удалить ментора ${mentor.name}?`)) {
          handleDeleteMentor(mentor.user_id)
        }
        break
    }
  }

  const handleDeleteMentor = async (mentorId: string) => {
    setDeletingMentorId(mentorId)
    try {
      await mentorsApi.deleteMentor(mentorId)
      queryClient.invalidateQueries(['admin-mentors'])
      queryClient.invalidateQueries(['mentor-stats'])
      toast.success('Ментор успешно удален')
    } catch (error: any) {
      console.error('Error deleting mentor:', error)
      const errorMessage = error?.response?.data?.detail || 'Произошла ошибка при удалении ментора'
      toast.error(`Ошибка: ${errorMessage}`)
    } finally {
      setDeletingMentorId(null)
    }
  }

  // Действия для ментора
  const getMentorActions = (mentor: MentorCard): AdminMentorAction[] => [
    {
      id: 'view',
      action: 'view',
      label: 'Просмотреть детали',
      icon: Eye,
      variant: 'outline'
    },
    {
      id: 'edit',
      action: 'edit',
      label: 'Редактировать',
      icon: UserCheck,
      variant: 'default'
    },
    {
      id: 'delete',
      action: 'delete',
      label: 'Удалить',
      icon: UserX,
      variant: 'destructive'
    },
  ]

  // Вычисляем total_pages
  const totalPages = mentorsData ? Math.ceil(mentorsData.total / (searchFilters.page_size || 20)) : 0

  if (mentorsLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded mb-4 w-48" />
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-24 bg-muted rounded" />
            ))}
          </div>
          <div className="h-96 bg-muted rounded" />
        </div>
      </div>
    )
  }

  if (mentorsError) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-red-500 mb-4">Ошибка загрузки данных</p>
          <Button onClick={() => queryClient.invalidateQueries(['admin-mentors'])}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Повторить
          </Button>
        </div>
      </div>
    )
  }

  return (
    <>
      <Helmet>
        <title>Управление менторами - MasterConnect Admin</title>
      </Helmet>

      <div className="space-y-6">
        {/* Заголовок */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Менторы</h1>
            <p className="text-muted-foreground">
              Управление менторами платформы
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button 
              onClick={() => setShowCreateModal(true)}
            >
              <UserCheck className="h-4 w-4 mr-2" />
              Добавить ментора
            </Button>
            <Button variant="outline" onClick={() => queryClient.invalidateQueries(['admin-mentors'])}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Обновить
            </Button>
          </div>
        </div>

        {/* Статистика */}
        {(mentorStats || statsError) && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Всего менторов</CardTitle>
                <GraduationCap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {statsLoading ? '...' : (mentorStats?.total_mentors || 0)}
                </div>
              </CardContent>
            </Card>
            
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Средний рейтинг</CardTitle>
                <Star className="h-4 w-4 text-yellow-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {statsLoading ? '...' : (Number(mentorStats?.average_rating) || 0).toFixed(1)}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Активные менторы</CardTitle>
                <UserCheck className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {statsLoading ? '...' : (mentorStats?.active_mentors || 0)}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Поиск и фильтры */}
        <Card>
          <CardHeader>
            <div className="flex items-center space-x-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                  <Input
                    placeholder="Поиск по имени, email, специализации..."
                    value={searchFilters.search || ''}
                    onChange={(e) => handleSearch(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {/* Фильтры удалены по требованию пользователя */}
          </CardContent>
        </Card>

        {/* Таблица менторов */}
        <Card>
          <CardHeader>
            <CardTitle>Список менторов</CardTitle>
          </CardHeader>
          <CardContent>
            {mentorsLoading ? (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                Загрузка менторов...
              </div>
            ) : mentorsData && mentorsData.mentors.length > 0 ? (
              <div className="space-y-4">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-3 font-medium">Ментор</th>
                        <th className="text-left p-3 font-medium">Специализация</th>
                        <th className="text-left p-3 font-medium">Рейтинг</th>
                        <th className="text-left p-3 font-medium">Цены</th>
                        <th className="text-left p-3 font-medium">Регистрация</th>
                        <th className="text-left p-3 font-medium">Действия</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mentorsData.mentors.map((mentor) => mentor && (
                        <tr key={mentor.user_id} className="border-b hover:bg-muted/50">
                          <td className="p-3">
                            <div className="flex items-center space-x-3">
                              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                                {mentor.avatar_url ? (
                                  <img 
                                    src={mentor.avatar_url} 
                                    alt={mentor.name || 'Ментор'}
                                    className="w-10 h-10 rounded-full object-cover"
                                  />
                                ) : (
                                  <GraduationCap className="h-5 w-5 text-primary" />
                                )}
                              </div>
                              <div>
                                <div className="font-medium">{mentor.name || 'Без имени'}</div>
                                <div className="text-sm text-muted-foreground">{mentor.user?.email}</div>
                              </div>
                            </div>
                          </td>
                          
                          <td className="p-3">
                            <div className="space-y-1">
                              <div className="flex items-center space-x-1 text-sm">
                                <Globe className="h-3 w-3" />
                                <span>{mentor.languages?.join(', ') || 'Не указано'}</span>
                              </div>
                              <div className="flex items-center space-x-1 text-sm">
                                <BookOpen className="h-3 w-3" />
                                <span>{mentor.subjects?.join(', ') || 'Не указано'}</span>
                              </div>
                              {(mentor.country || mentor.city) && (
                                <div className="text-xs text-muted-foreground">
                                  {[mentor.city, mentor.country].filter(Boolean).join(', ')}
                                </div>
                              )}
                            </div>
                          </td>
                          
                          <td className="p-3">
                            <div className="flex items-center space-x-1">
                              <Star className="h-4 w-4 text-yellow-500 fill-current" />
                              <span className="font-medium">{(Number(mentor.rating_avg) || 0).toFixed(1)}</span>
                              <span className="text-sm text-muted-foreground">({mentor.rating_count})</span>
                            </div>
                          </td>
                          
                          <td className="p-3">
                            <div className="space-y-1 text-sm">
                              {mentor.price_30 && (
                                <div className="flex items-center space-x-1">
                                  <Clock className="h-3 w-3" />
                                  <span>30м: {mentor.price_30}₸</span>
                                </div>
                              )}
                              {mentor.price_45 && (
                                <div className="flex items-center space-x-1">
                                  <Clock className="h-3 w-3" />
                                  <span>45м: {mentor.price_45}₸</span>
                                </div>
                              )}
                              {mentor.price_60 && (
                                <div className="flex items-center space-x-1">
                                  <Clock className="h-3 w-3" />
                                  <span>60м: {mentor.price_60}₸</span>
                                </div>
                              )}
                            </div>
                          </td>
                          
                          
                          <td className="p-3 text-sm text-muted-foreground">
                            {mentor.created_at ? new Date(mentor.created_at).toLocaleDateString('ru-RU') : '-'}
                          </td>
                          
                          <td className="p-3">
                            <div className="flex items-center space-x-1">
                              {getMentorActions(mentor).map((action) => {
                                const Icon = action.icon
                                const isLoading = action.action === 'delete' && deletingMentorId === mentor.user_id
                                return (
                                  <Button
                                    key={action.id}
                                    variant={action.variant || 'outline'}
                                    size="sm"
                                    onClick={() => handleMentorAction(mentor, action.action)}
                                    disabled={isLoading}
                                  >
                                    {isLoading ? (
                                      <RefreshCw className="h-3 w-3 animate-spin" />
                                    ) : (
                                      <Icon className="h-3 w-3" />
                                    )}
                                  </Button>
                                )
                              })}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Пагинация */}
                {mentorsData && totalPages > 1 && (
                  <div className="flex items-center justify-between mt-4">
                    <div className="text-sm text-muted-foreground">
                      Показано {((searchFilters.page || 1) - 1) * (searchFilters.page_size || 20) + 1}-
                      {Math.min((searchFilters.page || 1) * (searchFilters.page_size || 20), mentorsData.total)} из {mentorsData.total}
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleFilterChange({ page: (searchFilters.page || 1) - 1 })}
                        disabled={!searchFilters.page || searchFilters.page <= 1}
                      >
                        Назад
                      </Button>
                      <span className="text-sm">
                        Страница {searchFilters.page || 1} из {totalPages}
                      </span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleFilterChange({ page: (searchFilters.page || 1) + 1 })}
                        disabled={!searchFilters.page || searchFilters.page >= totalPages}
                      >
                        Вперед
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                Менторы не найдены
              </div>
            )}
          </CardContent>
        </Card>

        {/* Модальное окно деталей ментора */}
        {detailsMentorId && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={() => setDetailsMentorId(null)}>
            <div className="bg-background rounded-lg shadow-lg w-[600px] max-w-[90vw] max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
              <div className="border-b px-4 py-3 font-semibold flex items-center justify-between">
                <span>Детали ментора</span>
                <Button variant="ghost" size="sm" onClick={() => setDetailsMentorId(null)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <div className="p-4">
                {detailsLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="flex items-center space-x-2">
                      <RefreshCw className="h-4 w-4 animate-spin" />
                      <span>Загрузка деталей ментора...</span>
                    </div>
                  </div>
                ) : detailsMentor ? (
                  <div className="space-y-4">
                    {/* Основная информация */}
                    <div className="flex items-center space-x-4">
                      <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
                        {detailsMentor?.mentor?.avatar_url ? (
                          <img 
                            src={detailsMentor.mentor.avatar_url} 
                            alt={detailsMentor?.user?.name || 'Ментор'}
                            className="w-16 h-16 rounded-full object-cover"
                          />
                        ) : (
                          <GraduationCap className="h-8 w-8 text-primary" />
                        )}
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold">{detailsMentor?.user?.name || 'Без имени'}</h3>
                        <p className="text-muted-foreground">{detailsMentor?.user?.email}</p>
                      </div>
                    </div>

                    {/* Профессиональная информация */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium mb-2">Заголовок</h4>
                        <p className="text-sm text-muted-foreground">{detailsMentor?.mentor?.headline || 'Не указано'}</p>
                      </div>
                      <div>
                        <h4 className="font-medium mb-2">Рейтинг</h4>
                        <div className="flex items-center space-x-1">
                          <Star className="h-4 w-4 text-yellow-500 fill-current" />
                          <span>{(Number(detailsMentor?.mentor?.rating_avg) || 0).toFixed(1)} ({detailsMentor?.mentor?.rating_count || 0} отзывов)</span>
                        </div>
                      </div>
                    </div>

                    {/* Описание */}
                    {detailsMentor?.mentor?.bio && (
                      <div>
                        <h4 className="font-medium mb-2">Описание</h4>
                        <p className="text-sm text-muted-foreground">{detailsMentor.mentor.bio}</p>
                      </div>
                    )}

                    {/* Специализация */}
                    <div>
                      <h4 className="font-medium mb-2">Специализация</h4>
                      <div className="space-y-2">
                        <div>
                          <span className="text-sm font-medium">Языки: </span>
                          <span className="text-sm text-muted-foreground">{detailsMentor?.mentor?.languages?.join(', ') || 'Не указано'}</span>
                        </div>
                        <div>
                          <span className="text-sm font-medium">Предметы: </span>
                          <span className="text-sm text-muted-foreground">{detailsMentor?.mentor?.subjects?.join(', ') || 'Не указано'}</span>
                        </div>
                      </div>
                    </div>

                    {/* Цены */}
                    <div>
                      <h4 className="font-medium mb-2">Цены за консультации</h4>
                      <div className="grid grid-cols-3 gap-2">
                        {detailsMentor?.mentor?.price_30 && (
                          <div className="text-sm">
                            <span className="font-medium">30 мин:</span> {detailsMentor.mentor.price_30}₸
                          </div>
                        )}
                        {detailsMentor?.mentor?.price_45 && (
                          <div className="text-sm">
                            <span className="font-medium">45 мин:</span> {detailsMentor.mentor.price_45}₸
                          </div>
                        )}
                        {detailsMentor?.mentor?.price_60 && (
                          <div className="text-sm">
                            <span className="font-medium">60 мин:</span> {detailsMentor.mentor.price_60}₸
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Образование */}
                    {detailsMentor.universities && detailsMentor.universities.length > 0 && (
                      <div>
                        <h4 className="font-medium mb-2">Образование</h4>
                        <div className="space-y-2">
                          {detailsMentor.universities.map((university, index) => (
                            <div key={index} className="text-sm border rounded p-2">
                              <div className="font-medium">{university.university}</div>
                              {university.degree && <div>Степень: {university.degree}</div>}
                              {university.major && <div>Специальность: {university.major}</div>}
                              {university.year_from && university.year_to && (
                                <div>Период: {university.year_from} - {university.year_to}</div>
                              )}
                              {university.country && <div>Страна: {university.country}</div>}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Статистика */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium mb-2">Консультации</h4>
                        <div className="text-sm space-y-1">
                          <div>Всего: {detailsMentor.total_consultations}</div>
                          <div>Завершено: {detailsMentor.completed_consultations}</div>
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium mb-2">Регистрация</h4>
                        <div className="text-sm">
                          {detailsMentor?.user?.created_at ? new Date(detailsMentor.user.created_at).toLocaleDateString('ru-RU') : 'Не указано'}
                        </div>
                      </div>
                    </div>

                    {/* Действия */}
                  </div>
                ) : (
                  <div>Не удалось загрузить данные</div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Модальное окно создания ментора */}
      {showCreateModal && (
        <CreateMentorModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            queryClient.invalidateQueries(['admin-mentors'])
            queryClient.invalidateQueries(['mentor-stats'])
          }}
        />
      )}

      {/* Модальное окно редактирования ментора */}
      {showEditModal && editingMentorId && (
        <EditMentorModal
          isOpen={showEditModal}
          mentorId={editingMentorId}
          onClose={() => {
            setShowEditModal(false)
            setEditingMentorId(null)
          }}
          onSuccess={() => {
            setShowEditModal(false)
            setEditingMentorId(null)
            queryClient.invalidateQueries(['admin-mentors'])
            queryClient.invalidateQueries(['mentor-stats'])
            if (detailsMentorId === editingMentorId) {
              queryClient.invalidateQueries(['mentor-details', editingMentorId])
            }
          }}
        />
      )}
    </>
  )
}

// Компонент модального окна создания ментора
interface CreateMentorModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

const CreateMentorModal = ({ isOpen, onClose, onSuccess }: CreateMentorModalProps) => {
  const [formData, setFormData] = useState<CreateMentorRequest>({
    email: '',
    name: '',
    password: '',
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
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.email || !formData.name || !formData.password) {
      toast.error('Заполните обязательные поля: Email, Имя, Пароль')
      return
    }
    
    if (formData.password.length < 8) {
      toast.error('Пароль должен содержать минимум 8 символов')
      return
    }
    
    const hasLetter = /[a-zA-Z]/.test(formData.password)
    const hasDigit = /\d/.test(formData.password)
    if (!hasLetter || !hasDigit) {
      toast.error('Пароль должен содержать буквы и цифры')
      return
    }
    
    setIsLoading(true)

    try {
      const dataToSend = {
        email: formData.email,
        password: formData.password,
        name: formData.name,
        phone: formData.phone || null,
        bio: formData.bio || null,
        headline: formData.headline || null,
        price_30: formData.price_30 ?? null,
        price_45: formData.price_45 ?? null,
        price_60: formData.price_60 ?? null,
        avatar_url: formData.avatar_url || null,
        languages: formData.languages || [],
        send_welcome_email: formData.send_welcome_email
      }
      
      await adminApi.createMentor(dataToSend)
      toast.success('Ментор успешно создан')
      onSuccess()
      setFormData({
        email: '',
        name: '',
        password: '',
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
    } catch (error: any) {
      const errorDetail = error?.detail || error?.response?.data?.detail || 'Ошибка при создании ментора'
      toast.error(errorDetail)
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Создать ментора</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Email *</label>
              <Input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Имя *</label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Пароль *</label>
              <Input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Телефон</label>
              <Input
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Заголовок профиля</label>
            <Input
              value={formData.headline}
              onChange={(e) => setFormData({ ...formData, headline: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Биография</label>
            <textarea
              className="w-full p-2 border rounded-md"
              rows={3}
              value={formData.bio}
              onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Цена 30 мин (₸)</label>
              <Input
                type="number"
                value={formData.price_30 || ''}
                onChange={(e) => setFormData({ ...formData, price_30: e.target.value ? Number(e.target.value) : undefined })}
                placeholder="15000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Цена 45 мин (₸)</label>
              <Input
                type="number"
                value={formData.price_45 || ''}
                onChange={(e) => setFormData({ ...formData, price_45: e.target.value ? Number(e.target.value) : undefined })}
                placeholder="22500"
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

          <div className="flex justify-end space-x-2">
            <Button type="button" variant="outline" onClick={onClose}>
              Отмена
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Создание...' : 'Создать ментора'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

// Компонент модального окна редактирования ментора
interface EditMentorModalProps {
  isOpen: boolean
  mentorId: string
  onClose: () => void
  onSuccess: () => void
}

const EditMentorModal = ({ isOpen, mentorId, onClose, onSuccess }: EditMentorModalProps) => {
  const [formData, setFormData] = useState<AdminMentorUpdateData>({})
  const [isLoading, setIsLoading] = useState(false)

  // Загрузка данных ментора
  const { data: mentorData, isLoading: isLoadingData, error: mentorDataError } = useQuery(
    ['mentor-detail', mentorId],
    () => mentorsApi.getMentorAdmin(mentorId),
    { 
      enabled: isOpen && !!mentorId,
      onError: (error: any) => {
        console.error('Error loading mentor data:', error)
        const errorMessage = error?.response?.data?.detail || 'Ошибка загрузки данных ментора'
        toast.error(`Ошибка: ${errorMessage}`)
      }
    }
  )

  // Заполнение формы при загрузке данных
  React.useEffect(() => {
    if (mentorData) {
      setFormData({
        name: mentorData.user.name,
        phone: mentorData.user.phone,
        timezone: mentorData.user.timezone,
        locale: mentorData.user.locale,
        is_active: mentorData.user.is_active,
        headline: mentorData.mentor.headline,
        bio: mentorData.mentor.bio,
        price_30: mentorData.mentor.price_30,
        price_45: mentorData.mentor.price_45,
        price_60: mentorData.mentor.price_60,
        languages: mentorData.mentor.languages,
        subjects: mentorData.mentor.subjects,
        avatar_url: mentorData.mentor.avatar_url
      })
    }
  }, [mentorData])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      await mentorsApi.updateMentor(mentorId, formData)
      toast.success('Ментор успешно обновлен')
      onSuccess()
    } catch (error: any) {
      console.error('Error updating mentor:', error)
      const errorMessage = error?.response?.data?.detail || 'Произошла ошибка при обновлении ментора'
      toast.error(`Ошибка: ${errorMessage}`)
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Редактировать ментора</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X className="h-5 w-5" />
          </button>
        </div>

        {isLoadingData ? (
          <div className="text-center py-4">Загрузка...</div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Имя</label>
                <Input
                  value={formData.name || ''}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Телефон</label>
                <Input
                  value={formData.phone || ''}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Часовой пояс</label>
                <Input
                  value={formData.timezone || ''}
                  onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Локаль</label>
                <Input
                  value={formData.locale || ''}
                  onChange={(e) => setFormData({ ...formData, locale: e.target.value })}
                />
              </div>
            </div>

            <div>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.is_active ?? true}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                />
                <span className="text-sm font-medium">Активен</span>
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Заголовок профиля</label>
              <Input
                value={formData.headline || ''}
                onChange={(e) => setFormData({ ...formData, headline: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Биография</label>
              <textarea
                className="w-full p-2 border rounded-md"
                rows={3}
                value={formData.bio || ''}
                onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Цена 30 мин</label>
                <Input
                  type="number"
                  value={formData.price_30 || ''}
                  onChange={(e) => setFormData({ ...formData, price_30: e.target.value ? Number(e.target.value) : undefined })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Цена 45 мин</label>
                <Input
                  type="number"
                  value={formData.price_45 || ''}
                  onChange={(e) => setFormData({ ...formData, price_45: e.target.value ? Number(e.target.value) : undefined })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Цена 60 мин</label>
                <Input
                  type="number"
                  value={formData.price_60 || ''}
                  onChange={(e) => setFormData({ ...formData, price_60: e.target.value ? Number(e.target.value) : undefined })}
                />
              </div>
            </div>

            <div className="flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={onClose}>
                Отмена
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Сохранение...' : 'Сохранить'}
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
