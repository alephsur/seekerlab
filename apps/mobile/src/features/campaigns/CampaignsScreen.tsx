import {useCallback, useEffect, useState} from 'react';
import {RefreshControl, ScrollView, StyleSheet, Text, TextInput, View} from 'react-native';
import {api} from '../../api/client';
import type {Campaign} from '../../api/types';
import {Button, Card, ErrorState, Loading} from '../../components/ui';
import {colors} from '../../theme';

export function CampaignsScreen({onSelect}: {onSelect: (campaign: Campaign) => void}) {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const load = useCallback(async () => {
    setLoading(true); setError('');
    try {setCampaigns(await api.campaigns());}
    catch (error) {setError(error instanceof Error ? error.message : 'No se pudieron cargar las campañas');}
    finally {setLoading(false);}
  }, []);
  useEffect(() => {void load();}, [load]);

  const visible = campaigns.filter(campaign => campaign.title.toLowerCase().includes(search.toLowerCase()));
  return <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled"
    refreshControl={<RefreshControl refreshing={loading} onRefresh={() => void load()} tintColor={colors.accent}/> }>
    <Text style={styles.eyebrow}>PRUEBA. COMPARTE. MEJORA.</Text>
    <Text style={styles.hero}>Tu criterio hace{ '\n' }mejores apps.</Text>
    <Text style={styles.body}>Explora una prueba, sigue los pasos y comparte lo que has descubierto.</Text>
    <TextInput accessibilityLabel="Buscar campañas" placeholder="Buscar una prueba…" placeholderTextColor={colors.muted}
      value={search} onChangeText={setSearch} style={styles.search}/>
    <View style={styles.row}><Text style={styles.label}>PRUEBAS DISPONIBLES</Text><Text style={styles.count}>{visible.length}</Text></View>
    {error ? <ErrorState message={error} retry={() => void load()}/> : loading ? <Loading/> : visible.length === 0 ?
      <Card><Text style={styles.body}>No hay campañas para mostrar. Prueba otra búsqueda o carga los datos de ejemplo.</Text></Card> :
      visible.map(campaign => <Card key={campaign.id}>
        <View style={styles.row}><Text style={styles.chip}>EXPERIENCIA DE USUARIO</Text><Text style={styles.body}>{campaign.estimated_minutes} min</Text></View>
        <Text style={styles.title}>{campaign.title}</Text>
        <Text style={styles.body}>{campaign.description}</Text>
        <View style={styles.row}>
          <View><Text style={styles.reward}>{Number(campaign.reward_amount).toLocaleString('es-ES')} <Text style={styles.currency}>{campaign.currency}</Text></Text>
            <Text style={styles.caption}>Recompensa anunciada</Text></View>
          <Text style={styles.caption}>{campaign.capacity - campaign.submitted_count} plazas</Text>
        </View>
        <Button label="Ver prueba" onPress={() => onSelect(campaign)}/>
      </Card>)}
  </ScrollView>;
}

const styles = StyleSheet.create({
  container: {padding: 22, gap: 20, paddingBottom: 36},
  eyebrow: {color: colors.accent, fontSize: 11, letterSpacing: 2, fontWeight: '700'},
  hero: {color: colors.text, fontSize: 36, lineHeight: 42, fontWeight: '800', letterSpacing: -1.2},
  body: {color: colors.muted, fontSize: 14, lineHeight: 22},
  search: {backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, borderRadius: 12, color: colors.text, padding: 15},
  row: {flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10},
  label: {color: colors.muted, fontSize: 11, letterSpacing: 1.5, fontWeight: '700'},
  count: {color: colors.accent, fontSize: 14, fontWeight: '700'},
  chip: {color: colors.accent, fontSize: 10, fontWeight: '700', letterSpacing: 0.5},
  title: {color: colors.text, fontSize: 22, lineHeight: 28, fontWeight: '700'},
  reward: {color: colors.text, fontSize: 27, fontWeight: '700'},
  currency: {color: colors.accent, fontSize: 14},
  caption: {color: colors.muted, fontSize: 12, lineHeight: 18},
});
