import { useEffect } from 'react'
import { QueryClient, QueryClientProvider } from 'react-query'
import { BrowserRouter } from 'react-router-dom'
import { HelmetProvider } from 'react-helmet-async'

import { AppRouter } from '@/app/router/AppRouter'
import { Toaster } from '@/shared/ui/toaster'
import { PageLoader } from '@/shared/ui/PageLoader'
import { useAuthStore } from '@/shared/store/auth'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
})

function AuthInitializer({ children }: { children: React.ReactNode }) {
  const { initializeAuth, isLoading } = useAuthStore()

  useEffect(() => {
    // Инициализируем аутентификацию при загрузке приложения
    initializeAuth().catch(error => {
      console.warn('Failed to initialize auth:', error)
    })
  }, [initializeAuth])

  // Показываем загрузку пока проверяется аутентификация
  if (isLoading) {
    return <PageLoader />
  }

  return <>{children}</>
}

function App() {
  return (
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AuthInitializer>
            <div className="min-h-screen bg-background font-sans antialiased">
              <AppRouter />
              <Toaster />
            </div>
          </AuthInitializer>
        </BrowserRouter>
      </QueryClientProvider>
    </HelmetProvider>
  )
}

export default App
