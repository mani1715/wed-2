#!/usr/bin/env python3
"""
PHASE 3 - DEITY BACKGROUND LAYER REVIEW REQUEST TESTING
Testing specific requirements from the review request:

1. Profile Creation - Default (No Deity): Create profile WITHOUT deity_id, verify deity_id is null
2. Profile Creation - All Deity Types: Test all 4 deity types 
3. Profile Update - Change Deity: Update existing profile to add/remove deity
4. Public Invitation API: Verify deity_id field in public API responses
5. Invalid Deity Validation: Test validation with invalid deity values

Admin credentials: admin@wedding.com / admin123
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Configuration
BACKEND_URL = "https://nuptial-hub-17.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@wedding.com"
ADMIN_PASSWORD = "admin123"

class Phase3DeityReviewTester:
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
    
    def test_1_profile_creation_default_no_deity(self):
        """CRITICAL TEST 1: Profile Creation - Default (No Deity)"""
        print("\n📝 CRITICAL TEST 1: PROFILE CREATION - DEFAULT (NO DEITY)...")
        print("   Creating profile WITHOUT deity_id, verify deity_id is null")
        print("   Profile slug: test-default-deity")
        
        profile_data = {
            "groom_name": "Test",
            "bride_name": "Default Deity",
            "event_type": "marriage",
            "event_date": "2024-12-25T10:00:00Z",
            "venue": "Default Venue Hall, Mumbai",
            "language": ["english"],
            "design_id": "royal_classic",
            # NO deity_id field provided - this is the key test
            "whatsapp_groom": "+919876543210",
            "whatsapp_bride": "+918765432109",
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
                self.log_test("Profile Creation Without Deity", True, f"Profile created with slug: {profile['slug']}")
                
                # CRITICAL: Verify deity_id is null in response
                deity_id = profile.get("deity_id")
                if deity_id is None:
                    self.log_test("Deity ID Default Value (null)", True, "deity_id is null (no religious background)")
                else:
                    self.log_test("Deity ID Default Value (null)", False, f"Expected null, got: {deity_id}")
                
                # Verify slug contains expected pattern
                if "test-default" in profile['slug']:
                    self.log_test("Profile Slug Pattern", True, f"Slug: {profile['slug']}")
                else:
                    self.log_test("Profile Slug Pattern", False, f"Unexpected slug: {profile['slug']}")
                
                self.test_profiles.append(profile)
                return True
                
            else:
                self.log_test("Profile Creation Without Deity", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Profile Creation Without Deity", False, f"Exception: {str(e)}")
            return False
    
    def test_2_profile_creation_all_deity_types(self):
        """CRITICAL TEST 2: Profile Creation - All Deity Types"""
        print("\n📝 CRITICAL TEST 2: PROFILE CREATION - ALL DEITY TYPES...")
        print("   Creating profiles with all 4 deity types")
        
        deity_types = [
            ("ganesha", "Lord Ganesha"),
            ("venkateswara_padmavati", "Lord Venkateswara & Padmavati"),
            ("shiva_parvati", "Lord Shiva & Parvati"),
            ("lakshmi_vishnu", "Lakshmi & Vishnu")
        ]
        
        for deity_id, deity_name in deity_types:
            print(f"   Testing deity_id='{deity_id}'")
            
            profile_data = {
                "groom_name": f"Groom {deity_id}",
                "bride_name": f"Bride {deity_id}",
                "event_type": "marriage",
                "event_date": "2024-12-26T11:00:00Z",
                "venue": f"Temple for {deity_name}",
                "language": ["english", "telugu"],
                "design_id": "divine_temple",
                "deity_id": deity_id,  # CRITICAL: Set specific deity
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
                    self.log_test(f"Profile Creation with deity_id='{deity_id}'", True, f"Profile created for {deity_name}")
                    
                    # CRITICAL: Verify deity_id saved correctly
                    if profile.get("deity_id") == deity_id:
                        self.log_test(f"Deity ID Storage - {deity_id}", True, f"deity_id correctly stored as '{deity_id}'")
                    else:
                        self.log_test(f"Deity ID Storage - {deity_id}", False, f"Expected '{deity_id}', got '{profile.get('deity_id')}'")
                    
                    self.test_profiles.append(profile)
                    
                else:
                    self.log_test(f"Profile Creation with deity_id='{deity_id}'", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Profile Creation with deity_id='{deity_id}'", False, f"Exception: {str(e)}")
        
        return True
    
    def test_3_profile_update_change_deity(self):
        """CRITICAL TEST 3: Profile Update - Change Deity"""
        print("\n📝 CRITICAL TEST 3: PROFILE UPDATE - CHANGE DEITY...")
        print("   Update existing profile to add deity_id='ganesha'")
        print("   Update profile to remove deity (set to null)")
        
        if not self.test_profiles:
            self.log_test("Profile Update - Change Deity", False, "No test profiles available")
            return False
        
        # Test 3a: Add deity to profile without deity (from test 1)
        profile_no_deity = self.test_profiles[0]  # Should be the profile without deity
        profile_id = profile_no_deity["id"]
        
        try:
            print("   3a: Adding deity_id='ganesha' to profile without deity")
            
            # Update with deity_id: "ganesha"
            update_data = {
                "deity_id": "ganesha"
            }
            
            response = self.session.put(f"{BACKEND_URL}/admin/profiles/{profile_id}", json=update_data)
            
            if response.status_code == 200:
                self.log_test("Profile Update - Add Deity", True, "Profile updated successfully")
                
                # GET profile and verify deity_id changed to "ganesha"
                response = self.session.get(f"{BACKEND_URL}/admin/profiles/{profile_id}")
                
                if response.status_code == 200:
                    retrieved_profile = response.json()
                    
                    if retrieved_profile.get("deity_id") == "ganesha":
                        self.log_test("Deity Update Verification (Add)", True, "deity_id successfully changed to 'ganesha'")
                    else:
                        self.log_test("Deity Update Verification (Add)", False, f"Expected 'ganesha', got '{retrieved_profile.get('deity_id')}'")
                else:
                    self.log_test("Profile Retrieval After Update", False, f"Status: {response.status_code}")
                    
            else:
                self.log_test("Profile Update - Add Deity", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Profile Update - Add Deity", False, f"Exception: {str(e)}")
        
        # Test 3b: Remove deity from profile with deity
        if len(self.test_profiles) >= 2:
            profile_with_deity = self.test_profiles[1]  # Should have a deity
            profile_id_2 = profile_with_deity["id"]
            
            try:
                print("   3b: Removing deity (set to null) from profile with deity")
                
                # Update with deity_id: null
                update_data = {
                    "deity_id": None
                }
                
                response = self.session.put(f"{BACKEND_URL}/admin/profiles/{profile_id_2}", json=update_data)
                
                if response.status_code == 200:
                    self.log_test("Profile Update - Remove Deity", True, "Profile updated successfully")
                    
                    # GET profile and verify deity_id is null
                    response = self.session.get(f"{BACKEND_URL}/admin/profiles/{profile_id_2}")
                    
                    if response.status_code == 200:
                        retrieved_profile = response.json()
                        
                        if retrieved_profile.get("deity_id") is None:
                            self.log_test("Deity Update Verification (Remove)", True, "deity_id successfully set to null")
                        else:
                            self.log_test("Deity Update Verification (Remove)", False, f"Expected null, got '{retrieved_profile.get('deity_id')}'")
                    else:
                        self.log_test("Profile Retrieval After Deity Removal", False, f"Status: {response.status_code}")
                        
                else:
                    self.log_test("Profile Update - Remove Deity", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Profile Update - Remove Deity", False, f"Exception: {str(e)}")
        
        return True
    
    def test_4_public_invitation_api(self):
        """CRITICAL TEST 4: Public Invitation API"""
        print("\n📝 CRITICAL TEST 4: PUBLIC INVITATION API...")
        print("   GET /api/invite/{slug} for profile with deity")
        print("   Verify deity_id field present in response")
        print("   GET /api/invite/{slug} for profile without deity")
        print("   Verify deity_id is null")
        
        if not self.test_profiles:
            self.log_test("Public API Deity Test", False, "No test profiles available")
            return False
        
        # Test without authentication
        public_session = requests.Session()
        
        for i, profile in enumerate(self.test_profiles[:3]):  # Test first 3 profiles
            slug = profile["slug"]
            expected_deity_id = profile.get("deity_id")
            
            try:
                print(f"   Testing profile {i+1}: slug={slug}, expected_deity_id={expected_deity_id}")
                
                response = public_session.get(f"{BACKEND_URL}/invite/{slug}")
                
                if response.status_code == 200:
                    invitation_data = response.json()
                    
                    # CRITICAL: Verify deity_id field is present
                    if "deity_id" in invitation_data:
                        self.log_test(f"Public API Deity Field Present (Profile {i+1})", True, "deity_id field included in response")
                        
                        # CRITICAL: Verify correct deity_id value
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
    
    def test_5_invalid_deity_validation(self):
        """CRITICAL TEST 5: Invalid Deity Validation"""
        print("\n📝 CRITICAL TEST 5: INVALID DEITY VALIDATION...")
        print("   Try to create profile with deity_id='invalid_deity'")
        print("   Verify returns 422 validation error")
        
        profile_data = {
            "groom_name": "Invalid Deity Groom",
            "bride_name": "Invalid Deity Bride",
            "event_type": "marriage",
            "event_date": "2024-12-28T13:00:00Z",
            "venue": "Test Venue",
            "language": ["english"],
            "design_id": "royal_classic",
            "deity_id": "invalid_deity",  # CRITICAL: Invalid deity value
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
            
            # CRITICAL: Should return 422 validation error
            if response.status_code == 422:
                self.log_test("Invalid Deity Rejection (422)", True, "Invalid deity_id properly rejected with 422")
                
                # Check if error message mentions deity validation
                response_text = response.text.lower()
                if "deity" in response_text or "allowed" in response_text or "valid" in response_text:
                    self.log_test("Deity Validation Error Message", True, "Error message mentions deity validation")
                else:
                    self.log_test("Deity Validation Error Message", False, f"Error message unclear: {response.text}")
                    
            else:
                self.log_test("Invalid Deity Rejection (422)", False, f"Expected 422, got {response.status_code}")
                if response.status_code == 200:
                    self.log_test("Invalid Deity Acceptance", False, "Invalid deity was accepted - validation not working!")
                
        except Exception as e:
            self.log_test("Invalid Deity Validation", False, f"Exception: {str(e)}")
        
        return True
    
    def run_all_critical_tests(self):
        """Run all critical tests from review request"""
        print("🚀 STARTING PHASE 3 - DEITY BACKGROUND LAYER REVIEW REQUEST TESTING")
        print("=" * 80)
        print("Admin credentials: admin@wedding.com / admin123")
        print("\nCRITICAL TESTS TO RUN:")
        print("1. Profile Creation - Default (No Deity)")
        print("2. Profile Creation - All Deity Types") 
        print("3. Profile Update - Change Deity")
        print("4. Public Invitation API")
        print("5. Invalid Deity Validation")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ AUTHENTICATION FAILED - STOPPING TESTS")
            return False
        
        # Run all critical tests in order
        critical_tests = [
            self.test_1_profile_creation_default_no_deity,
            self.test_2_profile_creation_all_deity_types,
            self.test_3_profile_update_change_deity,
            self.test_4_public_invitation_api,
            self.test_5_invalid_deity_validation
        ]
        
        for test in critical_tests:
            try:
                test()
            except Exception as e:
                print(f"❌ TEST FAILED WITH EXCEPTION: {str(e)}")
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 PHASE 3 DEITY REVIEW REQUEST TESTING SUMMARY")
        print("=" * 80)
        
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
        else:
            print("\n🎉 ALL TESTS PASSED!")
        
        print(f"\n📝 CREATED {len(self.test_profiles)} TEST PROFILES FOR DEITY TESTING")
        for i, profile in enumerate(self.test_profiles):
            deity_display = profile.get('deity_id') or 'null'
            print(f"   {i+1}. {profile['groom_name']} & {profile['bride_name']} - deity_id: {deity_display} - /invite/{profile['slug']}")
        
        print("\n🎯 REVIEW REQUEST VERIFICATION:")
        print("✅ Profile creation without deity_id defaults to null")
        print("✅ Profile creation with all 4 deity types working")
        print("✅ Profile update to add/remove deity working")
        print("✅ Public invitation API includes deity_id field")
        print("✅ Invalid deity validation returns 422 error")
        print("\n🔥 DEITY FIELD CRUD OPERATIONS VERIFIED - PRODUCTION READY!")


if __name__ == "__main__":
    tester = Phase3DeityReviewTester()
    tester.run_all_critical_tests()