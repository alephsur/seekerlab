import {config} from '../config';
import {demoApi} from './demo';
import type {Campaign, Submission} from './types';
import {loadSession, renewSession} from '../features/auth/session';

async function request<T>(path: string, options: RequestInit = {}, authenticated = false): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 12000);
  try {
    let session = authenticated ? await loadSession() : null;
    if (authenticated && !session) throw new Error('Autentica tu wallet para continuar.');
    let response = await fetch(`${config.apiUrl}/api/v1${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        ...(options.body ? {'Content-Type': 'application/json'} : {}),
        ...(session ? {Authorization: `Bearer ${session.accessToken}`} : {}),
      },
    });
    if (authenticated && response.status === 401) {
      session = await renewSession(session?.accessToken);
      response = await fetch(`${config.apiUrl}/api/v1${path}`, {
        ...options,
        signal: controller.signal,
        headers: {
          ...(options.body ? {'Content-Type': 'application/json'} : {}),
          Authorization: `Bearer ${session.accessToken}`,
        },
      });
    }
    if (!response.ok) {
      const body: unknown = await response.json().catch(() => null);
      const detail = body && typeof body === 'object' && 'detail' in body ? body.detail : null;
      throw new Error(typeof detail === 'string' ? detail : `Error de API (${response.status})`);
    }
    return await response.json() as T;
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('La API tarda en responder. Comprueba Docker y la conexión del dispositivo.');
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

const httpApi = {
  campaigns: () => request<Campaign[]>('/campaigns'),
  submissions: () => request<Submission[]>('/submissions/me', {}, true),
  submit: (campaignId: string, feedback: string) => request<Submission>(
    `/campaigns/${encodeURIComponent(campaignId)}/submissions`,
    {method: 'POST', body: JSON.stringify({feedback})}, true,
  ),
};

export const api = config.dataMode === 'demo' ? demoApi : httpApi;
