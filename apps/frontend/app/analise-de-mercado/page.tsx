// app/analise-de-mercado/page.tsx
import Client from './Client'
import { getMarketIndexData } from '@/lib/market'

export const revalidate = 60 * 60 * 6

export default async function Page() {
  const data = await getMarketIndexData()
  return <Client data={data} />
}
