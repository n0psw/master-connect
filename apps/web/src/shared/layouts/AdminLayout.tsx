import { Outlet } from 'react-router-dom'

import { AdminHeader } from '@/shared/components/headers/AdminHeader'
import { AdminSidebar } from '@/shared/components/sidebars/AdminSidebar'

export const AdminLayout = () => {
  return (
    <div className="flex min-h-screen bg-background">
      <AdminSidebar />
      <div className="flex flex-1 flex-col">
        <AdminHeader />
        <main className="flex-1 p-6">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
