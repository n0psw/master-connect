import { Link } from 'react-router-dom'
import { Home, ArrowLeft } from 'lucide-react'
import { Helmet } from 'react-helmet-async'

import { Button } from '@/shared/ui/button'

export const NotFoundPage = () => {
  return (
    <>
      <Helmet>
        <title>Страница не найдена - MasterConnect</title>
      </Helmet>

      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="max-w-md text-center">
          <div className="mb-8">
            <h1 className="text-9xl font-bold text-primary/20">404</h1>
            <h2 className="text-3xl font-bold mb-4">Страница не найдена</h2>
            <p className="text-muted-foreground mb-8">
              Извините, запрашиваемая страница не существует или была перемещена.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild>
              <Link to="/">
                <Home className="mr-2 h-4 w-4" />
                На главную
              </Link>
            </Button>
            
            <Button variant="outline" onClick={() => window.history.back()}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Назад
            </Button>
          </div>
        </div>
      </div>
    </>
  )
}
