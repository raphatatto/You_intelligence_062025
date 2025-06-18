'use client';
import Image from 'next/image';
import { ExternalLink } from 'lucide-react';
import type { Noticia } from '@/app/types/noticia';

export default function NewsCard({ n }: { n: Noticia }) {
  return (
    <article className="flex flex-col rounded-xl bg-white shadow hover:shadow-lg transition">
      {n.imagem && (
        <Image
          src={n.imagem}
          alt={n.titulo}
          width={640}
          height={360}
          className="rounded-t-xl h-40 w-full object-cover"
          unoptimized
        />

      )}
      <div className="p-4 flex flex-col gap-2 flex-1">
        <h3 className="text-lg font-semibold">{n.titulo}</h3>
        <p className="text-sm text-gray-600 flex-1">{n.resumo}</p>
        <div className="text-xs text-gray-400 flex items-center justify-between">
          <span>{n.fonte}</span>
          <time>{new Date(n.data).toLocaleDateString('pt-BR')}</time>
        </div>
        <a
          href={n.url}
          target="_blank"
          rel="noopener"
          className="mt-2 inline-flex items-center gap-1 text-primary hover:underline text-sm"
        >
          Ler matéria <ExternalLink size={14} />
        </a>
      </div>
    </article>
  );
}
