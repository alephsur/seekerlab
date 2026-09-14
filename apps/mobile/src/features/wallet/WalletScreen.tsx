import {useState} from 'react';
import {ScrollView, Text} from 'react-native';
import {useMobileWallet} from '@wallet-ui/react-native-kit';
import {Button, Card} from '../../components/ui';
import {config} from '../../config';
import {colors} from '../../theme';
import {useAuth} from '../auth/AuthProvider';
import {createChallenge} from '../auth/session';

export function WalletScreen() {
  const {account, connect, disconnect, signIn} = useMobileWallet();
  const {identity, loading, authenticate, signOut} = useAuth();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const configured = /^https:\/\//.test(config.walletIdentityUri);
  async function toggle() {
    setBusy(true); setError('');
    try {
      if (account) {
        try {
          if (identity) await signOut();
        } finally {
          await disconnect();
        }
      } else {
        await connect();
      }
    }
    catch (error) {setError(error instanceof Error ? error.message : 'No se pudo conectar la wallet');}
    finally {setBusy(false);}
  }
  async function authenticateWallet() {
    setBusy(true); setError('');
    try {
      const challenge = await createChallenge();
      if (challenge.uri.replace(/\/$/, '') !== config.walletIdentityUri.replace(/\/$/, '')) {
        throw new Error('La URI SIWS de la API no coincide con la identidad configurada en la app.');
      }
      const output = await signIn(challenge);
      await authenticate(challenge, output);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'No se pudo autenticar la wallet');
    } finally {setBusy(false);}
  }
  return <ScrollView contentContainerStyle={{padding: 22, gap: 22}}>
    <Text style={{color: colors.text, fontSize: 32, fontWeight: '800'}}>Tu wallet.</Text>
    <Card><Text style={{color: colors.accent, fontSize: 12, fontWeight: '700'}}>SOLANA DEVNET</Text>
      <Text style={{color: colors.text, fontSize: 20, fontWeight: '700'}}>{account ? 'Wallet conectada' : 'Conecta desde tu móvil'}</Text>
      <Text style={{color: colors.muted, lineHeight: 23}}>La conexión utiliza Mobile Wallet Adapter. Las claves permanecen en tu wallet.</Text>
      {account ? <Text selectable style={{color: colors.text, lineHeight: 22}}>{account.address}</Text> : null}
      {!configured ? <Text style={{color: colors.muted, lineHeight: 22}}>Configura EXPO_PUBLIC_WALLET_IDENTITY_URI con tu dominio HTTPS para habilitar la conexión.</Text> : null}
      {error ? <Text accessibilityRole="alert" style={{color: colors.danger}}>{error}</Text> : null}
      <Button label={busy ? 'Abriendo wallet…' : account ? 'Desconectar' : 'Conectar wallet'} disabled={busy || (!account && !configured)} onPress={() => void toggle()}/>
      {account && !identity ? <Button label={busy ? 'Esperando firma…' : 'Autenticar con wallet'}
        disabled={busy || loading} onPress={() => void authenticateWallet()}/> : null}
    </Card>
    <Card><Text style={{color: colors.text, fontSize: 18, fontWeight: '700'}}>Estado de esta versión</Text>
      <Text style={{color: colors.muted, lineHeight: 23}}>{identity
        ? `Sesión SIWS activa para ${identity.walletAddress}. La firma demuestra el control de esta cuenta.`
        : 'Conectar permite elegir una cuenta. Autenticar es un segundo paso explícito que firma un desafío de un solo uso.'}</Text>
      <Text style={{color: colors.muted, lineHeight: 23}}>La verificación del Seeker Genesis Token, los pagos y el análisis con IA se incorporarán en las siguientes iteraciones.</Text>
    </Card>
  </ScrollView>;
}
