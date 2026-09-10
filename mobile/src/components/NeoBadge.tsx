import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { Colors, Shadow, Border, BorderRadius, Spacing } from '../theme/colors';

type NeoBadgeProps = {
  label: string;
  color?: string;
  textColor?: string;
  style?: ViewStyle;
};

export function NeoBadge({
  label,
  color = Colors.neonLime,
  textColor = Colors.onSurface,
  style,
}: NeoBadgeProps) {
  return (
    <View
      style={[
        styles.badge,
        { backgroundColor: color },
        style,
      ]}
    >
      <Text style={[styles.text, { color: textColor }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderWidth: Border.default,
    borderColor: Colors.stroke,
    borderRadius: BorderRadius.sm,
    alignSelf: 'flex-start',
  },
  text: {
    fontSize: 13,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
});
