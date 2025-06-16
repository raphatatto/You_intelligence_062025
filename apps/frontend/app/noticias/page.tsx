
import NewsCard from '@/components/noticias/NewsCard';
import { noticias } from '@/app/data/noticias';

export const metadata = { title: 'Notícias • You.On' };

export default function NoticiasPage() {
  return (
    <section className="space-y-6">
      <h1 className="text-2xl font-bold">Clipping de Energia & Mercado</h1>

      <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-6">
        {noticias.map(n => (
          <NewsCard key={n.id} n={n} />
        ))}
      </div>
    </section>
  );
}
