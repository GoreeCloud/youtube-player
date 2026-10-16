import { history$ } from '@/states/history'
import { normalizeSupportedUrl } from '@/lib/supported-url'

// Anything shorter is not worth resuming, and a video watched to (nearly) the
// end should start over instead.
const MIN_RESUME_SECONDS = 5
const END_MARGIN_SECONDS = 10

// lib/page's getVideoId would drag states/ui, and with it a states/tabs import
// cycle, into this module.
export function getVideoIdFromUrl(url: string) {
  const safeUrl = normalizeSupportedUrl(url)
  if (!safeUrl) return ''
  const parsed = new URL(safeUrl)
  // The same query parameter on a different page is not proof of a playing video.
  return parsed.pathname === '/watch' ? parsed.searchParams.get('v') || '' : ''
}

export function withResumeTime(url: string, current: number) {
  const seconds = Math.floor(current)
  // Corrupted playback ticks must not create t=NaNs, t=Infinitys or negative seeks.
  if (!Number.isSafeInteger(seconds) || seconds < 0) return url
  try {
    const next = new URL(url)
    next.searchParams.set('t', `${seconds}s`)
    return next.href
  } catch {
    return url
  }
}

export function withoutResumeTime(url: string) {
  try {
    const next = new URL(url)
    next.searchParams.delete('t')
    return next.href
  } catch {
    return url
  }
}

/** The last played video with its position baked into the url, when resuming it makes sense. */
export function getLastPlaying() {
  const last = history$.bookmarks[0].get()
  const safeUrl = normalizeSupportedUrl(last?.url || '')
  if (!last?.videoId || !safeUrl || getVideoIdFromUrl(safeUrl) !== last.videoId) {
    return undefined
  }
  const current = Number(last.current)
  const duration = Number(last.duration) || 0
  // Even finite persisted values can be too large to encode as a valid seek.
  if (!Number.isSafeInteger(Math.floor(current)) || current < MIN_RESUME_SECONDS) {
    return undefined
  }
  if (duration > 0 && current > duration - END_MARGIN_SECONDS) {
    return undefined
  }
  return { videoId: last.videoId, url: withResumeTime(safeUrl, current), current }
}
