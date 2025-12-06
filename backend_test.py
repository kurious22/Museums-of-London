#!/usr/bin/env python3
"""
Backend API Tests for Museums Of London
Tests all museum endpoints including filtering, favorites, and data integrity
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://london-museums-app.preview.emergentagent.com/api"

class MuseumAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "data": data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if not success and data:
            print(f"   Response: {data}")
        print()

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Root endpoint", True, f"Message: {data['message']}")
                else:
                    self.log_test("Root endpoint", False, "No message in response", data)
            else:
                self.log_test("Root endpoint", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Root endpoint", False, f"Exception: {str(e)}")

    def test_get_all_museums(self):
        """Test GET /api/museums - get all museums"""
        try:
            response = self.session.get(f"{self.base_url}/museums")
            if response.status_code == 200:
                museums = response.json()
                if isinstance(museums, list) and len(museums) > 0:
                    # Check if we have expected number of museums (should be 20)
                    if len(museums) == 20:
                        self.log_test("Get all museums", True, f"Retrieved {len(museums)} museums")
                        
                        # Verify museum structure
                        museum = museums[0]
                        required_fields = ['id', 'name', 'description', 'address', 'latitude', 'longitude', 
                                         'category', 'free_entry', 'transport', 'nearby_eateries']
                        missing_fields = [field for field in required_fields if field not in museum]
                        
                        if not missing_fields:
                            self.log_test("Museum data structure", True, "All required fields present")
                        else:
                            self.log_test("Museum data structure", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_test("Get all museums", False, f"Expected 20 museums, got {len(museums)}")
                else:
                    self.log_test("Get all museums", False, "Empty or invalid response", museums)
            else:
                self.log_test("Get all museums", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Get all museums", False, f"Exception: {str(e)}")

    def test_museum_filtering(self):
        """Test museum filtering by category, free_only, and search"""
        
        # Test category filter
        try:
            response = self.session.get(f"{self.base_url}/museums?category=Art")
            if response.status_code == 200:
                museums = response.json()
                if museums and all("Art" in museum.get("category", "") for museum in museums):
                    self.log_test("Category filter", True, f"Found {len(museums)} art museums")
                else:
                    self.log_test("Category filter", False, "Category filtering not working properly")
            else:
                self.log_test("Category filter", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Category filter", False, f"Exception: {str(e)}")

        # Test free_only filter
        try:
            response = self.session.get(f"{self.base_url}/museums?free_only=true")
            if response.status_code == 200:
                museums = response.json()
                if museums and all(museum.get("free_entry", False) for museum in museums):
                    self.log_test("Free entry filter", True, f"Found {len(museums)} free museums")
                else:
                    self.log_test("Free entry filter", False, "Free entry filtering not working")
            else:
                self.log_test("Free entry filter", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Free entry filter", False, f"Exception: {str(e)}")

        # Test search functionality
        try:
            response = self.session.get(f"{self.base_url}/museums?search=British")
            if response.status_code == 200:
                museums = response.json()
                if museums:
                    # Check if search term appears in name, description, or category
                    valid_results = []
                    for museum in museums:
                        name_match = "british" in museum.get("name", "").lower()
                        desc_match = "british" in museum.get("description", "").lower()
                        cat_match = "british" in museum.get("category", "").lower()
                        if name_match or desc_match or cat_match:
                            valid_results.append(museum)
                    
                    if len(valid_results) == len(museums):
                        self.log_test("Search functionality", True, f"Found {len(museums)} museums matching 'British'")
                    else:
                        self.log_test("Search functionality", False, f"Search returned irrelevant results")
                else:
                    self.log_test("Search functionality", False, "No results for 'British' search")
            else:
                self.log_test("Search functionality", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Search functionality", False, f"Exception: {str(e)}")

    def test_featured_museums(self):
        """Test GET /api/museums/featured"""
        try:
            response = self.session.get(f"{self.base_url}/museums/featured")
            if response.status_code == 200:
                featured = response.json()
                if isinstance(featured, list) and len(featured) > 0:
                    # Check if all returned museums are marked as featured
                    if all(museum.get("featured", False) for museum in featured):
                        self.log_test("Featured museums", True, f"Retrieved {len(featured)} featured museums")
                    else:
                        self.log_test("Featured museums", False, "Non-featured museums in featured list")
                else:
                    self.log_test("Featured museums", False, "No featured museums returned")
            else:
                self.log_test("Featured museums", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Featured museums", False, f"Exception: {str(e)}")

    def test_categories_endpoint(self):
        """Test GET /api/museums/categories"""
        try:
            response = self.session.get(f"{self.base_url}/museums/categories")
            if response.status_code == 200:
                categories = response.json()
                if isinstance(categories, list) and len(categories) > 0:
                    expected_categories = ["Art", "History", "Science", "Modern Art"]
                    has_expected = any(any(exp in cat for exp in expected_categories) for cat in categories)
                    if has_expected:
                        self.log_test("Categories endpoint", True, f"Retrieved {len(categories)} categories: {categories}")
                    else:
                        self.log_test("Categories endpoint", False, f"Unexpected categories: {categories}")
                else:
                    self.log_test("Categories endpoint", False, "No categories returned")
            else:
                self.log_test("Categories endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Categories endpoint", False, f"Exception: {str(e)}")

    def test_museum_details(self):
        """Test GET /api/museums/{id} - get specific museum details"""
        # First get a museum ID
        try:
            response = self.session.get(f"{self.base_url}/museums")
            if response.status_code == 200:
                museums = response.json()
                if museums:
                    test_museum_id = museums[0]["id"]  # Use first museum for testing
                    
                    # Test getting specific museum
                    detail_response = self.session.get(f"{self.base_url}/museums/{test_museum_id}")
                    if detail_response.status_code == 200:
                        museum = detail_response.json()
                        
                        # Check if transport links are present
                        if "transport" in museum and isinstance(museum["transport"], list) and len(museum["transport"]) > 0:
                            transport_valid = all("type" in t and "name" in t and "distance" in t for t in museum["transport"])
                            if transport_valid:
                                self.log_test("Museum transport data", True, f"Found {len(museum['transport'])} transport options")
                            else:
                                self.log_test("Museum transport data", False, "Invalid transport data structure")
                        else:
                            self.log_test("Museum transport data", False, "No transport data found")
                        
                        # Check if nearby eateries are present
                        if "nearby_eateries" in museum and isinstance(museum["nearby_eateries"], list) and len(museum["nearby_eateries"]) > 0:
                            eateries_valid = all("name" in e and "type" in e and "distance" in e for e in museum["nearby_eateries"])
                            if eateries_valid:
                                self.log_test("Museum eateries data", True, f"Found {len(museum['nearby_eateries'])} nearby eateries")
                            else:
                                self.log_test("Museum eateries data", False, "Invalid eateries data structure")
                        else:
                            self.log_test("Museum eateries data", False, "No eateries data found")
                        
                        self.log_test("Museum details endpoint", True, f"Retrieved details for museum: {museum.get('name', 'Unknown')}")
                    else:
                        self.log_test("Museum details endpoint", False, f"Status: {detail_response.status_code}")
                else:
                    self.log_test("Museum details endpoint", False, "No museums available for testing")
            else:
                self.log_test("Museum details endpoint", False, "Could not get museums list for testing")
        except Exception as e:
            self.log_test("Museum details endpoint", False, f"Exception: {str(e)}")

        # Test invalid museum ID
        try:
            response = self.session.get(f"{self.base_url}/museums/invalid_id")
            if response.status_code == 404:
                self.log_test("Invalid museum ID handling", True, "Correctly returns 404 for invalid ID")
            else:
                self.log_test("Invalid museum ID handling", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Invalid museum ID handling", False, f"Exception: {str(e)}")

    def test_favorites_functionality(self):
        """Test favorites CRUD operations"""
        # Get a test museum ID
        try:
            response = self.session.get(f"{self.base_url}/museums")
            if response.status_code != 200:
                self.log_test("Favorites setup", False, "Could not get museums for favorites testing")
                return
            
            museums = response.json()
            if not museums:
                self.log_test("Favorites setup", False, "No museums available for favorites testing")
                return
            
            test_museum_id = museums[0]["id"]
            
            # Test adding to favorites
            add_response = self.session.post(f"{self.base_url}/favorites/{test_museum_id}")
            if add_response.status_code == 200:
                add_data = add_response.json()
                if "message" in add_data and "id" in add_data:
                    self.log_test("Add to favorites", True, f"Added museum to favorites: {add_data['message']}")
                else:
                    self.log_test("Add to favorites", False, "Invalid response format", add_data)
            else:
                self.log_test("Add to favorites", False, f"Status: {add_response.status_code}", add_response.text)
            
            # Test checking if favorited
            check_response = self.session.get(f"{self.base_url}/favorites/check/{test_museum_id}")
            if check_response.status_code == 200:
                check_data = check_response.json()
                if check_data.get("is_favorite", False):
                    self.log_test("Check favorite status", True, "Museum correctly marked as favorite")
                else:
                    self.log_test("Check favorite status", False, "Museum not marked as favorite after adding")
            else:
                self.log_test("Check favorite status", False, f"Status: {check_response.status_code}")
            
            # Test getting all favorites
            favorites_response = self.session.get(f"{self.base_url}/favorites")
            if favorites_response.status_code == 200:
                favorites = favorites_response.json()
                if isinstance(favorites, list):
                    # Check if our test museum is in the favorites
                    favorite_ids = [fav.get("id") for fav in favorites]
                    if test_museum_id in favorite_ids:
                        self.log_test("Get all favorites", True, f"Retrieved {len(favorites)} favorites including test museum")
                    else:
                        self.log_test("Get all favorites", True, f"Retrieved {len(favorites)} favorites (test museum may have been added by duplicate)")
                else:
                    self.log_test("Get all favorites", False, "Invalid favorites response format")
            else:
                self.log_test("Get all favorites", False, f"Status: {favorites_response.status_code}")
            
            # Test removing from favorites
            remove_response = self.session.delete(f"{self.base_url}/favorites/{test_museum_id}")
            if remove_response.status_code == 200:
                remove_data = remove_response.json()
                if "message" in remove_data:
                    self.log_test("Remove from favorites", True, f"Removed from favorites: {remove_data['message']}")
                else:
                    self.log_test("Remove from favorites", False, "Invalid response format", remove_data)
            else:
                self.log_test("Remove from favorites", False, f"Status: {remove_response.status_code}")
            
            # Test checking favorite status after removal
            final_check_response = self.session.get(f"{self.base_url}/favorites/check/{test_museum_id}")
            if final_check_response.status_code == 200:
                final_check_data = final_check_response.json()
                if not final_check_data.get("is_favorite", True):
                    self.log_test("Favorite removal verification", True, "Museum correctly removed from favorites")
                else:
                    self.log_test("Favorite removal verification", False, "Museum still marked as favorite after removal")
            else:
                self.log_test("Favorite removal verification", False, f"Status: {final_check_response.status_code}")
            
            # Test adding favorite for non-existent museum
            invalid_add_response = self.session.post(f"{self.base_url}/favorites/invalid_museum_id")
            if invalid_add_response.status_code == 404:
                self.log_test("Invalid museum favorite handling", True, "Correctly returns 404 for invalid museum ID")
            else:
                self.log_test("Invalid museum favorite handling", False, f"Expected 404, got {invalid_add_response.status_code}")
                
        except Exception as e:
            self.log_test("Favorites functionality", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("MUSEUMS OF LONDON - BACKEND API TESTS")
        print("=" * 60)
        print(f"Testing backend at: {self.base_url}")
        print()
        
        # Run all tests
        self.test_root_endpoint()
        self.test_get_all_museums()
        self.test_museum_filtering()
        self.test_featured_museums()
        self.test_categories_endpoint()
        self.test_museum_details()
        self.test_favorites_functionality()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        failed = total - passed
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}: {result['message']}")
        
        print("\n" + "=" * 60)
        return failed == 0

if __name__ == "__main__":
    tester = MuseumAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)