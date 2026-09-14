import type { ExpoConfig } from 'expo/config';

const config: ExpoConfig = {
  name: 'SeekerLab',
  slug: 'seekerlab',
  scheme: 'seekerlab',
  version: '0.2.0',
  orientation: 'portrait',
  userInterfaceStyle: 'dark',
  platforms: ['android'],
  android: {package: 'com.seekerlab.app'},
  plugins: [
    'expo-dev-client',
    'expo-secure-store',
    ['expo-build-properties', {android: {usesCleartextTraffic: process.env.APP_VARIANT !== 'production'}}],
  ],
};

export default config;
