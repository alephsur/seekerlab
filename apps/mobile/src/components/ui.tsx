import type {ReactNode} from 'react';
import {ActivityIndicator, Pressable, StyleSheet, Text, View} from 'react-native';
import {colors} from '../theme';

export function Button({label, onPress, disabled = false, secondary = false}: {
  label: string; onPress: () => void; disabled?: boolean; secondary?: boolean;
}) {
  return <Pressable accessibilityRole="button" accessibilityState={{disabled}}
    disabled={disabled} onPress={onPress}
    style={({pressed}) => [styles.button, secondary && styles.secondary, {opacity: disabled ? 0.4 : pressed ? 0.7 : 1}]}>
    <Text style={[styles.buttonText, secondary && {color: colors.text}]}>{label}</Text>
  </Pressable>;
}

export function Card({children}: {children: ReactNode}) {
  return <View style={styles.card}>{children}</View>;
}

export function ErrorState({message, retry}: {message: string; retry: () => void}) {
  return <Card><Text accessibilityRole="alert" style={styles.error}>{message}</Text>
    <Button secondary label="Volver a intentar" onPress={retry}/></Card>;
}

export function Loading() {
  return <View style={{padding: 40}}><ActivityIndicator size="large" color={colors.accent}/></View>;
}

const styles = StyleSheet.create({
  button: {backgroundColor: colors.accent, padding: 16, borderRadius: 14, alignItems: 'center', minHeight: 52},
  secondary: {backgroundColor: colors.elevated, borderWidth: 1, borderColor: colors.border},
  buttonText: {color: colors.accentText, fontSize: 15, fontWeight: '700'},
  card: {padding: 20, borderRadius: 20, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, gap: 16},
  error: {color: colors.danger, fontSize: 15, lineHeight: 22},
});
