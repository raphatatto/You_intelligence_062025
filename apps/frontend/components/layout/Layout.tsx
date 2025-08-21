// components/layout/Layout.tsx
'use client'

import { useSidebar } from '@/contexts/SidebarContext'
import DetectivePanel from '../detective/Panel'
import clsx from 'clsx'
import Sidebar from '../ui/Sidebar'

export default function Layout({ children }: { children: React.ReactNode }) {
  const { collapsed } = useSidebar()

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main 
        className={clsx(
          "flex-1 overflow-auto transition-all duration-300 relative",
          collapsed ? "ml-20" : "ml-64"
        )}
      >
        {children}
        
      </main>
    </div>
  )
}