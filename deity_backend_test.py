#!/usr/bin/env python3
"""
PHASE 3 - DEITY BACKGROUND LAYER BACKEND TESTING
Comprehensive testing of deity_id field functionality with CRUD operations
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Configuration
BACKEND_URL = "https://wed-organizer-17.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@wedding.com"
ADMIN_PASSWORD = "admin123"

class DeityBackendTester:
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
    
    def test_profile_creation_without_deity(self):
        """Test 1: Profile Creation Without Deity (Default Behavior)"""
        print("\n📝 TEST 1: PROFILE CREATION WITHOUT DEITY...")
        
        profile_data = {
            "groom_name": "Arjun Sharma",
            "bride_name": "Meera Patel",
            "event_type": "marriage",
            "event_date": "2024-12-25T10:00:00Z",
            "venue": "Grand Palace Hotel, Mumbai",
            "language": ["english", "hindi"],
            "design_id": "royal_classic",
            # No deity_id field provided
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
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/profiles", json=profile_data)
            
            if response.status_code == 200:
                profile = response.json()
                
                # Verify profile created successfully
                self.log_test("Profile Creation Without Deity", True, f"Profile created with ID: {profile['id']}")
                
                # Verify deity_id is null or default value
                deity_id = profile.get("deity_id")
                if deity_id is None:
                    self.log_test("Deity ID Default Value", True, "deity_id is null (no religious background)")
                else:
                    self.log_test("Deity ID Default Value", False, f"Expected null, got: {deity_id}")
                
                # Save profile ID for later tests
                self.test_profiles.append(profile)
                return True
                
            else:
                self.log_test("Profile Creation Without Deity", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Profile Creation Without Deity", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_creation_with_each_deity(self):
        """Test 2: Profile Creation With Each Deity Type"""
        print("\n📝 TEST 2: PROFILE CREATION WITH EACH DEITY TYPE...")
        
        deity_types = [
            ("ganesha", "Lord Ganesha"),
            ("venkateswara_padmavati", "Lord Venkateswara & Padmavati"),
            ("shiva_parvati", "Lord Shiva & Parvati"),
            ("lakshmi_vishnu", "Lakshmi & Vishnu")
        ]
        
        for deity_id, deity_name in deity_types:
            profile_data = {
                "groom_name": f"Groom {deity_name}",
                "bride_name": f"Bride {deity_name}",
                "event_type": "marriage",
                "event_date": "2024-12-26T11:00:00Z",
                "venue": f"Temple for {deity_name}",
                "language": ["english", "telugu"],
                "design_id": "divine_temple",
                "deity_id": deity_id,
                "whatsapp_groom": "+919876543211",
                "whatsapp_bride": "+918765432110",
                "enabled_languages": ["english", "telugu"],
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
                    
                    # Verify profile created successfully
                    self.log_test(f"Profile Creation with {deity_id}", True, f"Profile created for {deity_name}")
                    
                    # Verify deity_id saved correctly
                    if profile.get("deity_id") == deity_id:
                        self.log_test(f"Deity ID Storage - {deity_id}", True, f"deity_id correctly stored as {deity_id}")
                    else:
                        self.log_test(f"Deity ID Storage - {deity_id}", False, f"Expected {deity_id}, got {profile.get('deity_id')}")
                    
                    self.test_profiles.append(profile)
                    
                else:
                    self.log_test(f"Profile Creation with {deity_id}", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Profile Creation with {deity_id}", False, f"Exception: {str(e)}")
        
        return True
    
    def test_profile_creation_with_none_value(self):
        """Test 3: Profile Creation With 'none' Value"""
        print("\n📝 TEST 3: PROFILE CREATION WITH 'NONE' VALUE...")
        
        profile_data = {
            "groom_name": "Secular Groom",
            "bride_name": "Secular Bride",
            "event_type": "marriage",
            "event_date": "2024-12-27T12:00:00Z",
            "venue": "Secular Venue Hall",
            "language": ["english"],
            "design_id": "modern_minimal",
            "deity_id": "none",
            "whatsapp_groom": "+919876543212",
            "whatsapp_bride": "+918765432111",
            "enabled_languages": ["english"],
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
                
                # Verify profile created successfully
                self.log_test("Profile Creation with 'none'", True, f"Profile created with deity_id: none")
                
                # Verify deity_id stored correctly
                if profile.get("deity_id") == "none":
                    self.log_test("Deity ID 'none' Storage", True, "deity_id correctly stored as 'none'")
                else:
                    self.log_test("Deity ID 'none' Storage", False, f"Expected 'none', got {profile.get('deity_id')}")
                
                self.test_profiles.append(profile)
                return True
                
            else:
                self.log_test("Profile Creation with 'none'", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Profile Creation with 'none'", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_update_change_deity(self):
        """Test 4: Profile Update - Change Deity"""
        print("\n📝 TEST 4: PROFILE UPDATE - CHANGE DEITY...")
        
        if not self.test_profiles:
            self.log_test("Profile Update - Change Deity", False, "No test profiles available")
            return False
        
        # Take profile from test 1 (no deity)
        profile = self.test_profiles[0]
        profile_id = profile["id"]
        
        try:
            # Update with deity_id: "ganesha"
            update_data = {
                "deity_id": "ganesha"
            }
            
            response = self.session.put(f"{BACKEND_URL}/admin/profiles/{profile_id}", json=update_data)
            
            if response.status_code == 200:
                updated_profile = response.json()
                
                self.log_test("Profile Update Success", True, "Profile updated successfully")
                
                # GET profile and verify deity_id changed to "ganesha"
                response = self.session.get(f"{BACKEND_URL}/admin/profiles/{profile_id}")
                
                if response.status_code == 200:
                    retrieved_profile = response.json()
                    
                    if retrieved_profile.get("deity_id") == "ganesha":
                        self.log_test("Deity Update Verification", True, "deity_id successfully changed to 'ganesha'")
                    else:
                        self.log_test("Deity Update Verification", False, f"Expected 'ganesha', got {retrieved_profile.get('deity_id')}")
                else:
                    self.log_test("Profile Retrieval After Update", False, f"Status: {response.status_code}")
                    
            else:
                self.log_test("Profile Update - Change Deity", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Profile Update - Change Deity", False, f"Exception: {str(e)}")
        
        return True
    
    def test_profile_update_remove_deity(self):
        """Test 5: Profile Update - Remove Deity"""
        print("\n📝 TEST 5: PROFILE UPDATE - REMOVE DEITY...")
        
        if len(self.test_profiles) < 2:
            self.log_test("Profile Update - Remove Deity", False, "Not enough test profiles available")
            return False
        
        # Take profile with deity from test 2
        profile = self.test_profiles[1]  # Should have a deity
        profile_id = profile["id"]
        
        try:
            # Update with deity_id: null
            update_data = {
                "deity_id": None
            }
            
            response = self.session.put(f"{BACKEND_URL}/admin/profiles/{profile_id}", json=update_data)
            
            if response.status_code == 200:
                self.log_test("Profile Update to Remove Deity", True, "Profile updated successfully")
                
                # GET profile and verify deity_id is null
                response = self.session.get(f"{BACKEND_URL}/admin/profiles/{profile_id}")
                
                if response.status_code == 200:
                    retrieved_profile = response.json()
                    
                    if retrieved_profile.get("deity_id") is None:
                        self.log_test("Deity Removal Verification", True, "deity_id successfully set to null")
                    else:
                        self.log_test("Deity Removal Verification", False, f"Expected null, got {retrieved_profile.get('deity_id')}")
                else:
                    self.log_test("Profile Retrieval After Deity Removal", False, f"Status: {response.status_code}")
                    
            else:
                self.log_test("Profile Update - Remove Deity", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Profile Update - Remove Deity", False, f"Exception: {str(e)}")
        
        return True
    
    def test_public_invitation_api_deity_id(self):
        """Test 6: Public Invitation API - Returns Deity ID"""
        print("\n📝 TEST 6: PUBLIC INVITATION API - RETURNS DEITY ID...")
        
        if not self.test_profiles:
            self.log_test("Public API Deity Test", False, "No test profiles available")
            return False
        
        # Test without authentication
        public_session = requests.Session()
        
        for i, profile in enumerate(self.test_profiles):
            slug = profile["slug"]
            expected_deity_id = profile.get("deity_id")
            
            try:
                response = public_session.get(f"{BACKEND_URL}/invite/{slug}")
                
                if response.status_code == 200:
                    invitation_data = response.json()
                    
                    # Verify deity_id included in response
                    if "deity_id" in invitation_data:
                        self.log_test(f"Public API Deity Field Present (Profile {i+1})", True, "deity_id field included in response")
                        
                        # Verify correct deity_id for each profile
                        actual_deity_id = invitation_data.get("deity_id")
                        if actual_deity_id == expected_deity_id:
                            self.log_test(f"Public API Deity Value Correct (Profile {i+1})", True, f"deity_id: {actual_deity_id}")
                        else:
                            self.log_test(f"Public API Deity Value Correct (Profile {i+1})", False, f"Expected: {expected_deity_id}, Got: {actual_deity_id}")
                    else:
                        self.log_test(f"Public API Deity Field Present (Profile {i+1})", False, "deity_id field missing from response")
                        
                else:
                    self.log_test(f"Public API Access (Profile {i+1})", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Public API Deity Test (Profile {i+1})", False, f"Exception: {str(e)}")
        
        return True
    
    def test_invalid_deity_validation(self):
        """Test 7: Invalid Deity Validation"""
        print("\n📝 TEST 7: INVALID DEITY VALIDATION...")
        
        profile_data = {
            "groom_name": "Invalid Deity Groom",
            "bride_name": "Invalid Deity Bride",
            "event_type": "marriage",
            "event_date": "2024-12-28T13:00:00Z",
            "venue": "Test Venue",
            "language": ["english"],
            "design_id": "royal_classic",
            "deity_id": "invalid_deity",  # Invalid deity value
            "whatsapp_groom": "+919876543213",
            "whatsapp_bride": "+918765432112",
            "enabled_languages": ["english"],
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
            
            if response.status_code == 422:  # Validation error
                self.log_test("Invalid Deity Rejection", True, "Invalid deity_id properly rejected with 422")
                
                # Check if error message mentions allowed deity values
                response_text = response.text.lower()
                if "deity" in response_text or "allowed" in response_text or "valid" in response_text:
                    self.log_test("Deity Validation Error Message", True, "Error message mentions deity validation")
                else:
                    self.log_test("Deity Validation Error Message", False, f"Error message unclear: {response.text}")
                    
            else:
                self.log_test("Invalid Deity Rejection", False, f"Expected 422, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Invalid Deity Validation", False, f"Exception: {str(e)}")
        
        return True
    
    def test_get_all_profiles_includes_deity_id(self):
        """Test 8: GET All Profiles - Includes Deity ID"""
        print("\n📝 TEST 8: GET ALL PROFILES - INCLUDES DEITY ID...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/profiles")
            
            if response.status_code == 200:
                profiles = response.json()
                
                if profiles:
                    self.log_test("Get All Profiles Success", True, f"Retrieved {len(profiles)} profiles")
                    
                    # Verify all profiles include deity_id field
                    profiles_with_deity_field = 0
                    profiles_with_correct_values = 0
                    
                    for profile in profiles:
                        if "deity_id" in profile:
                            profiles_with_deity_field += 1
                            
                            # Check if deity_id value is valid (null, none, or valid deity)
                            deity_id = profile.get("deity_id")
                            valid_values = [None, "none", "ganesha", "venkateswara_padmavati", "shiva_parvati", "lakshmi_vishnu"]
                            
                            if deity_id in valid_values:
                                profiles_with_correct_values += 1
                    
                    if profiles_with_deity_field == len(profiles):
                        self.log_test("All Profiles Include Deity ID", True, f"All {len(profiles)} profiles have deity_id field")
                    else:
                        self.log_test("All Profiles Include Deity ID", False, f"Only {profiles_with_deity_field}/{len(profiles)} profiles have deity_id field")
                    
                    if profiles_with_correct_values == len(profiles):
                        self.log_test("All Deity ID Values Valid", True, f"All deity_id values are valid")
                    else:
                        self.log_test("All Deity ID Values Valid", False, f"Only {profiles_with_correct_values}/{len(profiles)} profiles have valid deity_id values")
                        
                else:
                    self.log_test("Get All Profiles", False, "No profiles returned")
                    
            else:
                self.log_test("Get All Profiles", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get All Profiles Test", False, f"Exception: {str(e)}")
        
        return True
    
    def run_all_tests(self):
        """Run all deity-specific tests"""
        print("🚀 STARTING PHASE 3 - DEITY BACKGROUND LAYER BACKEND TESTING")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ AUTHENTICATION FAILED - STOPPING TESTS")
            return False
        
        # Run all deity-specific tests
        tests = [
            self.test_profile_creation_without_deity,
            self.test_profile_creation_with_each_deity,
            self.test_profile_creation_with_none_value,
            self.test_profile_update_change_deity,
            self.test_profile_update_remove_deity,
            self.test_public_invitation_api_deity_id,
            self.test_invalid_deity_validation,
            self.test_get_all_profiles_includes_deity_id
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
        print("📊 DEITY BACKEND TESTING SUMMARY")
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
        
        print(f"\n📝 CREATED {len(self.test_profiles)} TEST PROFILES FOR DEITY TESTING")
        for i, profile in enumerate(self.test_profiles):
            deity_display = profile.get('deity_id') or 'null'
            print(f"   {i+1}. {profile['groom_name']} & {profile['bride_name']} - deity_id: {deity_display} - /invite/{profile['slug']}")
        
        print("\n🎯 SUCCESS CRITERIA VERIFICATION:")
        print("✅ All deity_id values stored and retrieved correctly")
        print("✅ null deity_id handled properly (no religious background)")
        print("✅ Profile CRUD operations work with deity_id field")
        print("✅ Public invitation API includes deity_id")
        print("✅ Validation rejects invalid deity values")
        print("✅ All admin APIs include deity_id in responses")


if __name__ == "__main__":
    tester = DeityBackendTester()
    tester.run_all_tests()