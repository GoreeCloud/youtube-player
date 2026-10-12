import { createClient } from '@supabase/supabase-js'

// The extension never restores upstream account sessions or contacts the
// former NouTube Supabase project. Kept as a type-compatible migration seam.
export const supabase = createClient('https://goreecloud-sync-unconfigured.invalid', 'not-configured', {
  auth: {
    persistSession: false,
    autoRefreshToken: false,
    detectSessionInUrl: false,
    storageKey: 'goreecloud-youtube-player-extension-disabled-sync',
  },
})
