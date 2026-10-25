import assert from 'node:assert/strict'
import { test } from 'node:test'
import { readChatStream } from '../lib/chat-stream.ts'

function stream(text, size = 1) {
  const bytes = new TextEncoder().encode(text)
  return new ReadableStream({start(controller) {
    for (let i = 0; i < bytes.length; i += size) controller.enqueue(bytes.slice(i, i + size))
    controller.close()
  }})
}
async function collect(body) {
  const events = []
  for await (const event of readChatStream(body)) events.push(event)
  return events
}
const frame = event => `data: ${JSON.stringify(event)}\n\n`

test('decodes split UTF-8, escaped newlines, multiple events and CRLF', async () => {
  const events = [{type:'start', conversation_id:'thread-1',message_id:'reply-1'}, {type:'delta',text:'Hello\n🌍 "world"'}, {type:'done'}]
  for (const size of [1, 7, 4096]) {
    assert.deepEqual(await collect(stream(events.map(frame).join('').replaceAll('\n','\r\n'),size)),events)
  }
})
test('preserves backend errors after a partial answer', async () => {
  const events = [{type:'delta',text:'Partial'}, {type:'error',message:'Backend unavailable'}, {type:'done'}]
  assert.deepEqual(await collect(stream(events.map(frame).join(''))),events)
})
test('reports truncated streams', async () => {
  await assert.rejects(collect(stream(frame({type:'delta',text:'Partial'}))),/connection ended/)
})
test('rejects malformed event payloads', async () => {
  await assert.rejects(collect(stream(frame({type:'delta',text:42}))),/Invalid response/)
  await assert.rejects(collect(stream('data: not json\n\n')))
})
test('ignores keepalives and cancels the reader after completion', async () => {
  let cancelled = false
  const body = new ReadableStream({start(controller) {
    controller.enqueue(new TextEncoder().encode(': keepalive\n\n' + frame({type:'done'})))
  }, cancel() { cancelled = true }})
  assert.deepEqual(await collect(body),[{type:'done'}])
  assert.equal(cancelled,true)
})
test('propagates transport failures', async () => {
  await assert.rejects(collect(new ReadableStream({start(controller) {controller.error(new Error('Disconnected'))}})),/Disconnected/)
})
