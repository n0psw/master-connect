import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Утилита для объединения классов Tailwind CSS
 * Использует clsx для условной логики и twMerge для разрешения конфликтов
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
