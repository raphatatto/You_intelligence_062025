"use client"

// components/ui/CardKPI.tsx

type CardKPIProps = {
  title: string;
  value: string;
  icon: React.ReactNode;
  className?: string; // <-- adicione isso
};

export default function CardKPI({ title, value, icon, className = '' }: CardKPIProps) {
  return (
    <div className={`p-4 rounded-xl shadow ${className}`}>
      <div className="flex items-center space-x-3">
        <div className="text-xl">{icon}</div>
        <div className="flex flex-col">
          <span className="text-sm text-muted-foreground">{title}</span>
          <span className="text-2xl font-bold">{value}</span>
        </div>
      </div>
    </div>
  );
}
