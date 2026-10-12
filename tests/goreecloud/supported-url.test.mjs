import assert from 'node:assert/strict'
import test from 'node:test'
import { isSupportedUrl, normalizeSupportedUrl } from '../../lib/supported-url.ts'

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
