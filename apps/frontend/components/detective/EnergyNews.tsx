// components/detective/EnergyNews.tsx
'use client'

import { useState, useEffect } from 'react'
import { Zap, ExternalLink } from 'lucide-react'

export default function EnergyNews() {
  const [news, setNews] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulando busca de notícias (substitua por uma chamada real à API)
    const fetchNews = async () => {
      try {
        setLoading(true)
        // Exemplo de dados mockados
        const mockNews = [
          {
            id: 1,
            title: 'Novas políticas para energia renovável',
            source: 'Energia Hoje',
            date: '2023-11-15',
            url: '#'
          },
          {
            id: 2,
            title: 'Crescimento recorde da energia solar',
            source: 'Mercado Energético',
            date: '2023-11-10',
            url: '#'
          }
        ]
        setNews(mockNews)
      } catch (error) {
        console.error('Erro ao buscar notícias:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchNews()
  }, [])

  return (
    <div>
      <h3 className="font-bold mb-4 flex items-center gap-2">
        <Zap className="text-yellow-400" size={18} />
        Últimas Notícias do Setor
      </h3>
      
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-yellow-400"></div>
        </div>
      ) : (
        <div className="space-y-3">
          {news.map((item) => (
            <div key={item.id} className="bg-gray-700/50 p-3 rounded-lg">
              <h4 className="font-medium text-sm">{item.title}</h4>
              <div className="flex justify-between items-center mt-2">
                <span className="text-xs text-gray-400">
                  {item.source} • {new Date(item.date).toLocaleDateString()}
                </span>
                <a 
                  href={item.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-yellow-400 hover:text-yellow-300"
                >
                  <ExternalLink size={14} />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}