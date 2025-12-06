import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';

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
}

export default function AdminScreen() {
  const insets = useSafeAreaInsets();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [pin, setPin] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Museum form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [shortDescription, setShortDescription] = useState('');
  const [address, setAddress] = useState('');
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [category, setCategory] = useState('');
  const [freeEntry, setFreeEntry] = useState(true);
  const [openingHours, setOpeningHours] = useState('');
  const [website, setWebsite] = useState('');
  const [phone, setPhone] = useState('');
  const [rating, setRating] = useState('4.5');

  // Transport links
  const [transportLinks, setTransportLinks] = useState<TransportLink[]>([]);
  const [newTransportType, setNewTransportType] = useState('tube');
  const [newTransportName, setNewTransportName] = useState('');
  const [newTransportLine, setNewTransportLine] = useState('');
  const [newTransportDistance, setNewTransportDistance] = useState('');

  // Nearby eateries
  const [eateries, setEateries] = useState<NearbyEatery[]>([]);
  const [newEateryName, setNewEateryName] = useState('');
  const [newEateryType, setNewEateryType] = useState('Cafe');
  const [newEateryCuisine, setNewEateryCuisine] = useState('');
  const [newEateryDistance, setNewEateryDistance] = useState('');
  const [newEateryPrice, setNewEateryPrice] = useState('££');

  const verifyPin = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pin }),
      });
      const data = await response.json();
      if (response.ok) {
        setIsAuthenticated(true);
      } else {
        Alert.alert('Error', 'Invalid PIN. Please try again.');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to verify PIN.');
    } finally {
      setLoading(false);
    }
  };

  const addTransportLink = () => {
    if (!newTransportName || !newTransportDistance) {
      Alert.alert('Error', 'Please fill in transport name and distance.');
      return;
    }
    setTransportLinks([...transportLinks, {
      type: newTransportType,
      name: newTransportName,
      line: newTransportLine || undefined,
      distance: newTransportDistance,
    }]);
    setNewTransportName('');
    setNewTransportLine('');
    setNewTransportDistance('');
  };

  const removeTransportLink = (index: number) => {
    setTransportLinks(transportLinks.filter((_, i) => i !== index));
  };

  const addEatery = () => {
    if (!newEateryName || !newEateryDistance) {
      Alert.alert('Error', 'Please fill in eatery name and distance.');
      return;
    }
    setEateries([...eateries, {
      name: newEateryName,
      type: newEateryType,
      cuisine: newEateryCuisine || undefined,
      distance: newEateryDistance,
      price_range: newEateryPrice,
    }]);
    setNewEateryName('');
    setNewEateryCuisine('');
    setNewEateryDistance('');
  };

  const removeEatery = (index: number) => {
    setEateries(eateries.filter((_, i) => i !== index));
  };

  const submitMuseum = async () => {
    if (!name || !description || !shortDescription || !address || !latitude || !longitude || !imageUrl || !category || !openingHours) {
      Alert.alert('Error', 'Please fill in all required fields.');
      return;
    }

    setSubmitting(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/museums?pin=${pin}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          description,
          short_description: shortDescription,
          address,
          latitude: parseFloat(latitude),
          longitude: parseFloat(longitude),
          image_url: imageUrl,
          category,
          free_entry: freeEntry,
          opening_hours: openingHours,
          website: website || null,
          phone: phone || null,
          rating: parseFloat(rating),
          transport: transportLinks,
          nearby_eateries: eateries,
          featured: false,
        }),
      });
      const data = await response.json();
      if (response.ok) {
        Alert.alert('Success', `Museum "${name}" has been added successfully!`);
        // Reset form
        setName('');
        setDescription('');
        setShortDescription('');
        setAddress('');
        setLatitude('');
        setLongitude('');
        setImageUrl('');
        setCategory('');
        setOpeningHours('');
        setWebsite('');
        setPhone('');
        setRating('4.5');
        setTransportLinks([]);
        setEateries([]);
      } else {
        Alert.alert('Error', data.detail || 'Failed to add museum.');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to add museum.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <View style={[styles.container, { paddingTop: insets.top }]}>
        <StatusBar style="light" />
        <View style={styles.loginContainer}>
          <LinearGradient
            colors={['#E63946', '#F1A208']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.lockIcon}
          >
            <Ionicons name="lock-closed" size={40} color="#fff" />
          </LinearGradient>
          <Text style={styles.loginTitle}>Admin Access</Text>
          <Text style={styles.loginSubtitle}>Enter your PIN to add new museums</Text>
          
          <View style={styles.pinContainer}>
            <TextInput
              style={styles.pinInput}
              placeholder="Enter PIN"
              placeholderTextColor="#666"
              value={pin}
              onChangeText={setPin}
              keyboardType="number-pad"
              secureTextEntry
              maxLength={6}
            />
          </View>

          <TouchableOpacity
            style={styles.loginButton}
            onPress={verifyPin}
            disabled={loading || pin.length < 4}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <>
                <Ionicons name="key" size={20} color="#fff" />
                <Text style={styles.loginButtonText}>Unlock</Text>
              </>
            )}
          </TouchableOpacity>

          <Text style={styles.hintText}>Contact admin for access credentials</Text>
        </View>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView 
      style={[styles.container, { paddingTop: insets.top }]}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <StatusBar style="light" />

      {/* Header */}
      <View style={styles.header}>
        <Ionicons name="add-circle" size={28} color="#E63946" />
        <Text style={styles.headerTitle}>Add New Museum</Text>
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Basic Info Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Basic Information</Text>
          
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Museum Name *</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g., British Museum"
              placeholderTextColor="#666"
              value={name}
              onChangeText={setName}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Short Description *</Text>
            <TextInput
              style={styles.input}
              placeholder="Brief tagline (one line)"
              placeholderTextColor="#666"
              value={shortDescription}
              onChangeText={setShortDescription}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Full Description *</Text>
            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Detailed description..."
              placeholderTextColor="#666"
              value={description}
              onChangeText={setDescription}
              multiline
              numberOfLines={4}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Category *</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g., Art, History & Culture"
              placeholderTextColor="#666"
              value={category}
              onChangeText={setCategory}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Image URL *</Text>
            <TextInput
              style={styles.input}
              placeholder="https://..."
              placeholderTextColor="#666"
              value={imageUrl}
              onChangeText={setImageUrl}
            />
          </View>
        </View>

        {/* Location Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Location</Text>
          
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Address *</Text>
            <TextInput
              style={styles.input}
              placeholder="Full address"
              placeholderTextColor="#666"
              value={address}
              onChangeText={setAddress}
            />
          </View>

          <View style={styles.row}>
            <View style={[styles.inputGroup, { flex: 1 }]}>
              <Text style={styles.label}>Latitude *</Text>
              <TextInput
                style={styles.input}
                placeholder="51.5194"
                placeholderTextColor="#666"
                value={latitude}
                onChangeText={setLatitude}
                keyboardType="decimal-pad"
              />
            </View>
            <View style={[styles.inputGroup, { flex: 1 }]}>
              <Text style={styles.label}>Longitude *</Text>
              <TextInput
                style={styles.input}
                placeholder="-0.1269"
                placeholderTextColor="#666"
                value={longitude}
                onChangeText={setLongitude}
                keyboardType="decimal-pad"
              />
            </View>
          </View>
        </View>

        {/* Details Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Details</Text>
          
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Opening Hours *</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g., Daily 10:00-17:00"
              placeholderTextColor="#666"
              value={openingHours}
              onChangeText={setOpeningHours}
            />
          </View>

          <View style={styles.row}>
            <View style={[styles.inputGroup, { flex: 1 }]}>
              <Text style={styles.label}>Website</Text>
              <TextInput
                style={styles.input}
                placeholder="https://..."
                placeholderTextColor="#666"
                value={website}
                onChangeText={setWebsite}
              />
            </View>
            <View style={[styles.inputGroup, { flex: 1 }]}>
              <Text style={styles.label}>Phone</Text>
              <TextInput
                style={styles.input}
                placeholder="+44..."
                placeholderTextColor="#666"
                value={phone}
                onChangeText={setPhone}
              />
            </View>
          </View>

          <View style={styles.row}>
            <View style={[styles.inputGroup, { flex: 1 }]}>
              <Text style={styles.label}>Rating (0-5)</Text>
              <TextInput
                style={styles.input}
                placeholder="4.5"
                placeholderTextColor="#666"
                value={rating}
                onChangeText={setRating}
                keyboardType="decimal-pad"
              />
            </View>
            <View style={[styles.inputGroup, { flex: 1 }]}>
              <Text style={styles.label}>Free Entry?</Text>
              <TouchableOpacity
                style={[styles.toggleButton, freeEntry && styles.toggleButtonActive]}
                onPress={() => setFreeEntry(!freeEntry)}
              >
                <Text style={[styles.toggleText, freeEntry && styles.toggleTextActive]}>
                  {freeEntry ? 'YES - Free' : 'NO - Paid'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>

        {/* Transport Links Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Transport Links</Text>
          
          {transportLinks.map((t, index) => (
            <View key={index} style={styles.listItem}>
              <View style={styles.listItemContent}>
                <Ionicons
                  name={t.type === 'tube' ? 'subway' : t.type === 'bus' ? 'bus' : 'train'}
                  size={20}
                  color="#457B9D"
                />
                <View>
                  <Text style={styles.listItemTitle}>{t.name}</Text>
                  <Text style={styles.listItemSubtitle}>{t.line || t.type} - {t.distance}</Text>
                </View>
              </View>
              <TouchableOpacity onPress={() => removeTransportLink(index)}>
                <Ionicons name="close-circle" size={24} color="#E63946" />
              </TouchableOpacity>
            </View>
          ))}

          <View style={styles.addItemContainer}>
            <View style={styles.row}>
              <TouchableOpacity
                style={[styles.typeButton, newTransportType === 'tube' && styles.typeButtonActive]}
                onPress={() => setNewTransportType('tube')}
              >
                <Text style={styles.typeButtonText}>Tube</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.typeButton, newTransportType === 'bus' && styles.typeButtonActive]}
                onPress={() => setNewTransportType('bus')}
              >
                <Text style={styles.typeButtonText}>Bus</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.typeButton, newTransportType === 'train' && styles.typeButtonActive]}
                onPress={() => setNewTransportType('train')}
              >
                <Text style={styles.typeButtonText}>Train</Text>
              </TouchableOpacity>
            </View>
            <TextInput
              style={styles.input}
              placeholder="Station/Stop name"
              placeholderTextColor="#666"
              value={newTransportName}
              onChangeText={setNewTransportName}
            />
            <TextInput
              style={styles.input}
              placeholder="Line (optional)"
              placeholderTextColor="#666"
              value={newTransportLine}
              onChangeText={setNewTransportLine}
            />
            <TextInput
              style={styles.input}
              placeholder="Distance (e.g., 5 min walk)"
              placeholderTextColor="#666"
              value={newTransportDistance}
              onChangeText={setNewTransportDistance}
            />
            <TouchableOpacity style={styles.addButton} onPress={addTransportLink}>
              <Ionicons name="add" size={20} color="#fff" />
              <Text style={styles.addButtonText}>Add Transport</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Nearby Eateries Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Nearby Eateries</Text>
          
          {eateries.map((e, index) => (
            <View key={index} style={styles.listItem}>
              <View style={styles.listItemContent}>
                <Ionicons name="restaurant" size={20} color="#2A9D8F" />
                <View>
                  <Text style={styles.listItemTitle}>{e.name}</Text>
                  <Text style={styles.listItemSubtitle}>{e.type} - {e.distance} - {e.price_range}</Text>
                </View>
              </View>
              <TouchableOpacity onPress={() => removeEatery(index)}>
                <Ionicons name="close-circle" size={24} color="#E63946" />
              </TouchableOpacity>
            </View>
          ))}

          <View style={styles.addItemContainer}>
            <TextInput
              style={styles.input}
              placeholder="Eatery name"
              placeholderTextColor="#666"
              value={newEateryName}
              onChangeText={setNewEateryName}
            />
            <View style={styles.row}>
              {['Cafe', 'Restaurant', 'Pub'].map(type => (
                <TouchableOpacity
                  key={type}
                  style={[styles.typeButton, newEateryType === type && styles.typeButtonActive]}
                  onPress={() => setNewEateryType(type)}
                >
                  <Text style={styles.typeButtonText}>{type}</Text>
                </TouchableOpacity>
              ))}
            </View>
            <TextInput
              style={styles.input}
              placeholder="Cuisine (optional)"
              placeholderTextColor="#666"
              value={newEateryCuisine}
              onChangeText={setNewEateryCuisine}
            />
            <TextInput
              style={styles.input}
              placeholder="Distance (e.g., 5 min walk)"
              placeholderTextColor="#666"
              value={newEateryDistance}
              onChangeText={setNewEateryDistance}
            />
            <View style={styles.row}>
              {['£', '££', '£££'].map(price => (
                <TouchableOpacity
                  key={price}
                  style={[styles.typeButton, newEateryPrice === price && styles.typeButtonActive]}
                  onPress={() => setNewEateryPrice(price)}
                >
                  <Text style={styles.typeButtonText}>{price}</Text>
                </TouchableOpacity>
              ))}
            </View>
            <TouchableOpacity style={styles.addButton} onPress={addEatery}>
              <Ionicons name="add" size={20} color="#fff" />
              <Text style={styles.addButtonText}>Add Eatery</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Submit Button */}
        <TouchableOpacity
          style={styles.submitButton}
          onPress={submitMuseum}
          disabled={submitting}
        >
          {submitting ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Ionicons name="checkmark-circle" size={24} color="#fff" />
              <Text style={styles.submitButtonText}>Add Museum</Text>
            </>
          )}
        </TouchableOpacity>

        {/* Logout Button */}
        <TouchableOpacity
          style={styles.logoutButton}
          onPress={() => {
            setIsAuthenticated(false);
            setPin('');
          }}
        >
          <Ionicons name="log-out-outline" size={20} color="#E63946" />
          <Text style={styles.logoutButtonText}>Lock Admin Panel</Text>
        </TouchableOpacity>

        <View style={{ height: 100 }} />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F0F23',
  },
  loginContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  lockIcon: {
    width: 100,
    height: 100,
    borderRadius: 50,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  loginTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  loginSubtitle: {
    fontSize: 14,
    color: '#A8A8A8',
    marginTop: 8,
    textAlign: 'center',
  },
  pinContainer: {
    width: '100%',
    marginTop: 32,
  },
  pinInput: {
    backgroundColor: '#1A1A2E',
    borderRadius: 12,
    padding: 16,
    fontSize: 24,
    color: '#fff',
    textAlign: 'center',
    letterSpacing: 8,
  },
  loginButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#E63946',
    paddingVertical: 14,
    paddingHorizontal: 32,
    borderRadius: 25,
    marginTop: 24,
    gap: 8,
  },
  loginButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  hintText: {
    fontSize: 12,
    color: '#666',
    marginTop: 16,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 16,
    gap: 12,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  scrollView: {
    flex: 1,
    paddingHorizontal: 20,
  },
  section: {
    backgroundColor: '#1A1A2E',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 16,
  },
  inputGroup: {
    marginBottom: 12,
  },
  label: {
    fontSize: 13,
    color: '#A8A8A8',
    marginBottom: 6,
  },
  input: {
    backgroundColor: '#252542',
    borderRadius: 10,
    padding: 12,
    fontSize: 15,
    color: '#fff',
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  row: {
    flexDirection: 'row',
    gap: 12,
  },
  toggleButton: {
    backgroundColor: '#252542',
    borderRadius: 10,
    padding: 12,
    alignItems: 'center',
  },
  toggleButtonActive: {
    backgroundColor: '#2A9D8F',
  },
  toggleText: {
    color: '#A8A8A8',
    fontWeight: '600',
  },
  toggleTextActive: {
    color: '#fff',
  },
  listItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#252542',
    borderRadius: 10,
    padding: 12,
    marginBottom: 8,
  },
  listItemContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  listItemTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#fff',
  },
  listItemSubtitle: {
    fontSize: 12,
    color: '#A8A8A8',
  },
  addItemContainer: {
    borderTopWidth: 1,
    borderTopColor: '#333',
    paddingTop: 16,
    marginTop: 8,
    gap: 10,
  },
  typeButton: {
    flex: 1,
    backgroundColor: '#252542',
    borderRadius: 8,
    padding: 10,
    alignItems: 'center',
  },
  typeButtonActive: {
    backgroundColor: '#457B9D',
  },
  typeButtonText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: '500',
  },
  addButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#457B9D',
    borderRadius: 10,
    padding: 12,
    gap: 8,
  },
  addButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  submitButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#2A9D8F',
    borderRadius: 16,
    padding: 18,
    gap: 10,
    marginBottom: 12,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(230, 57, 70, 0.1)',
    borderRadius: 12,
    padding: 14,
    gap: 8,
  },
  logoutButtonText: {
    color: '#E63946',
    fontSize: 14,
    fontWeight: '600',
  },
});
