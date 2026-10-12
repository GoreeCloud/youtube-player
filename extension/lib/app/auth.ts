import { auth$ } from '@/states/auth'

export type LegacySession = {
  user: { id: string; email?: string }
  access_token: string
}

const DISABLED_MESSAGE = 'GoreeCloud account sync has not been configured or approved.'

export async function fetchPlan(_accessToken: string): Promise<string> {
  return 'free'
}

export async function applySession(_session: LegacySession | null): Promise<void> {
  auth$.assign({ loaded: true, userId: undefined, userEmail: undefined, user: undefined, accessToken: '', plan: 'free' })
}

export async function restoreSession(): Promise<LegacySession | null> {
  await applySession(null)
  return null
}

export function watchSession(): void {
  // Intentionally no upstream auth subscription.
}

export async function signIn(): Promise<LegacySession | null> {
  throw new Error(DISABLED_MESSAGE)
}

export async function signOut(): Promise<void> {
  await applySession(null)
}
