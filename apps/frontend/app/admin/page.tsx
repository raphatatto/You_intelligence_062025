import { useEffect, useState } from 'react';
import { getLeadsRaw, enrichGeo, enrichCNPJ } from '@/services/admin';


export default function PainelLeadsRaw() {
  const [leads, setLeads] = useState([]);
  const [selecionados, setSelecionados] = useState<string[]>([]);

  useEffect(() => {
    getLeadsRaw().then(setLeads);
  }, []);

  const handleEnriquecerGeo = async () => {
    await enrichGeo(selecionados);
  };

  const handleEnriquecerCNPJ = async () => {
    await enrichCNPJ(selecionados);
  };

  return (
    <div>
      <h2>Leads Raw</h2>
      <table>
        <thead>
          <tr>
            <th></th>
            <th>ID</th>
            <th>Bairro</th>
            <th>Distribuidora</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead: any) => (
            <tr key={lead.id}>
              <td>
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
              <td>{lead.id}</td>
              <td>{lead.bairro}</td>
              <td>{lead.distribuidora}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <button onClick={handleEnriquecerGeo}>Enriquecer com Google</button>
      <button onClick={handleEnriquecerCNPJ}>Enriquecer com CNPJ</button>
    </div>
  );
}
