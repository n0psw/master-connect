import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/ru'

export const DEFAULT_TZ = 'Etc/GMT-5' // фиксированный UTC+5 по требованию

dayjs.extend(utc)
dayjs.extend(timezone)
dayjs.extend(relativeTime)
dayjs.locale('ru')

export const mapTimezone = (tz?: string) => {
  if (!tz) return DEFAULT_TZ
  const normalized = tz.trim()
  if (normalized.toLowerCase() === 'asia/almaty') return DEFAULT_TZ
  return normalized
}

export const getClientTimezone = (userTz?: string) => {
  const browserTz = Intl.DateTimeFormat().resolvedOptions().timeZone
  return mapTimezone(userTz || browserTz || DEFAULT_TZ)
}

export const dayjsTz = (value?: dayjs.ConfigType, tz?: string) => {
  const targetTz = mapTimezone(tz)
  return dayjs(value).tz(targetTz)
}

export const formatDateTime = (
  value?: dayjs.ConfigType,
  tz?: string,
  pattern = 'DD.MM.YYYY HH:mm'
) => dayjsTz(value, tz).format(pattern)

export const formatFromNow = (value?: dayjs.ConfigType, tz?: string) =>
  dayjsTz(value, tz).fromNow()

export default dayjs

