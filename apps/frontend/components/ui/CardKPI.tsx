"use client"

// components/ui/CardKPI.tsx

type CardKPIProps = {
  title: string;
  value: string;
  icon: React.ReactNode;
  className?: string;
  trend?: string;
  trendValue?: string;
};

export default function CardKPI({ title, value, icon, className, trend = '', trendValue = '' }: CardKPIProps) {
  return (
    <div className={`p-4 rounded-xl shadow ${className}`}>
      <div className="flex items-center space-x-3">
        <div className="text-xl">{icon}</div>
        <div className="flex flex-col">
          <span className="text-sm text-muted-foreground">{title}</span>
          <span className="text-2xl font-bold">{value}</span>
          {trend && <span className="text-sm text-muted-foreground">{trend}</span>}
          {trendValue && <span className={`text-sm ${trend.startsWith('up') ? 'text-green-500' : 'text-red-500'}`}>{trendValue}</span>}
        </div>
      </div>
    </div>
  );
}
