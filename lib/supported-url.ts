const SUPPORTED_HOSTS = new Set(['youtube.com', 'www.youtube.com', 'm.youtube.com', 'music.youtube.com', 'youtu.be'])
const APP_LINK_SCHEME = /^(?:noutube|goreecloud-youtube-player):\/\//i

// Translate only a scheme at the start. Arbitrary or malformed custom links
// must never bypass the same YouTube-origin validation as normal HTTPS links.
function parseSupportedUrl(value: string): URL | null {
  // URL() silently strips some ASCII control characters; reject them first.
  if (!value || /[\u0000-\u001f\u007f]/.test(value)) return null
  try {
    const url = new URL(value.replace(APP_LINK_SCHEME, 'https://'))
    if (url.protocol !== 'https:' || !SUPPORTED_HOSTS.has(url.hostname) ||
        url.port || url.username || url.password) {
      return null
    }
    return url
  } catch {
    return null
  }
}

export function isSupportedUrl(value: string) {
  return parseSupportedUrl(value) !== null
}

export function normalizeSupportedUrl(value: string) {
  return parseSupportedUrl(value)?.href ?? ''
}

/** Extract a video ID only from known YouTube video routes on trusted origins.
 * A stray v= on search, channel or non-YouTube pages is not a video. */
export function getSupportedVideoId(value: string): string {
  const url = parseSupportedUrl(value)
  if (!url) return ''
  const segments = url.pathname.split('/').filter(Boolean)
  let id = ''
  if (url.hostname === 'youtu.be') {
    id = segments.length === 1 ? segments[0] : ''
  } else if (url.pathname === '/watch') {
    id = url.searchParams.get('v') || ''
  } else if (segments.length === 2 && ['shorts', 'live', 'embed'].includes(segments[0])) {
    id = segments[1]
  }
  return /^[A-Za-z0-9_-]{1,64}$/.test(id) ? id : ''
}

/* youtu.be only redirects to the watch page. Nothing that decides where a link
 * belongs recognises it as a video until it has been spelled out. */
export function expandShortUrl(value: string) {
  try {
    const url = new URL(value)
    const id = url.host === 'youtu.be' ? getSupportedVideoId(value) : ''
    if (!id) {
      return value
    }
    const watch = new URL('https://www.youtube.com/watch')
    watch.searchParams.set('v', id)
    // The start time and the playlist ride along on the share link.
    url.searchParams.forEach((param, key) => {
      if (key !== 'v') {
        watch.searchParams.set(key, param)
      }
    })
    return watch.href
  } catch {
    return value
  }
}
