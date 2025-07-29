// components/detective/MarketOverview.tsx
'use client'

import { TrendingUp, Zap, Battery, Droplet } from 'lucide-react'

export default function MarketOverview() {
  const metrics = [
    { icon: TrendingUp, label: 'Preço Médio', value: 'R$ 350,20', change: '+2.4%' },
    { icon: Zap, label: 'Demanda', value: '45.230 MW', change: '+1.1%' },
    { icon: Battery, label: 'Capacidade', value: '78.450 MW', change: '+5.3%' },
    { icon: Droplet, label: 'Hidrelétricas', value: '62%', change: '-3.2%' }
  ]

  return (
    <div className="space-y-6">
      {/* Cards de Métricas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map(({ icon: Icon, label, value, change }, index) => (
          <div key={index} className="bg-gray-800/50 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gray-700">
                <Icon className="text-blue-400" size={18} />
              </div>
              <div>
                <p className="text-sm text-gray-400">{label}</p>
                <div className="flex items-baseline gap-2">
                  <p className="text-lg font-semibold">{value}</p>
                  <span className={`text-xs ${
                    change.startsWith('+') ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {change}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Gráficos e Análises */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="bg-gray-800/50 rounded-lg p-4 lg:col-span-2 h-64">
          <h3 className="font-medium mb-3">Variação de Preços (Últimos 30 dias)</h3>
          <div className="h-48 bg-gray-900/30 rounded flex items-center justify-center text-gray-500">
            Gráfico será exibido aqui
          </div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4 h-64">
          <h3 className="font-medium mb-3">Distribuição por Fonte</h3>
          <div className="h-48 bg-gray-900/30 rounded flex items-center justify-center text-gray-500">
            Gráfico de pizza será exibido aqui
          </div>
        </div>
      </div>
    </div>
  )
}