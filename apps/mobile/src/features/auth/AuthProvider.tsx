import {createContext, type ReactNode, useContext, useEffect, useMemo, useState} from 'react';
import {useMobileWallet} from '@wallet-ui/react-native-kit';
import {config} from '../../config';
import {encodeEd25519SignatureForApi, encodeSiwsMessageForApi} from './siwsEncoding';
import {
  AuthRequestError,
  getCurrentIdentity,
  loadSession,
  renewSession,
  revokeSession,
  type AuthIdentity,
  type SiwsChallenge,
  verifyChallenge,
} from './session';

type SiwsOutput = {
  account: {address: string};
  signedMessage: Uint8Array;
  signature: Uint8Array;
};

type AuthContextValue = {
  identity: AuthIdentity | null;
  loading: boolean;
  authenticate: (challenge: SiwsChallenge, output: SiwsOutput) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({children}: {children: ReactNode}) {
  const {account} = useMobileWallet();
  const [identity, setIdentity] = useState<AuthIdentity | null>(null);
  const [loading, setLoading] = useState(config.dataMode !== 'demo');

  useEffect(() => {
    if (config.dataMode === 'demo') return;
    let active = true;
    void (async () => {
      try {
        const stored = await loadSession();
        if (!stored) return;
        if (active) setIdentity(stored.identity);
        try {
          const current = await getCurrentIdentity(stored.accessToken);
          if (active) setIdentity(current);
        } catch (error) {
          if (error instanceof AuthRequestError && error.status === 401) {
            const renewed = await renewSession(stored.accessToken);
            if (active) setIdentity(renewed.identity);
          }
        }
      } catch {
        if (active) setIdentity(null);
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {active = false;};
  }, []);

  useEffect(() => {
    if (account && identity && account.address !== identity.walletAddress) {
      void revokeSession().finally(() => setIdentity(null));
    }
  }, [account, identity]);

  const value = useMemo<AuthContextValue>(() => ({
    identity,
    loading,
    async authenticate(challenge, output) {
      const session = await verifyChallenge({
        nonce: challenge.nonce,
        account: {address: output.account.address},
        signedMessage: encodeSiwsMessageForApi(
          output.signedMessage, challenge, output.account.address,
        ),
        signature: encodeEd25519SignatureForApi(output.signature),
        signatureType: 'ed25519',
      });
      setIdentity(session.identity);
    },
    async signOut() {
      try {await revokeSession();} finally {setIdentity(null);}
    },
  }), [identity, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside AuthProvider');
  return context;
}
