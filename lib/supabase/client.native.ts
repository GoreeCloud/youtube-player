import { createClient } from '@supabase/supabase-js'

// Legacy account migration is pending. Never restore credentials from
// NouTube's persisted storage or connect to its historical Supabase project.
export const supabase = createClient('https://goreecloud-sync-unconfigured.invalid', 'not-configured', {
  auth: {
    persistSession: false,
    autoRefreshToken: false,
    detectSessionInUrl: false,
    storageKey: 'goreecloud-youtube-player-disabled-sync',
  },
})
