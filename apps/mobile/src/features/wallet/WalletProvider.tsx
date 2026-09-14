import type {ReactNode} from 'react';
import {createSolanaDevnet, MobileWalletProvider} from '@wallet-ui/react-native-kit';
import {config} from '../../config';
import {AuthProvider} from '../auth/AuthProvider';

const cluster = createSolanaDevnet({url: 'https://api.devnet.solana.com'});
const identity = {name: 'SeekerLab', uri: config.walletIdentityUri || 'https://example.com'};

export function WalletProvider({children}: {children: ReactNode}) {
  return <MobileWalletProvider cluster={cluster} identity={identity}>
    <AuthProvider>{children}</AuthProvider>
  </MobileWalletProvider>;
}
