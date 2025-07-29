// components/detective/NewsFeed.tsx
'use client'

import { Clock, ExternalLink } from 'lucide-react'

export default function NewsFeed() {
  const news = [
    {
      id: 1,
      title: 'Governo anuncia novos leilões de energia renovável',
      source: 'Energia Hoje',
      time: '2 horas atrás',
      category: 'Solar',
      url: '#'
    },
    {
      id: 2,
      title: 'Crise hídrica afeta geração nas principais hidrelétricas',
      source: 'Mercado Energético',
      time: '5 horas atrás',
      category: 'Hidrelétrica',
      url: '#'
    },
    // Adicione mais notícias...
  ]

  return (
    <div className="space-y-4">
      {news.map((item) => (
        <div key={item.id} className="bg-gray-800/50 rounded-lg p-4 hover:bg-gray-800/70 transition-colors">
          <div className="flex justify-between items-start">
            <div>
              <span className="inline-block px-2 py-1 text-xs rounded-full bg-blue-900/50 text-blue-400 mb-2">
                {item.category}
              </span>
              <h3 className="font-medium">{item.title}</h3>
            </div>
            <a 
              href={item.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white"
            >
              <ExternalLink size={16} />
            </a>
          </div>
          <div className="flex items-center gap-2 mt-3 text-sm text-gray-400">
            <Clock size={14} />
            <span>{item.time} • {item.source}</span>
          </div>
        </div>
      ))}
    </div>
  )
}