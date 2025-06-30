"use client";

import PainelLeadsRaw from "./PainelLeadsRaw";

export default function AdminPage() {
  return (
    <div className="p-6 bg-white text-gray-800 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">Painel Admin - Leads</h1>
      <PainelLeadsRaw />
    </div>
  );
}
