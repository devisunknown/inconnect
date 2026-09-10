import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  StatusBar,
} from 'react-native';
import { Colors, Shadow, Border, BorderRadius, Spacing } from '../theme/colors';
import { NeoButton } from '../components/NeoButton';
import { NeoBadge } from '../components/NeoBadge';

type WelcomeScreenProps = {
  onGetStarted: () => void;
  onSignIn: () => void;
};

export function WelcomeScreen({ onGetStarted, onSignIn }: WelcomeScreenProps) {
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={Colors.surface} />

      {/* Header */}
      <View style={styles.header}>
        <NeoBadge label="🔗 InConnect" color={Colors.vividYellow} />
      </View>

      {/* Main Content */}
      <View style={styles.content}>
        <Text style={styles.headline}>
          Connect{'\n'}with your{'\n'}
          <View style={styles.tribeHighlight}>
            <Text style={styles.tribeText}>tribe.</Text>
          </View>
        </Text>

        <Text style={styles.subtitle}>
          Join a high-energy space where connections feel real, raw, and unfiltered.
        </Text>

        {/* Avatar Grid Preview */}
        <View style={styles.avatarCard}>
          <View style={styles.avatarCardInner}>
            <View style={styles.avatarRow}>
              <View style={[styles.avatar, { backgroundColor: Colors.vividYellow }]}>
                <Text style={styles.avatarEmoji}>😊</Text>
              </View>
              <View style={[styles.avatar, { backgroundColor: Colors.surfaceContainer }]}>
                <Text style={styles.avatarEmoji}>🙂</Text>
              </View>
              <View style={[styles.avatar, { backgroundColor: Colors.neonLime }]}>
                <Text style={styles.avatarEmoji}>😎</Text>
              </View>
              <View style={[styles.avatar, { backgroundColor: Colors.primary }]}>
                <Text style={styles.avatarEmoji}>🤩</Text>
              </View>
            </View>
          </View>
          <View style={styles.chatBubble}>
            <Text style={styles.chatBubbleEmoji}>💬</Text>
          </View>
        </View>
      </View>

      {/* Buttons */}
      <View style={styles.buttons}>
        <NeoButton
          title="Get Started"
          onPress={onGetStarted}
          icon={<Text style={styles.arrowIcon}>→</Text>}
        />
        <NeoButton
          title="Sign In"
          onPress={onSignIn}
          variant="secondary"
        />
      </View>

      {/* Footer */}
      <Text style={styles.footer}>© 2026 InConnect</Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.surface,
    paddingHorizontal: Spacing.page,
  },
  header: {
    paddingTop: Spacing.lg,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    gap: Spacing.xl,
    paddingVertical: Spacing.xxl,
  },
  headline: {
    fontSize: 42,
    fontWeight: '800',
    color: Colors.onSurface,
    lineHeight: 48,
    letterSpacing: -1.5,
  },
  tribeHighlight: {
    backgroundColor: Colors.neonLime,
    borderWidth: Border.default,
    borderColor: Colors.stroke,
    paddingHorizontal: Spacing.sm,
    transform: [{ rotate: '-2deg' }],
    ...Shadow.neo,
    alignSelf: 'flex-start',
    marginTop: 4,
  },
  tribeText: {
    fontSize: 42,
    fontWeight: '800',
    color: Colors.onSurface,
    letterSpacing: -1.5,
  },
  subtitle: {
    fontSize: 18,
    color: Colors.onSurfaceVariant,
    lineHeight: 26,
    maxWidth: 320,
    fontWeight: '500',
  },
  avatarCard: {
    backgroundColor: Colors.surfaceOffWhite,
    borderWidth: Border.default,
    borderColor: Colors.stroke,
    ...Shadow.neo,
    padding: Spacing.md,
    marginTop: Spacing.md,
  },
  avatarCardInner: {
    backgroundColor: Colors.surfaceContainer,
    borderWidth: Border.default,
    borderColor: Colors.stroke,
    ...Shadow.neoSm,
    padding: Spacing.lg,
    alignItems: 'center',
  },
  avatarRow: {
    flexDirection: 'row',
    gap: Spacing.md,
    justifyContent: 'center',
  },
  avatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
    borderWidth: Border.default,
    borderColor: Colors.stroke,
    ...Shadow.neoSm,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarEmoji: {
    fontSize: 24,
  },
  chatBubble: {
    position: 'absolute',
    bottom: -16,
    right: -16,
    backgroundColor: Colors.surfaceContainer,
    borderWidth: Border.default,
    borderColor: Colors.stroke,
    ...Shadow.neo,
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
    transform: [{ rotate: '-12deg' }],
  },
  chatBubbleEmoji: {
    fontSize: 24,
  },
  buttons: {
    gap: Spacing.md,
    paddingBottom: Spacing.lg,
  },
  arrowIcon: {
    fontSize: 20,
    fontWeight: '800',
  },
  footer: {
    textAlign: 'center',
    fontSize: 12,
    color: Colors.onSurfaceVariant,
    paddingBottom: Spacing.lg,
  },
});
