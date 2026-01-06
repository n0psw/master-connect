import { useState } from 'react'
import { FileText, Download, Check, X, AlertCircle, Loader2 } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { toast } from 'sonner'

import { formatDateTime, getClientTimezone } from '@/shared/lib/dayjs'

import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Textarea } from '@/shared/ui/textarea'
import { Input } from '@/shared/ui/input'
import { paymentsApi } from '@/shared/api/payments'
import { bookingsApi } from '@/shared/api/bookings'
import type { PaymentEvidence } from '@/shared/api/payments'

// Функция для получения полного URL файла
const getFileUrl = (url?: string) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  // Если URL относительный, добавляем базовый URL API
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const baseUrl = apiUrl.replace('/api/v1', '')
  return `${baseUrl}${url}`
}

interface PaymentEvidenceViewerProps {
  bookingId: string
  onClose: () => void
  onSuccess?: () => void
}

export const PaymentEvidenceViewer = ({ 
  bookingId, 
  onClose, 
  onSuccess 
}: PaymentEvidenceViewerProps) => {
  const [paymentNotes, setPaymentNotes] = useState('')
  const [paymentReference, setPaymentReference] = useState('')
  const [selectedEvidence, setSelectedEvidence] = useState<PaymentEvidence | null>(null)
  
  const queryClient = useQueryClient()
  const tz = getClientTimezone()

  // Загружаем доказательства оплаты
  const { data: evidences, isLoading } = useQuery(
    ['payment-evidence', bookingId],
    () => paymentsApi.getEvidenceByBooking(bookingId),
    {
      onSuccess: (data) => {
        if (data.length > 0) {
          setSelectedEvidence(data[0])
        }
      },
      onError: (error: any) => {
        toast.error('Ошибка при загрузке доказательств: ' + (error?.detail || error?.message))
      }
    }
  )

  // Подтверждение оплаты
  const confirmMutation = useMutation(
    () => bookingsApi.confirmPayment(bookingId, {
      payment_confirmed: true,
      payment_notes: paymentNotes.trim() || undefined,
      payment_reference: paymentReference.trim() || undefined
    }),
    {
      onSuccess: () => {
        toast.success('Оплата подтверждена!')
        queryClient.invalidateQueries(['admin-bookings'])
        queryClient.invalidateQueries(['moderation-queue'])
        queryClient.invalidateQueries(['my-bookings'])
        queryClient.invalidateQueries(['booking-stats'])
        queryClient.invalidateQueries(['booking'])
        onSuccess?.()
        onClose()
      },
      onError: (error: any) => {
        toast.error('Ошибка при подтверждении оплаты: ' + (error?.detail || error?.message))
      }
    }
  )

  // Отклонение оплаты
  const rejectMutation = useMutation(
    () => bookingsApi.confirmPayment(bookingId, {
      payment_confirmed: false,
      payment_notes: paymentNotes.trim() || 'Оплата не подтверждена'
    }),
    {
      onSuccess: () => {
        toast.success('Оплата отклонена')
        queryClient.invalidateQueries(['admin-bookings'])
        queryClient.invalidateQueries(['moderation-queue'])
        queryClient.invalidateQueries(['my-bookings'])
        queryClient.invalidateQueries(['booking-stats'])
        queryClient.invalidateQueries(['booking'])
        onSuccess?.()
        onClose()
      },
      onError: (error: any) => {
        toast.error('Ошибка при отклонении оплаты: ' + (error?.detail || error?.message))
      }
    }
  )

  const handleConfirm = () => {
    if (!evidences || evidences.length === 0) {
      toast.error('Нет доказательств оплаты для подтверждения')
      return
    }
    confirmMutation.mutate()
  }

  const handleReject = () => {
    if (!paymentNotes.trim()) {
      toast.error('Укажите причину отклонения')
      return
    }
    rejectMutation.mutate()
  }

  if (isLoading) {
    return (
      <Card className="w-full max-w-4xl">
        <CardContent className="p-12 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    )
  }

  if (!evidences || evidences.length === 0) {
    return (
      <Card className="w-full max-w-4xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-yellow-600" />
            Доказательства оплаты
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-center py-12">
            <AlertCircle className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <p className="text-lg text-muted-foreground">
              Студент еще не загрузил доказательства оплаты
            </p>
          </div>
          <div className="flex justify-end">
            <Button variant="outline" onClick={onClose}>
              Закрыть
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full max-w-4xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Проверка доказательств оплаты
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Список доказательств */}
        <div>
          <label className="block text-sm font-medium mb-3">
            Загруженные доказательства ({evidences.length})
          </label>
          <div className="space-y-2">
            {evidences.map((evidence) => (
              <div
                key={evidence.id}
                className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                  selectedEvidence?.id === evidence.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedEvidence(evidence)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <FileText className="h-5 w-5 text-blue-600 mt-0.5" />
                    <div>
                      <p className="font-medium text-sm">
                        {evidence.creator_name || 'Студент'}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatDateTime(evidence.created_at, tz, 'DD MMMM YYYY, HH:mm')}
                      </p>
                      {evidence.comment_text && (
                        <p className="text-sm text-gray-700 mt-2">
                          {evidence.comment_text}
                        </p>
                      )}
                    </div>
                  </div>
                  {evidence.receipt_file_url && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        window.open(getFileUrl(evidence.receipt_file_url), '_blank')
                      }}
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Предпросмотр выбранного файла */}
        {selectedEvidence?.receipt_file_url && (
          <div>
            <label className="block text-sm font-medium mb-3">
              Предпросмотр файла
            </label>
            <div className="border rounded-lg overflow-hidden bg-gray-50">
              {selectedEvidence.receipt_file_url.toLowerCase().endsWith('.pdf') ? (
                <div className="p-8 text-center">
                  <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-sm text-muted-foreground mb-4">
                    PDF файл - откройте в новой вкладке для просмотра
                  </p>
                  <Button
                    variant="outline"
                    onClick={() => window.open(getFileUrl(selectedEvidence.receipt_file_url), '_blank')}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Открыть PDF
                  </Button>
                </div>
              ) : (
                <img
                  src={getFileUrl(selectedEvidence.receipt_file_url)}
                  alt="Доказательство оплаты"
                  className="w-full h-auto max-h-[500px] object-contain"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none'
                    e.currentTarget.parentElement!.innerHTML = `
                      <div class="p-8 text-center">
                        <p class="text-sm text-red-600">Не удалось загрузить изображение</p>
                      </div>
                    `
                  }}
                />
              )}
            </div>
          </div>
        )}

        {/* Поля для админа */}
        <div className="space-y-4">
          <div>
            <label htmlFor="payment-reference" className="block text-sm font-medium mb-2">
              Номер транзакции (необязательно)
            </label>
            <Input
              id="payment-reference"
              placeholder="Введите номер транзакции или ID платежа..."
              value={paymentReference}
              onChange={(e) => setPaymentReference(e.target.value)}
              maxLength={255}
            />
          </div>

          <div>
            <label htmlFor="payment-notes" className="block text-sm font-medium mb-2">
              Заметки администратора
            </label>
            <Textarea
              id="payment-notes"
              placeholder="Добавьте заметки о проверке оплаты..."
              value={paymentNotes}
              onChange={(e) => setPaymentNotes(e.target.value)}
              rows={3}
              maxLength={500}
            />
            <p className="text-xs text-gray-500 mt-1">
              {paymentNotes.length}/500 символов
            </p>
          </div>
        </div>

        {/* Информация */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
            <div className="text-sm">
              <p className="font-medium text-blue-800 mb-1">
                Важно!
              </p>
              <ul className="text-blue-700 space-y-1">
                <li>• Проверьте соответствие суммы и реквизитов</li>
                <li>• При подтверждении бронирование получит статус "Подтверждено"</li>
                <li>• При отклонении бронирование получит статус "Отклонено"</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Кнопки действий */}
        <div className="flex gap-3 justify-end">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={confirmMutation.isLoading || rejectMutation.isLoading}
          >
            Отмена
          </Button>
          <Button
            variant="destructive"
            onClick={handleReject}
            disabled={confirmMutation.isLoading || rejectMutation.isLoading}
            className="min-w-[120px]"
          >
            {rejectMutation.isLoading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Отклонение...
              </>
            ) : (
              <>
                <X className="h-4 w-4 mr-2" />
                Отклонить
              </>
            )}
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={confirmMutation.isLoading || rejectMutation.isLoading}
            className="min-w-[120px]"
          >
            {confirmMutation.isLoading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Подтверждение...
              </>
            ) : (
              <>
                <Check className="h-4 w-4 mr-2" />
                Подтвердить
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
