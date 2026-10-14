const SUPPORTED_HOSTS = new Set(['youtube.com', 'www.youtube.com', 'm.youtube.com', 'music.youtube.com', 'youtu.be'])
const APP_LINK_SCHEME = /^(?:noutube|goreecloud-youtube-player):\/\//i

// Translate only a scheme at the start. Arbitrary or malformed custom links
// must never bypass the same YouTube-origin validation as normal HTTPS links.
function parseSupportedUrl(value: string): URL | null {
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

/* youtu.be only redirects to the watch page. Nothing that decides where a link
 * belongs recognises it as a video until it has been spelled out. */
export function expandShortUrl(value: string) {
  try {
    const url = new URL(value)
    const id = url.host === 'youtu.be' ? url.pathname.split('/').filter(Boolean)[0] : ''
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
