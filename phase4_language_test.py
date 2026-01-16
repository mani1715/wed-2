#!/usr/bin/env python3
"""
PHASE 4 - EXTENDED MULTI-LANGUAGE SYSTEM BACKEND TESTING
Testing new language codes: tamil, kannada, malayalam
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Configuration
BACKEND_URL = "https://wed-dashboard.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@wedding.com"
ADMIN_PASSWORD = "admin123"

class Phase4LanguageTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_profiles = []
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def authenticate_admin(self):
        """Authenticate as admin and get token"""
        print("\n🔐 AUTHENTICATING ADMIN...")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                self.log_test("Admin Authentication", True, f"Token obtained for {data['admin']['email']}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_creation_new_languages(self):
        """Test 1: Profile Creation with New Languages"""
        print("\n🌏 TESTING PROFILE CREATION WITH NEW LANGUAGES...")
        
        # Test profiles with new language codes
        test_cases = [
            {
                "name": "Tamil Profile",
                "groom_name": "Arun Kumar",
                "bride_name": "Lakshmi Devi",
                "enabled_languages": ["tamil"],
                "venue": "Sri Meenakshi Temple, Madurai"
            },
            {
                "name": "Kannada Profile", 
                "groom_name": "Karthik Rao",
                "bride_name": "Priya Shetty",
                "enabled_languages": ["kannada"],
                "venue": "Mysore Palace Gardens, Mysore"
            },
            {
                "name": "Malayalam Profile",
                "groom_name": "Vishnu Nair",
                "bride_name": "Anjali Menon",
                "enabled_languages": ["malayalam"],
                "venue": "Backwater Resort, Alleppey"
            },
            {
                "name": "All Languages Profile",
                "groom_name": "Rajesh Sharma",
                "bride_name": "Kavitha Reddy",
                "enabled_languages": ["english", "tamil", "kannada", "malayalam"],
                "venue": "Grand Convention Center, Bangalore"
            }
        ]
        
        for test_case in test_cases:
            profile_data = {
                "groom_name": test_case["groom_name"],
                "bride_name": test_case["bride_name"],
                "event_type": "marriage",
                "event_date": "2024-12-25T10:00:00Z",
                "venue": test_case["venue"],
                "language": test_case["enabled_languages"],
                "design_id": "temple_divine",
                "enabled_languages": test_case["enabled_languages"],
                "sections_enabled": {
                    "opening": True,
                    "welcome": True,
                    "couple": True,
                    "photos": True,
                    "video": False,
                    "events": True,
                    "greetings": True,
                    "footer": True
                },
                "link_expiry_type": "days",
                "link_expiry_value": 30
            }
            
            try:
                response = self.session.post(f"{BACKEND_URL}/admin/profiles", json=profile_data)
                
                if response.status_code == 200:
                    profile = response.json()
                    
                    # Verify enabled_languages stored correctly
                    if profile.get("enabled_languages") == test_case["enabled_languages"]:
                        self.log_test(f"{test_case['name']} - Language Storage", True, 
                                    f"Languages: {profile['enabled_languages']}")
                    else:
                        self.log_test(f"{test_case['name']} - Language Storage", False, 
                                    f"Expected: {test_case['enabled_languages']}, Got: {profile.get('enabled_languages')}")
                    
                    # Verify profile created successfully
                    if profile.get("slug") and profile.get("invitation_link"):
                        self.log_test(f"{test_case['name']} - Profile Creation", True, 
                                    f"Slug: {profile['slug']}")
                    else:
                        self.log_test(f"{test_case['name']} - Profile Creation", False, 
                                    "Missing slug or invitation_link")
                    
                    self.test_profiles.append(profile)
                    
                else:
                    self.log_test(f"{test_case['name']} - Profile Creation", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test(f"{test_case['name']} - Profile Creation", False, f"Exception: {str(e)}")
        
        return True
    
    def test_multi_language_combinations(self):
        """Test 2: Multi-Language Combinations"""
        print("\n🔀 TESTING MULTI-LANGUAGE COMBINATIONS...")
        
        # Test various language combinations
        combinations = [
            {
                "name": "Telugu + Tamil",
                "groom_name": "Suresh Babu",
                "bride_name": "Meera Devi",
                "enabled_languages": ["telugu", "tamil"],
                "venue": "Heritage Hotel, Chennai"
            },
            {
                "name": "Hindi + Kannada + Malayalam",
                "groom_name": "Arjun Singh",
                "bride_name": "Deepika Nair",
                "enabled_languages": ["hindi", "kannada", "malayalam"],
                "venue": "Palace Grounds, Bangalore"
            },
            {
                "name": "All 6 Languages",
                "groom_name": "Vikram Reddy",
                "bride_name": "Sita Sharma",
                "enabled_languages": ["english", "telugu", "hindi", "tamil", "kannada", "malayalam"],
                "venue": "International Convention Center, Hyderabad"
            }
        ]
        
        for combo in combinations:
            profile_data = {
                "groom_name": combo["groom_name"],
                "bride_name": combo["bride_name"],
                "event_type": "marriage",
                "event_date": "2024-12-30T14:00:00Z",
                "venue": combo["venue"],
                "language": combo["enabled_languages"],
                "design_id": "royal_classic",
                "enabled_languages": combo["enabled_languages"],
                "sections_enabled": {
                    "opening": True,
                    "welcome": True,
                    "couple": True,
                    "photos": True,
                    "video": True,
                    "events": True,
                    "greetings": True,
                    "footer": True
                }
            }
            
            try:
                response = self.session.post(f"{BACKEND_URL}/admin/profiles", json=profile_data)
                
                if response.status_code == 200:
                    profile = response.json()
                    
                    # Verify all languages stored correctly
                    if set(profile.get("enabled_languages", [])) == set(combo["enabled_languages"]):
                        self.log_test(f"{combo['name']} - Combination Storage", True, 
                                    f"Languages: {profile['enabled_languages']}")
                    else:
                        self.log_test(f"{combo['name']} - Combination Storage", False, 
                                    f"Expected: {combo['enabled_languages']}, Got: {profile.get('enabled_languages')}")
                    
                    self.test_profiles.append(profile)
                    
                else:
                    self.log_test(f"{combo['name']} - Profile Creation", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test(f"{combo['name']} - Profile Creation", False, f"Exception: {str(e)}")
        
        return True
    
    def test_profile_update_languages(self):
        """Test 3: Profile Update with New Languages"""
        print("\n🔄 TESTING PROFILE UPDATE WITH NEW LANGUAGES...")
        
        # Create initial profile with English only
        initial_profile = {
            "groom_name": "Ramesh Kumar",
            "bride_name": "Sunita Devi",
            "event_type": "marriage",
            "event_date": "2024-12-28T16:00:00Z",
            "venue": "Garden Resort, Kerala",
            "language": ["english"],
            "design_id": "floral_soft",
            "enabled_languages": ["english"]
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/profiles", json=initial_profile)
            
            if response.status_code == 200:
                profile = response.json()
                profile_id = profile["id"]
                
                self.log_test("Initial Profile Creation", True, f"Profile ID: {profile_id}")
                
                # Update to add new languages
                update_data = {
                    "enabled_languages": ["english", "tamil", "kannada"]
                }
                
                response = self.session.put(f"{BACKEND_URL}/admin/profiles/{profile_id}", json=update_data)
                
                if response.status_code == 200:
                    updated_profile = response.json()
                    
                    # Verify languages updated correctly
                    expected_languages = ["english", "tamil", "kannada"]
                    if set(updated_profile.get("enabled_languages", [])) == set(expected_languages):
                        self.log_test("Profile Language Update", True, 
                                    f"Updated languages: {updated_profile['enabled_languages']}")
                    else:
                        self.log_test("Profile Language Update", False, 
                                    f"Expected: {expected_languages}, Got: {updated_profile.get('enabled_languages')}")
                    
                    # Verify slug remains unchanged
                    if updated_profile.get("slug") == profile.get("slug"):
                        self.log_test("Slug Persistence After Update", True, "Slug unchanged")
                    else:
                        self.log_test("Slug Persistence After Update", False, "Slug changed")
                    
                    self.test_profiles.append(updated_profile)
                    
                else:
                    self.log_test("Profile Language Update", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
                    
            else:
                self.log_test("Initial Profile Creation", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Profile Update Test", False, f"Exception: {str(e)}")
        
        return True
    
    def test_public_invitation_api_languages(self):
        """Test 4: Public Invitation API with New Languages"""
        print("\n🌐 TESTING PUBLIC INVITATION API WITH NEW LANGUAGES...")
        
        if not self.test_profiles:
            self.log_test("Public API Language Test", False, "No test profiles available")
            return False
        
        # Create profile specifically for public API testing
        public_test_profile = {
            "groom_name": "Anil Reddy",
            "bride_name": "Kavya Nair",
            "event_type": "marriage",
            "event_date": "2024-12-31T12:00:00Z",
            "venue": "Beach Resort, Goa",
            "language": ["tamil", "kannada"],
            "design_id": "cinematic_luxury",
            "enabled_languages": ["tamil", "kannada"],
            "sections_enabled": {
                "opening": True,
                "welcome": True,
                "couple": True,
                "photos": True,
                "video": False,
                "events": True,
                "greetings": True,
                "footer": True
            }
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/profiles", json=public_test_profile)
            
            if response.status_code == 200:
                profile = response.json()
                slug = profile["slug"]
                
                # Test public API without authentication
                public_session = requests.Session()
                
                response = public_session.get(f"{BACKEND_URL}/invite/{slug}")
                
                if response.status_code == 200:
                    invitation_data = response.json()
                    
                    # Verify enabled_languages field present
                    if "enabled_languages" in invitation_data:
                        self.log_test("Public API - Languages Field Present", True, 
                                    "enabled_languages field found")
                        
                        # Verify correct languages returned
                        expected_languages = ["tamil", "kannada"]
                        if set(invitation_data.get("enabled_languages", [])) == set(expected_languages):
                            self.log_test("Public API - Correct Languages", True, 
                                        f"Languages: {invitation_data['enabled_languages']}")
                        else:
                            self.log_test("Public API - Correct Languages", False, 
                                        f"Expected: {expected_languages}, Got: {invitation_data.get('enabled_languages')}")
                    else:
                        self.log_test("Public API - Languages Field Present", False, 
                                    "enabled_languages field missing")
                    
                    # Verify other required fields still present
                    required_fields = ["slug", "groom_name", "bride_name", "design_id"]
                    missing_fields = [field for field in required_fields if field not in invitation_data]
                    
                    if not missing_fields:
                        self.log_test("Public API - Complete Data", True, "All required fields present")
                    else:
                        self.log_test("Public API - Complete Data", False, f"Missing: {missing_fields}")
                    
                else:
                    self.log_test("Public API Access", False, f"Status: {response.status_code}")
                    
                self.test_profiles.append(profile)
                
            else:
                self.log_test("Public API Test Profile Creation", False, 
                            f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Public API Language Test", False, f"Exception: {str(e)}")
        
        return True
    
    def test_admin_profile_retrieval_languages(self):
        """Test 5: Admin Profile Retrieval with New Languages"""
        print("\n👨‍💼 TESTING ADMIN PROFILE RETRIEVAL WITH NEW LANGUAGES...")
        
        # Create multiple profiles with different language combinations
        test_profiles_data = [
            {
                "groom_name": "Mohan Lal",
                "bride_name": "Radha Devi",
                "enabled_languages": ["malayalam", "tamil"],
                "venue": "Cochin Palace, Kerala"
            },
            {
                "groom_name": "Ganesh Rao",
                "bride_name": "Lakshmi Bai",
                "enabled_languages": ["kannada", "english"],
                "venue": "Mysore Gardens, Karnataka"
            },
            {
                "groom_name": "Ravi Kumar",
                "bride_name": "Sita Devi",
                "enabled_languages": ["tamil", "telugu", "hindi"],
                "venue": "Temple Complex, Tamil Nadu"
            }
        ]
        
        created_profiles = []
        
        # Create test profiles
        for profile_data in test_profiles_data:
            full_profile = {
                "groom_name": profile_data["groom_name"],
                "bride_name": profile_data["bride_name"],
                "event_type": "marriage",
                "event_date": "2024-12-29T11:00:00Z",
                "venue": profile_data["venue"],
                "language": profile_data["enabled_languages"],
                "design_id": "heritage_scroll",
                "enabled_languages": profile_data["enabled_languages"]
            }
            
            try:
                response = self.session.post(f"{BACKEND_URL}/admin/profiles", json=full_profile)
                
                if response.status_code == 200:
                    profile = response.json()
                    created_profiles.append({
                        "profile": profile,
                        "expected_languages": profile_data["enabled_languages"]
                    })
                    
            except Exception as e:
                self.log_test(f"Profile Creation for Admin Test", False, f"Exception: {str(e)}")
        
        # Test GET all profiles
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/profiles")
            
            if response.status_code == 200:
                all_profiles = response.json()
                
                self.log_test("Admin Get All Profiles", True, f"Retrieved {len(all_profiles)} profiles")
                
                # Verify our created profiles are in the list with correct languages
                for created_profile_data in created_profiles:
                    profile_id = created_profile_data["profile"]["id"]
                    expected_languages = created_profile_data["expected_languages"]
                    
                    # Find profile in the list
                    found_profile = next((p for p in all_profiles if p["id"] == profile_id), None)
                    
                    if found_profile:
                        if set(found_profile.get("enabled_languages", [])) == set(expected_languages):
                            self.log_test(f"Admin API - Profile Languages ({found_profile['groom_name']})", True, 
                                        f"Languages: {found_profile['enabled_languages']}")
                        else:
                            self.log_test(f"Admin API - Profile Languages ({found_profile['groom_name']})", False, 
                                        f"Expected: {expected_languages}, Got: {found_profile.get('enabled_languages')}")
                    else:
                        self.log_test(f"Admin API - Profile Found", False, f"Profile {profile_id} not found")
                
            else:
                self.log_test("Admin Get All Profiles", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Admin Profile Retrieval Test", False, f"Exception: {str(e)}")
        
        # Test GET single profile
        if created_profiles:
            profile_id = created_profiles[0]["profile"]["id"]
            expected_languages = created_profiles[0]["expected_languages"]
            
            try:
                response = self.session.get(f"{BACKEND_URL}/admin/profiles/{profile_id}")
                
                if response.status_code == 200:
                    single_profile = response.json()
                    
                    if set(single_profile.get("enabled_languages", [])) == set(expected_languages):
                        self.log_test("Admin Get Single Profile - Languages", True, 
                                    f"Languages: {single_profile['enabled_languages']}")
                    else:
                        self.log_test("Admin Get Single Profile - Languages", False, 
                                    f"Expected: {expected_languages}, Got: {single_profile.get('enabled_languages')}")
                    
                else:
                    self.log_test("Admin Get Single Profile", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Admin Single Profile Test", False, f"Exception: {str(e)}")
        
        return True
    
    def test_language_validation(self):
        """Test 6: Language Validation"""
        print("\n✅ TESTING LANGUAGE VALIDATION...")
        
        # Test valid new language codes
        valid_languages = ["tamil", "kannada", "malayalam"]
        
        for lang in valid_languages:
            profile_data = {
                "groom_name": f"Test Groom {lang}",
                "bride_name": f"Test Bride {lang}",
                "event_type": "marriage",
                "event_date": "2024-12-27T10:00:00Z",
                "venue": f"Test Venue for {lang}",
                "language": [lang],
                "design_id": "modern_premium",
                "enabled_languages": [lang]
            }
            
            try:
                response = self.session.post(f"{BACKEND_URL}/admin/profiles", json=profile_data)
                
                if response.status_code == 200:
                    self.log_test(f"Valid Language Code: {lang}", True, f"Language '{lang}' accepted")
                else:
                    self.log_test(f"Valid Language Code: {lang}", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Valid Language Code: {lang}", False, f"Exception: {str(e)}")
        
        # Test mixed valid languages (old + new)
        mixed_profile = {
            "groom_name": "Mixed Language Groom",
            "bride_name": "Mixed Language Bride",
            "event_type": "marriage",
            "event_date": "2024-12-26T15:00:00Z",
            "venue": "Multi-Cultural Center",
            "language": ["english", "telugu", "tamil", "kannada", "malayalam"],
            "design_id": "artistic_handcrafted",
            "enabled_languages": ["english", "telugu", "tamil", "kannada", "malayalam"]
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/profiles", json=mixed_profile)
            
            if response.status_code == 200:
                profile = response.json()
                expected_languages = ["english", "telugu", "tamil", "kannada", "malayalam"]
                
                if set(profile.get("enabled_languages", [])) == set(expected_languages):
                    self.log_test("Mixed Language Validation", True, 
                                f"All languages accepted: {profile['enabled_languages']}")
                else:
                    self.log_test("Mixed Language Validation", False, 
                                f"Expected: {expected_languages}, Got: {profile.get('enabled_languages')}")
            else:
                self.log_test("Mixed Language Validation", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Mixed Language Validation", False, f"Exception: {str(e)}")
        
        # Test at least 1 language requirement
        empty_language_profile = {
            "groom_name": "No Language Groom",
            "bride_name": "No Language Bride",
            "event_type": "marriage",
            "event_date": "2024-12-25T12:00:00Z",
            "venue": "Test Venue",
            "language": [],
            "design_id": "temple_divine",
            "enabled_languages": []
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/profiles", json=empty_language_profile)
            
            if response.status_code == 422:  # Validation error expected
                self.log_test("Empty Language Validation", True, "Empty language array properly rejected")
            elif response.status_code == 200:
                # Check if it defaults to English
                profile = response.json()
                if profile.get("enabled_languages") == ["english"]:
                    self.log_test("Empty Language Default", True, "Defaults to English when empty")
                else:
                    self.log_test("Empty Language Handling", False, "Unexpected behavior with empty languages")
            else:
                self.log_test("Empty Language Validation", False, 
                            f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Empty Language Validation", False, f"Exception: {str(e)}")
        
        return True
    
    def run_all_tests(self):
        """Run all Phase 4 language tests"""
        print("🚀 STARTING PHASE 4 - EXTENDED MULTI-LANGUAGE SYSTEM TESTING")
        print("=" * 70)
        print("Testing new language codes: tamil, kannada, malayalam")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ AUTHENTICATION FAILED - STOPPING TESTS")
            return False
        
        # Run all tests
        tests = [
            self.test_profile_creation_new_languages,
            self.test_multi_language_combinations,
            self.test_profile_update_languages,
            self.test_public_invitation_api_languages,
            self.test_admin_profile_retrieval_languages,
            self.test_language_validation
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ TEST FAILED WITH EXCEPTION: {str(e)}")
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 PHASE 4 LANGUAGE TESTING SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n📝 CREATED {len(self.test_profiles)} TEST PROFILES WITH NEW LANGUAGES")
        for i, profile in enumerate(self.test_profiles):
            languages = profile.get('enabled_languages', [])
            print(f"   {i+1}. {profile['groom_name']} & {profile['bride_name']} - Languages: {languages}")
        
        print("\n🎯 PHASE 4 TESTING FOCUS:")
        print("   ✅ Tamil language code support")
        print("   ✅ Kannada language code support") 
        print("   ✅ Malayalam language code support")
        print("   ✅ Multi-language combinations (1-6 languages)")
        print("   ✅ Profile CRUD operations with new languages")
        print("   ✅ Public invitation API language support")
        print("   ✅ Admin profile retrieval with languages")
        print("   ✅ Language validation and error handling")


if __name__ == "__main__":
    tester = Phase4LanguageTester()
    tester.run_all_tests()