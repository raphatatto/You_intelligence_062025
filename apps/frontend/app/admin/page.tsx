'use client';

import AdminDashboard from './AdminDashboard';

export default function AdminPage() {
  return (
    <main className="p-6 space-y-12">
      <header className="text-center">
        <h1 className="text-4xl font-extrabold text-white">📊 Painel Geral de Administração</h1>
        <p className="text-zinc-400 mt-2">Visualize o status do banco, importações e enriquecimento em tempo real.</p>
      </header>

      <AdminDashboard />
    </main>
  );
}
