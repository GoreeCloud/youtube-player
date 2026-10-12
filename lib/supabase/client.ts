import { createClient } from '@supabase/supabase-js'

// Transition-only type-compatible client. Deliberately never targets an upstream
// host, restores historical credentials, or refreshes sessions.
// Replace only after GoreeCloud Identity/Sync contracts and tests are approved.
export const supabase = createClient('https://goreecloud-sync-unconfigured.invalid', 'not-configured', {
  auth: {
    persistSession: false,
    autoRefreshToken: false,
    detectSessionInUrl: false,
    storageKey: 'goreecloud-youtube-player-disabled-sync',
  },
})
