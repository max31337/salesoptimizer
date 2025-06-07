interface ProfilePictureCache {
  url: string
  timestamp: number
  lastModified?: string
}

const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes in milliseconds
const CACHE_KEY_PREFIX = 'profile_picture_cache_'

export class ProfilePictureCacheManager {
  /**
   * Get cached profile picture URL or return fresh URL if cache is invalid
   */
  static getCachedProfilePictureUrl(
    userId: string, 
    profilePictureUrl?: string | null,
    forceRefresh = false
  ): string | undefined {
    if (!profilePictureUrl) {
      return undefined
    }

    // If it's a full URL, handle it appropriately
    if (profilePictureUrl.startsWith('http')) {
      return this.handleExternalUrl(userId, profilePictureUrl, forceRefresh)
    }

    // Handle relative URLs (internal API)
    return this.handleInternalUrl(userId, profilePictureUrl, forceRefresh)
  }

  private static handleExternalUrl(
    userId: string,
    profilePictureUrl: string,
    forceRefresh: boolean
  ): string {
    if (forceRefresh) {
      return `${profilePictureUrl}?t=${Date.now()}`
    }

    const cached = this.getCacheEntry(userId)
    if (cached && this.isCacheValid(cached) && cached.url === profilePictureUrl) {
      return profilePictureUrl
    }

    // Cache the URL
    this.setCacheEntry(userId, {
      url: profilePictureUrl,
      timestamp: Date.now()
    })

    return profilePictureUrl
  }

  private static handleInternalUrl(
    userId: string,
    profilePictureUrl: string,
    forceRefresh: boolean
  ): string {
    const fullUrl = `${process.env.NEXT_PUBLIC_API_URL}${profilePictureUrl}`
    
    if (forceRefresh) {
      const cacheBustedUrl = `${fullUrl}?t=${Date.now()}`
      this.setCacheEntry(userId, {
        url: fullUrl,
        timestamp: Date.now()
      })
      return cacheBustedUrl
    }

    const cached = this.getCacheEntry(userId)
    if (cached && this.isCacheValid(cached) && cached.url === fullUrl) {
      return fullUrl
    }

    // Cache the URL and return it
    this.setCacheEntry(userId, {
      url: fullUrl,
      timestamp: Date.now()
    })

    return fullUrl
  }

  /**
   * Invalidate cache for a specific user (call this when profile picture is updated)
   */
  static invalidateCache(userId: string): void {
    try {
      localStorage.removeItem(CACHE_KEY_PREFIX + userId)
    } catch (error) {
      // Silently handle localStorage errors
      console.warn('Failed to invalidate profile picture cache:', error)
    }
  }

  /**
   * Clear all profile picture caches
   */
  static clearAllCaches(): void {
    try {
      const keysToRemove: string[] = []
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (key && key.startsWith(CACHE_KEY_PREFIX)) {
          keysToRemove.push(key)
        }
      }
      keysToRemove.forEach(key => localStorage.removeItem(key))
    } catch (error) {
      // Silently handle localStorage errors
      console.warn('Failed to clear profile picture caches:', error)
    }
  }

  private static getCacheEntry(userId: string): ProfilePictureCache | null {
    try {
      const cached = localStorage.getItem(CACHE_KEY_PREFIX + userId)
      if (cached) {
        return JSON.parse(cached)
      }
    } catch (error) {
      // Invalid JSON or localStorage error
      this.invalidateCache(userId)
    }
    return null
  }

  private static setCacheEntry(userId: string, cache: ProfilePictureCache): void {
    try {
      localStorage.setItem(CACHE_KEY_PREFIX + userId, JSON.stringify(cache))
    } catch (error) {
      // Silently handle localStorage errors (e.g., quota exceeded)
      console.warn('Failed to cache profile picture:', error)
    }
  }

  private static isCacheValid(cache: ProfilePictureCache): boolean {
    return (Date.now() - cache.timestamp) < CACHE_DURATION
  }

  /**
   * Get a cache-busted URL for immediate updates (when user uploads new picture)
   */
  static getFreshUrl(userId: string, profilePictureUrl: string): string {
    return this.getCachedProfilePictureUrl(userId, profilePictureUrl, true) || profilePictureUrl
  }
}
