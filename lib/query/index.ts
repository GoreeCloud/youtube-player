import { UseQueryOptions } from '@tanstack/react-query'
import { auth$ } from '@/states/auth'

export interface NoutubeIosEntitlement {
  status: string
  productId?: string | null
  expiresAt?: string | null
  willRenew?: boolean | null
  linkedEmail?: string | null
}

export interface NoutubeEntitlement {
  plan: string
  source: 'none' | 'stripe' | 'app_store'
  email?: string | null
  ios?: NoutubeIosEntitlement | null
}

export interface PrepareIosPurchaseResponse {
  appAccountToken: string
  email: string
  entitlement: NoutubeEntitlement
}

export interface SyncIosTransactionResponse {
  entitlement: NoutubeEntitlement
}

export interface WebAuthLinkResponse {
  token?: string | null
}

const defaultEntitlement: NoutubeEntitlement = {
  plan: 'free',
  source: 'none',
}

function getErrorMessage(payload: any, fallback?: string) {
  return payload?.error?.json?.message || payload?.message || fallback || 'Request failed'
}

// Explicitly fail closed: the imported API belongs to the upstream account
// and billing service. Never forward a GoreeCloud user's tokens or purchases.
async function callNoutubeApi<T>(
  _path: string,
  _init?: RequestInit,
  _authorization = auth$.accessToken.get(),
): Promise<T> {
  throw new Error('Legacy account, purchase and sync APIs are disabled in GoreeCloud YouTube Player.')
}

export const getMeQuery = (options?: Partial<UseQueryOptions<NoutubeEntitlement>>) => ({
  queryKey: ['me'],
  queryFn: async () => {
    if (!auth$.accessToken.get()) {
      return defaultEntitlement
    }
    return callNoutubeApi<NoutubeEntitlement>('noutube.me')
  },
  staleTime: 15 * 60 * 1000, // 15 minutes
  ...options,
})

export const fetchWebAuthLink = (accessToken: string) =>
  callNoutubeApi<WebAuthLinkResponse>('users.link', undefined, accessToken)

export const prepareIosPurchase = () =>
  callNoutubeApi<PrepareIosPurchaseResponse>('noutube.prepareIosPurchase', { method: 'POST' })

export const syncIosTransaction = (signedTransactionInfo: string) =>
  callNoutubeApi<SyncIosTransactionResponse>('noutube.syncIosTransaction', {
    method: 'POST',
    body: JSON.stringify({ signedTransactionInfo }),
  })
