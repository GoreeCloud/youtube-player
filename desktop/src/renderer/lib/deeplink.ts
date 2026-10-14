import { openSharedUrl } from '@/lib/page'
import { isSupportedUrl } from '@/lib/supported-url'
import '../../types'

export function handleDeeplink(link: string): void {
  if (!isSupportedUrl(link)) {
    return
  }
  // console.log('on deeplink', link)
  openSharedUrl(link)
}

window.noutubeDeeplink = handleDeeplink
