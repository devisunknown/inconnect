import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  StatusBar,
  ActivityIndicator,
} from 'react-native';
import { Colors, Shadow, Border, BorderRadius, Spacing } from '../theme/colors';
import { NeoButton } from '../components/NeoButton';
import { api } from '../api/client';

type Interest = {
  id: number;
  name: string;
  icon: string;
  category: string;
};

type OnboardingScreenProps = {
  token: string;
  onComplete: () => void;
  onBack: () => void;
};

export function OnboardingScreen({ token, onComplete, onBack }: OnboardingScreenProps) {
  const [interests, setInterests] = useState<Interest[]>([]);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>();

  useEffect(() => {
    loadInterests();
  }, []);

  const loadInterests = async () => {
    try {
      const data = await api.interests.list();
      setInterests(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleInterest = (id: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleSubmit = async () => {
    if (selected.size < 3) return;
    setSubmitting(true);
    setError(undefined);
    try {
      await api.interests.select(Array.from(selected), token);
      onComplete();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={Colors.surface} />

      {/* Status Bar Mockup */}
      <View style={styles.statusBar}>
        <Text style={styles.statusBarTime}>09:27</Text>
        <View style={styles.statusBarIcons}>
          <Text style={styles.statusIcon}>📶</Text>
          <Text style={styles.statusIcon}>📡</Text>
          <Text style={styles.statusIcon}>🔋</Text>
        </View>
      </View>

      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerRow}>
          <TouchableOpacity onPress={onBack} style={styles.backButton}>
            <Text style={styles.backArrow}>←</Text>
          </TouchableOpacity>
          <View style={styles.stepBadge}>
            <Text style={styles.stepText}>Step 2 of 3</Text>
          </View>
        </View>
        <Text style={styles.headline}>What are you into?</Text>
        <Text style={styles.subtitle}>
          Pick at least 3 interests to personalize your InConnect feed.
        </Text>
      </View>

      {/* Interest Chips */}
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={Colors.primary} />
        </View>
      ) : (
        <ScrollView
          style={styles.scrollArea}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.sectionHeader}>
            <View style={[styles.sectionDot, { backgroundColor: Colors.surfaceContainer }]} />
            <Text style={styles.sectionTitle}>Popular right now</Text>
          </View>

          <View style={styles.chipGrid}>
            {interests.map((interest) => {
              const isSelected = selected.has(interest.id);
              return (
                <TouchableOpacity
                  key={interest.id}
                  onPress={() => toggleInterest(interest.id)}
                  activeOpacity={0.7}
                  style={[
                    styles.chip,
                    Shadow.neoSm,
                    isSelected && styles.chipSelected,
                  ]}
                >
                  <Text style={styles.chipIcon}>
                    {interest.icon || '⭐'}
                  </Text>
                  <Text style={[styles.chipText, isSelected && styles.chipTextSelected]}>
                    {interest.name}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>

          {interests.length === 0 && !loading && (
            <Text style={styles.emptyText}>
              No interests available yet. Check back soon.
            </Text>
          )}
        </ScrollView>
      )}

      {/* Bottom Bar */}
      <View style={[styles.bottomBar, Shadow.neo]}>
        <View style={styles.bottomInfo}>
          <Text style={styles.selectedCount}>{selected.size} selected</Text>
          {selected.size < 3 && (
            <Text style={styles.hintText}>Select at least 3</Text>
          )}
        </View>

        {error && (
          <View style={[styles.errorBox, Shadow.neoSm]}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        <NeoButton
          title="Continue"
          onPress={handleSubmit}
          loading={submitting}
          disabled={selected.size < 3}
          icon={<Text style={styles.arrowIcon}>→</Text>}
          style={styles.continueButton}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.surface,
  },
  statusBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.page,
    paddingTop: Spacing.sm,
    paddingBottom: Spacing.xs,
  },
  statusBarTime: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.onSurface,
  },
  statusBarIcons: {
    flexDirection: 'row',
    gap: Spacing.xs,
  },
  statusIcon: {
    fontSize: 14,
  },
  header: {
    paddingHorizontal: Spacing.page,
    paddingBottom: Spacing.lg,
    gap: Spacing.sm,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  backButton: {
    width: 48,
    height: 48,
    borderRadius: BorderRadius.md,
    borderWidth: Border.default,
    borderColor: Colors.stroke,
    ...Shadow.neoSm,
    backgroundColor: Colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
  },
  backArrow: {
    fontSize: 22,
    fontWeight: '700',
    color: Colors.onSurface,
  },
  stepBadge: {
    backgroundColor: Colors.primary,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: 999,
    borderWidth: 2,
    borderColor: Colors.stroke,
  },
  stepText: {
    fontSize: 13,
    fontWeight: '700',
    color: Colors.white,
  },
  headline: {
    fontSize: 32,
    fontWeight: '800',
    color: Colors.onSurface,
    letterSpacing: -1,
  },
  subtitle: {
    fontSize: 18,
    color: Colors.onSurfaceVariant,
    fontWeight: '500',
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  scrollArea: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: Spacing.page,
    paddingBottom: 140,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    marginBottom: Spacing.lg,
  },
  sectionDot: {
    width: 16,
    height: 16,
    borderRadius: 4,
    borderWidth: 2,
    borderColor: Colors.stroke,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: Colors.onSurface,
  },
  chipGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.md,
  },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    backgroundColor: Colors.surface,
    borderWidth: Border.default,
    borderColor: Colors.stroke,
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
  },
  chipSelected: {
    backgroundColor: Colors.neonLime,
    transform: [{ translateX: 2 }, { translateY: 2 }],
    shadowColor: '#000',
    shadowOffset: { width: 1, height: 1 },
    shadowOpacity: 1,
    shadowRadius: 0,
    elevation: 2,
  },
  chipIcon: {
    fontSize: 18,
  },
  chipText: {
    fontSize: 15,
    fontWeight: '700',
    color: Colors.onSurface,
  },
  chipTextSelected: {
    color: Colors.onSurface,
  },
  emptyText: {
    fontSize: 16,
    color: Colors.onSurfaceVariant,
    textAlign: 'center',
    marginTop: Spacing.xxl,
  },
  bottomBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: Colors.surfaceContainer,
    borderTopWidth: Border.default,
    borderTopColor: Colors.stroke,
    paddingHorizontal: Spacing.page,
    paddingTop: Spacing.lg,
    paddingBottom: Spacing.xxl,
    gap: Spacing.md,
  },
  bottomInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  selectedCount: {
    fontSize: 15,
    fontWeight: '600',
    color: Colors.onSurfaceVariant,
  },
  hintText: {
    fontSize: 14,
    fontWeight: '700',
    color: Colors.error,
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
  continueButton: {
    backgroundColor: Colors.primary,
  },
  arrowIcon: {
    fontSize: 20,
    fontWeight: '800',
  },
});
