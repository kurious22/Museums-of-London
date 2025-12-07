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
  TextInput,
  FlatList,
} from 'react-native';
import ImageViewer from 'react-native-image-zoom-viewer';
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
  const [showTubeMapModal, setShowTubeMapModal] = useState(false);
  const [allMuseums, setAllMuseums] = useState<Museum[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Museum[]>([]);
  const [searching, setSearching] = useState(false);
  const [tipsExpanded, setTipsExpanded] = useState(false);

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

  const openTubeMap = () => {
    setShowTubeMapModal(true);
  };

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (query.trim().length === 0) {
      setSearchResults([]);
      return;
    }
    
    setSearching(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/museums?search=${encodeURIComponent(query)}`);
      const data = await response.json();
      setSearchResults(data);
    } catch (error) {
      console.error('Error searching museums:', error);
    } finally {
      setSearching(false);
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults([]);
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
          {/* London Skyline Image */}
          <Image 
            source={{ uri: 'https://customer-assets.emergentagent.com/job_london-museums-app/artifacts/gbnjdzz9_grok_image_3q2y6h~2.jpg' }}
            style={styles.skylineImage}
            resizeMode="cover"
          />

          <View style={styles.heroContent}>
            <Text style={styles.welcomeText}>WELCOME TO</Text>
            <Text style={styles.museumsOfText}>Museums of</Text>
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

          {/* Central Search Bar - In Hero */}
          <View style={styles.searchSectionInHero}>
            <View style={styles.searchBarContainer}>
              <View style={styles.searchBar}>
                {searching ? (
                  <ActivityIndicator size="small" color="#E63946" />
                ) : (
                  <Ionicons name="search" size={22} color="#A8A8A8" />
                )}
                <TextInput
                  style={styles.searchInput}
                  placeholder="Search museums by name..."
                  placeholderTextColor="#666"
                  value={searchQuery}
                  onChangeText={handleSearch}
                  autoCorrect={false}
                  autoCapitalize="words"
                />
                {searchQuery.length > 0 && (
                  <TouchableOpacity onPress={clearSearch}>
                    <Ionicons name="close-circle" size={22} color="#A8A8A8" />
                  </TouchableOpacity>
                )}
              </View>
            </View>
            
            {/* Search Results */}
            {searchQuery.length > 0 && (
              <View style={styles.searchResultsContainer}>
                {searching ? (
                  <ActivityIndicator size="small" color="#E63946" style={{ marginVertical: 20 }} />
                ) : searchResults.length > 0 ? (
                  searchResults.map((museum) => (
                    <TouchableOpacity
                      key={museum.id}
                      style={styles.searchResultItem}
                      onPress={() => {
                        clearSearch();
                        navigateToMuseum(museum.id);
                      }}
                      activeOpacity={0.7}
                    >
                      <Image source={{ uri: museum.image_url }} style={styles.searchResultImage} />
                      <View style={styles.searchResultInfo}>
                        <Text style={styles.searchResultName} numberOfLines={1}>
                          {museum.name}
                        </Text>
                        <Text style={styles.searchResultCategory}>{museum.category}</Text>
                        <View style={styles.searchResultBadge}>
                          {museum.free_entry && (
                            <View style={styles.searchFreeBadge}>
                              <Text style={styles.searchFreeBadgeText}>FREE</Text>
                            </View>
                          )}
                          <View style={styles.searchRatingBadge}>
                            <Ionicons name="star" size={10} color="#FFD700" />
                            <Text style={styles.searchRatingText}>{museum.rating}</Text>
                          </View>
                        </View>
                      </View>
                      <Ionicons name="chevron-forward" size={20} color="#666" />
                    </TouchableOpacity>
                  ))
                ) : (
                  <View style={styles.noResultsContainer}>
                    <Ionicons name="search-outline" size={40} color="#666" />
                    <Text style={styles.noResultsText}>No museums found</Text>
                  </View>
                )}
              </View>
            )}
          </View>
          
          {/* Hero Buttons */}
          <View style={styles.heroButtons}>
            <TouchableOpacity
              style={styles.tubeMapButton}
              onPress={openTubeMap}
              activeOpacity={0.8}
            >
              <Ionicons name="subway" size={18} color="#fff" />
              <Text style={styles.tubeMapButtonText}>London Underground</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.exploreButton}
              onPress={navigateToExplore}
            >
              <Ionicons name="compass" size={18} color="#fff" />
              <Text style={styles.exploreButtonText}>Explore Museums</Text>
            </TouchableOpacity>
          </View>
        </LinearGradient>

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

      {/* Tube Map Image Modal with Zoom */}
      <Modal
        visible={showTubeMapModal}
        animationType="fade"
        transparent={true}
        onRequestClose={() => setShowTubeMapModal(false)}
      >
        <View style={styles.imageModalContainer}>
          <View style={styles.imageHeader}>
            <Text style={styles.imageTitle}>London Underground Map</Text>
            <TouchableOpacity 
              onPress={() => setShowTubeMapModal(false)}
              style={styles.closeButton}
            >
              <Ionicons name="close-circle" size={40} color="#fff" />
            </TouchableOpacity>
          </View>
          <ImageViewer
            imageUrls={[{
              url: 'https://customer-assets.emergentagent.com/job_culture-compass-6/artifacts/gzyemsxs_tube-map-2025.jpg',
            }]}
            enableSwipeDown={true}
            onSwipeDown={() => setShowTubeMapModal(false)}
            backgroundColor="#000"
            renderIndicator={() => null}
            saveToLocalByLongPress={false}
            doubleClickInterval={250}
            maxOverflow={300}
            enablePreload={true}
          />
        </View>
      </Modal>

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
  // London Skyline Image
  skylineImage: {
    position: 'absolute',
    top: 10,
    right: 10,
    width: 100,
    height: 100,
    opacity: 0.7,
    borderRadius: 8,
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
  welcomeText: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.7)',
    letterSpacing: 4,
    fontWeight: '600',
  },
  museumsOfText: {
    fontSize: 24,
    fontWeight: '400',
    color: '#FFFFFF',
    marginTop: 8,
  },
  heroSubtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 16,
    lineHeight: 24,
  },
  heroButtons: {
    flexDirection: 'column',
    gap: 12,
    marginHorizontal: 20,
    marginTop: 8,
  },
  exploreButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#E63946',
    paddingVertical: 14,
    borderRadius: 20,
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
    paddingVertical: 10,
    borderRadius: 20,
    gap: 6,
  },
  tourButtonText: {
    color: '#E63946',
    fontSize: 13,
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
  // Search Section Styles (In Hero)
  searchSectionInHero: {
    marginHorizontal: 20,
    marginTop: 20,
    marginBottom: 12,
  },
  searchSection: {
    marginHorizontal: 20,
    marginVertical: 20,
    backgroundColor: '#1A1A2E',
    borderRadius: 20,
    padding: 20,
  },
  searchTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 16,
  },
  searchBarContainer: {
    marginBottom: 8,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0F0F23',
    borderRadius: 16,
    paddingHorizontal: 16,
    paddingVertical: 14,
    gap: 12,
    borderWidth: 2,
    borderColor: '#E63946',
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: '#fff',
  },
  searchResultsContainer: {
    marginTop: 12,
    maxHeight: 400,
  },
  searchResultItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0F0F23',
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
    gap: 12,
  },
  searchResultImage: {
    width: 60,
    height: 60,
    borderRadius: 8,
  },
  searchResultInfo: {
    flex: 1,
  },
  searchResultName: {
    fontSize: 15,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 2,
  },
  searchResultCategory: {
    fontSize: 12,
    color: '#E63946',
    marginBottom: 4,
  },
  searchResultBadge: {
    flexDirection: 'row',
    gap: 6,
    alignItems: 'center',
  },
  searchFreeBadge: {
    backgroundColor: '#2A9D8F',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
  },
  searchFreeBadgeText: {
    color: '#fff',
    fontSize: 9,
    fontWeight: 'bold',
  },
  searchRatingBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#333',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    gap: 3,
  },
  searchRatingText: {
    color: '#FFD700',
    fontSize: 10,
    fontWeight: '600',
  },
  noResultsContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 30,
  },
  noResultsText: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
  },
  // Tips Section Styles
  tipsContainer: {
    marginHorizontal: 20,
    marginVertical: 20,
    backgroundColor: '#1A1A2E',
    borderRadius: 20,
    overflow: 'hidden',
  },
  tipsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 20,
  },
  tipsHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    flex: 1,
  },
  tipsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    flex: 1,
  },
  tipsContent: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  tipItem: {
    flexDirection: 'row',
    marginBottom: 16,
    gap: 12,
  },
  tipNumber: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#E63946',
    alignItems: 'center',
    justifyContent: 'center',
  },
  tipNumberText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  tipTextContainer: {
    flex: 1,
  },
  tipTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#F1A208',
    marginBottom: 4,
  },
  tipDescription: {
    fontSize: 14,
    color: '#CCCCCC',
    lineHeight: 20,
  },
  // Image Modal Styles
  imageModalContainer: {
    flex: 1,
    backgroundColor: '#000',
  },
  imageHeader: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 50,
    backgroundColor: 'rgba(0,0,0,0.7)',
    zIndex: 10,
  },
  imageTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  closeButton: {
    padding: 5,
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
    justifyContent: 'center',
    backgroundColor: 'rgba(0, 25, 168, 0.9)',
    borderRadius: 20,
    paddingVertical: 14,
    gap: 8,
  },
  tubeMapButtonText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#fff',
  },
});
