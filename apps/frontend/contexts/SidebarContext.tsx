// contexts/SidebarContext.tsx
'use client'

import { createContext, useContext, useState } from 'react'

type SidebarContextType = {
  collapsed: boolean
  toggleSidebar: () => void
}

const SidebarContext = createContext<SidebarContextType>({
  collapsed: false,
  toggleSidebar: () => {}
})

export function SidebarProvider({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false)

  const toggleSidebar = () => {
    setCollapsed(!collapsed)
  }

  return (
    <SidebarContext.Provider value={{ collapsed, toggleSidebar }}>
      {children}
    </SidebarContext.Provider>
  )
}

export const useSidebar = () => useContext(SidebarContext)