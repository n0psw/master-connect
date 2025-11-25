import { useState, useRef } from 'react'
import { Upload, X, User } from 'lucide-react'
import { useMutation, useQueryClient } from 'react-query'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { profilesApi } from '@/shared/api/profiles'
import { getImageUrl } from '@/shared/utils/imageUtils'

interface AvatarUploadProps {
  currentAvatarUrl?: string | null
  userName?: string
  onSuccess?: () => void
}

export const AvatarUpload = ({ 
  currentAvatarUrl, 
  userName,
  onSuccess 
}: AvatarUploadProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [uploadedUrl, setUploadedUrl] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const queryClient = useQueryClient()

  const uploadMutation = useMutation(
    (file: File) => profilesApi.uploadAvatar(file),
    {
      onSuccess: async (data) => {
        setUploadedUrl(data.avatar_url)
        toast.success('Аватар успешно загружен!')
        
        await Promise.all([
          queryClient.invalidateQueries(['my-profile']),
          queryClient.invalidateQueries(['my-student-profile']),
          queryClient.invalidateQueries(['my-mentor-profile']),
          queryClient.invalidateQueries(['mentor-detail']),
          queryClient.invalidateQueries(['mentors-catalog']),
          queryClient.invalidateQueries(['my-bookings'])
        ])
        
        await Promise.all([
          queryClient.refetchQueries(['my-profile'], { active: true }),
          queryClient.refetchQueries(['my-mentor-profile'], { active: true }),
          queryClient.refetchQueries(['my-student-profile'], { active: true })
        ])
        
        setSelectedFile(null)
        setPreview(null)
        
        onSuccess?.()
      },
      onError: (error: any) => {
        toast.error('Ошибка при загрузке аватара: ' + (error?.detail || error?.message))
      }
    }
  )

  const handleFileSelect = (file: File) => {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      toast.error('Неподдерживаемый формат файла. Разрешены: JPG, PNG, WEBP')
      return
    }

    const maxSize = 5 * 1024 * 1024
    if (file.size > maxSize) {
      toast.error('Размер файла превышает 5MB')
      return
    }

    setSelectedFile(file)
    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleUpload = () => {
    if (!selectedFile) {
      toast.error('Выберите файл для загрузки')
      return
    }
    uploadMutation.mutate(selectedFile)
  }

  const handleRemove = () => {
    setSelectedFile(null)
    setPreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const displayAvatar = preview || uploadedUrl || currentAvatarUrl
  const initials = userName ? userName.charAt(0).toUpperCase() : 'U'

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-6">
        <div className="relative">
          {displayAvatar ? (
            <img
              src={getImageUrl(displayAvatar) || ''}
              alt="Аватар"
              className="w-32 h-32 rounded-full object-cover border-2 border-border"
              onError={(e) => {
                console.error('Failed to load avatar:', displayAvatar)
                e.currentTarget.style.display = 'none'
              }}
            />
          ) : (
            <div className="w-32 h-32 rounded-full bg-primary/10 flex items-center justify-center border-2 border-border">
              <span className="text-4xl font-semibold text-primary">{initials}</span>
            </div>
          )}
        </div>

        <div className="flex-1 space-y-2">
          <div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/jpg,image/png,image/webp"
              onChange={handleFileInput}
              className="hidden"
              id="avatar-upload"
            />
            <label htmlFor="avatar-upload">
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="cursor-pointer"
                asChild
              >
                <span>
                  <Upload className="h-4 w-4 mr-2" />
                  {selectedFile ? 'Изменить фото' : 'Загрузить фото'}
                </span>
              </Button>
            </label>
          </div>
          {selectedFile && (
            <div className="flex items-center gap-2">
              <Button
                type="button"
                variant="default"
                size="sm"
                onClick={handleUpload}
                disabled={uploadMutation.isLoading}
              >
                {uploadMutation.isLoading ? 'Загрузка...' : 'Сохранить'}
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleRemove}
                disabled={uploadMutation.isLoading}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          )}
          <p className="text-xs text-muted-foreground">
            JPG, PNG или WEBP. Максимум 5MB
          </p>
        </div>
      </div>
    </div>
  )
}

