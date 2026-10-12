import { ElectronAPI } from '@electron-toolkit/preload'
import '../../../content/types'

declare global {
  interface Window {
    electron: ElectronAPI
    api: unknown
  }
}
