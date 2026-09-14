import {useCallback, useEffect, useState} from 'react';
import {RefreshControl, ScrollView, Text} from 'react-native';
import {api} from '../../api/client';
import type {Submission} from '../../api/types';
import {Card, ErrorState, Loading} from '../../components/ui';
import {colors} from '../../theme';

export function SubmissionsScreen() {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const load = useCallback(async () => {
    setLoading(true); setError('');
    try {setSubmissions(await api.submissions());}
    catch (error) {setError(error instanceof Error ? error.message : 'No se pudieron cargar tus entregas');}
    finally {setLoading(false);}
  }, []);
  useEffect(() => {void load();}, [load]);
  return <ScrollView contentContainerStyle={{padding: 22, gap: 20}}
    refreshControl={<RefreshControl refreshing={loading} onRefresh={() => void load()} tintColor={colors.accent}/> }>
    <Text style={{fontSize: 32, fontWeight: '800', color: colors.text}}>Tus aportaciones.</Text>
    <Text style={{color: colors.muted, lineHeight: 22}}>El historial de las pruebas que has completado.</Text>
    {error ? <ErrorState message={error} retry={() => void load()}/> : loading ? <Loading/> : submissions.length === 0 ?
      <Card><Text style={{color: colors.muted, lineHeight: 22}}>Todavía no has enviado ninguna prueba. Explora las campañas para empezar.</Text></Card> :
      submissions.map(submission => <Card key={submission.id}>
        <Text style={{color: colors.accent, fontSize: 12, fontWeight: '700'}}>PENDIENTE DE REVISIÓN</Text>
        <Text style={{color: colors.text, lineHeight: 24}}>{submission.feedback}</Text>
        <Text style={{color: colors.muted, fontSize: 12}}>{new Date(submission.created_at).toLocaleString('es-ES')}</Text>
      </Card>)}
  </ScrollView>;
}
