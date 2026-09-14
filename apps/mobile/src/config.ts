const mode = process.env.EXPO_PUBLIC_DATA_MODE ?? 'api';
if (mode !== 'api' && mode !== 'demo') {
  throw new Error('EXPO_PUBLIC_DATA_MODE must be api or demo');
}

export const config = {
  apiUrl: (process.env.EXPO_PUBLIC_API_URL ?? 'http://10.0.2.2:8000').replace(/\/$/, ''),
  dataMode: mode,
  devTesterToken: process.env.EXPO_PUBLIC_DEV_TESTER_TOKEN ?? '',
  walletIdentityUri: process.env.EXPO_PUBLIC_WALLET_IDENTITY_URI ?? '',
} as const;
