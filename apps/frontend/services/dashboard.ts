export async function getResumoDashboard() {
  const res = await fetch('/v1/admin/dashboard/resumo');
  return await res.json();
}
