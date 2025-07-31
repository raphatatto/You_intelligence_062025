// components/ui/charts.tsx
'use client'

import React from 'react'
import {
  LineChart as RechartsLineChart,
  Line,
  BarChart as RechartsBarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  AreaChart as RechartsAreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts'

import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
  ZoomableGroup
} from 'react-simple-maps'
import { scaleLinear } from 'd3-scale'

// Tipos para os gráficos
interface ChartProps {
  data: any[]
  color?: string
  width?: string | number
  height?: string | number
}

interface MapChartProps {
  data: {
    id: string
    value: number
    name: string
    color?: string
    coordinates?: [number, number]
  }[]
  region?: 'world' | 'brazil'
  width?: string | number
  height?: string | number
  maxZoom?: number
}

interface BarChartProps extends ChartProps {
  colors?: string[]
}

interface PieChartProps extends ChartProps {
  colors?: string[]
  dataKey?: string
  nameKey?: string
}
export const CustomMapChart = ({
  data = [],
  region = 'world',
  width = '100%',
  height = 400,
  maxZoom = 5
}: MapChartProps) => {
  // Configurações de projeção por região
  const projectionConfig = {
    world: {
      scale: 150,
      center: [10, 20] as [number, number]
    },
    brazil: {
      scale: 800,
      center: [-54, -15] as [number, number]
    }
  }
   const colorScale = scaleLinear<string>()
    .domain([0, Math.max(...data.map(d => d.value))])
    .range(['#ffedea', '#ff5233'])

  return (
    <div style={{ width, height }} className="rounded-lg overflow-hidden bg-gray-800">
      <ComposableMap
        projection="geoMercator"
        projectionConfig={projectionConfig[region]}
      >
        <ZoomableGroup maxZoom={maxZoom}>
          <Geographies geography={getGeoJson(region)}>
            {({ geographies }) =>
              geographies.map((geo) => (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill="#374151"
                  stroke="#6b7280"
                  strokeWidth={0.5}
                  style={{
                    default: { outline: 'none' },
                    hover: { fill: '#4b5563', outline: 'none' },
                    pressed: { fill: '#6b7280', outline: 'none' }
                  }}
                />
              ))
            }
          </Geographies>
          
          {data.map(({ id, value, name, color, coordinates }) => {
            const coords = coordinates || getCoordinatesById(id, region)
            if (!coords) return null
            
            return (
              <Marker key={id} coordinates={coords}>
                <circle
                  r={Math.sqrt(value) * 0.8}
                  fill={color || colorScale(value)}
                  fillOpacity={0.6}
                  stroke={color || colorScale(value)}
                  strokeWidth={1}
                  className="transition-all duration-300 hover:r-6"
                />
                <text
                  textAnchor="middle"
                  y={-Math.sqrt(value) * 0.8 - 5}
                  fill="#fff"
                  fontSize={12}
                  className="font-medium"
                >
                  {name}
                </text>
                <text
                  textAnchor="middle"
                  y={-Math.sqrt(value) * 0.8 + 15}
                  fill="#d1d5db"
                  fontSize={10}
                >
                  {value.toLocaleString()}
                </text>
              </Marker>
            )
          })}
        </ZoomableGroup>
      </ComposableMap>
    </div>
  )
}
function getGeoJson(region: string) {
  // Você precisará importar os arquivos TopoJSON apropriados
  // Exemplo: import brazilGeoJson from './brazil-geo.json'
  return region === 'brazil' 
    ? require('./geojson/brazil.json') 
    : require('./geojson/world.json')
}

function getCoordinatesById(id: string, region: string): [number, number] | null {
  // Coordenadas aproximadas para regiões do Brasil
  const brazilCoordinates: Record<string, [number, number]> = {
    'BR-SE': [-45, -22],  // Sudeste
    'BR-S':  [-53, -27],  // Sul
    'BR-NE': [-42, -8],   // Nordeste
    'BR-N':  [-60, -5],   // Norte
    'BR-CO': [-55, -15]   // Centro-Oeste
  }

  // Coordenadas aproximadas para países (exemplos)
  const worldCoordinates: Record<string, [number, number]> = {
    'BR': [-55, -10],     // Brasil
    'US': [-100, 40],     // Estados Unidos
    'CN': [105, 35],      // China
    'IN': [78, 22],       // Índia
    'DE': [10, 51]        // Alemanha
  }

  return region === 'brazil' 
    ? brazilCoordinates[id] 
    : worldCoordinates[id] || null
}
// Componente LineChart personalizado
export const CustomLineChart = ({ data, color = '#3b82f6', width = '100%', height = 300 }: ChartProps) => {
  return (
    <ResponsiveContainer width={width} height={height}>
      <RechartsLineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey="name" stroke="#9ca3af" />
        <YAxis stroke="#9ca3af" />
        <Tooltip />
        <Line 
          type="monotone" 
          dataKey="value" 
          stroke={color} 
          strokeWidth={2} 
          dot={{ r: 4 }} 
          activeDot={{ r: 6 }} 
        />
      </RechartsLineChart>
    </ResponsiveContainer>
  )
}

// Componente BarChart personalizado
export const CustomBarChart = ({ data, colors = ['#3b82f6'], width = '100%', height = 300 }: BarChartProps) => {
  return (
    <ResponsiveContainer width={width} height={height}>
      <RechartsBarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey="name" stroke="#9ca3af" />
        <YAxis stroke="#9ca3af" />
        <Tooltip />
        <Legend />
        {data[0] && Object.keys(data[0])
          .filter(key => key !== 'name')
          .map((key, index) => (
            <Bar 
              key={key}
              dataKey={key}
              fill={colors[index % colors.length]}
              radius={[4, 4, 0, 0]}
            />
          ))}
      </RechartsBarChart>
    </ResponsiveContainer>
  )
}

// Componente PieChart personalizado
export const CustomPieChart = ({ 
  data, 
  colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
  width = '100%',
  height = 300,
  dataKey = 'value',
  nameKey = 'name'
}: PieChartProps) => {
  return (
    <ResponsiveContainer width={width} height={height}>
      <RechartsPieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          outerRadius={80}
          fill="#8884d8"
          dataKey={dataKey}
          nameKey={nameKey}
          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </RechartsPieChart>
    </ResponsiveContainer>
  )
}

// Componente AreaChart personalizado
export const CustomAreaChart = ({ data, color = '#3b82f6', width = '100%', height = 300 }: ChartProps) => {
  return (
    <ResponsiveContainer width={width} height={height}>
      <RechartsAreaChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey="name" stroke="#9ca3af" />
        <YAxis stroke="#9ca3af" />
        <Tooltip />
        <Area 
          type="monotone" 
          dataKey="value" 
          stroke={color} 
          fill={color}
          fillOpacity={0.2}
          strokeWidth={2}
        />
      </RechartsAreaChart>
    </ResponsiveContainer>
  )
}

