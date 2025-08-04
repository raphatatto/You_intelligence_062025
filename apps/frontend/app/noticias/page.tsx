'use client'

import { useEffect, useState } from 'react'
import { Newspaper, Clock, ExternalLink, Search, Frown } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'

// Tipagem dos artigos
type Article = {
  title: string
  description: string
  url: string
  urlToImage: string
  publishedAt: string
  source: { name: string }
  content: string
}

export default function NoticiasPage() {
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchNews = async () => {
    try {
      setLoading(true)
      setError(null)

      const now = Date.now()
      const query = encodeURIComponent(`"energia elétrica" OR "setor elétrico" OR "distribuidora de energia"`)
      const res = await fetch(
        `https://newsapi.org/v2/everything?q=${query}&language=pt&sortBy=publishedAt&apiKey=${process.env.NEXT_PUBLIC_NEWS_API_KEY}`
      )

      if (!res.ok) throw new Error('Falha ao carregar notícias')

      const data = await res.json()
      setArticles(data.articles || [])

      localStorage.setItem('lastNewsFetch', String(now))
      localStorage.setItem('cachedNews', JSON.stringify(data.articles || []))
    } catch (err) {
      console.error('Erro ao buscar notícias:', err)
      setError('Não foi possível carregar as notícias. Tente novamente mais tarde.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const lastFetch = localStorage.getItem('lastNewsFetch')
    const now = Date.now()

    if (lastFetch && now - parseInt(lastFetch) < 3600000) {
      console.log('⏳ Aguardando 1h para novo fetch de notícias')
      const cached = localStorage.getItem('cachedNews')
      if (cached) setArticles(JSON.parse(cached))
      setLoading(false)
      return
    }

    fetchNews()
  }, [])

  const handleAtualizarAgora = () => {
    localStorage.removeItem('lastNewsFetch')
    localStorage.removeItem('cachedNews')
    fetchNews()
  }

  return (
    <section className="container mx-auto px-4 py-12">
      <div className="max-w-6xl mx-auto">
        <div className="mb-12 text-center">
          <h1 className="text-4xl font-bold text-white mb-3">Clipping de Energia & Mercado</h1>
          <p className="text-lg text-gray-300 max-w-2xl mx-auto">
            Fique atualizado com as principais notícias do setor energético
          </p>
          <button
            onClick={handleAtualizarAgora}
            className="mt-4 text-sm text-primary underline hover:text-primary/80"
          >
            🔄 Atualizar notícias agora
          </button>
        </div>

        {error && (
          <div className="bg-red-900/20 border border-red-700 text-red-300 p-4 rounded-lg flex items-center gap-3 mb-8">
            <Frown size={24} />
            <div>
              <h3 className="font-bold">Erro ao carregar notícias</h3>
              <p>{error}</p>
            </div>
          </div>
        )}

        {loading ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <NewsCardSkeleton key={i} />
            ))}
          </div>
        ) : articles.length > 0 ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.map((article, index) => (
              <NewsCard key={index} article={article} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Frown size={48} className="mx-auto text-gray-500 mb-4" />
            <h3 className="text-xl font-medium text-gray-300">Nenhuma notícia encontrada</h3>
            <p className="text-gray-500 mt-2">Tente novamente mais tarde</p>
          </div>
        )}
      </div>
    </section>
  )
}

function NewsCardSkeleton() {
  return (
    <div className="bg-gray-800 rounded-xl overflow-hidden border border-gray-700">
      <Skeleton className="h-48 w-full bg-gray-700" />
      <div className="p-5 space-y-3">
        <Skeleton className="h-4 w-3/4 bg-gray-700" />
        <Skeleton className="h-3 w-full bg-gray-700" />
        <Skeleton className="h-3 w-full bg-gray-700" />
        <Skeleton className="h-3 w-1/2 bg-gray-700" />
      </div>
    </div>
  )
}

function NewsCard({ article }: { article: Article }) {
  const [imgError, setImgError] = useState(false)
  const imagemSegura = (!article.urlToImage || imgError) ? '/placeholder-news.jpg' : article.urlToImage

  return (
    <article className="group bg-gray-800 rounded-xl overflow-hidden border border-gray-700 hover:border-primary/50 transition-all duration-300 h-full flex flex-col">
      <div className="relative h-48 overflow-hidden">
        <img
          src={imagemSegura}
          alt={article.title}
          onError={() => setImgError(true)}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
      </div>

      <div className="p-5 flex flex-col flex-1">
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-3">
          <Newspaper size={14} />
          <span>{article.source?.name || 'Fonte desconhecida'}</span>
          <span className="mx-1">•</span>
          <Clock size={14} />
          <time>{new Date(article.publishedAt).toLocaleDateString('pt-BR')}</time>
        </div>

        <h2 className="text-xl font-bold text-white mb-2 line-clamp-2">{article.title}</h2>

        <p className="text-gray-300 mb-4 line-clamp-3 flex-1">
          {article.description || article.content?.split('…')[0] || 'Nenhuma descrição disponível.'}
        </p>

        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-auto inline-flex items-center gap-2 text-primary font-medium group/link"
        >
          <span className="group-hover/link:underline">Ler matéria completa</span>
          <ExternalLink size={16} className="transition-transform group-hover/link:translate-x-1" />
        </a>
      </div>
    </article>
  )
}
