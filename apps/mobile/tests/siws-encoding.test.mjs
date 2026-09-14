import assert from 'node:assert/strict';
import test from 'node:test';
import {
  buildSiwsMessage,
  encodeEd25519SignatureForApi,
  encodeSiwsMessageForApi,
} from '../src/features/auth/siwsEncoding.ts';

const challenge = {
  domain: 'example.ngrok-free.app',
  statement: 'Sign in to SeekerLab. This request does not authorize a payment.',
  uri: 'https://example.ngrok-free.app',
  version: '1',
  chainId: 'solana:devnet',
  nonce: '0123456789abcdef',
  issuedAt: '2026-09-14T16:00:00Z',
  expirationTime: '2026-09-14T16:05:00Z',
};
const address = '7V3jHXWKQQ7TkNaRwXzxZiUggX2EbzSfQa6xVWiG6sWJ';

test('encodes raw SIWS message and signature bytes once', () => {
  const message = buildSiwsMessage(challenge, address);
  const signature = Uint8Array.from({length: 64}, (_, index) => index);

  assert.equal(encodeSiwsMessageForApi(message, challenge, address), Buffer.from(message).toString('base64'));
  assert.equal(encodeEd25519SignatureForApi(signature), Buffer.from(signature).toString('base64'));
});

test('normalizes Base64URL message and Base64 signature text returned as bytes', () => {
  const message = buildSiwsMessage(challenge, address);
  const signature = Uint8Array.from({length: 64}, (_, index) => 255 - index);
  const encodedMessageBytes = new TextEncoder().encode(Buffer.from(message).toString('base64url'));
  const encodedSignatureBytes = new TextEncoder().encode(Buffer.from(signature).toString('base64'));

  assert.equal(
    encodeSiwsMessageForApi(encodedMessageBytes, challenge, address),
    Buffer.from(message).toString('base64'),
  );
  assert.equal(
    encodeEd25519SignatureForApi(encodedSignatureBytes),
    Buffer.from(signature).toString('base64'),
  );
});

test('does not normalize an encoded message that differs from the challenge', () => {
  const wrongMessage = new TextEncoder().encode('A different SIWS message');
  const encodedWrongMessage = new TextEncoder().encode(Buffer.from(wrongMessage).toString('base64url'));

  assert.notEqual(
    encodeSiwsMessageForApi(encodedWrongMessage, challenge, address),
    Buffer.from(wrongMessage).toString('base64'),
  );
});
