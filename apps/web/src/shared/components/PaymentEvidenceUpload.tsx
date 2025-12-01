import { useState } from 'react'
import { Upload, File, X, AlertCircle, CheckCircle } from 'lucide-react'
import { useMutation, useQueryClient } from 'react-query'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Textarea } from '@/shared/ui/textarea'
import { paymentsApi } from '@/shared/api/payments'
import { bookingsApi } from '@/shared/api/bookings'
import type { PaymentEvidence } from '@/shared/api/payments'

interface PaymentEvidenceUploadProps {
  bookingId: string
  onClose: () => void
  onSuccess?: () => void
}

export const PaymentEvidenceUpload = ({ 
  bookingId, 
  onClose, 
  onSuccess 
}: PaymentEvidenceUploadProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [comment, setComment] = useState('')
  const [isDragOver, setIsDragOver] = useState(false)
  
  const queryClient = useQueryClient()

  const markPaymentMutation = useMutation(
    () => bookingsApi.markPayment(bookingId),
    {
      onSuccess: () => {
        toast.success('Оплата отмечена. Ожидает подтверждения администратором.')
        queryClient.invalidateQueries(['my-bookings'])
        queryClient.invalidateQueries(['admin-bookings'])
        queryClient.invalidateQueries(['moderation-queue'])
        queryClient.invalidateQueries(['booking-stats'])
        onSuccess?.()
        onClose()
      },
      onError: (error: any) => {
        toast.error('Не удалось отметить оплату: ' + (error?.detail || error?.message))
      }
    }
  )

  const uploadMutation = useMutation(
    (data: { comment: string; file: File }) =>
      paymentsApi.createEvidence(bookingId, data.comment, data.file),
    {
      onSuccess: () => {
        toast.success('Доказательство оплаты загружено!')
        queryClient.invalidateQueries(['payment-evidence', bookingId])
        markPaymentMutation.mutate()
      },
      onError: (error: any) => {
        toast.error('Ошибка при загрузке файла: ' + (error?.detail || error?.message))
      }
    }
  )

  const handleFileSelect = (file: File) => {
    // Проверка типа файла
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
    if (!allowedTypes.includes(file.type)) {
      toast.error('Неподдерживаемый формат файла. Разрешены: PDF, JPG, PNG')
      return
    }

    // Проверка размера файла (10MB)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      toast.error('Размер файла превышает 10MB')
      return
    }

    setSelectedFile(file)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleSubmit = () => {
    if (!selectedFile) {
      toast.error('Выберите файл для загрузки')
      return
    }

    uploadMutation.mutate({
      comment: comment.trim(),
      file: selectedFile
    })
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Загрузка доказательства оплаты
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Загрузка файла */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Файл квитанции/чека *
          </label>
          
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragOver 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDrop={handleDrop}
            onDragOver={(e) => {
              e.preventDefault()
              setIsDragOver(true)
            }}
            onDragLeave={() => setIsDragOver(false)}
          >
            {selectedFile ? (
              <div className="flex items-center justify-between bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <File className="h-8 w-8 text-green-600" />
                  <div className="text-left">
                    <p className="font-medium text-green-800">{selectedFile.name}</p>
                    <p className="text-sm text-green-600">{formatFileSize(selectedFile.size)}</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedFile(null)}
                  className="text-red-600 hover:text-red-700"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <Upload className="h-12 w-12 text-gray-400 mx-auto" />
                <div>
                  <p className="text-lg font-medium text-gray-700">
                    Перетащите файл сюда или нажмите для выбора
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    Поддерживаемые форматы: PDF, JPG, PNG (максимум 10MB)
                  </p>
                </div>
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={handleFileInput}
                  className="hidden"
                  id="file-upload"
                />
                <Button
                  variant="outline"
                  onClick={() => document.getElementById('file-upload')?.click()}
                >
                  Выбрать файл
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* Комментарий */}
        <div>
          <label htmlFor="comment" className="block text-sm font-medium mb-2">
            Комментарий (необязательно)
          </label>
          <Textarea
            id="comment"
            placeholder="Дополнительная информация об оплате..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={3}
            maxLength={1000}
          />
          <p className="text-xs text-gray-500 mt-1">
            {comment.length}/1000 символов
          </p>
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
                <li>• Загрузите скриншот или PDF чек об оплате</li>
                <li>• После загрузки администратор проверит оплату вручную</li>
                <li>• После подтверждения статус бронирования изменится</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Кнопки */}
        <div className="flex gap-3 justify-end">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={uploadMutation.isLoading || markPaymentMutation.isLoading}
          >
            Отмена
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={
              !selectedFile ||
              uploadMutation.isLoading ||
              markPaymentMutation.isLoading
            }
            className="min-w-[120px]"
          >
            {uploadMutation.isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                Загрузка...
              </>
            ) : markPaymentMutation.isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                Отмечаем оплату...
              </>
            ) : (
              <>
                <CheckCircle className="h-4 w-4 mr-2" />
                Загрузить
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

