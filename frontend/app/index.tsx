import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Dimensions,
  Platform,
  RefreshControl,
  ImageBackground,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
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
}

export default function HomeScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [featuredMuseums, setFeaturedMuseums] = useState<Museum[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchFeaturedMuseums = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/museums/featured`);
      const data = await response.json();
      setFeaturedMuseums(data);
    } catch (error) {
      console.error('Error fetching museums:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchFeaturedMuseums();
  }, []);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchFeaturedMuseums();
  }, []);

  const navigateToMuseum = (id: string) => {
    router.push(`/museum/${id}`);
  };

  const navigateToExplore = () => {
    router.push('/explore');
  };

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <StatusBar style="light" />
      
      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#E63946" />
        }
      >
        {/* Hero Section with London Skyline */}
        <View style={styles.heroSection}>
          <ImageBackground
            source={{ uri: 'https://images.unsplash.com/photo-1503494975800-45129df82138?w=800' }}
            style={styles.heroImage}
            imageStyle={{ opacity: 0.7 }}
          >
            <View style={styles.heroOverlay}>
              <View style={styles.heroContent}>
                <Text style={styles.welcomeText}>Welcome to</Text>
                <Text style={styles.appTitle}>Museums of</Text>
                <Text style={styles.appTitleHighlight}>London</Text>
                <Text style={styles.heroSubtitle}>
                  Discover world-class art, history, and culture
                </Text>
              </View>
              
              <TouchableOpacity
                style={styles.exploreButton}
                onPress={navigateToExplore}
              >
                <Text style={styles.exploreButtonText}>Explore All Museums</Text>
                <Ionicons name="arrow-forward" size={20} color="#fff" />
              </TouchableOpacity>
            </View>
          </ImageBackground>
        </View>

        {/* Quick Stats */}
        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>20+</Text>
            <Text style={styles.statLabel}>Museums</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>FREE</Text>
            <Text style={styles.statLabel}>Most Entry</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>A-Z</Text>
            <Text style={styles.statLabel}>Categories</Text>
          </View>
        </View>

        {/* Featured Museums Section */}
        <View style={styles.sectionContainer}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Featured Museums</Text>
            <TouchableOpacity onPress={navigateToExplore}>
              <Text style={styles.seeAllText}>See All</Text>
            </TouchableOpacity>
          </View>

          {loading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#E63946" />
            </View>
          ) : (
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.featuredScroll}
            >
              {featuredMuseums.map((museum) => (
                <TouchableOpacity
                  key={museum.id}
                  style={styles.featuredCard}
                  onPress={() => navigateToMuseum(museum.id)}
                  activeOpacity={0.9}
                >
                  <Image
                    source={{ uri: museum.image_url }}
                    style={styles.featuredImage}
                  />
                  <View style={styles.featuredOverlay}>
                    <View style={styles.featuredBadge}>
                      <Text style={styles.badgeText}>
                        {museum.free_entry ? 'FREE' : 'PAID'}
                      </Text>
                    </View>
                    <View style={styles.featuredInfo}>
                      <Text style={styles.featuredName} numberOfLines={2}>
                        {museum.name}
                      </Text>
                      <Text style={styles.featuredCategory}>
                        {museum.category}
                      </Text>
                      <View style={styles.ratingContainer}>
                        <Ionicons name="star" size={14} color="#FFD700" />
                        <Text style={styles.ratingText}>{museum.rating}</Text>
                      </View>
                    </View>
                  </View>
                </TouchableOpacity>
              ))}
            </ScrollView>
          )}
        </View>

        {/* Categories Section */}
        <View style={styles.sectionContainer}>
          <Text style={styles.sectionTitle}>Explore by Category</Text>
          <View style={styles.categoriesGrid}>
            {[
              { name: 'Art', icon: 'color-palette', color: '#E63946' },
              { name: 'History', icon: 'time', color: '#457B9D' },
              { name: 'Science', icon: 'flask', color: '#2A9D8F' },
              { name: 'Culture', icon: 'globe', color: '#E9C46A' },
            ].map((category) => (
              <TouchableOpacity
                key={category.name}
                style={[styles.categoryCard, { borderColor: category.color }]}
                onPress={() => router.push(`/explore?category=${category.name}`)}
              >
                <View style={[styles.categoryIcon, { backgroundColor: category.color + '20' }]}>
                  <Ionicons name={category.icon as any} size={28} color={category.color} />
                </View>
                <Text style={styles.categoryName}>{category.name}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Quick Tips */}
        <View style={styles.tipsContainer}>
          <Text style={styles.tipsTitle}>Visitor Tips</Text>
          <View style={styles.tipItem}>
            <Ionicons name="ticket-outline" size={20} color="#E63946" />
            <Text style={styles.tipText}>Most major museums offer free entry</Text>
          </View>
          <View style={styles.tipItem}>
            <Ionicons name="time-outline" size={20} color="#E63946" />
            <Text style={styles.tipText}>Visit early morning to avoid crowds</Text>
          </View>
          <View style={styles.tipItem}>
            <Ionicons name="train-outline" size={20} color="#E63946" />
            <Text style={styles.tipText}>All museums are accessible by tube</Text>
          </View>
        </View>

        <View style={{ height: 30 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F0F23',
  },
  scrollView: {
    flex: 1,
  },
  heroSection: {
    height: 380,
    marginBottom: 20,
  },
  heroImage: {
    flex: 1,
    width: '100%',
  },
  heroOverlay: {
    flex: 1,
    backgroundColor: 'rgba(15, 15, 35, 0.75)',
    justifyContent: 'flex-end',
    padding: 20,
    paddingBottom: 30,
  },
  heroContent: {
    marginBottom: 24,
  },
  welcomeText: {
    fontSize: 16,
    color: '#A8A8A8',
    letterSpacing: 2,
    textTransform: 'uppercase',
  },
  appTitle: {
    fontSize: 42,
    fontWeight: '300',
    color: '#FFFFFF',
    marginTop: 8,
  },
  appTitleHighlight: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#E63946',
  },
  heroSubtitle: {
    fontSize: 16,
    color: '#CCCCCC',
    marginTop: 12,
    lineHeight: 24,
  },
  exploreButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#E63946',
    paddingVertical: 16,
    paddingHorizontal: 28,
    borderRadius: 30,
    gap: 10,
  },
  exploreButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  statsContainer: {
    flexDirection: 'row',
    backgroundColor: '#1A1A2E',
    marginHorizontal: 20,
    marginBottom: 24,
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#E63946',
  },
  statLabel: {
    fontSize: 12,
    color: '#A8A8A8',
    marginTop: 4,
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: '#333',
  },
  sectionContainer: {
    marginBottom: 28,
    paddingHorizontal: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  seeAllText: {
    fontSize: 14,
    color: '#E63946',
    fontWeight: '600',
  },
  loadingContainer: {
    height: 220,
    justifyContent: 'center',
    alignItems: 'center',
  },
  featuredScroll: {
    paddingRight: 20,
  },
  featuredCard: {
    width: width * 0.65,
    height: 220,
    marginRight: 16,
    borderRadius: 20,
    overflow: 'hidden',
    backgroundColor: '#1A1A2E',
  },
  featuredImage: {
    width: '100%',
    height: '100%',
    position: 'absolute',
  },
  featuredOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.4)',
    padding: 16,
    justifyContent: 'space-between',
  },
  featuredBadge: {
    alignSelf: 'flex-start',
    backgroundColor: '#E63946',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  badgeText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: 'bold',
  },
  featuredInfo: {
    gap: 4,
  },
  featuredName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  featuredCategory: {
    fontSize: 13,
    color: '#CCCCCC',
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 4,
  },
  ratingText: {
    fontSize: 13,
    color: '#FFD700',
    fontWeight: '600',
  },
  categoriesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginTop: 16,
  },
  categoryCard: {
    width: (width - 52) / 2,
    backgroundColor: '#1A1A2E',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    borderWidth: 1,
  },
  categoryIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  categoryName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#fff',
  },
  tipsContainer: {
    marginHorizontal: 20,
    backgroundColor: '#1A1A2E',
    borderRadius: 16,
    padding: 20,
  },
  tipsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 16,
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 12,
  },
  tipText: {
    fontSize: 14,
    color: '#CCCCCC',
    flex: 1,
  },
});
