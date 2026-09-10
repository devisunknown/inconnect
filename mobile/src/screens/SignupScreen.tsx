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

type SignupScreenProps = {
  onSignup: (data: {
    firstName: string;
    username: string;
    email: string;
    password1: string;
    password2: string;
  }) => void;
  onLogin: () => void;
  loading?: boolean;
  error?: string;
};

export function SignupScreen({
  onSignup,
  onLogin,
  loading = false,
  error,
}: SignupScreenProps) {
  const [firstName, setFirstName] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password1, setPassword1] = useState('');
  const [password2, setPassword2] = useState('');
  const [termsAccepted, setTermsAccepted] = useState(false);

  const handleSignup = () => {
    if (firstName.trim() && username.trim() && email.trim() && password1 && password2 && termsAccepted) {
      onSignup({
        firstName: firstName.trim(),
        username: username.trim(),
        email: email.trim(),
        password1,
        password2,
      });
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
            {/* Sign Up Badge */}
            <View style={[styles.badge, { backgroundColor: Colors.neonLime }]}>
              <Text style={styles.badgeText}>SIGN UP</Text>
            </View>

            {/* Header */}
            <View style={styles.header}>
              <Text style={styles.headline}>Join the Sphere</Text>
              <Text style={styles.subtitle}>
                Connect with brutal efficiency.
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
                label="Full Name"
                value={firstName}
                onChangeText={setFirstName}
                placeholder="Jane Doe"
              />

              <NeoInput
                label="Username"
                value={username}
                onChangeText={setUsername}
                placeholder="jane_doe"
              />

              <NeoInput
                label="Email"
                value={email}
                onChangeText={setEmail}
                placeholder="jane@example.com"
                keyboardType="email-address"
              />

              <NeoInput
                label="Password"
                value={password1}
                onChangeText={setPassword1}
                placeholder="••••••••"
                secureTextEntry
              />

              <NeoInput
                label="Confirm Password"
                value={password2}
                onChangeText={setPassword2}
                placeholder="••••••••"
                secureTextEntry
              />

              {/* Terms Checkbox */}
              <TouchableOpacity
                style={styles.termsRow}
                onPress={() => setTermsAccepted(!termsAccepted)}
                activeOpacity={0.7}
              >
                <View style={[styles.checkbox, termsAccepted && styles.checkboxChecked]}>
                  {termsAccepted && <Text style={styles.checkmark}>✓</Text>}
                </View>
                <Text style={styles.termsText}>
                  I agree to the{' '}
                  <Text style={styles.termsLink}>Terms of Service</Text>
                  {' '}and{' '}
                  <Text style={styles.termsLink}>Privacy Policy</Text>.
                </Text>
              </TouchableOpacity>

              <NeoButton
                title="Create Account"
                onPress={handleSignup}
                loading={loading}
                disabled={!termsAccepted}
                icon={<Text style={styles.arrowIcon}>→</Text>}
                style={styles.signupButton}
              />
            </View>

            {/* Divider */}
            <View style={styles.divider} />

            {/* Login Link */}
            <View style={styles.loginRow}>
              <Text style={styles.loginText}>Already have an account? </Text>
              <TouchableOpacity onPress={onLogin}>
                <View style={[styles.loginButton, Shadow.neoSm]}>
                  <Text style={styles.loginButtonText}>Log In</Text>
                </View>
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
  badge: {
    position: 'absolute',
    top: -15,
    left: -Border.default,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderWidth: Border.default,
    borderColor: Colors.stroke,
    borderTopLeftRadius: BorderRadius.lg,
    borderTopRightRadius: BorderRadius.sm,
    ...Shadow.neo,
    zIndex: 10,
  },
  badgeText: {
    fontSize: 13,
    fontWeight: '700',
    color: Colors.onSurface,
    textTransform: 'uppercase',
  },
  header: {
    marginTop: Spacing.lg,
    paddingBottom: Spacing.md,
    borderBottomWidth: Border.default,
    borderBottomColor: Colors.stroke,
    gap: Spacing.xs,
  },
  headline: {
    fontSize: 32,
    fontWeight: '800',
    color: Colors.onSurface,
    letterSpacing: -1,
    textTransform: 'uppercase',
  },
  subtitle: {
    fontSize: 18,
    color: Colors.onSurfaceVariant,
    fontWeight: '700',
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
  termsRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: Spacing.md,
    marginTop: Spacing.sm,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderWidth: 2,
    borderColor: Colors.stroke,
    backgroundColor: Colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 2,
  },
  checkboxChecked: {
    backgroundColor: Colors.vividYellow,
  },
  checkmark: {
    fontSize: 16,
    fontWeight: '800',
    color: Colors.onSurface,
  },
  termsText: {
    flex: 1,
    fontSize: 15,
    color: Colors.onSurface,
    lineHeight: 22,
    fontWeight: '500',
  },
  termsLink: {
    fontWeight: '800',
    textDecorationLine: 'underline',
  },
  signupButton: {
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
  loginRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loginText: {
    fontSize: 16,
    color: Colors.onSurfaceVariant,
    fontWeight: '500',
  },
  loginButton: {
    backgroundColor: Colors.surface,
    borderWidth: 2,
    borderColor: Colors.stroke,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
  },
  loginButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: Colors.onSurface,
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
