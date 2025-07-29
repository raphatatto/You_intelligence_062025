'use client'

import { FileText } from 'lucide-react'

export default function SectorReports() {
  return (
    <div>
      <h3 className="font-bold mb-4 flex items-center gap-2">
        <FileText className="text-blue-400" size={18} />
        Relatórios Setoriais
      </h3>
      <div className="space-y-3">
        <div className="bg-gray-700/50 p-3 rounded-lg">
          <h4 className="font-medium text-sm">Relatório Anual 2023</h4>
          <p className="text-xs text-gray-400 mt-1">Energias Renováveis</p>
        </div>
      </div>
    </div>
  )
}