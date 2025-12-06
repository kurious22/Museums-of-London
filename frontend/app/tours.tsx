import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  RefreshControl,
  Dimensions,
  Linking,
  Platform,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter, useFocusEffect } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';

const { width } = Dimensions.get('window');
const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

interface Museum {
  id: string;
  name: string;
  short_description: string;
  image_url: string;
  category: string;
  free_entry: boolean;
  rating: number;
  address: string;
  latitude: number;
  longitude: number;
}

interface Tour {
  id: string;
  name: string;
  description: string;
  duration: string;
  distance: string;
  museum_ids: string[];
  museums: Museum[];
  color: string;
}

export default function ToursScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [tours, setTours] = useState<Tour[]>([]);
  const [customTours, setCustomTours] = useState<Tour[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<'predefined' | 'custom'>('predefined');

  const fetchTours = async () => {
    try {
      const [toursRes, customRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/tours`),
        fetch(`${BACKEND_URL}/api/tours/custom/list`)
      ]);
      const toursData = await toursRes.json();
      const customData = await customRes.json();
      setTours(toursData);
      setCustomTours(customData);
    } catch (error) {
      console.error('Error fetching tours:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchTours();
    }, [])
  );

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchTours();
  }, []);

  const openTourInMaps = (tour: Tour) => {
    if (!tour.museums || tour.museums.length === 0) return;

    // Create waypoints from museums
    const waypoints = tour.museums.map(m => `${m.latitude},${m.longitude}`).join('|');
    const origin = `${tour.museums[0].latitude},${tour.museums[0].longitude}`;
    const destination = `${tour.museums[tour.museums.length - 1].latitude},${tour.museums[tour.museums.length - 1].longitude}`;
    const waypointsMiddle = tour.museums.slice(1, -1).map(m => `${m.latitude},${m.longitude}`).join('|');

    const url = Platform.select({
      ios: `maps://app?saddr=${origin}&daddr=${destination}${waypointsMiddle ? `&waypoints=${waypointsMiddle}` : ''}`,
      android: `https://www.google.com/maps/dir/?api=1&origin=${origin}&destination=${destination}${waypointsMiddle ? `&waypoints=${waypointsMiddle}` : ''}&travelmode=walking`,
      default: `https://www.google.com/maps/dir/?api=1&origin=${origin}&destination=${destination}${waypointsMiddle ? `&waypoints=${waypointsMiddle}` : ''}&travelmode=walking`,
    });

    Linking.openURL(url);
  };

  const deleteCustomTour = async (tourId: string) => {
    try {
      await fetch(`${BACKEND_URL}/api/tours/custom/${tourId}`, { method: 'DELETE' });
      setCustomTours(customTours.filter(t => t.id !== tourId));
    } catch (error) {
      console.error('Error deleting tour:', error);
    }
  };

  const renderTourCard = (tour: Tour, isCustom: boolean = false) => (
    <View key={tour.id} style={styles.tourCard}>
      <LinearGradient
        colors={[tour.color || '#E63946', tour.color ? `${tour.color}80` : '#E6394680']}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.tourHeader}
      >
        <View style={styles.tourHeaderContent}>
          <Ionicons name="map" size={32} color="#fff" />
          <View style={styles.tourTitleContainer}>
            <Text style={styles.tourName}>{tour.name}</Text>
            {!isCustom && (
              <View style={styles.tourMeta}>
                <Text style={styles.tourMetaText}>{tour.duration}</Text>
                <Text style={styles.tourMetaDot}>•</Text>
                <Text style={styles.tourMetaText}>{tour.distance}</Text>
              </View>
            )}
          </View>
        </View>
        {isCustom && (
          <TouchableOpacity
            style={styles.deleteButton}
            onPress={() => deleteCustomTour(tour.id)}
          >
            <Ionicons name="trash-outline" size={20} color="#fff" />
          </TouchableOpacity>
        )}
      </LinearGradient>

      {!isCustom && tour.description && (
        <Text style={styles.tourDescription}>{tour.description}</Text>
      )}

      <View style={styles.museumsContainer}>
        <Text style={styles.museumsTitle}>
          {tour.museums?.length || 0} Museums in this tour
        </Text>
        {tour.museums?.map((museum, index) => (
          <TouchableOpacity
            key={museum.id}
            style={styles.museumItem}
            onPress={() => router.push(`/museum/${museum.id}`)}
          >
            <View style={styles.museumIndex}>
              <Text style={styles.museumIndexText}>{index + 1}</Text>
            </View>
            <Image source={{ uri: museum.image_url }} style={styles.museumThumb} />
            <View style={styles.museumInfo}>
              <Text style={styles.museumName} numberOfLines={1}>{museum.name}</Text>
              <Text style={styles.museumCategory}>{museum.category}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#666" />
          </TouchableOpacity>
        ))}
      </View>

      <TouchableOpacity
        style={[styles.startTourButton, { backgroundColor: tour.color || '#E63946' }]}
        onPress={() => openTourInMaps(tour)}
      >
        <Ionicons name="navigate" size={20} color="#fff" />
        <Text style={styles.startTourText}>Start Tour in Maps</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <StatusBar style="light" />

      {/* Header */}
      <View style={styles.header}>
        <Ionicons name="map" size={28} color="#E63946" />
        <Text style={styles.headerTitle}>Walking Tours</Text>
      </View>
      <Text style={styles.headerSubtitle}>Explore multiple museums in one trip</Text>

      {/* Tabs */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'predefined' && styles.tabActive]}
          onPress={() => setActiveTab('predefined')}
        >
          <Ionicons
            name="compass"
            size={18}
            color={activeTab === 'predefined' ? '#E63946' : '#666'}
          />
          <Text style={[styles.tabText, activeTab === 'predefined' && styles.tabTextActive]}>
            Curated Tours
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'custom' && styles.tabActive]}
          onPress={() => setActiveTab('custom')}
        >
          <Ionicons
            name="create"
            size={18}
            color={activeTab === 'custom' ? '#E63946' : '#666'}
          />
          <Text style={[styles.tabText, activeTab === 'custom' && styles.tabTextActive]}>
            My Tours ({customTours.length})
          </Text>
        </TouchableOpacity>
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#E63946" />
        </View>
      ) : (
        <ScrollView
          style={styles.scrollView}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#E63946" />
          }
        >
          {activeTab === 'predefined' ? (
            <>
              {tours.map(tour => renderTourCard(tour))}
            </>
          ) : (
            <>
              {customTours.length === 0 ? (
                <View style={styles.emptyContainer}>
                  <Ionicons name="create-outline" size={60} color="#333" />
                  <Text style={styles.emptyTitle}>No custom tours yet</Text>
                  <Text style={styles.emptySubtitle}>
                    Create your own walking tour by selecting museums from the Explore tab
                  </Text>
                  <TouchableOpacity
                    style={styles.createButton}
                    onPress={() => router.push('/explore')}
                  >
                    <Text style={styles.createButtonText}>Explore Museums</Text>
                  </TouchableOpacity>
                </View>
              ) : (
                customTours.map(tour => renderTourCard(tour, true))
              )}
            </>
          )}

          <View style={{ height: 100 }} />
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F0F23',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 16,
    gap: 12,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#A8A8A8',
    paddingHorizontal: 20,
    marginTop: 4,
    marginBottom: 16,
  },
  tabContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    gap: 12,
    marginBottom: 16,
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    backgroundColor: '#1A1A2E',
    borderRadius: 12,
    gap: 8,
  },
  tabActive: {
    backgroundColor: 'rgba(230, 57, 70, 0.2)',
    borderWidth: 1,
    borderColor: '#E63946',
  },
  tabText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  tabTextActive: {
    color: '#E63946',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollView: {
    flex: 1,
    paddingHorizontal: 20,
  },
  tourCard: {
    backgroundColor: '#1A1A2E',
    borderRadius: 20,
    marginBottom: 20,
    overflow: 'hidden',
  },
  tourHeader: {
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  tourHeaderContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
    flex: 1,
  },
  tourTitleContainer: {
    flex: 1,
  },
  tourName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  tourMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
    gap: 6,
  },
  tourMetaText: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.8)',
  },
  tourMetaDot: {
    color: 'rgba(255,255,255,0.5)',
  },
  deleteButton: {
    padding: 8,
  },
  tourDescription: {
    fontSize: 14,
    color: '#A8A8A8',
    padding: 16,
    paddingTop: 0,
    lineHeight: 20,
  },
  museumsContainer: {
    padding: 16,
    paddingTop: 0,
  },
  museumsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 12,
  },
  museumItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#252542',
    borderRadius: 12,
    padding: 10,
    marginBottom: 8,
    gap: 12,
  },
  museumIndex: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#E63946',
    justifyContent: 'center',
    alignItems: 'center',
  },
  museumIndexText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#fff',
  },
  museumThumb: {
    width: 50,
    height: 50,
    borderRadius: 8,
  },
  museumInfo: {
    flex: 1,
  },
  museumName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#fff',
  },
  museumCategory: {
    fontSize: 12,
    color: '#A8A8A8',
    marginTop: 2,
  },
  startTourButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    margin: 16,
    marginTop: 8,
    padding: 14,
    borderRadius: 12,
    gap: 8,
  },
  startTourText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 80,
    paddingHorizontal: 40,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 20,
  },
  emptySubtitle: {
    fontSize: 14,
    color: '#A8A8A8',
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 20,
  },
  createButton: {
    backgroundColor: '#E63946',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 20,
    marginTop: 20,
  },
  createButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
});
