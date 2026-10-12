import { supabase } from './client'

const LEGACY_SERVICES_UNAVAILABLE = 'Account services are unavailable until GoreeCloud Identity and Sync are verified.'

// Local sign-out cannot contact an inherited account provider.
export const signOut = () => supabase.auth.signOut({ scope: 'local' })

export const openDeleteAccount = async (_accessToken: string): Promise<void> => {
  throw new Error(LEGACY_SERVICES_UNAVAILABLE)
}

// Do not redeem NouTube-authored deep-link tokens in GoreeCloud packages.
export const onReceiveAuthUrl = (_url: string): void => {
  return
}
