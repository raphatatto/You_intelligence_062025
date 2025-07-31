// components/market/GenerationSources.tsx
'use client'

import { CustomPieChart  } from '@/components/ui/charts'

export function GenerationSources() {
  const data = [
    { name: 'Hidrelétrica', value: 45 },
    { name: 'Eólica', value: 15 },
    // ... mais dados
  ]

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-gray-800/50 rounded-lg p-4">
        <h3 className="font-medium mb-4">Distribuição por Fonte</h3>
        <CustomPieChart  data={data} />
      </div>
      
      {/* Outras visualizações */}
    </div>
  )
}