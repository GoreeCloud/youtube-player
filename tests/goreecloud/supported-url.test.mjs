import assert from 'node:assert/strict'
import test from 'node:test'
import { isSupportedUrl, isSafeExternalUrl, findSupportedLaunchUrl, normalizeSupportedUrl } from '../../lib/supported-url.ts'

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
