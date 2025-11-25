import { Outlet } from 'react-router-dom'

import { PublicHeader } from '@/shared/components/headers/PublicHeader'
import { PublicFooter } from '@/shared/components/footers/PublicFooter'

export const PublicLayout = () => {
  return (
    <div className="flex min-h-screen flex-col">
      <PublicHeader />
      <main className="flex-1">
        <Outlet />
      </main>
      <PublicFooter />
    </div>
  )
}
