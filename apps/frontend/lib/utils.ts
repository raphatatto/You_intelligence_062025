// lib/utils.ts
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { format, formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'

/**
 * Combina classes Tailwind CSS de forma segura e sem conflitos
 * @param inputs Classes CSS para combinar
 * @returns String com classes combinadas e otimizadas
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Formata uma data para exibição amigável
 * @param date Data a ser formatada (string, Date ou número)
 * @param formatString String de formatação (padrão: 'dd/MM/yyyy')
 * @returns Data formatada
 */
export function formatDate(
  date: string | Date | number,
  formatString: string = 'dd/MM/yyyy'
): string {
  return format(new Date(date), formatString, { locale: ptBR })
}

/**
 * Retorna a distância de tempo entre a data atual e a data fornecida
 * @param date Data a ser comparada
 * @returns String com a distância de tempo (ex: "há 2 dias")
 */
export function timeAgo(date: string | Date | number): string {
  return formatDistanceToNow(new Date(date), {
    addSuffix: true,
    locale: ptBR
  })
}

/**
 * Encurta um texto para um determinado comprimento
 * @param text Texto a ser encurtado
 * @param length Comprimento máximo (padrão: 50)
 * @returns Texto encurtado com "..." se necessário
 */
export function truncate(text: string, length: number = 50): string {
  return text.length > length ? `${text.substring(0, length)}...` : text
}

/**
 * Formata números para exibição (ex: 1000 → 1K)
 * @param num Número a ser formatado
 * @param digits Número de dígitos decimais (padrão: 1)
 * @returns String formatada
 */
export function formatNumber(num: number, digits: number = 1): string {
  const lookup = [
    { value: 1, symbol: '' },
    { value: 1e3, symbol: 'K' },
    { value: 1e6, symbol: 'M' },
    { value: 1e9, symbol: 'G' },
    { value: 1e12, symbol: 'T' },
    { value: 1e15, symbol: 'P' },
    { value: 1e18, symbol: 'E' }
  ]
  const rx = /\.0+$|(\.[0-9]*[1-9])0+$/
  const item = lookup.slice().reverse().find(item => num >= item.value)
  return item ? (num / item.value).toFixed(digits).replace(rx, '$1') + item.symbol : '0'
}

/**
 * Gera um ID único
 * @returns String com ID único
 */
export function generateId(): string {
  return Math.random().toString(36).substring(2, 9)
}

/**
 * Converte uma string para formato slug (URL amigável)
 * @param text Texto a ser convertido
 * @returns String no formato slug
 */
export function slugify(text: string): string {
  return text
    .toString()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w-]+/g, '')
    .replace(/--+/g, '-')
}

/**
 * Remove acentos de uma string
 * @param text Texto a ser processado
 * @returns Texto sem acentos
 */
export function removeAccents(text: string): string {
  return text.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
}

/**
 * Converte um objeto em query string
 * @param params Objeto com parâmetros
 * @returns String de query (ex: "param1=value1&param2=value2")
 */
export function objectToQueryString(params: Record<string, any>): string {
  return Object.keys(params)
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&')
}

/**
 * Extrai parâmetros de uma query string
 * @param queryString String de query (ex: "?param1=value1&param2=value2")
 * @returns Objeto com parâmetros
 */
export function queryStringToObject(queryString: string): Record<string, string> {
  return Object.fromEntries(new URLSearchParams(queryString))
}

/**
 * Debounce function para otimizar chamadas frequentes
 * @param func Função a ser executada
 * @param wait Tempo de espera em ms (padrão: 300)
 * @returns Função debounced
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number = 300
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

/**
 * Throttle function para limitar chamadas frequentes
 * @param func Função a ser executada
 * @param limit Tempo mínimo entre chamadas em ms (padrão: 300)
 * @returns Função throttled
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number = 300
): (...args: Parameters<T>) => void {
  let inThrottle: boolean
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}