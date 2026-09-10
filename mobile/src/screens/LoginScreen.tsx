import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  StatusBar,
} from 'react-native';
import { Colors, Shadow, Border, BorderRadius, Spacing } from '../theme/colors';
import { NeoInput } from '../components/NeoInput';
import { NeoButton } from '../components/NeoButton';
import { NeoCard } from '../components/NeoCard';

type LoginScreenProps = {
  onLogin: (username: string, password: string) => void;
  onSignUp: () => void;
  onForgotPassword: () => void;
  loading?: boolean;
  error?: string;
};

export function LoginScreen({
  onLogin,
  onSignUp,
  onForgotPassword,
  loading = false,
  error,
}: LoginScreenProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = () => {
    if (username.trim() && password.trim()) {
      onLogin(username.trim(), password);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={Colors.surface} />
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          {/* Card */}
          <View style={[styles.card, Shadow.neo]}>
            {/* Auth Badge */}
            <View style={[styles.authBadge, { backgroundColor: Colors.neonLime }]}>
              <Text style={styles.authBadgeText}>Auth</Text>
            </View>

            {/* Header */}
            <View style={styles.header}>
              <Text style={styles.headline}>Welcome Back</Text>
              <Text style={styles.subtitle}>
                Log in to InConnect to continue your journey.
              </Text>
            </View>

            {/* Error */}
            {error && (
              <View style={[styles.errorBox, Shadow.neoSm]}>
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}

            {/* Form */}
            <View style={styles.form}>
              <NeoInput
                label="Username"
                value={username}
                onChangeText={setUsername}
                placeholder="username"
              />

              <View>
                <NeoInput
                  label="Password"
                  value={password}
                  onChangeText={setPassword}
                  placeholder="••••••••"
                  secureTextEntry
                />
                <TouchableOpacity onPress={onForgotPassword} style={styles.forgotLink}>
                  <Text style={styles.forgotText}>Forgot Password?</Text>
                </TouchableOpacity>
              </View>

              <NeoButton
                title="Login"
                onPress={handleLogin}
                loading={loading}
                icon={<Text style={styles.arrowIcon}>→</Text>}
                style={styles.loginButton}
              />
            </View>

            {/* Divider */}
            <View style={styles.divider} />

            {/* Sign Up Link */}
            <View style={styles.signupRow}>
              <Text style={styles.signupText}>Don't have an account? </Text>
              <TouchableOpacity onPress={onSignUp}>
                <Text style={styles.signupLink}>Sign Up</Text>
              </TouchableOpacity>
            </View>

            {/* Footer Links */}
            <View style={styles.divider} />
            <View style={styles.footerLinks}>
              <TouchableOpacity>
                <Text style={styles.footerLink}>Terms</Text>
              </TouchableOpacity>
              <TouchableOpacity>
                <Text style={styles.footerLink}>Privacy</Text>
              </TouchableOpacity>
            </View>
          </View>

          <Text style={styles.copyright}>© 2026 InConnect</Text>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.surface,
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: Spacing.page,
    paddingVertical: Spacing.xxl,
  },
  card: {
    backgroundColor: Colors.surfaceOffWhite,
    borderWidth: Border.default,
    borderColor: Colors.stroke,
    borderRadius: BorderRadius.lg,
    padding: Spacing.xl,
    gap: Spacing.lg,
  },
  authBadge: {
    position: 'absolute',
    top: -Border.default,
    left: -Border.default,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderWidth: Border.default,
    borderColor: Colors.stroke,
    borderTopLeftRadius: BorderRadius.lg,
    borderBottomRightRadius: BorderRadius.lg,
  },
  authBadgeText: {
    fontSize: 13,
    fontWeight: '700',
    color: Colors.onSurface,
    textTransform: 'uppercase',
  },
  header: {
    marginTop: Spacing.xxl,
    gap: Spacing.xs,
  },
  headline: {
    fontSize: 32,
    fontWeight: '800',
    color: Colors.onSurface,
    letterSpacing: -1,
  },
  subtitle: {
    fontSize: 16,
    color: Colors.onSurfaceVariant,
    fontWeight: '500',
  },
  errorBox: {
    backgroundColor: Colors.errorContainer,
    borderWidth: Border.default,
    borderColor: Colors.stroke,
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
  },
  errorText: {
    fontSize: 13,
    fontWeight: '600',
    color: Colors.onErrorContainer,
  },
  form: {
    gap: Spacing.lg,
  },
  forgotLink: {
    alignSelf: 'flex-end',
    marginTop: Spacing.xs,
  },
  forgotText: {
    fontSize: 13,
    fontWeight: '700',
    color: Colors.primary,
  },
  loginButton: {
    marginTop: Spacing.sm,
  },
  arrowIcon: {
    fontSize: 20,
    fontWeight: '800',
  },
  divider: {
    borderWidth: 1,
    borderColor: Colors.stroke,
    borderStyle: 'dashed',
  },
  signupRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  signupText: {
    fontSize: 16,
    color: Colors.onSurfaceVariant,
    fontWeight: '500',
  },
  signupLink: {
    fontSize: 16,
    fontWeight: '700',
    color: Colors.primary,
    textDecorationLine: 'underline',
  },
  footerLinks: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: Spacing.xl,
  },
  footerLink: {
    fontSize: 13,
    fontWeight: '700',
    color: Colors.primary,
    textDecorationLine: 'underline',
  },
  copyright: {
    textAlign: 'center',
    fontSize: 12,
    color: Colors.onSurfaceVariant,
    marginTop: Spacing.lg,
  },
});
