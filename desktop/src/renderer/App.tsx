import contentJs from '../../../assets/scripts/main.bjs?raw'
import { MainPage } from '../../../components/page/MainPage'
import { Toaster } from 'react-hot-toast'
import { useObserveEffect } from '@legendapp/state/react'
import { useEffect } from 'react'
import { initUiChannel } from './ipc/ui'
import { handleShortcuts } from './lib/shortcuts'

function App(): React.JSX.Element {
  useEffect(() => {
    initUiChannel()
    window.addEventListener('keyup', handleShortcuts)
    return () => window.removeEventListener('keyup', handleShortcuts)
  }, [])

  return (
    <>
      <MainPage contentJs={contentJs} />
      <Toaster position="bottom-right" />
    </>
  )
}
export default App
