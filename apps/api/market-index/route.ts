// app/api/market-index/route.ts
import { NextResponse } from 'next/server'
// app/api/market-index/route.ts
import { getMarketIndexData, REVALIDATE_SECONDS } from ''


export const revalidate = REVALIDATE_SECONDS;

export async function GET() {
  try {
    const data = await getMarketIndexData();
    return NextResponse.json(data);
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
