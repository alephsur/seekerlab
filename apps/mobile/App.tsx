import {useEffect, useState} from 'react';
import {BackHandler, KeyboardAvoidingView, Pressable, StatusBar, StyleSheet, Text, View} from 'react-native';
import {SafeAreaProvider, SafeAreaView} from 'react-native-safe-area-context';
import type {Campaign} from './src/api/types';
import {config} from './src/config';
import {CampaignsScreen} from './src/features/campaigns/CampaignsScreen';
import {CampaignDetail} from './src/features/campaigns/CampaignDetail';
import {SubmissionsScreen} from './src/features/submissions/SubmissionsScreen';
import {WalletProvider} from './src/features/wallet/WalletProvider';
import {WalletScreen} from './src/features/wallet/WalletScreen';
import {useAuth} from './src/features/auth/AuthProvider';
import {colors} from './src/theme';

type Tab = 'campaigns' | 'submissions' | 'wallet';
const tabs: {key: Tab; label: string}[] = [
  {key: 'campaigns', label: 'Explorar'}, {key: 'submissions', label: 'Mis entregas'}, {key: 'wallet', label: 'Wallet'},
];

function Shell() {
  const {identity} = useAuth();
  const [tab, setTab] = useState<Tab>('campaigns');
  const [selected, setSelected] = useState<Campaign | null>(null);
  useEffect(() => {
    const subscription = BackHandler.addEventListener('hardwareBackPress', () => {
      if (selected) {setSelected(null); return true;}
      if (tab !== 'campaigns') {setTab('campaigns'); return true;}
      return false;
    });
    return () => subscription.remove();
  }, [selected, tab]);

  return <SafeAreaView style={styles.safe}>
    <StatusBar barStyle="light-content"/>
    <View style={styles.header}><View style={styles.brand}><Text style={styles.mark}>S</Text><Text style={styles.wordmark}>SeekerLab<Text style={{color: colors.accent}}>.</Text></Text></View>
      <Text style={styles.version}>0.2 / DEV</Text></View>
    <View style={styles.banner}><Text style={styles.bannerText}>{config.dataMode === 'demo'
      ? 'DEMO LOCAL · datos en memoria · sin pagos'
      : identity ? 'SESIÓN SIWS · sin pagos' : 'DESARROLLO · autentica tu wallet · sin pagos'}</Text></View>
    <KeyboardAvoidingView style={{flex: 1}}>
      {selected ? <CampaignDetail key={selected.id} campaign={selected} onBack={() => setSelected(null)} onSubmitted={() => {setSelected(null); setTab('submissions');}}/> :
        tab === 'campaigns' ? <CampaignsScreen onSelect={setSelected}/> : tab === 'submissions' ? <SubmissionsScreen/> : <WalletScreen/>}
    </KeyboardAvoidingView>
    <View style={styles.tabs}>{tabs.map(item => <Pressable key={item.key} accessibilityRole="tab" accessibilityState={{selected: tab === item.key}}
      onPress={() => {setSelected(null); setTab(item.key);}} style={[styles.tab, tab === item.key && styles.activeTab]}>
      <Text style={[styles.tabText, tab === item.key && {color: colors.accent}]}>{item.label}</Text>
    </Pressable>)}</View>
  </SafeAreaView>;
}

export default function App() {
  return <SafeAreaProvider><WalletProvider><Shell/></WalletProvider></SafeAreaProvider>;
}

const styles = StyleSheet.create({
  safe: {flex: 1, backgroundColor: colors.background},
  header: {paddingHorizontal: 22, paddingVertical: 18, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between'},
  brand: {flexDirection: 'row', alignItems: 'center', gap: 10},
  mark: {backgroundColor: colors.accent, color: colors.accentText, borderRadius: 10, overflow: 'hidden', paddingHorizontal: 10, paddingVertical: 4, fontSize: 24, fontWeight: '900'},
  wordmark: {color: colors.text, fontSize: 22, fontWeight: '800', letterSpacing: -0.7},
  version: {color: colors.muted, fontSize: 10, letterSpacing: 1},
  banner: {backgroundColor: colors.elevated, paddingVertical: 8, paddingHorizontal: 20},
  bannerText: {color: colors.muted, fontSize: 10, textAlign: 'center', letterSpacing: 0.5},
  tabs: {flexDirection: 'row', borderTopColor: colors.border, borderTopWidth: 1, padding: 10, gap: 6},
  tab: {flex: 1, paddingVertical: 15, alignItems: 'center', borderRadius: 12},
  activeTab: {backgroundColor: colors.surface},
  tabText: {color: colors.muted, fontSize: 13, fontWeight: '700'},
});
