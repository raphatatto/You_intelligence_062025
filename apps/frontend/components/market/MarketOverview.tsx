// components/market/MarketOverview.tsx
'use client'
import { CustomLineChart, CustomBarChart } from '@/components/ui/charts'
export function MarketOverview() {
  const priceData = [
    { name: 'Jan', value: 320 },
    { name: 'Fev', value: 340 },
    // ... mais dados
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800/50 rounded-lg p-4">
          <h3 className="font-medium mb-4">Variação de Preços (12 meses)</h3>
          <CustomLineChart data={priceData} color="#3b82f6" />
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4">
          <h3 className="font-medium mb-4">Demanda por Fonte</h3>
          <CustomBarChart
            data={[
              { name: 'Hidrelétrica', value: 45 },
              { name: 'Termelétrica', value: 25 },
              // ... mais dados
            ]} 
            colors={['#10b981', '#ef4444', '#f59e0b']}
          />
        </div>
      </div>
      
      {/* Outras visualizações */}
    </div>
  )
}