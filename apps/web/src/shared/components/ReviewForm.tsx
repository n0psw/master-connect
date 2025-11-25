import { useState } from 'react'
import { Star, Send, X } from 'lucide-react'
import { useMutation, useQueryClient } from 'react-query'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Textarea } from '@/shared/ui/textarea'
import { reviewsApi } from '@/shared/api/reviews'
import type { ReviewCreate } from '@/shared/api/reviews'

interface ReviewFormProps {
  bookingId: string
  mentorName: string
  onClose: () => void
  onSuccess?: () => void
}

export const ReviewForm = ({ bookingId, mentorName, onClose, onSuccess }: ReviewFormProps) => {
  const [rating, setRating] = useState(0)
  const [hoveredRating, setHoveredRating] = useState(0)
  const [text, setText] = useState('')
  
  const queryClient = useQueryClient()

  const createReviewMutation = useMutation(
    (data: ReviewCreate) => reviewsApi.createReview(data),
    {
      onSuccess: (review) => {
        toast.success('Отзыв успешно опубликован!')
        queryClient.invalidateQueries(['my-bookings'])
        queryClient.invalidateQueries(['my-reviews'])
        // Инвалидируем кэш отзывов ментора и данных ментора
        queryClient.invalidateQueries(['mentor-reviews'])
        queryClient.invalidateQueries(['mentor-review-stats'])
        queryClient.invalidateQueries(['mentor'])
        onSuccess?.()
        onClose()
      },
      onError: (error: any) => {
        toast.error('Ошибка при публикации отзыва: ' + (error?.detail || error?.message))
      }
    }
  )

  const handleSubmit = () => {
    if (rating === 0) {
      toast.error('Пожалуйста, поставьте оценку')
      return
    }

    if (text.trim().length < 10) {
      toast.error('Отзыв должен содержать минимум 10 символов')
      return
    }

    createReviewMutation.mutate({
      booking_id: bookingId,
      rating,
      text: text.trim()
    })
  }

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Оставить отзыв</CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-sm text-muted-foreground mt-2">
          Консультация с {mentorName}
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Рейтинг */}
        <div>
          <label className="block text-sm font-medium mb-3">
            Оцените консультацию *
          </label>
          <div className="flex items-center gap-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() => setRating(star)}
                onMouseEnter={() => setHoveredRating(star)}
                onMouseLeave={() => setHoveredRating(0)}
                className="transition-transform hover:scale-110"
              >
                <Star
                  className={`h-8 w-8 ${
                    star <= (hoveredRating || rating)
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-gray-300'
                  }`}
                />
              </button>
            ))}
            {rating > 0 && (
              <span className="ml-2 text-sm text-muted-foreground">
                {rating === 1 && 'Плохо'}
                {rating === 2 && 'Неудовлетворительно'}
                {rating === 3 && 'Нормально'}
                {rating === 4 && 'Хорошо'}
                {rating === 5 && 'Отлично'}
              </span>
            )}
          </div>
        </div>

        {/* Текст отзыва */}
        <div>
          <label htmlFor="review-text" className="block text-sm font-medium mb-2">
            Ваш отзыв *
          </label>
          <Textarea
            id="review-text"
            placeholder="Расскажите о вашем опыте консультации..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={6}
            maxLength={2000}
          />
          <p className="text-xs text-muted-foreground mt-1">
            {text.length}/2000 символов (минимум 10)
          </p>
        </div>

        {/* Информация */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="text-sm text-blue-700">
            <p className="font-medium mb-1">Советы по написанию отзыва:</p>
            <ul className="space-y-1">
              <li>• Опишите, что вам понравилось или не понравилось</li>
              <li>• Укажите, насколько полезной была консультация</li>
              <li>• Будьте честны и конструктивны</li>
            </ul>
          </div>
        </div>

        {/* Кнопки */}
        <div className="flex gap-3 justify-end">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={createReviewMutation.isLoading}
          >
            Отмена
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={createReviewMutation.isLoading || rating === 0 || text.trim().length < 10}
          >
            {createReviewMutation.isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                Публикация...
              </>
            ) : (
              <>
                <Send className="h-4 w-4 mr-2" />
                Опубликовать отзыв
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

