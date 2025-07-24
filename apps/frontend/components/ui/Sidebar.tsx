'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';
import {
  Home,
  MapPinned,
  BarChart2,
  MapIcon,
  LayoutDashboard,
  ChevronRight,
  Settings,
  User,
  LogOut
} from 'lucide-react';
import { useState } from 'react';
import { useSidebar } from '@/contexts/SidebarContext'

const links = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/mapa', label: 'Mapa interativo', icon: MapPinned },
  { href: '/leads', label: 'Dados', icon: BarChart2 },
  { href: '/mapaHeat', label: 'Mapa de calor', icon: MapIcon },
];


export default function Sidebar() {
  const pathname = usePathname();
  const { collapsed, toggleSidebar } = useSidebar()

  return (
    <aside className={clsx(
      "fixed inset-y-0 left-0 bg-black text-white flex flex-col border-r border-gray-800 transition-all duration-300 z-50",
      collapsed ? "w-20" : "w-64"
    )}>
      {/* Topo com logo e botão de collapse */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-gray-800">
        {!collapsed && (
          <Image
            src="/logo-verde.png"
            alt="You.On"
            height={32}
            width={120}
            priority
            className="transition-opacity duration-300"
          />
        )}
        {collapsed && (
          <Image
            src="/icone-verde.png"
            alt="You.On"
            height={32}
            width={32}
            priority
            className="mx-auto"
          />
        )}
        <button 
          onClick={toggleSidebar}
          className="p-1 rounded-md hover:bg-gray-800 text-gray-400 hover:text-white"
        >
          <ChevronRight className={clsx(
            "transition-transform duration-300",
            collapsed ? "rotate-180" : ""
          )} size={20} />
        </button>

      </div>

      {/* Navegação */}
      <nav className="flex-1 mt-4 space-y-1 px-2 overflow-y-auto">
        {links.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                'flex items-center gap-3 px-3 py-3 rounded-lg transition-all',
                active
                  ? 'bg-[#b3d430]/10 text-white font-medium'
                  : 'hover:bg-gray-800/50 text-gray-300 hover:text-white'
              )}
            >
              <div className={clsx(
                "p-2 rounded-lg",
                active ? "bg-[#b3d430] text-white" : "bg-gray-800 text-[#b3d430]"
              )}>
                <Icon size={18} />
              </div>
              {!collapsed && (
                <span className="truncate transition-opacity duration-200">
                  {label}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Área do usuário */}
      <div className="border-t border-gray-800 p-4">
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

        {!collapsed && (
          <div className="mt-2 space-y-1">
            <Link
              href="/admin"
              className="flex items-center gap-3 px-3 py-2 text-sm rounded-md transition hover:bg-gray-800/50 text-gray-300 hover:text-white"
            >
              <Settings size={16} />
              <span>Configurações</span>
            </Link>
            <button className="flex items-center gap-3 w-full px-3 py-2 text-sm rounded-md transition hover:bg-gray-800/50 text-gray-300 hover:text-white">
              <LogOut size={16} />
              <span>Sair</span>
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}