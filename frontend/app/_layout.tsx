import React from 'react';
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Platform, StyleSheet } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

const HomeIcon = ({ color, size }: { color: string; size: number }) => (
  <Ionicons name="home" size={size} color={color} />
);

const ExploreIcon = ({ color, size }: { color: string; size: number }) => (
  <Ionicons name="compass" size={size} color={color} />
);

const ToursIcon = ({ color, size }: { color: string; size: number }) => (
  <Ionicons name="map" size={size} color={color} />
);

const FavoritesIcon = ({ color, size }: { color: string; size: number }) => (
  <Ionicons name="heart" size={size} color={color} />
);

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <Tabs
        screenOptions={{
          headerShown: false,
          tabBarStyle: styles.tabBar,
          tabBarActiveTintColor: '#E63946',
          tabBarInactiveTintColor: '#A8A8A8',
          tabBarLabelStyle: styles.tabBarLabel,
          tabBarIconStyle: { marginBottom: -2 },
        }}
      >
        <Tabs.Screen
          name="index"
          options={{
            title: 'Home',
            tabBarIcon: HomeIcon,
          }}
        />
        <Tabs.Screen
          name="explore"
          options={{
            title: 'Explore',
            tabBarIcon: ExploreIcon,
          }}
        />
        <Tabs.Screen
          name="tours"
          options={{
            title: 'Tours',
            tabBarIcon: ToursIcon,
          }}
        />
        <Tabs.Screen
          name="favorites"
          options={{
            title: 'Favorites',
            tabBarIcon: FavoritesIcon,
          }}
        />
        <Tabs.Screen
          name="admin"
          options={{
            title: 'Admin',
            tabBarIcon: AdminIcon,
          }}
        />
        <Tabs.Screen
          name="museum/[id]"
          options={{
            href: null,
          }}
        />
        <Tabs.Screen
          name="tour/[id]"
          options={{
            href: null,
          }}
        />
      </Tabs>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: '#1A1A2E',
    borderTopWidth: 0,
    elevation: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -3 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    height: Platform.OS === 'ios' ? 90 : 70,
    paddingBottom: Platform.OS === 'ios' ? 30 : 10,
    paddingTop: 10,
  },
  tabBarLabel: {
    fontSize: 11,
    fontWeight: '600',
  },
});
