import { useState } from 'react'
import { Helmet } from 'react-helmet-async'
import { Star, MessageSquare, Calendar, AlertCircle } from 'lucide-react'
import { useQuery } from 'react-query'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { ReviewsList } from '@/shared/components/ReviewsList'
import { reviewsApi } from '@/shared/api/reviews'

export const StudentReviewsPage = () => {
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 10

  // Загрузка отзывов
  const { data: reviewsData, isLoading, error } = useQuery(
    ['my-reviews', currentPage],
    () => {
      console.log('Fetching reviews...', { page: currentPage, pageSize })
      return reviewsApi.getMyReviews(currentPage, pageSize)
    },
    {
      keepPreviousData: true,
      retry: 1,
      refetchOnWindowFocus: false,
      onError: (error: any) => {
        console.error('Reviews fetch error:', error)
        toast.error('Ошибка при загрузке отзывов: ' + (error?.detail || error?.message))
      },
      onSuccess: (data) => {
        console.log('Reviews fetched successfully:', data)
      }
    }
  )

  const totalPages = reviewsData ? Math.ceil(reviewsData.total / pageSize) : 0

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded mb-4" />
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-48 bg-muted rounded" />
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
          Не удалось загрузить ваши отзывы
        </p>
        <Button onClick={() => window.location.reload()}>
          Попробовать снова
        </Button>
      </div>
    )
  }

  return (
    <>
      <Helmet>
        <title>Мои отзывы - MasterConnect</title>
      </Helmet>

      <div className="space-y-8">
        {/* Заголовок */}
        <div>
          <h1 className="text-3xl font-bold mb-4">Мои отзывы</h1>
          <p className="text-muted-foreground">
            Отзывы, которые вы оставили после консультаций
          </p>
        </div>

        {/* Статистика */}
        {reviewsData && reviewsData.total > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                    <MessageSquare className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{reviewsData.total}</p>
                    <p className="text-sm text-muted-foreground">Всего отзывов</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 rounded-full bg-yellow-100 flex items-center justify-center">
                    <Star className="h-6 w-6 text-yellow-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">
                      {reviewsData.reviews.length > 0
                        ? (reviewsData.reviews.reduce((sum, r) => sum + r.rating, 0) / reviewsData.reviews.length).toFixed(1)
                        : '0.0'}
                    </p>
                    <p className="text-sm text-muted-foreground">Средняя оценка</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
                    <Calendar className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{reviewsData.reviews.length}</p>
                    <p className="text-sm text-muted-foreground">На этой странице</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Список отзывов */}
        <Card>
          <CardHeader>
            <CardTitle>Ваши отзывы</CardTitle>
          </CardHeader>
          <CardContent>
            {reviewsData && reviewsData.reviews.length > 0 ? (
              <>
                <ReviewsList reviews={reviewsData.reviews} showMentorName={true} />

                {/* Пагинация */}
                {totalPages > 1 && (
                  <div className="flex justify-center mt-8">
                    <div className="flex items-center space-x-2">
                      {/* Предыдущая */}
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={currentPage <= 1}
                        onClick={() => setCurrentPage(currentPage - 1)}
                      >
                        Назад
                      </Button>

                      {/* Номера страниц */}
                      {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                        const page = i + 1
                        return (
                          <Button
                            key={page}
                            variant={currentPage === page ? "default" : "outline"}
                            size="sm"
                            onClick={() => setCurrentPage(page)}
                          >
                            {page}
                          </Button>
                        )
                      })}

                      {/* Следующая */}
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={currentPage >= totalPages}
                        onClick={() => setCurrentPage(currentPage + 1)}
                      >
                        Далее
                      </Button>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-12">
                <MessageSquare className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">У вас пока нет отзывов</h3>
                <p className="text-muted-foreground mb-4">
                  Отзывы появятся после завершения консультаций
                </p>
                <Button onClick={() => window.location.href = '/mentors'}>
                  Найти ментора
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </>
  )
}

