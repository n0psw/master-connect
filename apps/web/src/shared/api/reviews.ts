import { api } from './client'

export interface Review {
  id: string
  booking_id: string
  student_id: string
  mentor_id: string
  rating: number
  text: string
  created_at: string
  updated_at: string
  student_name?: string
  student_avatar_url?: string
  mentor_name?: string
  mentor_avatar_url?: string
}

export interface ReviewCreate {
  booking_id: string
  rating: number
  text: string
}

export interface ReviewUpdate {
  rating?: number
  text?: string
}

export interface ReviewList {
  reviews: Review[]
  total: number
  page: number
  page_size: number
}

export interface ReviewStats {
  total_reviews: number
  average_rating: number
  rating_distribution: Record<number, number>
  positive_reviews: number
  negative_reviews: number
}

export const reviewsApi = {
  // Создание отзыва
  async createReview(data: ReviewCreate): Promise<Review> {
    const response = await api.post<Review>('/reviews', data)
    return response.data
  },

  // Получение отзыва по ID
  async getReview(reviewId: string): Promise<Review> {
    const response = await api.get<Review>(`/reviews/${reviewId}`)
    return response.data
  },

  // Получение отзывов ментора
  async getMentorReviews(mentorId: string, page: number = 1, pageSize: number = 20): Promise<ReviewList> {
    const response = await api.get<ReviewList>(`/reviews/mentor/${mentorId}`, {
      params: { page, page_size: pageSize }
    })
    return response.data
  },

  // Получение статистики отзывов ментора
  async getMentorReviewStats(mentorId: string): Promise<ReviewStats> {
    const response = await api.get<ReviewStats>(`/reviews/mentor/${mentorId}/stats`)
    return response.data
  },

  // Получение моих отзывов (студент)
  async getMyReviews(page: number = 1, pageSize: number = 20): Promise<ReviewList> {
    const response = await api.get<ReviewList>('/reviews/my', {
      params: { page, page_size: pageSize }
    })
    return response.data
  },

  // Обновление отзыва
  async updateReview(reviewId: string, data: ReviewUpdate): Promise<Review> {
    const response = await api.put<Review>(`/reviews/${reviewId}`, data)
    return response.data
  },

  // Удаление отзыва
  async deleteReview(reviewId: string): Promise<void> {
    await api.delete(`/reviews/${reviewId}`)
  },
}

