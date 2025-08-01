// components/ui/skeleton.tsx
export function Skeleton({ className }: { className?: string }) {
  return (
    <div 
      className={`animate-pulse bg-gray-700 rounded-md ${className}`}
    />
  )
}