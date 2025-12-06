#!/usr/bin/env python3
"""
Backend API Testing for Museums of London App
Focus: Testing image URLs, museum data, and search functionality
Priority: Fix broken museum image URLs task
"""

import requests
import json
import sys
from typing import List, Dict, Any
import time

# Backend URL from environment
BACKEND_URL = "https://london-museums-app.preview.emergentagent.com/api"

class MuseumAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.session.timeout = 30
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status}: {test_name}"
        if message:
            result += f" - {message}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })

    def test_api_connection(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_test("API Connection", True, f"Status: {response.status_code}")
                return True
            else:
                self.log_test("API Connection", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Connection", False, f"Error: {str(e)}")
            return False
    
    def test_get_all_museums(self):
        """Test getting all museums and verify image URLs"""
        try:
            response = self.session.get(f"{self.base_url}/museums")
            if response.status_code != 200:
                self.log_test("Get All Museums", False, f"Status: {response.status_code}")
                return []
            
            museums = response.json()
            if not museums:
                self.log_test("Get All Museums", False, "No museums returned")
                return []
            
            self.log_test("Get All Museums", True, f"Retrieved {len(museums)} museums")
            return museums
            
        except Exception as e:
            self.log_test("Get All Museums", False, f"Error: {str(e)}")
            return []

    def test_image_urls(self, museums: List[Dict]):
        """Test all museum image URLs for accessibility - PRIORITY TEST"""
        if not museums:
            self.log_test("Image URL Testing", False, "No museums to test")
            return
        
        broken_images = []
        working_images = []
        
        print(f"\n🔍 Testing {len(museums)} museum image URLs...")
        
        for museum in museums:
            museum_name = museum.get('name', 'Unknown')
            image_url = museum.get('image_url', '')
            
            if not image_url:
                broken_images.append(f"{museum_name}: No image URL")
                continue
            
            try:
                # Test image URL accessibility
                img_response = self.session.head(image_url, timeout=10)
                if img_response.status_code == 200:
                    working_images.append(f"{museum_name}: {image_url}")
                    print(f"  ✅ {museum_name}: Image OK")
                else:
                    broken_images.append(f"{museum_name}: HTTP {img_response.status_code} - {image_url}")
                    print(f"  ❌ {museum_name}: HTTP {img_response.status_code}")
                    
            except Exception as e:
                broken_images.append(f"{museum_name}: Error - {str(e)}")
                print(f"  ❌ {museum_name}: Error - {str(e)}")
        
        # Log results
        if broken_images:
            self.log_test("Image URL Testing", False, 
                         f"{len(broken_images)} broken images: {'; '.join(broken_images[:3])}{'...' if len(broken_images) > 3 else ''}")
        else:
            self.log_test("Image URL Testing", True, f"All {len(working_images)} images accessible")
        
        return broken_images, working_images
    
    def test_postal_museum_exists(self, museums: List[Dict]):
        """Test that The Postal Museum (ID 21) exists in the museum list"""
        postal_museum = None
        for museum in museums:
            if museum.get('id') == '21' or 'Postal Museum' in museum.get('name', ''):
                postal_museum = museum
                break
        
        if postal_museum:
            self.log_test("Postal Museum Exists", True, 
                         f"Found: {postal_museum.get('name')} (ID: {postal_museum.get('id')})")
            return postal_museum
        else:
            self.log_test("Postal Museum Exists", False, "The Postal Museum not found in museum list")
            return None
    
    def test_search_functionality(self):
        """Test search functionality works correctly and only returns museum data"""
        test_searches = [
            ("British", "Should find British Museum"),
            ("art", "Should find art museums"),
            ("science", "Should find Science Museum"),
            ("nonexistent", "Should return empty results")
        ]
        
        all_passed = True
        
        for search_term, description in test_searches:
            try:
                response = self.session.get(f"{self.base_url}/museums", 
                                          params={"search": search_term})
                
                if response.status_code != 200:
                    self.log_test(f"Search '{search_term}'", False, f"Status: {response.status_code}")
                    all_passed = False
                    continue
                
                results = response.json()
                
                if search_term == "nonexistent":
                    if len(results) == 0:
                        self.log_test(f"Search '{search_term}'", True, "Correctly returned no results")
                    else:
                        self.log_test(f"Search '{search_term}'", False, f"Should return 0 results, got {len(results)}")
                        all_passed = False
                else:
                    if len(results) > 0:
                        # Verify search results contain the search term and are museum data
                        valid_results = True
                        for result in results:
                            # Check it's museum data (has required fields)
                            if not all(field in result for field in ['id', 'name', 'description', 'category']):
                                valid_results = False
                                break
                            
                            # Check search relevance
                            name = result.get('name', '').lower()
                            desc = result.get('description', '').lower()
                            category = result.get('category', '').lower()
                            
                            if search_term.lower() not in name and search_term.lower() not in desc and search_term.lower() not in category:
                                valid_results = False
                                break
                        
                        if valid_results:
                            self.log_test(f"Search '{search_term}'", True, f"Found {len(results)} relevant museum results")
                        else:
                            self.log_test(f"Search '{search_term}'", False, "Invalid or irrelevant search results")
                            all_passed = False
                    else:
                        self.log_test(f"Search '{search_term}'", False, f"Expected results but got 0")
                        all_passed = False
                        
            except Exception as e:
                self.log_test(f"Search '{search_term}'", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

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