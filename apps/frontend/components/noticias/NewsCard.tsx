'use client'

import { ExternalLink, Clock, Newspaper } from 'lucide-react'
import Image from 'next/image'

type NewsProps = {
  n: {
    title: string
    description: string
    url: string
    image: string
    publishedAt: string
    source: { name: string }
  }
}

export default function NewsCard({ n }: NewsProps) {
  const formattedDate = new Date(n.publishedAt).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  })

  return (
    <article className="group relative h-full">
      <a
        href={n.url}
        target="_blank"
        rel="noopener noreferrer"
        className="h-full flex flex-col bg-gray-800 rounded-xl overflow-hidden border border-gray-700 hover:border-primary/50 transition-all duration-300 shadow-lg hover:shadow-xl"
        aria-label={`Ler notícia: ${n.title}`}
      >
        {/* Imagem com fallback */}
        <div className="relative h-48 w-full overflow-hidden bg-gray-700">
          {n.image ? (
            <Image
              src={n.image}
              alt={n.title}
              fill
              className="object-cover transition-transform duration-500 group-hover:scale-105"
              onError={(e) => {
                (e.target as HTMLImageElement).src = '/placeholder-news.jpg'
              }}
              unoptimized
            />
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500">
              <Newspaper size={48} />
            </div>
          )}
        </div>

        {/* Conteúdo */}
        <div className="p-5 flex flex-col flex-1">
          {/* Meta informações */}
          <div className="flex items-center gap-2 text-sm text-gray-400 mb-3 flex-wrap">
            <div className="flex items-center gap-1">
              <Newspaper className="h-4 w-4" />
              <span>{n.source?.name || 'Fonte desconhecida'}</span>
            </div>
            <span className="text-gray-600">•</span>
            <div className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              <time dateTime={n.publishedAt}>{formattedDate}</time>
            </div>
          </div>

          {/* Título */}
          <h2 className="text-xl font-bold text-white mb-3 line-clamp-2">
            {n.title}
          </h2>

          {/* Descrição */}
          <p className="text-gray-300 mb-5 line-clamp-3 flex-1">
            {n.description || 'Nenhuma descrição disponível.'}
          </p>

          {/* Link */}
          <div className="mt-auto flex items-center gap-2 text-primary font-medium group-hover:underline">
            <span>Ler matéria completa</span>
            <ExternalLink className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </div>
        </div>

        {/* Efeito hover */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      </a>
    </article>
  )
}