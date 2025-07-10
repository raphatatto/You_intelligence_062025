export async function geocodificarCEP(cep: string): Promise<{ lat: number; lng: number } | null> {
  try {
    const cepLimpo = cep.replace(/\D/g, '') // 🔥 remove traços, espaços, etc.

    const res = await fetch(`/api/geocode?cep=${cepLimpo}`)
    const data = await res.json()

    if (!data || data.length === 0) return null

    return {
      lat: parseFloat(data[0].lat),
      lng: parseFloat(data[0].lon),
    }
  } catch (err) {
    console.error('Erro ao geocodificar CEP:', cep, err)
    return null
  }
}
