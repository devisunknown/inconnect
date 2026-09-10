import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { Colors, Shadow, Border, BorderRadius, Spacing } from '../theme/colors';

type NeoButtonProps = {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline';
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  style?: ViewStyle;
  textStyle?: TextStyle;
};

export function NeoButton({
  title,
  onPress,
  variant = 'primary',
  loading = false,
  disabled = false,
  icon,
  style,
  textStyle,
}: NeoButtonProps) {
  const bgColor =
    variant === 'primary'
      ? Colors.vividYellow
      : variant === 'secondary'
        ? Colors.surfaceOffWhite
        : 'transparent';

  const textColor =
    variant === 'outline' ? Colors.onSurface : Colors.onSurface;

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.7}
      style={[
        styles.button,
        Shadow.neo,
        { backgroundColor: bgColor, borderWidth: Border.default, borderColor: Colors.stroke },
        (disabled || loading) && styles.disabled,
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={Colors.onSurface} />
      ) : (
        <>
          <Text style={[styles.text, { color: textColor }, textStyle]}>{title}</Text>
          {icon}
        </>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: Spacing.lg,
    paddingHorizontal: Spacing.xl,
    borderRadius: BorderRadius.lg,
    gap: Spacing.sm,
  },
  text: {
    fontSize: 18,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: -0.5,
  },
  disabled: {
    opacity: 0.5,
  },
});
