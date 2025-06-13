"use client"
import Link from 'next/link';
import {usePathname} from 'next/navigation';
import {clsx} from 'clsx';

const links = [
  {href: '/',         label: 'Dashboard'},
  {href: '/mapa',     label: 'Mapa'},
  {href: '/leads',    label: 'Leads'},
  {href: '/dados',    label: 'Dados'},
  {href: '/noticias', label: 'Notícias'},
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 w-56 bg-gray-900 text-white">
      <div className="flex items-center h-16 px-4 text-xl font-bold">
        You.On
      </div>

      <nav className="mt-4 space-y-1">
        {links.map(({href, label}) => (
          <Link
            key={href}
            href={href}
            className={clsx(
              'block px-4 py-2 hover:bg-gray-800 rounded-md',
              pathname === href && 'bg-gray-800 font-semibold'
            )}
          >
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
