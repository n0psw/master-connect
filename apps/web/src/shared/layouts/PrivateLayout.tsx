import { Outlet } from 'react-router-dom'

import { PrivateHeader } from '@/shared/components/headers/PrivateHeader'
import { PrivateSidebar } from '@/shared/components/sidebars/PrivateSidebar'

export const PrivateLayout = () => {
  return (
    <div className="flex min-h-screen bg-background">
      <PrivateSidebar />
      <div className="flex flex-1 flex-col">
        <PrivateHeader />
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
