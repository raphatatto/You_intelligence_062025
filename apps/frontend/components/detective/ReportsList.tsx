// components/detective/ReportsList.tsx
'use client'

import { FileText, Download } from 'lucide-react'

export default function ReportsList() {
  const reports = [
    {
      id: 1,
      title: 'Relatório Anual de Energia Renovável 2023',
      date: '15/11/2023',
      size: '2.4 MB',
      url: '#'
    },
    // Adicione mais relatórios...
  ]

  return (
    <div className="space-y-3">
      {reports.map((report) => (
        <div key={report.id} className="flex items-center justify-between bg-gray-800/50 rounded-lg p-4">
          <div className="flex items-center gap-3">a
            <div className="p-2 rounded-lg bg-gray-700">
              <FileText className="text-blue-400" size={18} />
            </div>
            <div>
              <h3 className="font-medium">{report.title}</h3>
              <p className="text-sm text-gray-400">{report.date} • {report.size}</p>
            </div>
          </div>
          <a 
            href={report.url} 
            download
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg"
          >
            <Download size={18} />
          </a>
        </div>
      ))}
    </div>
  )
}