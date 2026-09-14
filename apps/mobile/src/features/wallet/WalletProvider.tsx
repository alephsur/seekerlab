import type {ReactNode} from 'react';
import {createSolanaDevnet, MobileWalletProvider} from '@wallet-ui/react-native-kit';
import {config} from '../../config';

const cluster = createSolanaDevnet({url: 'https://api.devnet.solana.com'});
const identity = {name: 'SeekerLab', uri: config.walletIdentityUri || 'https://example.com'};

export function WalletProvider({children}: {children: ReactNode}) {
  return <MobileWalletProvider cluster={cluster} identity={identity}>{children}</MobileWalletProvider>;
}
