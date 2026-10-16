import { beforeEach, describe, expect, it } from 'bun:test'
import { history$ } from '@/states/history'
import { getLastPlaying, getVideoIdFromUrl, withResumeTime, withoutResumeTime } from './last-playing'

const setLastPlaying = (entry: { current: number; duration: number; url?: string }) => {
  history$.bookmarks.set([
    {
      id: 'last',
      videoId: 'abc123',
      url: entry.url ?? 'https://www.youtube.com/watch?v=abc123',
      title: 'last',
      duration: entry.duration,
      current: entry.current,
      updatedAt: Date.now(),
    },
  ])
}

describe('getLastPlaying', () => {
  beforeEach(() => {
    history$.bookmarks.set([])
  })

  it('returns nothing without history', () => {
    expect(getLastPlaying()).toBeUndefined()
  })

  it('bakes the position into the url', () => {
    setLastPlaying({ current: 123.7, duration: 600 })
    expect(getLastPlaying()?.url).toBe('https://www.youtube.com/watch?v=abc123&t=123s')
  })

  it('replaces the stale position saved by the player', () => {
    setLastPlaying({ current: 200, duration: 600, url: 'https://www.youtube.com/watch?v=abc123&t=10s' })
    expect(getLastPlaying()?.url).toBe('https://www.youtube.com/watch?v=abc123&t=200s')
  })

  it('skips a video barely started', () => {
    setLastPlaying({ current: 2, duration: 600 })
    expect(getLastPlaying()).toBeUndefined()
  })

  it('skips a video watched to the end', () => {
    setLastPlaying({ current: 595, duration: 600 })
    expect(getLastPlaying()).toBeUndefined()
  })

  it('ignores corrupt or unrepresentable playback positions', () => {
    for (const current of [NaN, Infinity, -Infinity, Number.MAX_VALUE]) {
      setLastPlaying({ current, duration: 0 })
      expect(getLastPlaying()).toBeUndefined()
    }
  })

  it('does not resume a saved link from another origin or an unrelated page', () => {
    for (const url of [
      'https://example.com/watch?v=abc123',
      'https://www.youtube.com/results?search_query=test&v=abc123',
      'https://www.youtube.com/watch?v=different',
    ]) {
      setLastPlaying({ current: 100, duration: 600, url })
      expect(getLastPlaying()).toBeUndefined()
    }
  })

  it('normalizes a supported legacy link before resuming', () => {
    setLastPlaying({ current: 30, duration: 600, url: 'noutube://www.youtube.com/watch?v=abc123' })
    expect(getLastPlaying()?.url).toBe('https://www.youtube.com/watch?v=abc123&t=30s')
  })
})

describe('withResumeTime', () => {
  it('keeps other params', () => {
    expect(withResumeTime('https://www.youtube.com/watch?v=abc123&list=PL1', 30)).toBe(
      'https://www.youtube.com/watch?v=abc123&list=PL1&t=30s',
    )
  })

  it('returns invalid urls untouched', () => {
    expect(withResumeTime('not a url', 30)).toBe('not a url')
  })

  it('never embeds corrupt or negative seek positions', () => {
    const url = 'https://www.youtube.com/watch?v=abc123'
    for (const current of [NaN, Infinity, -Infinity, -1, Number.MAX_VALUE]) {
      expect(withResumeTime(url, current)).toBe(url)
    }
  })
})

describe('getVideoIdFromUrl', () => {
  it('reads the video id', () => {
    expect(getVideoIdFromUrl('https://m.youtube.com/watch?v=abc123&t=5s')).toBe('abc123')
  })

  it('returns empty for non video urls', () => {
    expect(getVideoIdFromUrl('https://www.youtube.com/')).toBe('')
    expect(getVideoIdFromUrl('nope')).toBe('')
    expect(getVideoIdFromUrl('https://example.com/watch?v=abc123')).toBe('')
    expect(getVideoIdFromUrl('https://www.youtube.com/results?v=abc123')).toBe('')
    expect(getVideoIdFromUrl('http://www.youtube.com/watch?v=abc123')).toBe('')
  })
})

describe('withoutResumeTime', () => {
  it('drops a stale position and keeps the rest', () => {
    expect(withoutResumeTime('https://www.youtube.com/watch?v=abc123&t=90s&list=PL1')).toBe(
      'https://www.youtube.com/watch?v=abc123&list=PL1',
    )
  })

  it('returns invalid urls untouched', () => {
    expect(withoutResumeTime('not a url')).toBe('not a url')
  })
})
