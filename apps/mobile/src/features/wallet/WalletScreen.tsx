import {useState} from 'react';
import {ScrollView, Text} from 'react-native';
import {useMobileWallet} from '@wallet-ui/react-native-kit';
import {Button, Card} from '../../components/ui';
import {config} from '../../config';
import {colors} from '../../theme';

export function WalletScreen() {
  const {account, connect, disconnect} = useMobileWallet();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const configured = /^https:\/\//.test(config.walletIdentityUri);
  async function toggle() {
    setBusy(true); setError('');
    try {if (account) await disconnect(); else await connect();}
    catch (error) {setError(error instanceof Error ? error.message : 'No se pudo conectar la wallet');}
    finally {setBusy(false);}
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
    </Card>
    <Card><Text style={{color: colors.text, fontSize: 18, fontWeight: '700'}}>Estado de esta versión</Text>
      <Text style={{color: colors.muted, lineHeight: 23}}>La sesión del backend sigue usando el usuario de desarrollo. Conectar una wallet todavía no autentica las peticiones ni verifica un Seeker Genesis Token. Los pagos y el análisis con IA se incorporarán en las siguientes iteraciones.</Text>
    </Card>
  </ScrollView>;
}
