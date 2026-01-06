import { Star, User } from 'lucide-react'

import { formatFromNow, getClientTimezone } from '@/shared/lib/dayjs'

import { Card, CardContent } from '@/shared/ui/card'
import type { Review } from '@/shared/api/reviews'

interface ReviewsListProps {
  reviews: Review[]
  showMentorName?: boolean
}

export const ReviewsList = ({ reviews, showMentorName = false }: ReviewsListProps) => {
  const tz = getClientTimezone()

  if (reviews.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Пока нет отзывов</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {reviews.map((review) => (
        <Card key={review.id}>
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              {/* Аватар */}
              <div className="flex-shrink-0">
                {review.student_avatar_url ? (
                  <img
                    src={review.student_avatar_url}
                    alt={review.student_name || 'Студент'}
                    className="h-12 w-12 rounded-full object-cover"
                  />
                ) : (
                  <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center">
                    <User className="h-6 w-6 text-muted-foreground" />
                  </div>
                )}
              </div>

              {/* Содержание */}
              <div className="flex-1 min-w-0">
                {/* Заголовок */}
                <div className="flex items-start justify-between gap-4 mb-2">
                  <div>
                    <p className="font-semibold">
                      {review.student_name || 'Студент'}
                    </p>
                    {showMentorName && review.mentor_name && (
                      <p className="text-sm text-muted-foreground">
                        Консультация с {review.mentor_name}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-1">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star
                        key={i}
                        className={`h-4 w-4 ${
                          i < review.rating
                            ? 'fill-yellow-400 text-yellow-400'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                </div>

                {/* Текст отзыва */}
                <p className="text-sm text-gray-700 mb-2 whitespace-pre-wrap">
                  {review.text}
                </p>

                {/* Дата */}
                <p className="text-xs text-muted-foreground">
                  {formatFromNow(review.created_at, tz)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

