/**
 * Get a cookie value by name
 */
export function getCookie(name: string): string | null {
  if (typeof document === 'undefined') {
    return null // SSR safety
  }

  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() || null
  }
  
  return null
}

/**
 * Set a cookie
 */
export function setCookie(name: string, value: string, days: number = 7): void {
  if (typeof document === 'undefined') {
    return // SSR safety
  }

  const expires = new Date()
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000)
  
  document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;secure;samesite=strict`
}

/**
 * Delete a cookie
 */
export function deleteCookie(name: string): void {
  if (typeof document === 'undefined') {
    return // SSR safety
  }

  document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`
}
