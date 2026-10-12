const SUPPORTED_HOSTS = new Set(['youtube.com', 'www.youtube.com', 'm.youtube.com', 'music.youtube.com', 'youtu.be'])
const LEGACY_LINK_PREFIX = 'noutube://'

/** Only convert the exact legacy link prefix, never a substring of an unrelated URL. */
export function normalizeSupportedUrl(value: string) {
  return value.startsWith(LEGACY_LINK_PREFIX)
    ? `https://${value.slice(LEGACY_LINK_PREFIX.length)}`
    : value
}

/** Untrusted links may originate in the clipboard, OS share sheets or desktop IPC. */
export function isSupportedUrl(value: string) {
  if (!value || /[\u0000-\u001f\u007f]/.test(value)) {
    return false
  }
  if (value.startsWith('noutube:') && !value.startsWith(LEGACY_LINK_PREFIX)) {
    return false
  }
  try {
    const url = new URL(normalizeSupportedUrl(value))
    return (
      (url.protocol === 'http:' || url.protocol === 'https:') &&
      SUPPORTED_HOSTS.has(url.hostname) &&
      !url.username &&
      !url.password &&
      !url.port
    )
  } catch {
    return false
  }
}

/**
 * Resolve video IDs across regular watch pages, Shorts, live streams,
 * YouTube embed pages, and youtu.be shares without trusting a lookalike host.
 */
export function getSupportedVideoId(value: string): string | undefined {
  if (!isSupportedUrl(value)) return undefined
  const url = new URL(normalizeSupportedUrl(value))
  const segments = url.pathname.split('/').filter(Boolean)
  let id: string | null | undefined

  if (url.hostname === 'youtu.be') {
    id = segments.length === 1 ? segments[0] : undefined
  } else if (segments.length === 1 && segments[0] === 'watch') {
    id = url.searchParams.get('v')
  } else if (
    segments.length === 2 &&
    ['shorts', 'live', 'embed'].includes(segments[0])
  ) {
    id = segments[1]
  }

  return id && /^[A-Za-z0-9_-]{1,64}$/.test(id) ? id : undefined
}

/** Find the first trusted shared link among arbitrary OS process arguments. */
export function findSupportedLaunchUrl(args: readonly string[]): string | undefined {
  return args.find(isSupportedUrl)
}

/** Only ordinary web destinations may leave the sandboxed player through the OS. */
export function isSafeExternalUrl(value: string) {
  if (!value || /[\u0000-\u001f\u007f]/.test(value)) {
    return false
  }
  try {
    const url = new URL(value)
    return (
      (url.protocol === 'http:' || url.protocol === 'https:') &&
      Boolean(url.hostname) &&
      !url.username &&
      !url.password
    )
  } catch {
    return false
  }
}

/* youtu.be only redirects to the watch page. Nothing that decides where a link
 * belongs recognises it as a video until it has been spelled out. */
export function expandShortUrl(value: string) {
  // Share-link canonicalization must obey the same host and path rules as
  // thumbnail extraction; never silently truncate an ambiguous short path.
  if (!isSupportedUrl(value)) return value
  try {
    const url = new URL(normalizeSupportedUrl(value))
    if (url.hostname !== 'youtu.be') return value
    const id = getSupportedVideoId(value)
    if (!id) return value
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
