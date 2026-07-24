/**
 * Format numbers with commas (e.g. 12345 -> 12,345)
 */
export function formatNumber(num) {
  if (num === undefined || num === null) return '0'
  return new Intl.NumberFormat().format(num)
}

/**
 * Format time in milliseconds to human readable format (e.g. 12.34ms or 1.25s)
 */
export function formatTime(ms) {
  if (ms === undefined || ms === null) return '0ms'
  if (ms >= 1000) {
    return `${(ms / 1000).toFixed(2)}s`
  }
  return `${ms.toFixed(1)}ms`
}

/**
 * Format date string to locale relative time or short date
 */
export function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

/**
 * Capitalize string (e.g. naive_chunker -> Naive Chunker)
 */
export function formatTechniqueName(name) {
  if (!name) return ''
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
