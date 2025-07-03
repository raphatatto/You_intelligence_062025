import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const cep = String(req.query.cep || '').replace(/\D/g, '') // garante só números


  if (!cep || cep.length < 5) {
    return res.status(400).json({ error: 'CEP inválido' })
  }

  const url = `https://nominatim.openstreetmap.org/search?format=json&country=Brazil&postalcode=${cep}&limit=1`

  try {
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'You.On Frontend Dev',
      },
    })

    const data = await response.json()
    return res.status(200).json(data)
  } catch (err) {
    console.error('Erro ao buscar no Nominatim:', err)
    return res.status(500).json({ error: 'Erro ao geocodificar o CEP' })
  }
}
