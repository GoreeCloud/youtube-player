import { describe, expect, it } from 'bun:test'
import { getSupportedVideoId, isSupportedUrl, normalizeSupportedUrl } from './supported-url'

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
      'https://www.youtube.com/wa\ntch?v=abc',
      'https://www.youtube.com/watch?v=abc\t123',
      'noutube://attacker.example/watch?v=abc',
      'noutube:auth',
      'goreecloud-youtube-player://attacker.example/watch?v=abc',
    ]) {
      expect(isSupportedUrl(link)).toBe(false)
      expect(normalizeSupportedUrl(link)).toBe('')
    }
  })
})

describe('getSupportedVideoId', () => {
  it('recognizes valid watch, share, Shorts, live and embed routes', () => {
    for (const url of [
      'https://www.youtube.com/watch?v=abc123&t=10',
      'https://m.youtube.com/watch?v=abc123',
      'https://music.youtube.com/watch?v=abc123',
      'https://youtu.be/abc123?t=4',
      'https://www.youtube.com/shorts/abc123',
      'https://www.youtube.com/live/abc123',
      'https://www.youtube.com/embed/abc123',
      'goreecloud-youtube-player://www.youtube.com/watch?v=abc123',
    ]) {
      expect(getSupportedVideoId(url)).toBe('abc123')
    }
  })

  it('ignores deceptive, unrelated and malformed video URLs', () => {
    for (const url of [
      'https://example.com/watch?v=abc123',
      'https://www.youtube.com.evil.example/watch?v=abc123',
      'https://evil.example@www.youtube.com/watch?v=abc123',
      'http://www.youtube.com/watch?v=abc123',
      'https://www.youtube.com:8443/watch?v=abc123',
      'https://www.youtube.com/results?search_query=cat&v=abc123',
      'https://www.youtube.com/@somebody?v=abc123',
      'https://www.youtube.com/shorts/abc123/extra',
      'https://youtu.be/abc123/extra',
      'https://www.youtube.com/watch?v=abc%2Fdef',
      `https://www.youtube.com/watch?v=${'x'.repeat(65)}`,
      'javascript:alert(1)',
      '',
    ]) {
      expect(getSupportedVideoId(url)).toBe('')
    }
  })
})
