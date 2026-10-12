import assert from 'node:assert/strict'
import test from 'node:test'
import { isSupportedUrl, isSafeExternalUrl, findSupportedLaunchUrl, getSupportedVideoId, expandShortUrl, normalizeSupportedUrl } from '../../lib/supported-url.ts'

test('allows approved YouTube hosts with HTTPS or legacy links', () => {
  for (const input of [
    'https://www.youtube.com/watch?v=abc',
    'https://music.youtube.com/watch?v=abc',
    'http://m.youtube.com/shorts/abc',
    'https://youtu.be/abc',
    'noutube://www.youtube.com/watch?v=abc',
  ]) {
    assert.equal(isSupportedUrl(input), true, input)
  }
  assert.equal(normalizeSupportedUrl('noutube://youtu.be/abc'), 'https://youtu.be/abc')
})

test('rejects malformed, unrelated, or deceptive input', () => {
  for (const input of [
    '',
    'noutube:javascript:alert(1)',
    'noutube:auth?code=private',
    'noutube://example.com/watch?v=abc',
    'https://youtube.com.evil.example/watch?v=abc',
    'https://evil.example/@youtube.com',
    'https://user@www.youtube.com/watch?v=abc',
    'https://user:secret@www.youtube.com/watch?v=abc',
    'https://www.youtube.com:444/watch?v=abc',
    'javascript:https://www.youtube.com/watch?v=abc',
    'https://www.youtube.com/watch?v=abc\n',
  ]) {
    assert.equal(isSupportedUrl(input), false, input)
  }
  assert.equal(
    normalizeSupportedUrl('https://example.com/?next=noutube://www.youtube.com'),
    'https://example.com/?next=noutube://www.youtube.com',
  )
})

test('only ordinary web links may be handed to the OS', () => {
  for (const url of ['https://example.com/article', 'http://example.org:8080/path']) {
    assert.equal(isSafeExternalUrl(url), true, url)
  }
  for (const url of [
    '',
    'file:///etc/passwd',
    'javascript:alert(1)',
    'data:text/html,hello',
    'intent://scan/#Intent',
    'mailto:someone@example.com',
    'noutube://www.youtube.com/watch?v=abc',
    'https://user:pass@example.com/',
    'https://example.com/hello\nworld',
    'not a URL',
  ]) {
    assert.equal(isSafeExternalUrl(url), false, url)
  }
})


test('OS argv selects the first validated YouTube link, never a legacy auth token', () => {
  const malicious = [
    '--profile=Default',
    'noutube:auth?code=private',
    'noutube://not-youtube.example/clip',
    'file:///tmp/request.json',
    'https://user:secret@www.youtube.com/watch?v=abc',
  ]
  assert.equal(findSupportedLaunchUrl(malicious), undefined)
  assert.equal(
    findSupportedLaunchUrl([...malicious, 'noutube://youtu.be/approved', 'https://www.youtube.com/watch?v=later']),
    'noutube://youtu.be/approved',
  )
  assert.equal(
    findSupportedLaunchUrl(['--launch', 'https://music.youtube.com/watch?v=first', 'noutube://youtu.be/second']),
    'https://music.youtube.com/watch?v=first',
  )
})


test('extracts IDs for watch pages, Shorts, live links, embeds and short shares', () => {
  const cases = [
    ['https://www.youtube.com/watch?v=ABCDEFGHI01', 'ABCDEFGHI01'],
    ['https://music.youtube.com/watch?v=ABC_def-12&list=PL123', 'ABC_def-12'],
    ['https://m.youtube.com/shorts/ABCDEFGHI01', 'ABCDEFGHI01'],
    ['https://youtube.com/live/ABC_def-12?feature=share', 'ABC_def-12'],
    ['https://www.youtube.com/embed/ABCDEFGHI01?start=120', 'ABCDEFGHI01'],
    ['https://youtu.be/ABC_def-12?t=45', 'ABC_def-12'],
    ['noutube://youtu.be/ABCDEFGHI01?t=30', 'ABCDEFGHI01'],
  ]
  for (const [url, id] of cases) {
    assert.equal(getSupportedVideoId(url), id, url)
  }
})

test('never extracts thumbnails from spoofed hosts, credentials, or invalid IDs', () => {
  for (const url of [
    '',
    'https://youtube.com.evil.example/watch?v=ABCDEFGHI01',
    'https://user@www.youtube.com/watch?v=ABCDEFGHI01',
    'https://www.youtube.com:444/watch?v=ABCDEFGHI01',
    'https://www.youtube.com/watch?v=has%20spaces',
    'https://www.youtube.com/shorts/a/b',
    'https://www.youtube.com/live/',
    'https://youtu.be/ABC_def-12/other',
    'noutube:auth?code=token',
    'javascript:https://www.youtube.com/watch?v=ABCDEFGHI01',
  ]) {
    assert.equal(getSupportedVideoId(url), undefined, url)
  }
})


test('canonicalizes only a single trusted youtu.be video path', () => {
  assert.equal(
    expandShortUrl('https://youtu.be/ABC_def-12?t=45&list=PL123&v=spoofed'),
    'https://www.youtube.com/watch?v=ABC_def-12&t=45&list=PL123',
  )
  assert.equal(
    expandShortUrl('noutube://youtu.be/ABCDEFGHI01?t=30'),
    'https://www.youtube.com/watch?v=ABCDEFGHI01&t=30',
  )
})

test('does not rewrite ambiguous, untrusted, or ordinary watch URLs', () => {
  for (const input of [
    'https://youtu.be/ABC_def-12/extra?t=10',
    'https://youtu.be/invalid%20id?t=10',
    'https://user@youtu.be/ABCDEFGHI01',
    'https://youtu.be.evil.example/ABCDEFGHI01',
    'https://youtu.be:444/ABCDEFGHI01',
    'javascript:https://youtu.be/ABCDEFGHI01',
    'https://www.youtube.com/watch?v=ABCDEFGHI01',
    'not a URL',
  ]) {
    assert.equal(expandShortUrl(input), input)
  }
})
