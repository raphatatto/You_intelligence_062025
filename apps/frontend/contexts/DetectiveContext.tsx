// contexts/DetectiveContext.tsx
'use client'

import { createContext, useContext, useState } from 'react'

type DetectiveContextType = {
  activeFeature: string | null
  setActiveFeature: (feature: string | null) => void
}

const DetectiveContext = createContext<DetectiveContextType>({
  activeFeature: null,
  setActiveFeature: () => {}
})

export function DetectiveProvider({ children }: { children: React.ReactNode }) {
  const [activeFeature, setActiveFeature] = useState<string | null>(null)

  return (
    <DetectiveContext.Provider value={{ activeFeature, setActiveFeature }}>
      {children}
    </DetectiveContext.Provider>
  )
}

export const useDetective = () => useContext(DetectiveContext)