export async function getLeadsRaw() {
  const res = await fetch('/v1/admin/leads/raw');
  return await res.json();
}

export async function enrichGeo(leadIds: string[]) {
  const res = await fetch('/v1/admin/enrich/geo', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lead_ids: leadIds }),
  });
  return await res.json();
}

export async function enrichCNPJ(leadIds: string[]) {
  const res = await fetch('/v1/admin/enrich/cnpj', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lead_ids: leadIds }),
  });
  return await res.json();
}
