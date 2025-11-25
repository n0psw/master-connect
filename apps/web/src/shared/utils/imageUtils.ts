export const getImageUrl = (url: string | null | undefined): string | null => {
  if (!url) return null
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  if (url.startsWith('/uploads')) {
    const baseUrl = import.meta.env.VITE_API_URL?.replace('/api/v1', '') || 'http://localhost:8000'
    return `${baseUrl}${url}`
  }
  return url
}

