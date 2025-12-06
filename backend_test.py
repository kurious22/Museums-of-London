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

    def test_museum_details(self, museum_id: str = "21"):
        """Test getting specific museum details"""
        try:
            response = self.session.get(f"{self.base_url}/museums/{museum_id}")
            
            if response.status_code == 200:
                museum = response.json()
                required_fields = ['id', 'name', 'description', 'address', 'image_url', 'transport', 'nearby_eateries']
                missing_fields = [field for field in required_fields if not museum.get(field)]
                
                if missing_fields:
                    self.log_test(f"Museum Details (ID {museum_id})", False, 
                                f"Missing fields: {', '.join(missing_fields)}")
                else:
                    self.log_test(f"Museum Details (ID {museum_id})", True, 
                                f"All required fields present for {museum.get('name')}")
                return museum
            else:
                self.log_test(f"Museum Details (ID {museum_id})", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test(f"Museum Details (ID {museum_id})", False, f"Error: {str(e)}")
            return None
    
    def test_featured_museums(self):
        """Test featured museums endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/museums/featured")
            
            if response.status_code == 200:
                featured = response.json()
                if len(featured) > 0:
                    self.log_test("Featured Museums", True, f"Retrieved {len(featured)} featured museums")
                    return featured
                else:
                    self.log_test("Featured Museums", False, "No featured museums returned")
                    return []
            else:
                self.log_test("Featured Museums", False, f"Status: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_test("Featured Museums", False, f"Error: {str(e)}")
            return []
    
    def test_favorites_endpoints(self):
        """Test favorites functionality"""
        test_museum_id = "1"  # British Museum
        
        try:
            # Test adding favorite
            response = self.session.post(f"{self.base_url}/favorites/{test_museum_id}")
            if response.status_code in [200, 201]:
                self.log_test("Add Favorite", True, "Successfully added to favorites")
            else:
                self.log_test("Add Favorite", False, f"Status: {response.status_code}")
                return False
            
            # Test checking favorite
            response = self.session.get(f"{self.base_url}/favorites/check/{test_museum_id}")
            if response.status_code == 200:
                result = response.json()
                if result.get('is_favorite'):
                    self.log_test("Check Favorite", True, "Correctly identified as favorite")
                else:
                    self.log_test("Check Favorite", False, "Not identified as favorite")
            else:
                self.log_test("Check Favorite", False, f"Status: {response.status_code}")
            
            # Test getting favorites list
            response = self.session.get(f"{self.base_url}/favorites")
            if response.status_code == 200:
                favorites = response.json()
                self.log_test("Get Favorites List", True, f"Retrieved {len(favorites)} favorites")
            else:
                self.log_test("Get Favorites List", False, f"Status: {response.status_code}")
            
            # Test removing favorite
            response = self.session.delete(f"{self.base_url}/favorites/{test_museum_id}")
            if response.status_code == 200:
                self.log_test("Remove Favorite", True, "Successfully removed from favorites")
            else:
                self.log_test("Remove Favorite", False, f"Status: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Favorites Endpoints", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests and return summary"""
        print("🏛️  Museums of London Backend API Testing")
        print("=" * 50)
        print("🎯 PRIORITY: Testing 'Fix broken museum image URLs' task")
        print("=" * 50)
        
        # Test API connection first
        if not self.test_api_connection():
            print("\n❌ Cannot connect to API. Stopping tests.")
            return False
        
        print("\n📋 Testing Museum Data and Image URLs...")
        
        # Get all museums
        museums = self.test_get_all_museums()
        if not museums:
            print("\n❌ Cannot retrieve museums. Stopping tests.")
            return False
        
        # Test image URLs (main focus)
        print(f"\n🖼️  Testing Image URLs for {len(museums)} museums...")
        broken_images, working_images = self.test_image_urls(museums)
        
        # Test Postal Museum exists
        print(f"\n📮 Checking for The Postal Museum...")
        postal_museum = self.test_postal_museum_exists(museums)
        
        # Test search functionality
        print(f"\n🔍 Testing Search Functionality...")
        search_passed = self.test_search_functionality()
        
        # Test museum details
        print(f"\n📄 Testing Museum Details...")
        if postal_museum:
            self.test_museum_details(postal_museum.get('id', '21'))
        else:
            self.test_museum_details('1')  # Test with British Museum
        
        # Test featured museums
        print(f"\n⭐ Testing Featured Museums...")
        self.test_featured_museums()
        
        # Test favorites
        print(f"\n❤️  Testing Favorites Functionality...")
        self.test_favorites_endpoints()
        
        # Summary
        print(f"\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        total_tests = len(self.test_results)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Critical issues summary
        critical_issues = []
        if broken_images:
            critical_issues.append(f"🖼️  {len(broken_images)} broken image URLs")
        
        failed_tests = [r for r in self.test_results if not r['passed']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['message']}")
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in critical_issues:
                print(f"  • {issue}")
        
        # Image URL detailed report
        if broken_images:
            print(f"\n🖼️  BROKEN IMAGE URLS DETAILS:")
            for broken in broken_images:
                print(f"  • {broken}")
        
        return len(critical_issues) == 0 and passed_tests == total_tests

def main():
    """Main test execution"""
    tester = MuseumAPITester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 All tests passed! Backend is working correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️  Some tests failed. Check the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()