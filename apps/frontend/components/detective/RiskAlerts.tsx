'use client'

import { AlertCircle } from 'lucide-react'

export default function RiskAlerts() {
  return (
    <div>
      <h3 className="font-bold mb-4 flex items-center gap-2">
        <AlertCircle className="text-red-400" size={18} />
        Alertas de Risco
      </h3>
      <div className="space-y-3">
        <div className="bg-gray-700/50 p-3 rounded-lg">
          <h4 className="font-medium text-sm">Mudança Regulatória</h4>
          <p className="text-xs text-gray-400 mt-1">Novas taxas para geração distribuída</p>
        </div>
      </div>
    </div>
  )
}