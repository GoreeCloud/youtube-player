import { View } from 'react-native'
import { NouText } from '../NouText'

export const SettingsModalTabSync = () => (
  <View className="rounded-[24px] bg-white px-5 py-6 dark:bg-zinc-900">
    <NouText className="text-lg font-semibold">GoreeCloud Sync is not connected</NouText>
    <NouText className="mt-3 text-sm leading-6 text-zinc-600 dark:text-zinc-400">
      Your local bookmarks, history and settings remain available on this device. This development
      build does not sign in to NouTube, send data to its servers or offer upstream subscriptions.
    </NouText>
    <NouText className="mt-3 text-sm leading-6 text-zinc-600 dark:text-zinc-400">
      Secure GoreeCloud Identity and Sync support will become available only after integration and
      migration testing are complete.
    </NouText>
  </View>
)
