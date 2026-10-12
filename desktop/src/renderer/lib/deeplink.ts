import { openSharedUrl } from '@/lib/page'
import { isSupportedUrl } from '@/lib/supported-url'
import '../../types'

export function handleDeeplink(link: string): void {
  // Never parse or navigate unchecked OS/desktop IPC input. The same
  // allowlist already governs clipboard and other shared destinations.
  if (!isSupportedUrl(link)) return
  openSharedUrl(link)
}

window.noutubeDeeplink = handleDeeplink
