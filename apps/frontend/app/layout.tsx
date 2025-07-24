// app/layout.tsx
import './globals.css';

import { SidebarProvider } from '@/contexts/SidebarContext'
import Layout from '@/components/layout/Layout'

export const metadata = { title: 'You.On Front' };

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body>
        <SidebarProvider>
          <Layout>
            {children}
          </Layout>
        </SidebarProvider>
      </body>
    </html>
  );
}
