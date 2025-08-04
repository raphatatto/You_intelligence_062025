// components/NewsCardSkeleton.tsx
import { Skeleton } from '@/components/ui/skeleton' // Ou seu componente Skeleton

export function NewsCardSkeleton() {
  return (
    <div className="bg-gray-800 rounded-xl overflow-hidden border border-gray-700 h-full">
      {/* Placeholder da imagem */}
      <Skeleton className="h-48 w-full bg-gray-700 rounded-none" />
      
      {/* Placeholder do conteúdo */}
      <div className="p-5 space-y-4">
        {/* Linha para fonte/data */}
        <div className="flex items-center gap-3">
          <Skeleton className="h-4 w-20 bg-gray-700" />
          <Skeleton className="h-1 w-1 bg-gray-600 rounded-full" />
          <Skeleton className="h-4 w-24 bg-gray-700" />
        </div>
        
        {/* Placeholder do título */}
        <Skeleton className="h-6 w-full bg-gray-700" />
        <Skeleton className="h-6 w-4/5 bg-gray-700" />
        
        {/* Placeholder da descrição */}
        <Skeleton className="h-4 w-full bg-gray-700" />
        <Skeleton className="h-4 w-full bg-gray-700" />
        <Skeleton className="h-4 w-3/4 bg-gray-700" />
        
        {/* Placeholder do link */}
        <Skeleton className="h-4 w-32 mt-6 bg-gray-700" />
      </div>
    </div>
  )
}