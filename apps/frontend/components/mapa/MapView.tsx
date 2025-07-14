'use client'

import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api'
import { useLeads } from '@/components/hooks/useLeads'
import { Lead } from '@/app/types/lead'

const containerStyle = {
  width: '100%',
  height: '600px',
}

const center = {
  lat: -23.55,
  lng: -46.63,
}

export default function MapaGoogle() {
  const { leads } = useLeads()

  return (
    <LoadScript googleMapsApiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY!}>
      <GoogleMap
        mapContainerStyle={containerStyle}
        center={center}
        zoom={5.5}
      >
        {leads
          .filter((l) => !isNaN(l.latitude) && !isNaN(l.longitude))
          .map((lead: Lead) => (
            <Marker
              key={lead.id}
              position={{ lat: lead.latitude, lng: lead.longitude }}
              title={`DIC: ${lead.dicMed?.toFixed(2)} | ${lead.segmento}`}
            />
          ))}
      </GoogleMap>
    </LoadScript>
  )
}
