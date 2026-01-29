 import { useParams, Link, useNavigate } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { Star, MapPin, Calendar, Clock, ArrowLeft, MessageCircle, Heart } from 'lucide-react'
import { useQuery } from 'react-query'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { ReviewsList } from '@/shared/components/ReviewsList'
import { mentorsApi } from '@/shared/api/mentors'
import { reviewsApi } from '@/shared/api/reviews'
import { useAuthStore } from '@/shared/store/auth'
import type { MentorDetail } from '@/shared/types/mentors'
import { getImageUrl } from '@/shared/utils/imageUtils'

export const MentorDetailPage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { isAuthenticated, user } = useAuthStore()

  // Запрос данных ментора
  const { 
    data: mentor, 
    isLoading, 
    error 
  } = useQuery(
    ['mentor', id],
    () => mentorsApi.getMentor(id!),
    {
      enabled: !!id,
      onError: (error: any) => {
        toast.error('Ошибка при загрузке ментора: ' + (error?.detail || error?.message))
      }
    }
  )

  // Запрос отзывов ментора
  const { data: reviewsData, error: reviewsError } = useQuery(
    ['mentor-reviews', id],
    () => reviewsApi.getMentorReviews(id!, 1, 10),
    {
      enabled: !!id,
      onError: (error: any) => {
        console.error('Ошибка при загрузке отзывов:', error)
      },
      retry: 1,
    }
  )

  // Запрос статистики отзывов
  const { data: reviewStats } = useQuery(
    ['mentor-review-stats', id],
    () => reviewsApi.getMentorReviewStats(id!),
    {
      enabled: !!id,
    }
  )

  if (isLoading) {
    return (
      <div className="container-wide py-8">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-muted rounded mb-4" />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <div className="h-64 bg-muted rounded mb-4" />
                <div className="h-48 bg-muted rounded" />
              </div>
              <div>
                <div className="h-80 bg-muted rounded" />
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error || !mentor) {
    const mentorsPath = isAuthenticated && user?.role === 'student' ? '/student/mentors' : '/mentors'
    return (
      <div className="container-wide py-8">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-destructive text-lg mb-4">Ментор не найден</p>
          <Button onClick={() => navigate(mentorsPath)}>
            Вернуться к каталогу
          </Button>
        </div>
      </div>
    )
  }

  const priceOptions = [mentor.mentor.price_30, mentor.mentor.price_60].filter(Boolean).map(Number) as number[]
  const minPrice = priceOptions.length > 0 ? Math.min(...priceOptions) : null

  const mentorsPath = isAuthenticated && user?.role === 'student' ? '/student/mentors' : '/mentors'

  const handleBookConsultation = () => {
    if (!isAuthenticated) {
      toast.info('Войдите в аккаунт, чтобы забронировать консультацию')
      navigate('/login', { state: { from: location.pathname } })
      return
    }

    if (user?.role !== 'student') {
      toast.error('Только студенты могут бронировать консультации')
      return
    }

    // TODO: Перейти к странице бронирования
    navigate(`/student/book-consultation/${mentor.user.id}`)
  }

  return (
    <>
      <Helmet>
        <title>{mentor.user.name || 'Ментор'} - MasterConnect</title>
        <meta 
          name="description" 
          content={`Консультации с ${mentor.user.name}. ${mentor.mentor.headline || 'Опытный ментор для поступления в университет.'}`} 
        />
      </Helmet>

      <div className="container-wide py-8">
        <div className="max-w-6xl mx-auto">
          {/* Навигация */}
          <div className="mb-6">
            <Button 
              variant="ghost" 
              onClick={() => navigate(mentorsPath)}
              className="flex items-center gap-2 mb-4"
            >
              <ArrowLeft className="h-4 w-4" />
              Назад к каталогу
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Основная информация */}
            <div className="lg:col-span-2 space-y-6">
              {/* Заголовок */}
              <Card>
                <CardContent className="p-6">
                  <div className="flex flex-col md:flex-row items-start gap-6">
                    {/* Аватар */}
                    <div className="flex-shrink-0">
                      <div className="w-32 h-32 bg-primary/10 rounded-full flex items-center justify-center">
                        {getImageUrl(mentor.mentor.avatar_url || mentor.user?.avatar_url) ? (
                          <img 
                            src={getImageUrl(mentor.mentor.avatar_url || mentor.user?.avatar_url)!} 
                            alt={mentor.user.name || 'Ментор'} 
                            className="w-full h-full rounded-full object-cover"
                          />
                        ) : (
                          <span className="text-4xl font-semibold text-primary">
                            {(mentor.user.name || 'М')[0].toUpperCase()}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Информация */}
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
                            {mentor.user.name || 'Ментор'}
                          </h1>
                          
                          {mentor.mentor.headline && (
                            <p className="text-lg text-muted-foreground mb-3">
                              {mentor.mentor.headline}
                            </p>
                          )}

                          {/* Локация */}
                          {mentor.universities.length > 0 && (
                            <div className="flex items-center text-muted-foreground mb-2">
                              <MapPin className="h-4 w-4 mr-2" />
                              {[
                                mentor.universities[0].city, 
                                mentor.universities[0].country
                              ].filter(Boolean).join(', ')}
                            </div>
                          )}

                          {/* Рейтинг */}
                          <div className="flex items-center mb-3">
                            <div className="flex items-center text-yellow-500 mr-4">
                              <Star className="h-5 w-5 fill-current" />
                              <span className="ml-1 font-semibold text-lg">
                                {(Number(mentor.mentor.rating_avg) || 0).toFixed(1)}
                              </span>
                            </div>
                            <span className="text-muted-foreground">
                              {mentor.mentor.rating_count} отзывов • {mentor.total_consultations} консультаций
                            </span>
                          </div>

                          {/* Языки */}
                          <div className="flex flex-wrap gap-2 mb-3">
                            {mentor.mentor.languages.map((lang) => (
                              <span 
                                key={lang} 
                                className="bg-primary/10 text-primary px-3 py-1 rounded-full text-sm"
                              >
                                {lang}
                              </span>
                            ))}
                          </div>
                        </div>

                        {/* Цены */}
                        <div className="text-right">
                        <div className="text-2xl font-bold text-primary mb-1">
                          {minPrice !== null ? `от ${minPrice.toLocaleString()} ₸` : 'По запросу'}
                        </div>
                          <div className="text-sm text-muted-foreground">за консультацию</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* О менторе */}
              {mentor.mentor.bio && (
                <Card>
                  <CardHeader>
                    <CardTitle>О менторе</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground whitespace-pre-wrap leading-relaxed">
                      {mentor.mentor.bio}
                    </p>
                  </CardContent>
                </Card>
              )}

              {/* Образование */}
              {mentor.universities.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Образование</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {mentor.universities.map((edu) => (
                      <div key={edu.id} className="border-l-2 border-primary/20 pl-4">
                        <h4 className="font-semibold text-lg">{edu.university}</h4>
                        {edu.major && (
                          <p className="text-muted-foreground">{edu.major}</p>
                        )}
                        <div className="text-sm text-muted-foreground mt-1">
                          {[
                            edu.degree,
                            edu.year_from && edu.year_to ? `${edu.year_from}-${edu.year_to}` : null,
                            [edu.city, edu.country].filter(Boolean).join(', ')
                          ].filter(Boolean).join(' • ')}
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Предметные области */}
              {mentor.mentor.subjects.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Предметные области</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {mentor.mentor.subjects.map((subject) => (
                        <span 
                          key={subject} 
                          className="bg-muted px-3 py-2 rounded-lg text-sm"
                        >
                          {subject}
                        </span>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Боковая панель */}
            <div className="space-y-6">
              {/* Цены и бронирование */}
              <Card>
                <CardHeader>
                  <CardTitle>Забронировать консультацию</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Варианты длительности */}
                  <div className="space-y-3">
                    {mentor.mentor.price_30 && (
                      <div className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <div className="font-medium">30 минут</div>
                          <div className="text-sm text-muted-foreground">
                            Короткая консультация
                          </div>
                        </div>
                        <div className="text-lg font-semibold">
                          {Number(mentor.mentor.price_30).toLocaleString()} ₸
                        </div>
                      </div>
                    )}

                    {mentor.mentor.price_60 && (
                      <div className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <div className="font-medium">60 минут</div>
                          <div className="text-sm text-muted-foreground">
                            Развернутая консультация
                          </div>
                        </div>
                        <div className="text-lg font-semibold">
                          {Number(mentor.mentor.price_60).toLocaleString()} ₸
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Кнопка бронирования */}
                  <Button 
                    className="w-full" 
                    size="lg"
                    onClick={handleBookConsultation}
                  >
                    <Calendar className="h-5 w-5 mr-2" />
                    Забронировать консультацию
                  </Button>

                  <div className="text-center text-xs text-muted-foreground">
                    Безопасная оплата • Возможность отмены
                  </div>
                </CardContent>
              </Card>

              {/* Статистика */}
              <Card>
                <CardHeader>
                  <CardTitle>Статистика</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Консультаций проведено</span>
                    <span className="font-semibold">{mentor.total_consultations}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Средний рейтинг</span>
                    <span className="font-semibold flex items-center">
                      {(Number(mentor.mentor.rating_avg) || 0).toFixed(1)}
                      <Star className="h-4 w-4 text-yellow-500 fill-current ml-1" />
                    </span>
                  </div>

                  {mentor.response_rate && (
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Скорость ответа</span>
                      <span className="font-semibold">{Math.round(mentor.response_rate)}%</span>
                    </div>
                  )}

                  {mentor.avg_response_time_hours && (
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Время ответа</span>
                      <span className="font-semibold">
                        ~{Math.round(mentor.avg_response_time_hours)}ч
                      </span>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Дополнительные действия */}
              <Card>
                <CardContent className="p-4 space-y-3">
                  <Button variant="outline" className="w-full">
                    <MessageCircle className="h-4 w-4 mr-2" />
                    Задать вопрос
                  </Button>
                  
                  <Button variant="outline" className="w-full">
                    <Heart className="h-4 w-4 mr-2" />
                    Добавить в избранное
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Отзывы */}
          <Card className="mt-8">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Отзывы студентов</CardTitle>
                {reviewStats && reviewStats.total_reviews > 0 && (
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span className="font-semibold">{reviewStats.average_rating.toFixed(1)}</span>
                      <span className="text-muted-foreground">({reviewStats.total_reviews})</span>
                    </div>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {reviewsError ? (
                <div className="text-center py-8">
                  <p className="text-destructive">
                    Ошибка при загрузке отзывов. Попробуйте обновить страницу.
                  </p>
                </div>
              ) : reviewsData && reviewsData.reviews.length > 0 ? (
                <ReviewsList reviews={reviewsData.reviews} />
              ) : (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">
                    Пока нет отзывов. Будьте первым!
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  )
}
