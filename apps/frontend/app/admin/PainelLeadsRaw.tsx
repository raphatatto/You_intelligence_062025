"use client";

import { useEffect, useState } from "react";
import { getLeadsRaw, enrichGeo, enrichCNPJ } from "@/services/admin";

export default function PainelLeadsRaw() {
  const [leads, setLeads] = useState([]);
  const [selecionados, setSelecionados] = useState<string[]>([]);

  useEffect(() => {
    getLeadsRaw().then(setLeads);
  }, []);

  const handleEnriquecerGeo = async () => {
    if (selecionados.length === 0) return alert("Selecione pelo menos 1 lead");
    await enrichGeo(selecionados);
    alert("Enriquecimento com Google iniciado.");
  };

  const handleEnriquecerCNPJ = async () => {
    if (selecionados.length === 0) return alert("Selecione pelo menos 1 lead");
    await enrichCNPJ(selecionados);
    alert("Enriquecimento com CNPJ iniciado.");
  };

  return (
    <div className="bg-white shadow rounded-xl p-6 text-gray-800">
      <h2 className="text-xl font-semibold mb-4">Leads com status RAW</h2>

      <table className="w-full table-auto border text-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="p-2 border">✓</th>
            <th className="p-2 border">ID</th>
            <th className="p-2 border">Bairro</th>
            <th className="p-2 border">Distribuidora</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead: any) => (
            <tr key={lead.id} className="even:bg-gray-50">
              <td className="p-2 border text-center">
                <input
                  type="checkbox"
                  onChange={(e) => {
                    const checked = e.target.checked;
                    setSelecionados((prev) =>
                      checked ? [...prev, lead.id] : prev.filter((id) => id !== lead.id)
                    );
                  }}
                />
              </td>
              <td className="p-2 border">{lead.id}</td>
              <td className="p-2 border">{lead.bairro}</td>
              <td className="p-2 border">{lead.distribuidora}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="mt-6 flex gap-4">
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          onClick={handleEnriquecerGeo}
        >
          Enriquecer com Google
        </button>
        <button
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          onClick={handleEnriquecerCNPJ}
        >
          Enriquecer com CNPJ
        </button>
      </div>
    </div>
  );
}
