'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';
import { 
  Home, MapPinned, BarChart2, MapIcon, LayoutDashboard,
  ChevronRight, Settings, User, LogOut, Search, Globe, 
  Zap, AlertCircle, TrendingUp, FileText, Bell, Bot, GitGraph} from 'lucide-react';
import { useState } from 'react';
import { useSidebar } from '@/contexts/SidebarContext';

const mainLinks = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/mapa', label: 'Mapa interativo', icon: MapPinned },
  { href: '/leads', label: 'Dados', icon: BarChart2 },
  { href: '/mapaHeat', label: 'Mapa de calor', icon: MapIcon },
  { href: '/detetive', label: 'Detetive', icon: Search },
  { href: '/noticias', label: 'Notícias', icon: Bell },
  { href: '/youknow', label: 'YouKnow', icon: Bot },
  { href: '/analise-de-mercado', label: 'Análise de Mercado', icon: GitGraph },
];

const detectiveFeatures = [
  { id: 'market-analysis', label: 'Análise de Mercado', icon: TrendingUp, color: 'text-purple-400',  href: '/analise-de-mercado'},
  { id: 'energy-news', label: 'Notícias de Energia', icon: Zap, color: 'text-yellow-400' },
  { id: 'reports', label: 'Relatórios Setoriais', icon: FileText, color: 'text-blue-400' },
  { id: 'global-trends', label: 'Tendências Globais', icon: Globe, color: 'text-green-400' },
  { id: 'risk-alerts', label: 'Alertas de Risco', icon: AlertCircle, color: 'text-red-400' },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { collapsed, toggleSidebar } = useSidebar();
  const [detectiveExpanded, setDetectiveExpanded] = useState(false);
  const [activeDetectiveFeature, setActiveDetectiveFeature] = useState<string | null>(null);

  return (
    <aside className={clsx(
      "fixed inset-y-0 left-0 bg-black text-white flex flex-col border-r border-gray-800 transition-all duration-300 z-50",
      collapsed ? "w-20" : "w-64"
    )}>
      {/* Topo com logo */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-gray-800">
        {!collapsed ? (
          <Image src="/logo-verde.png" alt="You.On" height={32} width={120} priority />
        ) : (
          <Image src="/icone-verde.png" alt="You.On" height={32} width={32} priority />
        )}
        <button 
          onClick={toggleSidebar}
          className="p-1 rounded-md hover:bg-gray-800 text-gray-400 hover:text-white"
        >
          <ChevronRight className={clsx("transition-transform duration-300", collapsed && "rotate-180")} size={20} />
        </button>
      </div>

      {/* Navegação principal */}
      <nav className="flex-1 mt-4 space-y-1 px-2 overflow-y-auto">
        {mainLinks.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={clsx(
              'flex items-center gap-3 px-3 py-3 rounded-lg transition-all',
              pathname === href
                ? 'bg-[#b3d430]/10 text-white font-medium'
                : 'hover:bg-gray-800/50 text-gray-300 hover:text-white'
            )}
          >
            <div className={clsx(
              "p-2 rounded-lg",
              pathname === href ? "bg-[#b3d430] text-white" : "bg-gray-800 text-[#b3d430]"
            )}>
              <Icon size={18} />
            </div>
            {!collapsed && <span>{label}</span>}
          </Link>
        ))}

        {/* Seção Detetive */}
        <div className="mt-6">
          <button
            onClick={() => setDetectiveExpanded(!detectiveExpanded)}
            className={clsx(
              "w-full flex items-center justify-between px-3 py-3 rounded-lg transition-all",
              "hover:bg-gray-800/50 text-gray-300 hover:text-white",
              detectiveExpanded && "bg-gray-800/30"
            )}
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-indigo-900/50 text-indigo-300">
                <Search size={18} />
              </div>
              {!collapsed && <span>Detetive de Mercado</span>}
            </div>
            {!collapsed && (
              <ChevronRight 
                size={18} 
                className={clsx(
                  "transition-transform duration-200",
                  detectiveExpanded && "rotate-90"
                )} 
              />
            )}
          </button>

          {detectiveExpanded && !collapsed && (
            <div className="ml-2 pl-6 mt-1 space-y-1 border-l-2 border-gray-700">
              {detectiveFeatures.map(({ id, label, icon: Icon, color, href }) => (
                <Link
                  key={id}
                  href={href || '#'}
                  className={clsx(
                    "w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-all text-sm",
                    "hover:bg-gray-800/30",
                    pathname === href ? "text-white font-medium" : "text-gray-400"
                  )}
                  onClick={() => setActiveDetectiveFeature(id)}
                >
                  <Icon size={16} className={clsx(
                    color, 
                    pathname === href ? "opacity-100" : "opacity-70"
                  )} />
                  <span>{label}</span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </nav>

      {/* Área do usuário */}
      <div className="border-t border-gray-800 p-4">
         <Link href="/admin">
        <div className={clsx(
          "flex items-center gap-3 p-2 rounded-lg hover:bg-gray-800/50 transition-colors cursor-pointer",
          collapsed ? "justify-center" : ""
        )}>
          <Image
            src="/icone-verde.png"
            alt="User"
            width={40}
            height={40}
            className="rounded-full border-2 border-[#b3d430]"
          />
          {!collapsed && (
            <div className="overflow-hidden">
              <p className="font-medium truncate">Admin</p>
              <p className="text-xs text-gray-400 truncate">admin@youon.com</p>
            </div>
          )}
        </div>
        </Link>
      </div>
    </aside>
  );
}