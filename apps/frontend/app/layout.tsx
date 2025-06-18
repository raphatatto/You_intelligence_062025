// app/layout.tsx
import './globals.css';
import Sidebar from '@/components/ui/Sidebar';

export const metadata = { title: 'You.On Front' };

export default function RootLayout({children}: {children: React.ReactNode}) {
  return (
    <html lang="pt-BR">
      <body className="flex">
        <Sidebar />
        <main className="ml-56 flex-1 min-h-screen bg-black p-6 ">
          {children}
        </main>
      </body>
    </html>
  );
}
