'use client'

import { useSidebar } from '@/contexts/SidebarContext'
import { 
  TrendingUp, Zap, FileText, Globe, AlertCircle, 
  X, ChevronDown 
} from 'lucide-react'
import { JSX, useState } from 'react'
import clsx from 'clsx'
import * as Components from './index'

type FeatureKey = keyof typeof Components

const featureComponents: Record<FeatureKey, JSX.Element> = {
  'MarketAnalysis': <Components.MarketAnalysis />,
  'EnergyNews': <Components.EnergyNews />,
  'SectorReports': <Components.SectorReports />,
  'GlobalTrends': <Components.GlobalTrends />,
  'RiskAlerts': <Components.RiskAlerts />
}

function isFeatureKey(key: string | null): key is FeatureKey {
  return key ? key in Components : false
}

export default function DetectivePanel() {
  const { collapsed } = useSidebar()
  const [activeFeature, setActiveFeature] = useState<string | null>(null)
  const [expanded, setExpanded] = useState(false)

  if (collapsed || !activeFeature) return null

  const CurrentComponent = isFeatureKey(activeFeature) 
    ? featureComponents[activeFeature] 
    : null

  return (
    <div className={clsx(
      "fixed bottom-0 left-64 w-80 bg-gray-800 border-t border-r border-gray-700 rounded-tr-lg shadow-xl transition-all duration-300 z-40",
      collapsed ? "left-20" : "left-64",
      expanded ? "h-[70vh]" : "h-16"
    )}>
      {/* ... resto do código permanece igual ... */}
    </div>
  )
}

// ... implementações dos componentes MarketAnalysis, EnergyNews, etc ...
// Componentes de exemplo para cada funcionalidade
function MarketAnalysis() {
  return (
    <div>
      <h3 className="font-bold mb-3">Análise do Mercado Energético</h3>
      <div className="space-y-4">
        <div className="bg-gray-700/50 p-3 rounded-lg">
          <h4 className="font-medium text-sm mb-1">Preços de Energia</h4>
          <p className="text-xs text-gray-300">Variação mensal: +2.4%</p>
        </div>
        {/* Mais widgets de análise */}
      </div>
    </div>
  )
}

