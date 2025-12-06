import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Linking,
  Platform,
  Alert,
  Share,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams, useFocusEffect } from 'expo-router';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

interface TransportLink {
  type: string;
  name: string;
  line?: string;
  routes?: string[];
  distance: string;
}

interface NearbyEatery {
  name: string;
  type: string;
  cuisine?: string;
  distance: string;
  price_range: string;
  address?: string;
  latitude?: number;
  longitude?: number;
}

interface Museum {
  id: string;
  name: string;
  description: string;
  short_description: string;
  address: string;
  latitude: number;
  longitude: number;
  image_url: string;
  category: string;
  free_entry: boolean;
  opening_hours: string;
  website?: string;
  phone?: string;
  transport: TransportLink[];
  nearby_eateries: NearbyEatery[];
  rating: number;
}

export default function MuseumDetailScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { id } = useLocalSearchParams();
  const [museum, setMuseum] = useState<Museum | null>(null);
  const [loading, setLoading] = useState(true);
  const [isFavorite, setIsFavorite] = useState(false);

  const fetchMuseum = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/museums/${id}`);
      const data = await response.json();
      setMuseum(data);
    } catch (error) {
      console.error('Error fetching museum:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkFavorite = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/favorites/check/${id}`);
      const data = await response.json();
      setIsFavorite(data.is_favorite);
    } catch (error) {
      console.error('Error checking favorite:', error);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchMuseum();
      checkFavorite();
    }, [id])
  );

  const toggleFavorite = async () => {
    try {
      if (isFavorite) {
        await fetch(`${BACKEND_URL}/api/favorites/${id}`, { method: 'DELETE' });
      } else {
        await fetch(`${BACKEND_URL}/api/favorites/${id}`, { method: 'POST' });
      }
      setIsFavorite(!isFavorite);
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  const openDirections = () => {
    if (!museum) return;

    const scheme = Platform.select({
      ios: 'maps:',
      android: 'geo:',
    });

    const url = Platform.select({
      ios: `${scheme}?daddr=${museum.latitude},${museum.longitude}&dirflg=d`,
      android: `${scheme}${museum.latitude},${museum.longitude}?q=${museum.latitude},${museum.longitude}(${encodeURIComponent(
        museum.name
      )})`,
      default: `https://www.google.com/maps/dir/?api=1&destination=${museum.latitude},${museum.longitude}`,
    });

    Linking.openURL(url).catch(() => {
      // Fallback to Google Maps in browser
      Linking.openURL(
        `https://www.google.com/maps/dir/?api=1&destination=${museum.latitude},${museum.longitude}`
      );
    });
  };

  const openEateryDirections = (eatery: NearbyEatery) => {
    if (!eatery.latitude || !eatery.longitude) {
      // If no coordinates, just show an alert or do nothing
      return;
    }

    const scheme = Platform.select({
      ios: 'maps:',
      android: 'geo:',
    });

    const url = Platform.select({
      ios: `${scheme}?daddr=${eatery.latitude},${eatery.longitude}&dirflg=w`,
      android: `${scheme}${eatery.latitude},${eatery.longitude}?q=${eatery.latitude},${eatery.longitude}(${encodeURIComponent(
        eatery.name
      )})`,
      default: `https://www.google.com/maps/dir/?api=1&destination=${eatery.latitude},${eatery.longitude}&travelmode=walking`,
    });

    Linking.openURL(url).catch(() => {
      Linking.openURL(
        `https://www.google.com/maps/dir/?api=1&destination=${eatery.latitude},${eatery.longitude}&travelmode=walking`
      );
    });
  };

  const openWebsite = () => {
    if (museum?.website) {
      Linking.openURL(museum.website);
    }
  };

  const callMuseum = () => {
    if (museum?.phone) {
      Linking.openURL(`tel:${museum.phone}`);
    }
  };

  const shareMuseum = async () => {
    if (!museum) return;
    try {
      await Share.share({
        message: `Check out ${museum.name} in London! ${museum.website || ''}`,
        title: museum.name,
      });
    } catch (error) {
      console.error('Error sharing:', error);
    }
  };

  const getTransportIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'tube':
        return 'subway-outline';
      case 'bus':
        return 'bus-outline';
      case 'train':
        return 'train-outline';
      default:
        return 'walk-outline';
    }
  };

  const getEateryIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'pub':
        return 'beer-outline';
      case 'cafe':
        return 'cafe-outline';
      case 'wine bar':
        return 'wine-outline';
      default:
        return 'restaurant-outline';
    }
  };

  if (loading) {
    return (
      <View style={[styles.container, styles.loadingContainer]}>
        <ActivityIndicator size="large" color="#E63946" />
      </View>
    );
  }

  if (!museum) {
    return (
      <View style={[styles.container, styles.loadingContainer]}>
        <Text style={styles.errorText}>Museum not found</Text>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Text style={styles.backButtonText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar style="light" />

      {/* Hero Image */}
      <View style={styles.heroContainer}>
        <Image source={{ uri: museum.image_url }} style={styles.heroImage} />
        <View style={styles.heroOverlay} />

        {/* Back Button & Actions */}
        <View style={[styles.headerActions, { top: insets.top + 10 }]}>
          <TouchableOpacity style={styles.headerButton} onPress={() => router.back()}>
            <Ionicons name="arrow-back" size={24} color="#fff" />
          </TouchableOpacity>
          <View style={styles.headerRight}>
            <TouchableOpacity style={styles.headerButton} onPress={shareMuseum}>
              <Ionicons name="share-outline" size={24} color="#fff" />
            </TouchableOpacity>
            <TouchableOpacity style={styles.headerButton} onPress={toggleFavorite}>
              <Ionicons
                name={isFavorite ? 'heart' : 'heart-outline'}
                size={24}
                color={isFavorite ? '#E63946' : '#fff'}
              />
            </TouchableOpacity>
          </View>
        </View>

        {/* Museum Info Overlay */}
        <View style={styles.heroInfo}>
          <View style={styles.badges}>
            {museum.free_entry ? (
              <View style={styles.freeBadge}>
                <Text style={styles.badgeText}>FREE ENTRY</Text>
              </View>
            ) : (
              <View style={styles.paidBadge}>
                <Text style={styles.badgeText}>TICKETED</Text>
              </View>
            )}
            <View style={styles.ratingBadge}>
              <Ionicons name="star" size={14} color="#FFD700" />
              <Text style={styles.ratingText}>{museum.rating}</Text>
            </View>
          </View>
          <Text style={styles.museumName}>{museum.name}</Text>
          <Text style={styles.museumCategory}>{museum.category}</Text>
        </View>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Quick Actions */}
        <View style={styles.quickActions}>
          <TouchableOpacity style={styles.actionButton} onPress={openDirections}>
            <View style={styles.actionIcon}>
              <Ionicons name="navigate" size={24} color="#E63946" />
            </View>
            <Text style={styles.actionText}>Directions</Text>
          </TouchableOpacity>

          {museum.website && (
            <TouchableOpacity style={styles.actionButton} onPress={openWebsite}>
              <View style={styles.actionIcon}>
                <Ionicons name="globe" size={24} color="#457B9D" />
              </View>
              <Text style={styles.actionText}>Website</Text>
            </TouchableOpacity>
          )}

          {museum.phone && (
            <TouchableOpacity style={styles.actionButton} onPress={callMuseum}>
              <View style={styles.actionIcon}>
                <Ionicons name="call" size={24} color="#2A9D8F" />
              </View>
              <Text style={styles.actionText}>Call</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* About Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>About</Text>
          <Text style={styles.description}>{museum.description}</Text>
        </View>

        {/* Details Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Details</Text>
          <View style={styles.detailItem}>
            <Ionicons name="location-outline" size={20} color="#E63946" />
            <Text style={styles.detailText}>{museum.address}</Text>
          </View>
          <View style={styles.detailItem}>
            <Ionicons name="time-outline" size={20} color="#E63946" />
            <Text style={styles.detailText}>{museum.opening_hours}</Text>
          </View>
        </View>

        {/* Transport Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="train-outline" size={22} color="#E63946" />
            <Text style={styles.sectionTitle}>Getting There</Text>
          </View>
          {museum.transport.map((t, index) => (
            <View key={index} style={styles.transportItem}>
              <View style={styles.transportIcon}>
                <Ionicons name={getTransportIcon(t.type) as any} size={24} color="#fff" />
              </View>
              <View style={styles.transportInfo}>
                <Text style={styles.transportName}>{t.name}</Text>
                {t.line && <Text style={styles.transportLine}>{t.line}</Text>}
                {t.routes && (
                  <Text style={styles.transportLine}>Routes: {t.routes.join(', ')}</Text>
                )}
                <Text style={styles.transportDistance}>{t.distance}</Text>
              </View>
            </View>
          ))}
        </View>

        {/* Nearby Eateries Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="restaurant-outline" size={22} color="#E63946" />
            <Text style={styles.sectionTitle}>Places to Eat</Text>
          </View>
          {museum.nearby_eateries.map((e, index) => (
            <View key={index} style={styles.eateryItem}>
              <View style={styles.eateryIcon}>
                <Ionicons name={getEateryIcon(e.type) as any} size={24} color="#fff" />
              </View>
              <View style={styles.eateryInfo}>
                <Text style={styles.eateryName}>{e.name}</Text>
                <Text style={styles.eateryDetails}>
                  {e.type} {e.cuisine ? `• ${e.cuisine}` : ''}
                </Text>
                <View style={styles.eateryMeta}>
                  <Text style={styles.eateryDistance}>{e.distance}</Text>
                  <Text style={styles.eateryPrice}>{e.price_range}</Text>
                </View>
              </View>
            </View>
          ))}
        </View>

        <View style={{ height: 100 }} />
      </ScrollView>

      {/* Bottom CTA */}
      <View style={[styles.bottomCTA, { paddingBottom: insets.bottom + 10 }]}>
        <TouchableOpacity style={styles.ctaButton} onPress={openDirections}>
          <Ionicons name="navigate" size={20} color="#fff" />
          <Text style={styles.ctaButtonText}>Get Directions</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F0F23',
  },
  loadingContainer: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    fontSize: 18,
    color: '#fff',
    marginBottom: 20,
  },
  backButton: {
    backgroundColor: '#E63946',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 20,
  },
  backButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  heroContainer: {
    height: 340,
    position: 'relative',
  },
  heroImage: {
    width: '100%',
    height: '100%',
  },
  heroOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.4)',
  },
  headerActions: {
    position: 'absolute',
    left: 16,
    right: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  headerButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerRight: {
    flexDirection: 'row',
    gap: 10,
  },
  heroInfo: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
  },
  badges: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 12,
  },
  freeBadge: {
    backgroundColor: '#2A9D8F',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  paidBadge: {
    backgroundColor: '#E9C46A',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  badgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  ratingBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 16,
    gap: 4,
  },
  ratingText: {
    color: '#FFD700',
    fontSize: 13,
    fontWeight: '600',
  },
  museumName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 4,
  },
  museumCategory: {
    fontSize: 15,
    color: '#CCCCCC',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#222',
  },
  actionButton: {
    alignItems: 'center',
  },
  actionIcon: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: '#1A1A2E',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  actionText: {
    fontSize: 13,
    color: '#A8A8A8',
  },
  section: {
    paddingVertical: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#222',
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 4,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 12,
  },
  description: {
    fontSize: 15,
    color: '#CCCCCC',
    lineHeight: 24,
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    marginBottom: 12,
  },
  detailText: {
    flex: 1,
    fontSize: 15,
    color: '#CCCCCC',
    lineHeight: 22,
  },
  transportItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1A1A2E',
    padding: 14,
    borderRadius: 12,
    marginBottom: 10,
    gap: 14,
  },
  transportIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#457B9D',
    justifyContent: 'center',
    alignItems: 'center',
  },
  transportInfo: {
    flex: 1,
  },
  transportName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  transportLine: {
    fontSize: 13,
    color: '#A8A8A8',
    marginTop: 2,
  },
  transportDistance: {
    fontSize: 12,
    color: '#E63946',
    marginTop: 4,
  },
  eateryItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1A1A2E',
    padding: 14,
    borderRadius: 12,
    marginBottom: 10,
    gap: 14,
  },
  eateryIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#2A9D8F',
    justifyContent: 'center',
    alignItems: 'center',
  },
  eateryInfo: {
    flex: 1,
  },
  eateryName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  eateryDetails: {
    fontSize: 13,
    color: '#A8A8A8',
    marginTop: 2,
  },
  eateryMeta: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 4,
  },
  eateryDistance: {
    fontSize: 12,
    color: '#E63946',
  },
  eateryPrice: {
    fontSize: 12,
    color: '#2A9D8F',
    fontWeight: '600',
  },
  bottomCTA: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: '#0F0F23',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#222',
  },
  ctaButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#E63946',
    paddingVertical: 16,
    borderRadius: 12,
    gap: 10,
  },
  ctaButtonText: {
    color: '#fff',
    fontSize: 17,
    fontWeight: '600',
  },
});
