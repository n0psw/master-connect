export const getImageUrl = (url: string | null | undefined): string | null => {
  if (!url) return null
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  if (url.startsWith('/uploads')) {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
    const baseUrl = apiUrl.replace('/api/v1', '')
    return `${baseUrl}${url}`
  }
  return url
}

