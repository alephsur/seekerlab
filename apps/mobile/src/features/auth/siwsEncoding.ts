import {fromUint8Array, toUint8Array} from '@wallet-ui/react-native-kit';

type SiwsMessageFields = {
  domain: string;
  statement: string;
  uri: string;
  version: '1';
  chainId: string;
  nonce: string;
  issuedAt: string;
  expirationTime: string;
};

function bytesEqual(left: Uint8Array, right: Uint8Array): boolean {
  if (left.length !== right.length) return false;
  return left.every((value, index) => value === right[index]);
}

function decodeEncodedBytes(value: Uint8Array): Uint8Array | null {
  const encoded = new TextDecoder().decode(value);
  if (!/^[A-Za-z0-9+/_-]+={0,2}$/.test(encoded)) return null;
  try {
    return toUint8Array(encoded);
  } catch {
    return null;
  }
}

export function buildSiwsMessage(
  challenge: SiwsMessageFields,
  address: string,
): Uint8Array {
  return new TextEncoder().encode(
    `${challenge.domain} wants you to sign in with your Solana account:\n` +
    `${address}\n\n` +
    `${challenge.statement}\n\n` +
    `URI: ${challenge.uri}\n` +
    `Version: ${challenge.version}\n` +
    `Chain ID: ${challenge.chainId}\n` +
    `Nonce: ${challenge.nonce}\n` +
    `Issued At: ${challenge.issuedAt}\n` +
    `Expiration Time: ${challenge.expirationTime}`,
  );
}

export function encodeSiwsMessageForApi(
  value: Uint8Array,
  challenge: SiwsMessageFields,
  address: string,
): string {
  const expected = buildSiwsMessage(challenge, address);
  if (bytesEqual(value, expected)) return fromUint8Array(value);

  const decoded = decodeEncodedBytes(value);
  return fromUint8Array(decoded && bytesEqual(decoded, expected) ? decoded : value);
}

export function encodeEd25519SignatureForApi(value: Uint8Array): string {
  if (value.length === 64) return fromUint8Array(value);
  const decoded = decodeEncodedBytes(value);
  return fromUint8Array(decoded?.length === 64 ? decoded : value);
}
