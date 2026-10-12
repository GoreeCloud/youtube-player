import { View } from 'react-native'
import { NouText } from '@/components/NouText'
import { sectionLabelCls, surfaceCls } from '@/components/modal/SettingsTree'

export const SyncSection = () => (
  <View>
    <NouText className={sectionLabelCls}>GoreeCloud Sync</NouText>
    <View className={surfaceCls}>
      <View className="gap-3 px-5 py-5">
        <NouText className="text-lg font-semibold">Cloud sync is not connected</NouText>
        <NouText className="text-sm leading-6 text-zinc-600 dark:text-zinc-400">
          Bookmarks and preferences remain available locally. The extension will not sign in
          to NouTube or send account data to its legacy servers.
        </NouText>
        <NouText className="text-sm leading-6 text-zinc-600 dark:text-zinc-400">
          GoreeCloud Identity and Sync require a separately reviewed, tested integration.
        </NouText>
      </View>
    </View>
  </View>
)
