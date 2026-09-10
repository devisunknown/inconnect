import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { Colors, Shadow, Border, BorderRadius, Spacing } from '../theme/colors';

type NeoCardProps = {
  children: React.ReactNode;
  style?: ViewStyle;
  variant?: 'default' | 'flat';
};

export function NeoCard({ children, style, variant = 'default' }: NeoCardProps) {
  return (
    <View
      style={[
        styles.card,
        variant === 'default' && Shadow.neo,
        style,
      ]}
    >
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surfaceOffWhite,
    borderWidth: Border.default,
    borderColor: Colors.stroke,
    borderRadius: BorderRadius.lg,
    padding: Spacing.xl,
  },
});
