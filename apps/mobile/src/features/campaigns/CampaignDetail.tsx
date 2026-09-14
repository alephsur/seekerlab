import {useState} from 'react';
import {ScrollView, StyleSheet, Text, TextInput, View} from 'react-native';
import {api} from '../../api/client';
import type {Campaign} from '../../api/types';
import {Button, Card} from '../../components/ui';
import {colors} from '../../theme';

export function CampaignDetail({campaign, onBack, onSubmitted}: {
  campaign: Campaign; onBack: () => void; onSubmitted: () => void;
}) {
  const [feedback, setFeedback] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [sent, setSent] = useState(false);
  async function submit() {
    if (busy || sent) return;
    setBusy(true); setError('');
    try {await api.submit(campaign.id, feedback.trim()); setSent(true);}
    catch (error) {setError(error instanceof Error ? error.message : 'No se pudo enviar la prueba');}
    finally {setBusy(false);}
  }
  return <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
    <Button secondary label="Volver a las pruebas" onPress={onBack}/>
    <Text style={styles.title}>{campaign.title}</Text>
    <Text style={styles.body}>{campaign.description}</Text>
    <Card><Text style={styles.heading}>Tu prueba, paso a paso</Text>
      {campaign.instructions.map((instruction, index) => <View key={`${index}-${instruction}`} style={styles.step}>
        <Text style={styles.number}>{String(index + 1).padStart(2, '0')}</Text><Text style={[styles.body, {flex: 1}]}>{instruction}</Text>
      </View>)}
    </Card>
    <Text style={styles.body}>Recompensa anunciada: {campaign.reward_amount} {campaign.currency}. En esta base de desarrollo no se procesan pagos.</Text>
    {sent ? <Card><Text style={styles.heading}>Respuesta recibida</Text><Text style={styles.body}>Tu entrega está pendiente de revisión.</Text>
      <Button label="Ver mis entregas" onPress={onSubmitted}/></Card> : <Card>
      <Text style={styles.heading}>¿Qué has descubierto?</Text>
      <Text style={styles.body}>Explica qué hiciste, qué esperabas y qué sucedió. Incluye una mejora concreta.</Text>
      <TextInput accessibilityLabel="Observaciones de la prueba" multiline textAlignVertical="top" maxLength={5000}
        placeholder="Al abrir la campaña esperaba encontrar…" placeholderTextColor={colors.muted}
        style={styles.input} value={feedback} onChangeText={setFeedback} editable={!busy}/>
      <Text style={styles.body}>{feedback.trim().length}/5000 · mínimo 20 caracteres</Text>
      {error ? <Text accessibilityRole="alert" style={styles.error}>{error}</Text> : null}
      <Button label={busy ? 'Enviando…' : 'Enviar observaciones'} disabled={busy || feedback.trim().length < 20}
        onPress={() => void submit()}/>
    </Card>}
  </ScrollView>;
}

const styles = StyleSheet.create({
  container: {padding: 22, gap: 22, paddingBottom: 48},
  title: {color: colors.text, fontSize: 32, fontWeight: '800', lineHeight: 38},
  heading: {color: colors.text, fontSize: 19, fontWeight: '700'},
  body: {color: colors.muted, fontSize: 14, lineHeight: 22},
  step: {flexDirection: 'row', gap: 14},
  number: {color: colors.accent, fontWeight: '700', fontSize: 16},
  input: {minHeight: 170, borderRadius: 12, borderWidth: 1, borderColor: colors.border, padding: 14, color: colors.text, fontSize: 15, lineHeight: 23},
  error: {color: colors.danger, lineHeight: 22},
});
