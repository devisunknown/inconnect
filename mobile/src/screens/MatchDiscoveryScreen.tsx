import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { Colors, Spacing, BorderRadius, Shadow, Border } from '../theme/colors';
import { api, Match } from '../api/client';
import { NeoButton } from '../components/NeoButton';
import { NeoCard } from '../components/NeoCard';
import { NeoBadge } from '../components/NeoBadge';

interface MatchDiscoveryScreenProps {
  token: string;
  onViewProfile: (userId: number) => void;
  onMessage: (chatId: number) => void;
  onAddFriend: (userId: number) => void;
  onBack: () => void;
}

export function MatchDiscoveryScreen({
  token,
  onViewProfile,
  onMessage,
  onAddFriend,
  onBack,
}: MatchDiscoveryScreenProps) {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMatches = async () => {
    try {
      setError(null);
      const data = await api.matches.list(token);
      setMatches(data);
    } catch (e: any) {
      setError(e.message || 'Failed to load matches');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchMatches();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchMatches();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={Colors.primary} />
        <Text style={styles.loadingText}>Finding your matches...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <Text style={styles.backButtonText}>←</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Discover</Text>
        <View style={styles.headerRight} />
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={Colors.primary}
          />
        }
      >
        <View style={styles.heroSection}>
          <Text style={styles.heroEmoji}>🎯</Text>
          <Text style={styles.heroTitle}>Find Your Match</Text>
          <Text style={styles.heroSubtitle}>People who share your interests</Text>
        </View>

        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
            <NeoButton
              title="Retry"
              onPress={fetchMatches}
              variant="secondary"
              style={styles.retryButton}
            />
          </View>
        )}

        {matches.length === 0 && !error ? (
          <NeoCard style={styles.emptyCard}>
            <Text style={styles.emptyIcon}>🔍</Text>
            <Text style={styles.emptyTitle}>No matches found yet</Text>
            <Text style={styles.emptyText}>
              Add interests to find people who share your vibe.
            </Text>
          </NeoCard>
        ) : (
          matches.map((match) => (
            <NeoCard key={match.user_id} style={styles.matchCard}>
              <View style={styles.matchHeader}>
                <View style={styles.avatarContainer}>
                  <View style={styles.avatar}>
                    <Text style={styles.avatarText}>
                      {match.full_name.charAt(0).toUpperCase()}
                    </Text>
                  </View>
                </View>
                <View style={styles.matchInfo}>
                  <View style={styles.matchNameRow}>
                    <Text style={styles.matchName} numberOfLines={1}>
                      {match.full_name}
                    </Text>
                    <NeoBadge
                      label={`${match.score}% Match`}
                      style={styles.scoreBadge}
                    />
                  </View>
                  <Text style={styles.matchBio} numberOfLines={2}>
                    {match.bio || 'Looking for people who share their interests.'}
                  </Text>
                </View>
              </View>

              <View style={styles.interestsContainer}>
                {match.shared_interests.map((interest) => (
                  <NeoBadge
                    key={interest.id}
                    label={`${interest.icon} ${interest.name}`}
                    style={styles.interestBadge}
                  />
                ))}
              </View>

              <View style={styles.actions}>
                <NeoButton
                  title="View Profile"
                  onPress={() => onViewProfile(match.user_id)}
                  variant="secondary"
                  style={styles.actionButton}
                />
                {match.existing_chat_id ? (
                  <NeoButton
                    title="Message"
                    onPress={() => onMessage(match.existing_chat_id!)}
                    variant="primary"
                    style={styles.actionButton}
                  />
                ) : (
                  <NeoButton
                    title="Add Friend"
                    onPress={() => onAddFriend(match.user_id)}
                    variant="primary"
                    style={styles.actionButton}
                  />
                )}
              </View>
            </NeoCard>
          ))
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.surface,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.surface,
  },
  loadingText: {
    marginTop: Spacing.md,
    fontSize: 16,
    color: Colors.onSurfaceVariant,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.page,
    paddingVertical: Spacing.lg,
    backgroundColor: Colors.surfaceContainer,
    borderBottomWidth: Border.default,
    borderBottomColor: Colors.stroke,
    ...Shadow.neoSm,
  },
  backButton: {
    width: 44,
    height: 44,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.surfaceOffWhite,
    borderWidth: Border.default,
    borderColor: Colors.stroke,
    borderRadius: BorderRadius.sm,
  },
  backButtonText: {
    fontSize: 20,
    fontWeight: '700',
    color: Colors.onSurface,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: Colors.primary,
    letterSpacing: -0.5,
  },
  headerRight: {
    width: 44,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: Spacing.page,
    paddingBottom: Spacing.xxl * 2,
  },
  heroSection: {
    alignItems: 'center',
    marginBottom: Spacing.xl,
    paddingVertical: Spacing.lg,
  },
  heroEmoji: {
    fontSize: 48,
    marginBottom: Spacing.sm,
  },
  heroTitle: {
    fontSize: 28,
    fontWeight: '800',
    color: Colors.onSurface,
    letterSpacing: -1,
  },
  heroSubtitle: {
    fontSize: 16,
    color: Colors.onSurfaceVariant,
    marginTop: Spacing.xs,
  },
  errorContainer: {
    backgroundColor: Colors.errorContainer,
    borderWidth: Border.default,
    borderColor: Colors.error,
    borderRadius: BorderRadius.md,
    padding: Spacing.lg,
    marginBottom: Spacing.xl,
    alignItems: 'center',
  },
  errorText: {
    color: Colors.onErrorContainer,
    fontSize: 14,
    marginBottom: Spacing.md,
    textAlign: 'center',
  },
  retryButton: {
    minWidth: 120,
  },
  emptyCard: {
    alignItems: 'center',
    paddingVertical: Spacing.xxl,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: Spacing.md,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: Colors.onSurface,
    marginBottom: Spacing.sm,
  },
  emptyText: {
    fontSize: 14,
    color: Colors.onSurfaceVariant,
    textAlign: 'center',
    lineHeight: 20,
  },
  matchCard: {
    marginBottom: Spacing.lg,
  },
  matchHeader: {
    flexDirection: 'row',
    marginBottom: Spacing.md,
  },
  avatarContainer: {
    marginRight: Spacing.md,
  },
  avatar: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: Colors.primary,
    borderWidth: Border.default,
    borderColor: Colors.stroke,
    justifyContent: 'center',
    alignItems: 'center',
    ...Shadow.neoSm,
  },
  avatarText: {
    fontSize: 28,
    fontWeight: '800',
    color: Colors.white,
  },
  matchInfo: {
    flex: 1,
  },
  matchNameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: Spacing.xs,
  },
  matchName: {
    fontSize: 18,
    fontWeight: '700',
    color: Colors.onSurface,
    flex: 1,
    marginRight: Spacing.sm,
  },
  scoreBadge: {
    backgroundColor: Colors.vividYellow,
  },
  matchBio: {
    fontSize: 14,
    color: Colors.onSurfaceVariant,
    lineHeight: 20,
  },
  interestsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.sm,
    marginBottom: Spacing.lg,
  },
  interestBadge: {
    backgroundColor: Colors.neonLime,
  },
  actions: {
    flexDirection: 'row',
    gap: Spacing.md,
  },
  actionButton: {
    flex: 1,
  },
});
