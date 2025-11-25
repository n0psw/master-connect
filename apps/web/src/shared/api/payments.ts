import { api } from './client'

export interface PaymentEvidence {
  id: string
  booking_id: string
  created_by: string
  comment_text?: string
  receipt_file_url?: string
  created_at: string
  creator_name?: string
}

export interface PaymentEvidenceCreate {
  booking_id: string
  comment_text?: string
}

export interface PaymentEvidenceUpdate {
  comment_text?: string
}

export const paymentsApi = {
  // Создание доказательства оплаты с загрузкой файла
  async createEvidence(
    bookingId: string,
    commentText: string,
    file: File
  ): Promise<PaymentEvidence> {
    const formData = new FormData()
    formData.append('booking_id', bookingId)
    formData.append('comment_text', commentText || '')
    formData.append('file', file)

    const response = await api.post<PaymentEvidence>('/payments/evidence', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Получение всех доказательств оплаты для бронирования
  async getEvidenceByBooking(bookingId: string): Promise<PaymentEvidence[]> {
    const response = await api.get<PaymentEvidence[]>(`/payments/evidence/booking/${bookingId}`)
    return response.data
  },

  // Получение конкретного доказательства оплаты
  async getEvidence(evidenceId: string): Promise<PaymentEvidence> {
    const response = await api.get<PaymentEvidence>(`/payments/evidence/${evidenceId}`)
    return response.data
  },

  // Обновление доказательства оплаты
  async updateEvidence(
    evidenceId: string,
    data: PaymentEvidenceUpdate
  ): Promise<PaymentEvidence> {
    const response = await api.put<PaymentEvidence>(`/payments/evidence/${evidenceId}`, data)
    return response.data
  },

  // Удаление доказательства оплаты
  async deleteEvidence(evidenceId: string): Promise<void> {
    await api.delete(`/payments/evidence/${evidenceId}`)
  },
}

