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
  Linking,
  Alert,
  Modal,
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
  const [showMapModal, setShowMapModal] = useState(false);
  const [allMuseums, setAllMuseums] = useState<Museum[]>([]);

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

  const fetchAllMuseums = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/museums`);
      const data = await response.json();
      setAllMuseums(data);
    } catch (error) {
      console.error('Error fetching all museums:', error);
    }
  };

  const openMuseumMap = () => {
    fetchAllMuseums();
    setShowMapModal(true);
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

  const navigateToTours = () => {
    router.push('/tours');
  };

  const openTubeMap = async () => {
    const tubeMapUrl = 'https://tfl.gov.uk/maps/track/tube';
    try {
      const supported = await Linking.canOpenURL(tubeMapUrl);
      if (supported) {
        await Linking.openURL(tubeMapUrl);
      } else {
        Alert.alert('Error', 'Cannot open the Tube map');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to open the Tube map');
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#E63946" />
        }
      >
        {/* Colorful Hero Section with London Theme */}
        <LinearGradient
          colors={['#1A1A2E', '#16213E', '#0F3460', '#E94560']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={[styles.heroSection, { paddingTop: insets.top + 20 }]}
        >
          {/* Small London Skyline Top Right */}
          <View style={styles.smallSkyline}>
            <View style={styles.smallBigBen}>
              <View style={styles.smallBigBenTower} />
              <View style={styles.smallBigBenSpire} />
            </View>
            <View style={[styles.smallBuilding, { height: 30 }]} />
            <View style={styles.smallShard} />
            <View style={[styles.smallBuilding, { height: 25 }]} />
            <View style={styles.smallLondonEye} />
          </View>

          <View style={styles.heroContent}>
            <Text style={styles.welcomeText}>WELCOME TO</Text>
            <Text style={styles.appTitle}>Museums of</Text>
            <View style={styles.londonRow}>
              <View style={styles.londonBadge}>
                <Text style={styles.londonText}>LONDON</Text>
              </View>
              <Ionicons name="globe-outline" size={28} color="#fff" style={styles.londonGlobe} />
            </View>
            <Text style={styles.heroSubtitle}>
              Discover world-class art, history, and culture
            </Text>
          </View>
          
          <View style={styles.heroButtons}>
            <TouchableOpacity
              style={styles.exploreButton}
              onPress={navigateToExplore}
            >
              <Ionicons name="compass" size={20} color="#fff" />
              <Text style={styles.exploreButtonText}>Explore Museums</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.tourButton}
              onPress={navigateToTours}
            >
              <Ionicons name="map" size={20} color="#E63946" />
              <Text style={styles.tourButtonText}>Walking Tours</Text>
            </TouchableOpacity>
          </View>

          {/* Tube Map Button */}
          <TouchableOpacity
            style={styles.tubeMapButton}
            onPress={openTubeMap}
            activeOpacity={0.8}
          >
            <View style={styles.tubeMapIconContainer}>
              <Ionicons name="subway" size={24} color="#fff" />
            </View>
            <View style={styles.tubeMapTextContainer}>
              <Text style={styles.tubeMapTitle}>London Underground Map</Text>
              <Text style={styles.tubeMapSubtitle}>View the Tube network</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#fff" />
          </TouchableOpacity>
        </LinearGradient>

        {/* Colorful Quick Stats */}
        <View style={styles.statsContainer}>
          <LinearGradient
            colors={['#E63946', '#F1A208']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={styles.statCard}
          >
            <Ionicons name="business" size={28} color="#fff" />
            <Text style={styles.statNumber}>20+</Text>
            <Text style={styles.statLabel}>Museums</Text>
          </LinearGradient>
          
          <LinearGradient
            colors={['#2A9D8F', '#38B000']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={styles.statCard}
          >
            <Ionicons name="ticket" size={28} color="#fff" />
            <Text style={styles.statNumber}>FREE</Text>
            <Text style={styles.statLabel}>Entry</Text>
          </LinearGradient>
          
          <TouchableOpacity onPress={openMuseumMap}>
            <LinearGradient
              colors={['#457B9D', '#1D3557']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.statCard}
            >
              <Ionicons name="map" size={28} color="#fff" />
              <Text style={styles.statNumber}>MAP</Text>
              <Text style={styles.statLabel}>View All</Text>
            </LinearGradient>
          </TouchableOpacity>
        </View>

        {/* Featured Museums Section */}
        <View style={styles.sectionContainer}>
          <View style={styles.sectionHeader}>
            <View style={styles.sectionTitleContainer}>
              <Ionicons name="star" size={22} color="#F1A208" />
              <Text style={styles.sectionTitle}>Featured Museums</Text>
            </View>
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
              {featuredMuseums.map((museum, index) => (
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
                  <LinearGradient
                    colors={['transparent', 'rgba(0,0,0,0.8)']}
                    style={styles.featuredOverlay}
                  >
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
                  </LinearGradient>
                </TouchableOpacity>
              ))}
            </ScrollView>
          )}
        </View>

        {/* Colorful Categories Section */}
        <View style={styles.sectionContainer}>
          <View style={styles.sectionTitleContainer}>
            <Ionicons name="grid" size={22} color="#457B9D" />
            <Text style={styles.sectionTitle}>Explore by Category</Text>
          </View>
          <View style={styles.categoriesGrid}>
            {[
              { name: 'Art', icon: 'color-palette', colors: ['#E63946', '#FF6B6B'] },
              { name: 'History', icon: 'time', colors: ['#457B9D', '#6BA3BE'] },
              { name: 'Science', icon: 'flask', colors: ['#2A9D8F', '#52C9B9'] },
              { name: 'Culture', icon: 'globe', colors: ['#E9C46A', '#F4D35E'] },
            ].map((category) => (
              <TouchableOpacity
                key={category.name}
                onPress={() => router.push(`/explore?category=${category.name}`)}
                activeOpacity={0.8}
              >
                <LinearGradient
                  colors={category.colors}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 1 }}
                  style={styles.categoryCard}
                >
                  <View style={styles.categoryIcon}>
                    <Ionicons name={category.icon as any} size={32} color="#fff" />
                  </View>
                  <Text style={styles.categoryName}>{category.name}</Text>
                </LinearGradient>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Walking Tours Promo */}
        <View style={styles.sectionContainer}>
          <TouchableOpacity onPress={navigateToTours} activeOpacity={0.9}>
            <LinearGradient
              colors={['#9B59B6', '#3498DB', '#1ABC9C']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={styles.tourPromo}
            >
              <View style={styles.tourPromoContent}>
                <Ionicons name="walk" size={40} color="#fff" />
                <View style={styles.tourPromoText}>
                  <Text style={styles.tourPromoTitle}>Walking Tours</Text>
                  <Text style={styles.tourPromoSubtitle}>
                    Explore multiple museums in one day with our curated routes!
                  </Text>
                </View>
              </View>
              <View style={styles.tourPromoArrow}>
                <Ionicons name="arrow-forward-circle" size={32} color="#fff" />
              </View>
            </LinearGradient>
          </TouchableOpacity>
        </View>

        {/* Fun Tips Section */}
        <View style={styles.tipsContainer}>
          <View style={styles.sectionTitleContainer}>
            <Ionicons name="bulb" size={22} color="#F1A208" />
            <Text style={styles.sectionTitle}>Visitor Tips</Text>
          </View>
          <View style={styles.tipsList}>
            {[
              { icon: 'ticket-outline', text: 'Most major museums offer free entry', color: '#2A9D8F' },
              { icon: 'time-outline', text: 'Visit early morning to avoid crowds', color: '#E63946' },
              { icon: 'train-outline', text: 'All museums are accessible by tube', color: '#457B9D' },
              { icon: 'camera-outline', text: 'Photography usually allowed (no flash)', color: '#9B59B6' },
            ].map((tip, index) => (
              <View key={index} style={styles.tipItem}>
                <View style={[styles.tipIconContainer, { backgroundColor: tip.color + '20' }]}>
                  <Ionicons name={tip.icon as any} size={20} color={tip.color} />
                </View>
                <Text style={styles.tipText}>{tip.text}</Text>
              </View>
            ))}
          </View>
        </View>

        <View style={{ height: 30 }} />
      </ScrollView>

      {/* Museum Map Modal */}
      <Modal
        visible={showMapModal}
        animationType="slide"
        transparent={false}
        onRequestClose={() => setShowMapModal(false)}
      >
        <View style={styles.mapModalContainer}>
          <View style={styles.mapHeader}>
            <Text style={styles.mapTitle}>London Museums Map</Text>
            <TouchableOpacity onPress={() => setShowMapModal(false)}>
              <Ionicons name="close-circle" size={32} color="#E63946" />
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.mapScrollView}>
            {/* Cartoon Map Background */}
            <View style={styles.cartoonMap}>
              <Text style={styles.mapWatermark}>London</Text>
              
              {/* River Thames illustration */}
              <View style={styles.thamesRiver} />

              {/* Museum Pins */}
              {allMuseums.map((museum, index) => (
                <TouchableOpacity
                  key={museum.id}
                  style={[styles.museumPin, { 
                    top: `${15 + (index % 6) * 14}%`, 
                    left: `${10 + (index % 4) * 22}%` 
                  }]}
                  onPress={() => {
                    setShowMapModal(false);
                    router.push(`/museum/${museum.id}`);
                  }}
                >
                  <View style={styles.pinHead}>
                    <Ionicons name="business" size={16} color="#fff" />
                  </View>
                  <View style={styles.pinStick} />
                  <Text style={styles.pinLabel}>{museum.name}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </ScrollView>
        </View>
      </Modal>
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
    paddingHorizontal: 20,
    paddingBottom: 30,
    minHeight: 420,
  },
  // Small Skyline Top Right
  smallSkyline: {
    position: 'absolute',
    top: 10,
    right: 15,
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 3,
    opacity: 0.6,
  },
  smallBigBen: {
    alignItems: 'center',
  },
  smallBigBenTower: {
    width: 6,
    height: 22,
    backgroundColor: '#fff',
  },
  smallBigBenSpire: {
    width: 0,
    height: 0,
    borderLeftWidth: 3,
    borderRightWidth: 3,
    borderBottomWidth: 6,
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
    borderBottomColor: '#fff',
    transform: [{ rotate: '180deg' }],
  },
  smallBuilding: {
    width: 8,
    backgroundColor: '#fff',
    borderTopLeftRadius: 2,
    borderTopRightRadius: 2,
  },
  smallShard: {
    width: 0,
    height: 0,
    borderLeftWidth: 4,
    borderRightWidth: 4,
    borderBottomWidth: 28,
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
    borderBottomColor: '#fff',
  },
  smallLondonEye: {
    width: 16,
    height: 16,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#fff',
  },
  londonRow: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    marginTop: 8,
  },
  londonBadge: {
    backgroundColor: '#E63946',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  londonText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    letterSpacing: 2,
  },
  londonGlobe: {
    marginLeft: 12,
  },
  heroSubtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 16,
    lineHeight: 24,
  },
  heroButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  exploreButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#E63946',
    paddingVertical: 14,
    borderRadius: 25,
    gap: 8,
  },
  exploreButtonText: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '600',
  },
  tourButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
    paddingVertical: 14,
    borderRadius: 25,
    gap: 8,
  },
  tourButtonText: {
    color: '#E63946',
    fontSize: 15,
    fontWeight: '600',
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginTop: -15,
    marginBottom: 24,
    gap: 10,
  },
  statCard: {
    flex: 1,
    alignItems: 'center',
    padding: 16,
    borderRadius: 16,
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 6,
  },
  statLabel: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 2,
  },
  sectionContainer: {
    marginBottom: 24,
    paddingHorizontal: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
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
  },
  categoryCard: {
    width: (width - 52) / 2,
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
  },
  categoryIcon: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  categoryName: {
    fontSize: 15,
    fontWeight: '600',
    color: '#fff',
  },
  tourPromo: {
    borderRadius: 20,
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  tourPromoContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    gap: 16,
  },
  tourPromoText: {
    flex: 1,
  },
  tourPromoTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  tourPromoSubtitle: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.9)',
    marginTop: 4,
    lineHeight: 18,
  },
  tourPromoArrow: {
    marginLeft: 8,
  },
  tipsContainer: {
    marginHorizontal: 20,
    backgroundColor: '#1A1A2E',
    borderRadius: 20,
    padding: 20,
  },
  tipsList: {
    gap: 12,
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
  },
  tipIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  tipText: {
    fontSize: 14,
    color: '#CCCCCC',
    flex: 1,
  },
  // Museum Map Modal Styles
  mapModalContainer: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  mapHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 50,
    backgroundColor: '#fff',
    borderBottomWidth: 2,
    borderBottomColor: '#E63946',
  },
  mapTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1D3557',
  },
  mapScrollView: {
    flex: 1,
  },
  cartoonMap: {
    minHeight: 1200,
    backgroundColor: '#E8F4F8',
    position: 'relative',
    padding: 20,
  },
  mapWatermark: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: [{ translateX: -50 }, { translateY: -50 }],
    fontSize: 80,
    fontWeight: 'bold',
    color: 'rgba(157, 201, 219, 0.3)',
    letterSpacing: 10,
  },
  thamesRiver: {
    position: 'absolute',
    top: '60%',
    left: 0,
    right: 0,
    height: 60,
    backgroundColor: '#5FA8D3',
    borderRadius: 30,
    opacity: 0.5,
  },
  museumPin: {
    position: 'absolute',
    alignItems: 'center',
    width: 80,
  },
  pinHead: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#E63946',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 3,
    borderColor: '#fff',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  pinStick: {
    width: 3,
    height: 15,
    backgroundColor: '#8B2E2E',
  },
  pinLabel: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#1D3557',
    textAlign: 'center',
    marginTop: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
  },
  tubeMapButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 25, 168, 0.9)',
    borderRadius: 16,
    padding: 16,
    marginHorizontal: 20,
    marginTop: 20,
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.2)',
    shadowColor: '#0019A8',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  tubeMapIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  tubeMapTextContainer: {
    flex: 1,
  },
  tubeMapTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 2,
  },
  tubeMapSubtitle: {
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.8)',
  },
});
