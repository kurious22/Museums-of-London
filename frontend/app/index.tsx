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
          {/* Large London Skyline Silhouette */}
          <View style={styles.skylineContainer}>
            <View style={styles.skylineBuildings}>
              {/* Big Ben */}
              <View style={styles.bigBen}>
                <View style={styles.bigBenTower} />
                <View style={styles.bigBenTop} />
                <View style={styles.bigBenSpire} />
              </View>
              {/* Building 1 */}
              <View style={[styles.building, { height: 90, width: 40 }]} />
              {/* London Eye */}
              <View style={styles.londonEye}>
                <View style={styles.londonEyeWheel} />
                <View style={styles.londonEyeBase} />
              </View>
              {/* Tower Bridge */}
              <View style={styles.towerBridge}>
                <View style={styles.bridgeTower} />
                <View style={styles.bridgeSpan} />
                <View style={styles.bridgeTower} />
              </View>
              {/* Building 2 */}
              <View style={[styles.building, { height: 110, width: 35 }]} />
              {/* The Shard */}
              <View style={styles.shard} />
              {/* St Paul's Dome */}
              <View style={styles.stPauls}>
                <View style={styles.stPaulsDome} />
                <View style={styles.stPaulsBase} />
              </View>
              {/* Building 3 */}
              <View style={[styles.building, { height: 70, width: 45 }]} />
            </View>
          </View>

          {/* London Street Sign */}
          <View style={styles.streetSignContainer}>
            <View style={styles.streetSignPost} />
            <View style={styles.streetSign}>
              <Text style={styles.streetSignText}>LONDON</Text>
            </View>
          </View>

          <View style={styles.heroContent}>
            <Text style={styles.welcomeText}>WELCOME TO</Text>
            <Text style={styles.appTitle}>Museums of</Text>
            <View style={styles.londonBadge}>
              <Text style={styles.londonText}>LONDON</Text>
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
          
          <LinearGradient
            colors={['#457B9D', '#1D3557']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={styles.statCard}
          >
            <Ionicons name="footsteps" size={28} color="#fff" />
            <Text style={styles.statNumber}>5</Text>
            <Text style={styles.statLabel}>Tours</Text>
          </LinearGradient>
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
  skylineContainer: {
    position: 'absolute',
    bottom: 60,
    left: 0,
    right: 0,
    height: 180,
    opacity: 0.4,
  },
  skylineBuildings: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'space-around',
    height: '100%',
    paddingHorizontal: 5,
  },
  building: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 4,
    borderTopRightRadius: 4,
  },
  bigBen: {
    alignItems: 'center',
  },
  bigBenTower: {
    width: 28,
    height: 100,
    backgroundColor: '#fff',
  },
  bigBenTop: {
    width: 36,
    height: 20,
    backgroundColor: '#fff',
    marginTop: -2,
  },
  bigBenSpire: {
    width: 0,
    height: 0,
    borderLeftWidth: 12,
    borderRightWidth: 12,
    borderBottomWidth: 30,
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
    borderBottomColor: '#fff',
    transform: [{ rotate: '180deg' }],
  },
  londonEye: {
    alignItems: 'center',
  },
  londonEyeWheel: {
    width: 70,
    height: 70,
    borderRadius: 35,
    borderWidth: 4,
    borderColor: '#fff',
  },
  londonEyeBase: {
    width: 5,
    height: 35,
    backgroundColor: '#fff',
    marginTop: -2,
  },
  towerBridge: {
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
  bridgeTower: {
    width: 20,
    height: 85,
    backgroundColor: '#fff',
  },
  bridgeSpan: {
    width: 30,
    height: 20,
    backgroundColor: '#fff',
    marginBottom: 30,
  },
  shard: {
    width: 0,
    height: 0,
    borderLeftWidth: 16,
    borderRightWidth: 16,
    borderBottomWidth: 140,
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
    borderBottomColor: '#fff',
  },
  stPauls: {
    alignItems: 'center',
  },
  stPaulsDome: {
    width: 50,
    height: 30,
    borderTopLeftRadius: 25,
    borderTopRightRadius: 25,
    backgroundColor: '#fff',
  },
  stPaulsBase: {
    width: 60,
    height: 40,
    backgroundColor: '#fff',
    marginTop: -2,
  },
  figuresContainer: {
    position: 'absolute',
    bottom: 240,
    right: 20,
    flexDirection: 'row',
    gap: 15,
  },
  // Female Figure (Pink/Magenta)
  femaleFigure: {
    alignItems: 'center',
  },
  femaleHead: {
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: '#E91E63',
  },
  femaleNeck: {
    width: 6,
    height: 4,
    backgroundColor: '#E91E63',
    marginTop: 1,
  },
  femaleBodyContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginTop: 1,
  },
  femaleArm: {
    width: 5,
    height: 24,
    backgroundColor: '#E91E63',
    borderRadius: 3,
    marginTop: 2,
  },
  femaleArmRight: {
    marginLeft: 2,
  },
  femaleBody: {
    alignItems: 'center',
    marginHorizontal: 2,
  },
  femaleTorso: {
    width: 16,
    height: 14,
    backgroundColor: '#E91E63',
    borderTopLeftRadius: 5,
    borderTopRightRadius: 5,
  },
  femaleWaist: {
    width: 14,
    height: 4,
    backgroundColor: '#E91E63',
  },
  femaleSkirt: {
    width: 0,
    height: 0,
    borderLeftWidth: 14,
    borderRightWidth: 14,
    borderTopWidth: 18,
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
    borderTopColor: '#E91E63',
  },
  femaleLegs: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: 18,
    marginTop: 2,
  },
  femaleLeg: {
    width: 6,
    height: 24,
    backgroundColor: '#E91E63',
    borderRadius: 3,
  },
  // Male Figure (Teal/Cyan)
  maleFigure: {
    alignItems: 'center',
  },
  maleHead: {
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: '#00BCD4',
  },
  maleBody: {
    width: 18,
    height: 26,
    backgroundColor: '#00BCD4',
    borderTopLeftRadius: 4,
    borderTopRightRadius: 4,
    marginTop: 2,
  },
  maleLegs: {
    flexDirection: 'row',
    gap: 4,
  },
  maleLeg: {
    width: 6,
    height: 22,
    backgroundColor: '#00BCD4',
  },
  heroContent: {
    marginTop: 20,
    marginBottom: 24,
  },
  welcomeText: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.7)',
    letterSpacing: 4,
    fontWeight: '600',
  },
  appTitle: {
    fontSize: 38,
    fontWeight: '300',
    color: '#FFFFFF',
    marginTop: 8,
  },
  londonBadge: {
    backgroundColor: '#E63946',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    alignSelf: 'flex-start',
    marginTop: 8,
  },
  londonText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    letterSpacing: 2,
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
