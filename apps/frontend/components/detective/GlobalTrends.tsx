'use client'

import { Globe } from 'lucide-react'

export default function GlobalTrends() {
  return (
    <div>
      <h3 className="font-bold mb-4 flex items-center gap-2">
        <Globe className="text-green-400" size={18} />
        Tendências Globais
      </h3>
      <div className="space-y-3">
        <div className="bg-gray-700/50 p-3 rounded-lg">
          <h4 className="font-medium text-sm">Adoção de Energia Solar</h4>
          <p className="text-xs text-gray-400 mt-1">Crescimento de 35% em 2023</p>
        </div>
      </div>
    </div>
  )
}