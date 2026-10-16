import { ui$, updateUrl } from '@/states/ui'
import { settings$ } from '@/states/settings'
import { debounce } from 'es-toolkit'
import { expandShortUrl, getSupportedVideoId, isSupportedUrl, normalizeSupportedUrl } from './supported-url'
import { removeTrackingParams } from './tracking-url'

export { getPageType } from './page-type'

export function fixPageTitle(title: string) {
  return title.replace(/ - YouTube( Music)*$/, '')
}

export function fixSharingUrl(v: string) {
  return removeTrackingParams(v)
}

export function getVideoThumbnail(id: string) {
  return `https://img.youtube.com/vi/${id}/hqdefault.jpg`
}

/** Used by the playing queue and thumbnail preview; never trust a bare v= query. */
export function getVideoId(url: string) {
  return getSupportedVideoId(url)
}

export function getThumbnail(url: string) {
  const id = getVideoId(url)
  return id ? getVideoThumbnail(id) : undefined
}

export function openSharedUrl(url: string) {
  try {
    const fixed = fixSharingUrl(url)
    if (isSupportedUrl(fixed)) {
      updateUrl(expandShortUrl(normalizeSupportedUrl(fixed)))
    }
  } catch (error) {
    console.error(error)
  }
}

export const setPageUrl = debounce(async function (url: string) {
  if (!url) {
    return
  }
  ui$.pageUrl.set(url)
  const { host } = new URL(url)
  settings$.home.set(host === 'music.youtube.com' ? 'yt-music' : 'yt')
}, 300)
