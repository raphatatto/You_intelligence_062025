'use client'

import { TrendingUp } from 'lucide-react'

export default function MarketAnalysis() {
  return (
    <div>
      <h3 className="font-bold mb-4 flex items-center gap-2">
        <TrendingUp className="text-purple-400" size={18} />
        Análise de Mercado
      </h3>
      <div className="space-y-3">
        <div className="bg-gray-700/50 p-3 rounded-lg">
          <h4 className="font-medium text-sm">Preços de Energia</h4>
          <p className="text-xs text-gray-400 mt-1">Variação mensal: +2.4%</p>
        </div>
        {/* Adicione mais widgets conforme necessário */}
      </div>
    </div>
  )
}