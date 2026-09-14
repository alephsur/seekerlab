import * as SecureStore from 'expo-secure-store';
import {config} from '../../config';

const SESSION_KEY = 'seekerlab.siws.session.v1';

export type AuthIdentity = {
  id: string;
  walletAddress: string;
  role: 'tester';
};

export type AuthSession = {
  accessToken: string;
  refreshToken: string;
  tokenType: 'bearer';
  expiresIn: number;
  refreshExpiresIn: number;
  identity: AuthIdentity;
};

export type SiwsChallenge = {
  domain: string;
  statement: string;
  uri: string;
  version: '1';
  chainId: string;
  nonce: string;
  issuedAt: string;
  expirationTime: string;
};

type SiwsProof = {
  nonce: string;
  account: {address: string};
  signedMessage: string;
  signature: string;
  signatureType: 'ed25519';
};

export class AuthRequestError extends Error {
  constructor(message: string, readonly status: number) {
    super(message);
    this.name = 'AuthRequestError';
  }
}

async function authRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${config.apiUrl}/api/v1/auth${path}`, {
    ...options,
    headers: {
      ...(options.body ? {'Content-Type': 'application/json'} : {}),
      ...options.headers,
    },
  });
  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null);
    const detail = body && typeof body === 'object' && 'detail' in body ? body.detail : null;
    throw new AuthRequestError(
      typeof detail === 'string' ? detail : `Error de autenticación (${response.status})`,
      response.status,
    );
  }
  if (response.status === 204) return undefined as T;
  return await response.json() as T;
}

export async function loadSession(): Promise<AuthSession | null> {
  const value = await SecureStore.getItemAsync(SESSION_KEY);
  if (!value) return null;
  try {
    const session = JSON.parse(value) as AuthSession;
    return session.accessToken && session.refreshToken && session.identity?.walletAddress
      ? session : null;
  } catch {
    await clearSession();
    return null;
  }
}

export async function saveSession(session: AuthSession): Promise<void> {
  await SecureStore.setItemAsync(SESSION_KEY, JSON.stringify(session));
}

export async function clearSession(): Promise<void> {
  await SecureStore.deleteItemAsync(SESSION_KEY);
}

export function createChallenge(): Promise<SiwsChallenge> {
  return authRequest('/siws/challenge', {method: 'POST'});
}

export async function verifyChallenge(proof: SiwsProof): Promise<AuthSession> {
  const session = await authRequest<AuthSession>('/siws/verify', {
    method: 'POST', body: JSON.stringify(proof),
  });
  await saveSession(session);
  return session;
}

let refreshPromise: Promise<AuthSession> | null = null;

export async function renewSession(failedAccessToken?: string): Promise<AuthSession> {
  if (refreshPromise) return refreshPromise;
  refreshPromise = (async () => {
    const current = await loadSession();
    if (!current) throw new Error('Autentica tu wallet para continuar.');
    if (failedAccessToken && current.accessToken !== failedAccessToken) return current;
    try {
      const renewed = await authRequest<AuthSession>('/session/refresh', {
        method: 'POST', body: JSON.stringify({refreshToken: current.refreshToken}),
      });
      await saveSession(renewed);
      return renewed;
    } catch (error) {
      if (error instanceof AuthRequestError && error.status === 401) await clearSession();
      throw error;
    }
  })();
  try {
    return await refreshPromise;
  } finally {
    refreshPromise = null;
  }
}

export async function revokeSession(): Promise<void> {
  const current = await loadSession();
  try {
    if (current) {
      await authRequest<void>('/session/revoke', {
        method: 'POST', headers: {Authorization: `Bearer ${current.accessToken}`},
      });
    }
  } finally {
    await clearSession();
  }
}

export async function getCurrentIdentity(accessToken: string): Promise<AuthIdentity> {
  return authRequest('/me', {headers: {Authorization: `Bearer ${accessToken}`}});
}
