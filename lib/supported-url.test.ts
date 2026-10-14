import { describe, expect, it } from 'bun:test'
import { isSupportedUrl, normalizeSupportedUrl } from './supported-url'

describe('YouTube deep link safety', () => {
  it('accepts HTTPS and converts validated legacy and GoreeCloud custom links', () => {
    expect(isSupportedUrl('https://www.youtube.com/watch?v=abc')).toBe(true)
    expect(normalizeSupportedUrl('noutube://www.youtube.com/watch?v=abc')).toBe('https://www.youtube.com/watch?v=abc')
    expect(normalizeSupportedUrl('goreecloud-youtube-player://music.youtube.com/watch?v=abc')).toBe('https://music.youtube.com/watch?v=abc')
  })

  it('rejects insecure schemes, forged domains and embedded credentials', () => {
    for (const link of [
      'http://www.youtube.com/watch?v=abc',
      'https://www.youtube.com.attacker.example/watch?v=abc',
      'https://attacker.example@www.youtube.com/watch?v=abc',
      'https://www.youtube.com:4040/watch?v=abc',
      'noutube://attacker.example/watch?v=abc',
      'noutube:auth',
      'goreecloud-youtube-player://attacker.example/watch?v=abc',
    ]) {
      expect(isSupportedUrl(link)).toBe(false)
      expect(normalizeSupportedUrl(link)).toBe('')
    }
  })
})
