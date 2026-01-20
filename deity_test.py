#!/usr/bin/env python3
"""
PHASE 3 - Deity Background Layer Backend Testing
Testing deity_id field CRUD operations as per review request
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Configuration
BACKEND_URL = "https://wed-management.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@wedding.com"
ADMIN_PASSWORD = "admin123"

class DeityBackgroundTester:
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
    
    def test_profile_creation_without_deity_id(self):
        """Test 1: Profile creation WITHOUT deity_id - should default to null"""
        print("\n📝 TEST 1: Profile creation WITHOUT deity_id...")
        
        profile_data = {
            "groom_name": "Arjun Sharma",
            "bride_name": "Meera Patel",
            "event_type": "marriage",
            "event_date": "2024-12-25T10:00:00Z",
            "venue": "Grand Palace Hotel, Mumbai",
            "language": ["english", "hindi"],
            "design_id": "divine_temple",
            "whatsapp_groom": "+919876543210",
            "whatsapp_bride": "+918765432109",
            "enabled_languages": ["english", "hindi"],
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
            # No deity_id specified
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/profiles", json=profile_data)
            
            if response.status_code == 200:
                profile = response.json()
                
                # Verify deity_id defaults to null
                deity_id = profile.get("deity_id")
                if deity_id is None:
                    self.log_test("Profile creation without deity_id defaults to null", True, "deity_id is null as expected")
                else:
                    self.log_test("Profile creation without deity_id defaults to null", False, f"Expected null, got: {deity_id}")
                
                self.test_profiles.append(profile)
                return True
                
            else:
                self.log_test("Profile creation without deity_id", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Profile creation without deity_id", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_creation_with_ganesha(self):
        """Test 2: Profile creation WITH deity_id='ganesha'"""
        print("\n📝 TEST 2: Profile creation WITH deity_id='ganesha'...")
        
        profile_data = {
            "groom_name": "Vikram Reddy",
            "bride_name": "Priya Nair",
            "event_type": "marriage",
            "event_date": "2024-12-28T11:00:00Z",
            "venue": "Temple Gardens, Bangalore",
            "language": ["english", "telugu"],
            "design_id": "royal_classic",
            "deity_id": "ganesha",
            "whatsapp_groom": "+919123456789",
            "whatsapp_bride": "+918987654321",
            "enabled_languages": ["english", "telugu", "hindi"],
            "sections_enabled": {
                "opening": True,
                "welcome": True,
                "couple": True,
                "photos": True,
                "video": True,
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
                
                # Verify deity_id is stored correctly
                if profile.get("deity_id") == "ganesha":
                    self.log_test("Profile creation with deity_id='ganesha'", True, "deity_id stored correctly")
                else:
                    self.log_test("Profile creation with deity_id='ganesha'", False, f"Expected 'ganesha', got: {profile.get('deity_id')}")
                
                self.test_profiles.append(profile)
                return True
                
            else:
                self.log_test("Profile creation with deity_id='ganesha'", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Profile creation with deity_id='ganesha'", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_creation_with_venkateswara_padmavati(self):
        """Test 3: Profile creation WITH deity_id='venkateswara_padmavati'"""
        print("\n📝 TEST 3: Profile creation WITH deity_id='venkateswara_padmavati'...")
        
        profile_data = {
            "groom_name": "Karthik Iyer",
            "bride_name": "Ananya Reddy",
            "event_type": "marriage",
            "event_date": "2024-12-30T09:00:00Z",
            "venue": "Tirumala Temple Complex, Tirupati",
            "language": ["telugu", "english"],
            "design_id": "royal_classic",
            "deity_id": "venkateswara_padmavati",
            "whatsapp_groom": "+919234567890",
            "whatsapp_bride": "+918876543210",
            "enabled_languages": ["telugu", "english", "hindi"],
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
            "link_expiry_value": 45
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/profiles", json=profile_data)
            
            if response.status_code == 200:
                profile = response.json()
                
                # Verify deity_id is stored correctly
                if profile.get("deity_id") == "venkateswara_padmavati":
                    self.log_test("Profile creation with deity_id='venkateswara_padmavati'", True, "deity_id stored correctly")
                else:
                    self.log_test("Profile creation with deity_id='venkateswara_padmavati'", False, f"Expected 'venkateswara_padmavati', got: {profile.get('deity_id')}")
                
                self.test_profiles.append(profile)
                return True
                
            else:
                self.log_test("Profile creation with deity_id='venkateswara_padmavati'", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Profile creation with deity_id='venkateswara_padmavati'", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_creation_with_shiva_parvati(self):
        """Test 4: Profile creation WITH deity_id='shiva_parvati'"""
        print("\n📝 TEST 4: Profile creation WITH deity_id='shiva_parvati'...")
        
        profile_data = {
            "groom_name": "Rohit Gupta",
            "bride_name": "Kavya Sharma",
            "event_type": "marriage",
            "event_date": "2025-01-15T16:00:00Z",
            "venue": "Shiva Temple, Varanasi",
            "language": ["hindi", "english"],
            "design_id": "cinematic_luxury",
            "deity_id": "shiva_parvati",
            "whatsapp_groom": "+919345678901",
            "whatsapp_bride": "+918765432198",
            "enabled_languages": ["hindi", "english"],
            "sections_enabled": {
                "opening": True,
                "welcome": True,
                "couple": True,
                "photos": True,
                "video": True,
                "events": True,
                "greetings": True,
                "footer": True
            },
            "link_expiry_type": "days",
            "link_expiry_value": 60
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/profiles", json=profile_data)
            
            if response.status_code == 200:
                profile = response.json()
                
                # Verify deity_id is stored correctly
                if profile.get("deity_id") == "shiva_parvati":
                    self.log_test("Profile creation with deity_id='shiva_parvati'", True, "deity_id stored correctly")
                else:
                    self.log_test("Profile creation with deity_id='shiva_parvati'", False, f"Expected 'shiva_parvati', got: {profile.get('deity_id')}")
                
                self.test_profiles.append(profile)
                return True
                
            else:
                self.log_test("Profile creation with deity_id='shiva_parvati'", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Profile creation with deity_id='shiva_parvati'", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_creation_with_lakshmi_vishnu(self):
        """Test 5: Profile creation WITH deity_id='lakshmi_vishnu'"""
        print("\n📝 TEST 5: Profile creation WITH deity_id='lakshmi_vishnu'...")
        
        profile_data = {
            "groom_name": "Aditya Joshi",
            "bride_name": "Riya Mehta",
            "event_type": "marriage",
            "event_date": "2025-02-14T12:00:00Z",
            "venue": "Lakshmi Narayan Temple, Delhi",
            "language": ["hindi", "english"],
            "design_id": "floral_soft",
            "deity_id": "lakshmi_vishnu",
            "whatsapp_groom": "+919456789012",
            "whatsapp_bride": "+918654321987",
            "enabled_languages": ["hindi", "english", "telugu"],
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
                
                # Verify deity_id is stored correctly
                if profile.get("deity_id") == "lakshmi_vishnu":
                    self.log_test("Profile creation with deity_id='lakshmi_vishnu'", True, "deity_id stored correctly")
                else:
                    self.log_test("Profile creation with deity_id='lakshmi_vishnu'", False, f"Expected 'lakshmi_vishnu', got: {profile.get('deity_id')}")
                
                self.test_profiles.append(profile)
                return True
                
            else:
                self.log_test("Profile creation with deity_id='lakshmi_vishnu'", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Profile creation with deity_id='lakshmi_vishnu'", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_creation_with_none(self):
        """Test 6: Profile creation WITH deity_id='none'"""
        print("\n📝 TEST 6: Profile creation WITH deity_id='none'...")
        
        profile_data = {
            "groom_name": "Sameer Khan",
            "bride_name": "Fatima Ali",
            "event_type": "marriage",
            "event_date": "2025-03-20T14:00:00Z",
            "venue": "Grand Ballroom, Hyderabad",
            "language": ["english", "hindi"],
            "design_id": "modern_minimal",
            "deity_id": "none",
            "whatsapp_groom": "+919567890123",
            "whatsapp_bride": "+918543219876",
            "enabled_languages": ["english", "hindi"],
            "sections_enabled": {
                "opening": True,
                "welcome": True,
                "couple": True,
                "photos": True,
                "video": True,
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
                
                # Verify deity_id is stored as 'none'
                if profile.get("deity_id") == "none":
                    self.log_test("Profile creation with deity_id='none'", True, "deity_id stored as 'none'")
                else:
                    self.log_test("Profile creation with deity_id='none'", False, f"Expected 'none', got: {profile.get('deity_id')}")
                
                self.test_profiles.append(profile)
                return True
                
            else:
                self.log_test("Profile creation with deity_id='none'", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Profile creation with deity_id='none'", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_update_null_to_ganesha(self):
        """Test 7: Profile update to change deity_id from null to 'ganesha'"""
        print("\n📝 TEST 7: Profile update from null to 'ganesha'...")
        
        if not self.test_profiles:
            self.log_test("Profile update null to ganesha", False, "No test profiles available")
            return False
        
        # Use first profile (which should have null deity_id)
        profile = self.test_profiles[0]
        profile_id = profile["id"]
        
        update_data = {
            "deity_id": "ganesha"
        }
        
        try:
            response = self.session.put(f"{BACKEND_URL}/admin/profiles/{profile_id}", json=update_data)
            
            if response.status_code == 200:
                updated_profile = response.json()
                
                # Verify deity_id was updated to 'ganesha'
                if updated_profile.get("deity_id") == "ganesha":
                    self.log_test("Profile update null to 'ganesha'", True, "deity_id updated successfully")
                    
                    # Update our local copy
                    self.test_profiles[0] = updated_profile
                else:
                    self.log_test("Profile update null to 'ganesha'", False, f"Expected 'ganesha', got: {updated_profile.get('deity_id')}")
                
                return True
                
            else:
                self.log_test("Profile update null to 'ganesha'", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Profile update null to 'ganesha'", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_update_ganesha_to_null(self):
        """Test 8: Profile update to change deity_id from 'ganesha' to null"""
        print("\n📝 TEST 8: Profile update from 'ganesha' to null...")
        
        if len(self.test_profiles) < 2:
            self.log_test("Profile update ganesha to null", False, "Not enough test profiles available")
            return False
        
        # Use second profile (which should have 'ganesha' deity_id)
        profile = self.test_profiles[1]
        profile_id = profile["id"]
        
        update_data = {
            "deity_id": None
        }
        
        try:
            response = self.session.put(f"{BACKEND_URL}/admin/profiles/{profile_id}", json=update_data)
            
            if response.status_code == 200:
                updated_profile = response.json()
                
                # Verify deity_id was updated to null
                if updated_profile.get("deity_id") is None:
                    self.log_test("Profile update 'ganesha' to null", True, "deity_id updated to null successfully")
                    
                    # Update our local copy
                    self.test_profiles[1] = updated_profile
                else:
                    self.log_test("Profile update 'ganesha' to null", False, f"Expected null, got: {updated_profile.get('deity_id')}")
                
                return True
                
            else:
                self.log_test("Profile update 'ganesha' to null", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Profile update 'ganesha' to null", False, f"Exception: {str(e)}")
            return False
    
    def test_get_profile_by_id_includes_deity_id(self):
        """Test 9: GET profile by ID should include deity_id in response"""
        print("\n📝 TEST 9: GET profile by ID includes deity_id...")
        
        if not self.test_profiles:
            self.log_test("GET profile by ID includes deity_id", False, "No test profiles available")
            return False
        
        # Test with multiple profiles to verify different deity_id values
        for i, profile in enumerate(self.test_profiles[:3]):  # Test first 3 profiles
            profile_id = profile["id"]
            
            try:
                response = self.session.get(f"{BACKEND_URL}/admin/profiles/{profile_id}")
                
                if response.status_code == 200:
                    retrieved_profile = response.json()
                    
                    # Verify deity_id field is present in response
                    if "deity_id" in retrieved_profile:
                        expected_deity_id = profile.get("deity_id")
                        actual_deity_id = retrieved_profile.get("deity_id")
                        
                        if expected_deity_id == actual_deity_id:
                            self.log_test(f"GET profile by ID includes deity_id (Profile {i+1})", True, f"deity_id: {actual_deity_id}")
                        else:
                            self.log_test(f"GET profile by ID includes deity_id (Profile {i+1})", False, f"Expected: {expected_deity_id}, Got: {actual_deity_id}")
                    else:
                        self.log_test(f"GET profile by ID includes deity_id (Profile {i+1})", False, "deity_id field missing from response")
                        
                else:
                    self.log_test(f"GET profile by ID (Profile {i+1})", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"GET profile by ID test (Profile {i+1})", False, f"Exception: {str(e)}")
        
        return True
    
    def test_get_all_profiles_includes_deity_id(self):
        """Test 10: GET all profiles should include deity_id in response"""
        print("\n📝 TEST 10: GET all profiles includes deity_id...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/profiles")
            
            if response.status_code == 200:
                all_profiles = response.json()
                
                if not all_profiles:
                    self.log_test("GET all profiles includes deity_id", False, "No profiles returned")
                    return False
                
                # Check if deity_id field is present in all profiles
                profiles_with_deity_id = 0
                for profile in all_profiles:
                    if "deity_id" in profile:
                        profiles_with_deity_id += 1
                
                if profiles_with_deity_id == len(all_profiles):
                    self.log_test("GET all profiles includes deity_id", True, f"All {len(all_profiles)} profiles include deity_id field")
                else:
                    self.log_test("GET all profiles includes deity_id", False, f"Only {profiles_with_deity_id}/{len(all_profiles)} profiles include deity_id")
                
                return True
                
            else:
                self.log_test("GET all profiles includes deity_id", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("GET all profiles includes deity_id", False, f"Exception: {str(e)}")
            return False
    
    def test_public_invitation_api_includes_deity_id(self):
        """Test 11: Public invitation API GET /api/invite/:slug should include deity_id in response"""
        print("\n📝 TEST 11: Public invitation API includes deity_id...")
        
        if not self.test_profiles:
            self.log_test("Public invitation API includes deity_id", False, "No test profiles available")
            return False
        
        # Test without authentication
        public_session = requests.Session()
        
        # Test with multiple profiles to verify different deity_id values
        for i, profile in enumerate(self.test_profiles[:3]):  # Test first 3 profiles
            slug = profile["slug"]
            
            try:
                response = public_session.get(f"{BACKEND_URL}/invite/{slug}")
                
                if response.status_code == 200:
                    invitation_data = response.json()
                    
                    # Verify deity_id field is present in response
                    if "deity_id" in invitation_data:
                        expected_deity_id = profile.get("deity_id")
                        actual_deity_id = invitation_data.get("deity_id")
                        
                        if expected_deity_id == actual_deity_id:
                            self.log_test(f"Public API includes deity_id (Profile {i+1})", True, f"deity_id: {actual_deity_id}")
                        else:
                            self.log_test(f"Public API includes deity_id (Profile {i+1})", False, f"Expected: {expected_deity_id}, Got: {actual_deity_id}")
                    else:
                        self.log_test(f"Public API includes deity_id (Profile {i+1})", False, "deity_id field missing from response")
                        
                else:
                    self.log_test(f"Public API access (Profile {i+1})", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Public API test (Profile {i+1})", False, f"Exception: {str(e)}")
        
        return True
    
    def test_invalid_deity_id_rejection(self):
        """Test 12: Invalid deity_id should be rejected with validation error"""
        print("\n📝 TEST 12: Invalid deity_id rejection...")
        
        # Test with invalid deity_id
        invalid_profile_data = {
            "groom_name": "Test Groom",
            "bride_name": "Test Bride",
            "event_type": "marriage",
            "event_date": "2025-01-01T10:00:00Z",
            "venue": "Test Venue",
            "language": ["english"],
            "design_id": "royal_classic",
            "deity_id": "invalid_deity_name",  # Invalid deity_id
            "enabled_languages": ["english"],
            "sections_enabled": {
                "opening": True,
                "welcome": True,
                "couple": True,
                "photos": False,
                "video": False,
                "events": True,
                "greetings": True,
                "footer": True
            }
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/profiles", json=invalid_profile_data)
            
            # Should return validation error (422)
            if response.status_code == 422:
                self.log_test("Invalid deity_id rejection", True, "Invalid deity_id properly rejected with 422")
            elif response.status_code == 200:
                # If it succeeds, check if the invalid value was stored
                profile = response.json()
                if profile.get("deity_id") == "invalid_deity_name":
                    self.log_test("Invalid deity_id rejection", False, "Invalid deity_id was accepted and stored")
                else:
                    self.log_test("Invalid deity_id rejection", True, f"Invalid deity_id was transformed/rejected, stored as: {profile.get('deity_id')}")
            else:
                self.log_test("Invalid deity_id rejection", False, f"Unexpected status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Invalid deity_id rejection", False, f"Exception: {str(e)}")
        
        # Test with another invalid deity_id in profile update
        if self.test_profiles:
            profile_id = self.test_profiles[0]["id"]
            
            try:
                update_data = {
                    "deity_id": "another_invalid_deity"
                }
                
                response = self.session.put(f"{BACKEND_URL}/admin/profiles/{profile_id}", json=update_data)
                
                if response.status_code == 422:
                    self.log_test("Invalid deity_id rejection in update", True, "Invalid deity_id in update properly rejected")
                elif response.status_code == 200:
                    updated_profile = response.json()
                    if updated_profile.get("deity_id") == "another_invalid_deity":
                        self.log_test("Invalid deity_id rejection in update", False, "Invalid deity_id in update was accepted")
                    else:
                        self.log_test("Invalid deity_id rejection in update", True, f"Invalid deity_id in update was transformed/rejected, stored as: {updated_profile.get('deity_id')}")
                else:
                    self.log_test("Invalid deity_id rejection in update", False, f"Unexpected status code: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Invalid deity_id rejection in update", False, f"Exception: {str(e)}")
        
        return True
    
    def run_all_deity_tests(self):
        """Run all deity_id field tests"""
        print("🕉️ STARTING PHASE 3 - DEITY BACKGROUND LAYER BACKEND TESTING")
        print("=" * 70)
        print("Testing deity_id field CRUD operations as per review request")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ AUTHENTICATION FAILED - STOPPING TESTS")
            return False
        
        # Run all deity tests in sequence
        tests = [
            self.test_profile_creation_without_deity_id,
            self.test_profile_creation_with_ganesha,
            self.test_profile_creation_with_venkateswara_padmavati,
            self.test_profile_creation_with_shiva_parvati,
            self.test_profile_creation_with_lakshmi_vishnu,
            self.test_profile_creation_with_none,
            self.test_profile_update_null_to_ganesha,
            self.test_profile_update_ganesha_to_null,
            self.test_get_profile_by_id_includes_deity_id,
            self.test_get_all_profiles_includes_deity_id,
            self.test_public_invitation_api_includes_deity_id,
            self.test_invalid_deity_id_rejection
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
        print("📊 DEITY BACKGROUND LAYER TEST SUMMARY")
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
        
        print(f"\n📝 CREATED {len(self.test_profiles)} TEST PROFILES WITH DEITY_ID TESTING")
        for i, profile in enumerate(self.test_profiles):
            deity_display = profile.get('deity_id') if profile.get('deity_id') is not None else 'null'
            print(f"   {i+1}. {profile['groom_name']} & {profile['bride_name']} - deity_id: {deity_display} - /invite/{profile['slug']}")
        
        print("\n🕉️ DEITY_ID FIELD VERIFICATION COMPLETE")
        print("All CRUD operations tested for deity background layer functionality")


if __name__ == "__main__":
    tester = DeityBackgroundTester()
    tester.run_all_deity_tests()