export async function getStatusImportacoes() {
  const res = await fetch('/v1/admin/importacoes');
  return await res.json();
}

export async function dispararImportacao(payload: {
  distribuidora: string;
  prefixo: string;
  ano: number;
  url: string;
  camadas: string[];
}) {
  const res = await fetch('/v1/admin/importacoes/rodar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return await res.json();
}
