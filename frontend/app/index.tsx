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
import i18n from '../i18n/config';

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
  const [currencyAmount, setCurrencyAmount] = useState('100');
  const [selectedCurrency, setSelectedCurrency] = useState('USD');
  const [convertedAmount, setConvertedAmount] = useState('0');
  const [showLanguageModal, setShowLanguageModal] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState({ code: 'en', name: 'English', flag: '🇬🇧' });
  const [, forceUpdate] = useState({});

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

  const convertCurrency = (amount: string, fromCurrency: string) => {
    const numAmount = parseFloat(amount) || 0;
    // Exchange rates to GBP (approximate)
    const rates: { [key: string]: number } = {
      'USD': 0.79,
      'EUR': 0.85,
      'JPY': 0.0054,
      'AUD': 0.51,
      'CAD': 0.58,
      'CHF': 0.90,
      'CNY': 0.11,
      'INR': 0.0095,
      'KRW': 0.00059,
      'MXN': 0.039,
      'BRL': 0.13,
      'SGD': 0.58,
      'NZD': 0.47,
      'HKD': 0.10,
      'AED': 0.22,
      'GBP': 1.00,
    };
    const converted = numAmount * (rates[fromCurrency] || 1);
    setConvertedAmount(converted.toFixed(2));
  };

  useEffect(() => {
    convertCurrency(currencyAmount, selectedCurrency);
  }, [currencyAmount, selectedCurrency]);

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
          {/* Language Selector Button - Top Right */}
          <TouchableOpacity 
            style={styles.languageButton}
            onPress={() => setShowLanguageModal(true)}
            activeOpacity={0.8}
          >
            <Text style={styles.languageFlag}>{selectedLanguage.flag}</Text>
            <Ionicons name="chevron-down" size={16} color="#fff" />
          </TouchableOpacity>

          <View style={styles.heroContent}>
            <Text style={styles.welcomeText}>{i18n.t('welcome')}</Text>
            <Text style={styles.museumsOfText}>{i18n.t('museumsOf')}</Text>
            <View style={styles.londonRow}>
              <View style={styles.londonBadge}>
                <Text style={styles.londonText}>{i18n.t('london')}</Text>
              </View>
              <Ionicons name="globe-outline" size={28} color="#fff" style={styles.londonGlobe} />
            </View>
            <Text style={styles.heroSubtitle}>
              {i18n.t('subtitle')}
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
                  placeholder={i18n.t('searchPlaceholder')}
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

        {/* Museum Tips Section - Collapsible */}
        <View style={styles.tipsContainer}>
          <TouchableOpacity 
            style={styles.tipsHeader}
            onPress={() => setTipsExpanded(!tipsExpanded)}
            activeOpacity={0.7}
          >
            <View style={styles.tipsHeaderLeft}>
              <Ionicons name="bulb" size={22} color="#F1A208" />
              <Text style={styles.tipsTitle}>Top 10 Tips for Visiting Museums</Text>
            </View>
            <Ionicons 
              name={tipsExpanded ? "chevron-up" : "chevron-down"} 
              size={24} 
              color="#fff" 
            />
          </TouchableOpacity>

          {tipsExpanded && (
            <View style={styles.tipsContent}>
              {[
                { title: "Plan Ahead", desc: "Research the museums you want to visit and their exhibitions. Some may require advanced bookings, especially for special exhibits." },
                { title: "Check Opening Hours", desc: "Many museums have varying opening times, so make sure to check before you go." },
                { title: "Free Entry", desc: "Many of London's museums, like the British Museum and the Natural History Museum, offer free entry. Take advantage of this!" },
                { title: "Visit on Weekdays", desc: "If possible, visit during weekdays to avoid large crowds, especially during peak tourist seasons." },
                { title: "Use the Audio Guide", desc: "Many museums offer audio guides or apps; they can enrich your experience by providing in-depth information about exhibits." },
                { title: "Take Your Time", desc: "Don't rush through the exhibits; spend time at the pieces that interest you the most." },
                { title: "Join a Guided Tour", desc: "Consider joining a guided tour for insights from knowledgeable guides and to explore sections you might overlook." },
                { title: "Stay Together", desc: "If visiting with a group, set meeting points or times to regroup since museums can be large and overwhelming." },
                { title: "Explore the Gift Shops", desc: "Museum gift shops often sell unique items related to the exhibitions and can be a great place to find souvenirs." },
                { title: "Check Temporary Exhibitions", desc: "Look for any temporary exhibitions that may be taking place during your visit, as they often feature special collections or themes." }
              ].map((tip, index) => (
                <View key={index} style={styles.tipItem}>
                  <View style={styles.tipNumber}>
                    <Text style={styles.tipNumberText}>{index + 1}</Text>
                  </View>
                  <View style={styles.tipTextContainer}>
                    <Text style={styles.tipTitle}>{tip.title}</Text>
                    <Text style={styles.tipDescription}>{tip.desc}</Text>
                  </View>
                </View>
              ))}
            </View>
          )}
        </View>

        {/* Currency Conversion Section */}
        <View style={styles.currencyContainer}>
          <View style={styles.currencyHeader}>
            <Ionicons name="cash" size={22} color="#2A9D8F" />
            <Text style={styles.currencyTitle}>Currency Converter</Text>
          </View>
          <Text style={styles.currencySubtitle}>Convert to British Pounds (GBP)</Text>
          
          <View style={styles.currencyContent}>
            <View style={styles.currencyInputRow}>
              <View style={styles.currencyInputContainer}>
                <Text style={styles.currencyLabel}>Amount</Text>
                <TextInput
                  style={styles.currencyInput}
                  value={currencyAmount}
                  onChangeText={setCurrencyAmount}
                  keyboardType="numeric"
                  placeholder="100"
                  placeholderTextColor="#666"
                />
              </View>
              
              <View style={styles.currencyPickerContainer}>
                <View style={styles.currencyLabelRow}>
                  <Text style={styles.currencyLabel}>From </Text>
                  <Text style={styles.currencyScrollHint}>scroll left to right</Text>
                </View>
                <View style={styles.currencyPickerWrapper}>
                  <ScrollView 
                    horizontal 
                    showsHorizontalScrollIndicator={false} 
                    style={styles.currencyScroll}
                    contentContainerStyle={{ paddingRight: 8 }}
                  >
                    {['USD', 'EUR', 'JPY', 'CNY', 'AUD', 'CAD', 'CHF', 'INR', 'KRW', 'MXN', 'BRL', 'SGD', 'NZD', 'HKD', 'AED'].map((currency) => (
                      <TouchableOpacity
                        key={currency}
                        style={[
                          styles.currencyOption,
                          selectedCurrency === currency && styles.currencyOptionActive
                        ]}
                        onPress={() => setSelectedCurrency(currency)}
                      >
                        <Text style={[
                          styles.currencyOptionText,
                          selectedCurrency === currency && styles.currencyOptionTextActive
                        ]}>
                          {currency}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </ScrollView>
                </View>
              </View>
            </View>
            
            <View style={styles.currencyResultContainer}>
              <Ionicons name="arrow-down" size={24} color="#2A9D8F" />
              <View style={styles.currencyResult}>
                <Text style={styles.currencyResultAmount}>£{convertedAmount}</Text>
                <Text style={styles.currencyResultLabel}>GBP</Text>
              </View>
            </View>
            
            <Text style={styles.currencyDisclaimer}>
              * Approximate rates. Check current rates before exchanging.
            </Text>
          </View>
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

      {/* Language Selection Modal */}
      <Modal
        visible={showLanguageModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowLanguageModal(false)}
      >
        <View style={styles.languageModalOverlay}>
          <View style={styles.languageModalContainer}>
            <View style={styles.languageModalHeader}>
              <Text style={styles.languageModalTitle}>{i18n.t('selectLanguage')}</Text>
              <TouchableOpacity onPress={() => setShowLanguageModal(false)}>
                <Ionicons name="close" size={28} color="#fff" />
              </TouchableOpacity>
            </View>
            
            <ScrollView style={styles.languageList}>
              {[
                { code: 'en', name: 'English', flag: '🇬🇧' },
                { code: 'es', name: 'Español', flag: '🇪🇸' },
                { code: 'fr', name: 'Français', flag: '🇫🇷' },
                { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
                { code: 'zh', name: '中文', flag: '🇨🇳' },
                { code: 'ja', name: '日本語', flag: '🇯🇵' },
                { code: 'ko', name: '한국어', flag: '🇰🇷' },
                { code: 'pt', name: 'Português', flag: '🇵🇹' },
                { code: 'it', name: 'Italiano', flag: '🇮🇹' },
                { code: 'ru', name: 'Русский', flag: '🇷🇺' },
                { code: 'ar', name: 'العربية', flag: '🇸🇦' },
                { code: 'hi', name: 'हिन्दी', flag: '🇮🇳' },
                { code: 'nl', name: 'Nederlands', flag: '🇳🇱' },
                { code: 'tr', name: 'Türkçe', flag: '🇹🇷' },
                { code: 'pl', name: 'Polski', flag: '🇵🇱' },
                { code: 'sv', name: 'Svenska', flag: '🇸🇪' },
                { code: 'no', name: 'Norsk', flag: '🇳🇴' },
                { code: 'da', name: 'Dansk', flag: '🇩🇰' },
                { code: 'fi', name: 'Suomi', flag: '🇫🇮' },
                { code: 'el', name: 'Ελληνικά', flag: '🇬🇷' },
              ].map((language) => (
                <TouchableOpacity
                  key={language.code}
                  style={[
                    styles.languageItem,
                    selectedLanguage.code === language.code && styles.languageItemActive
                  ]}
                  onPress={() => {
                    setSelectedLanguage(language);
                    i18n.locale = language.code;
                    setShowLanguageModal(false);
                    forceUpdate({});
                    Alert.alert(
                      i18n.t('languageChanged'),
                      `${i18n.t('languageSetTo')} ${language.name}`,
                      [{ text: 'OK' }]
                    );
                  }}
                  activeOpacity={0.7}
                >
                  <Text style={styles.languageItemFlag}>{language.flag}</Text>
                  <Text style={styles.languageItemName}>{language.name}</Text>
                  {selectedLanguage.code === language.code && (
                    <Ionicons name="checkmark-circle" size={24} color="#2A9D8F" />
                  )}
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
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
  // Currency Conversion Styles
  currencyContainer: {
    marginHorizontal: 20,
    marginVertical: 20,
    backgroundColor: '#1A1A2E',
    borderRadius: 20,
    padding: 20,
  },
  currencyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 4,
  },
  currencyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  currencySubtitle: {
    fontSize: 14,
    color: '#2A9D8F',
    marginBottom: 20,
  },
  currencyContent: {
    gap: 16,
  },
  currencyInputRow: {
    gap: 16,
  },
  currencyInputContainer: {
    marginBottom: 12,
  },
  currencyLabelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  currencyLabel: {
    fontSize: 14,
    color: '#CCCCCC',
  },
  currencyScrollHint: {
    fontSize: 12,
    color: '#E63946',
    fontStyle: 'italic',
  },
  currencyInput: {
    backgroundColor: '#0F0F23',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 18,
    color: '#fff',
    borderWidth: 2,
    borderColor: '#2A9D8F',
  },
  currencyPickerContainer: {
    marginBottom: 12,
  },
  currencyPickerWrapper: {
    backgroundColor: '#0F0F23',
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#2A9D8F',
    padding: 8,
    height: 50,
  },
  currencyScroll: {
    flex: 1,
  },
  currencyOption: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
    marginRight: 8,
    backgroundColor: '#1A1A2E',
  },
  currencyOptionActive: {
    backgroundColor: '#2A9D8F',
  },
  currencyOptionText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#CCCCCC',
  },
  currencyOptionTextActive: {
    color: '#fff',
  },
  currencyResultContainer: {
    alignItems: 'center',
    gap: 12,
    paddingVertical: 16,
  },
  currencyResult: {
    alignItems: 'center',
    backgroundColor: '#0F0F23',
    borderRadius: 16,
    padding: 20,
    width: '100%',
  },
  currencyResultAmount: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#2A9D8F',
    marginBottom: 4,
  },
  currencyResultLabel: {
    fontSize: 16,
    color: '#CCCCCC',
    fontWeight: '600',
  },
  currencyDisclaimer: {
    fontSize: 12,
    color: '#999',
    fontStyle: 'italic',
    textAlign: 'center',
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
  // Language Selector Styles
  languageButton: {
    position: 'absolute',
    top: 10,
    right: 20,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    gap: 6,
    zIndex: 10,
  },
  languageFlag: {
    fontSize: 20,
  },
  languageModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'flex-end',
  },
  languageModalContainer: {
    backgroundColor: '#1A1A2E',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    maxHeight: '80%',
  },
  languageModalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  languageModalTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
  },
  languageList: {
    padding: 16,
  },
  languageItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    marginBottom: 8,
    backgroundColor: '#0F0F23',
    borderRadius: 12,
    gap: 16,
  },
  languageItemActive: {
    backgroundColor: '#2A4A3F',
    borderWidth: 2,
    borderColor: '#2A9D8F',
  },
  languageItemFlag: {
    fontSize: 28,
  },
  languageItemName: {
    fontSize: 18,
    color: '#fff',
    flex: 1,
    fontWeight: '500',
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
