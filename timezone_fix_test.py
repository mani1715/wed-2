#!/usr/bin/env python3
"""
CRITICAL TIMEZONE FIX TESTING for Wedding Invitation Platform
FOCUS: Testing timezone-aware datetime comparisons and default is_active=True fix
"""

import requests
import json
from datetime import datetime, timedelta, timezone
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔗 Testing timezone fix at: {API_BASE}")

class TimezoneFixTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_profiles = []  # Store test profile data
        
    def log_test(self, test_name, success, details=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        if not success:
            print()
    
    def authenticate_admin(self):
        """Authenticate as admin"""
        print("\n🔐 Authenticating Admin...")
        
        login_data = {
            "email": "admin@wedding.com",
            "password": "admin123"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.admin_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_test("Admin Authentication", True, f"Token obtained for {data['admin']['email']}")
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No access token in response")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_creation_default_expiry(self):
        """Test CRITICAL: Profile creation with default expiry (30 days)"""
        print("\n🕒 Testing Profile Creation with Default Expiry...")
        
        if not self.admin_token:
            self.log_test("Profile Creation Default Expiry", False, "No admin token")
            return False
        
        # Create profile WITHOUT specifying expiry - should default to 30 days
        profile_data = {
            "groom_name": "Rajesh Kumar",
            "bride_name": "Priya Sharma", 
            "event_type": "marriage",
            "event_date": (datetime.now() + timedelta(days=45)).isoformat(),
            "venue": "Grand Ballroom, Taj Palace, New Delhi",
            "language": ["english", "hindi"],
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
            # NOT specifying link_expiry_type or link_expiry_value
        }
        
        try:
            response = self.session.post(f"{API_BASE}/admin/profiles", json=profile_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Store for later tests
                self.test_profiles.append({
                    "id": data["id"],
                    "slug": data["slug"],
                    "name": f"{data['groom_name']} & {data['bride_name']}"
                })
                
                # Verify default values
                expiry_type = data.get("link_expiry_type")
                expiry_value = data.get("link_expiry_value") 
                expiry_date = data.get("link_expiry_date")
                is_active = data.get("is_active")
                
                # Check defaults
                if expiry_type != "days":
                    self.log_test("Default Expiry Type", False, f"Expected 'days', got '{expiry_type}'")
                    return False
                
                if expiry_value != 30:
                    self.log_test("Default Expiry Value", False, f"Expected 30, got {expiry_value}")
                    return False
                
                if not is_active:
                    self.log_test("Default is_active", False, f"Expected True, got {is_active}")
                    return False
                
                if not expiry_date:
                    self.log_test("Expiry Date Calculation", False, "No expiry date calculated")
                    return False
                
                # Verify expiry date is approximately 30 days from now
                expiry_dt = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                expected_expiry = datetime.now(timezone.utc) + timedelta(days=30)
                time_diff = abs((expiry_dt - expected_expiry).total_seconds())
                
                if time_diff > 300:  # More than 5 minutes difference
                    self.log_test("Expiry Date Accuracy", False, 
                                f"Expected ≈{expected_expiry}, got {expiry_dt}")
                    return False
                
                self.log_test("Profile Creation Default Expiry", True, 
                            f"✅ Defaults: type=days, value=30, is_active=True, expiry≈30 days")
                return True
                
            else:
                self.log_test("Profile Creation Default Expiry", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Profile Creation Default Expiry", False, f"Exception: {str(e)}")
            return False
    
    def test_immediate_public_access(self):
        """Test CRITICAL: Public invitation access immediately after creation"""
        print("\n🔗 Testing Immediate Public Invitation Access...")
        
        if not self.test_profiles:
            self.log_test("Immediate Public Access", False, "No test profiles available")
            return False
        
        # Test accessing the newly created profile immediately
        profile = self.test_profiles[0]
        slug = profile["slug"]
        
        try:
            # Use new session without auth for public access
            public_session = requests.Session()
            response = public_session.get(f"{API_BASE}/invite/{slug}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify all required fields are present
                required_fields = ["slug", "groom_name", "bride_name", "event_type", "event_date", "venue"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Immediate Public Access", False, 
                                f"Missing fields: {missing_fields}")
                    return False
                
                # Verify it's the correct profile
                if data["slug"] != slug:
                    self.log_test("Immediate Public Access", False, "Slug mismatch in response")
                    return False
                
                self.log_test("Immediate Public Access", True, 
                            f"✅ {profile['name']} invitation accessible immediately")
                return True
                
            elif response.status_code == 410:
                self.log_test("Immediate Public Access", False, 
                            "❌ CRITICAL: New profile returns 'Link Expired' (410)")
                return False
            else:
                self.log_test("Immediate Public Access", False, 
                            f"Unexpected status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Immediate Public Access", False, f"Exception: {str(e)}")
            return False
    
    def test_multiple_expiry_options(self):
        """Test various expiry options work immediately"""
        print("\n⏰ Testing Multiple Expiry Options...")
        
        if not self.admin_token:
            self.log_test("Multiple Expiry Options", False, "No admin token")
            return False
        
        test_cases = [
            {"name": "1 Day Expiry", "type": "days", "value": 1},
            {"name": "7 Days Expiry", "type": "days", "value": 7}, 
            {"name": "30 Days Expiry", "type": "days", "value": 30}
        ]
        
        all_passed = True
        
        for i, case in enumerate(test_cases):
            profile_data = {
                "groom_name": f"Groom {i+1}",
                "bride_name": f"Bride {i+1}",
                "event_type": "marriage",
                "event_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "venue": f"Venue {i+1}",
                "language": ["english"],
                "sections_enabled": {
                    "opening": True,
                    "welcome": True,
                    "couple": True,
                    "photos": False,
                    "video": False,
                    "events": True,
                    "greetings": True,
                    "footer": True
                },
                "link_expiry_type": case["type"],
                "link_expiry_value": case["value"]
            }
            
            try:
                # Create profile
                response = self.session.post(f"{API_BASE}/admin/profiles", json=profile_data)
                
                if response.status_code != 200:
                    self.log_test(f"Create {case['name']}", False, f"Status: {response.status_code}")
                    all_passed = False
                    continue
                
                data = response.json()
                slug = data["slug"]
                
                # Store for cleanup
                self.test_profiles.append({
                    "id": data["id"],
                    "slug": slug,
                    "name": f"{data['groom_name']} & {data['bride_name']}"
                })
                
                # Verify expiry settings
                if (data.get("link_expiry_type") != case["type"] or 
                    data.get("link_expiry_value") != case["value"]):
                    self.log_test(f"Create {case['name']}", False, "Expiry settings incorrect")
                    all_passed = False
                    continue
                
                # Test immediate access
                public_session = requests.Session()
                invite_response = public_session.get(f"{API_BASE}/invite/{slug}")
                
                if invite_response.status_code == 200:
                    self.log_test(f"Access {case['name']}", True, "✅ Accessible immediately")
                elif invite_response.status_code == 410:
                    self.log_test(f"Access {case['name']}", False, "❌ Shows as expired immediately")
                    all_passed = False
                else:
                    self.log_test(f"Access {case['name']}", False, f"Status: {invite_response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Test {case['name']}", False, f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_timezone_aware_comparison(self):
        """Test that timezone-aware datetime comparisons work correctly"""
        print("\n🌍 Testing Timezone-Aware DateTime Comparisons...")
        
        if not self.test_profiles:
            self.log_test("Timezone Comparison", False, "No test profiles available")
            return False
        
        # Test accessing profiles created with different expiry times
        success_count = 0
        
        for profile in self.test_profiles[:3]:  # Test first 3 profiles
            try:
                public_session = requests.Session()
                response = public_session.get(f"{API_BASE}/invite/{profile['slug']}")
                
                if response.status_code == 200:
                    success_count += 1
                    self.log_test(f"Timezone Check: {profile['name'][:20]}...", True, 
                                "✅ Timezone comparison working")
                elif response.status_code == 410:
                    self.log_test(f"Timezone Check: {profile['name'][:20]}...", False, 
                                "❌ Timezone comparison issue - shows expired")
                else:
                    self.log_test(f"Timezone Check: {profile['name'][:20]}...", False, 
                                f"Unexpected status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Timezone Check: {profile['name'][:20]}...", False, 
                            f"Exception: {str(e)}")
        
        if success_count >= 2:
            self.log_test("Overall Timezone Comparison", True, 
                        f"✅ {success_count} profiles working with timezone-aware comparisons")
            return True
        else:
            self.log_test("Overall Timezone Comparison", False, 
                        f"❌ Only {success_count} profiles working - timezone issue")
            return False
    
    def test_profile_crud_operations(self):
        """Test basic CRUD operations work with timezone fix"""
        print("\n📝 Testing Profile CRUD Operations...")
        
        if not self.admin_token:
            self.log_test("Profile CRUD", False, "No admin token")
            return False
        
        try:
            # Test GET all profiles
            response = self.session.get(f"{API_BASE}/admin/profiles")
            
            if response.status_code != 200:
                self.log_test("Get All Profiles", False, f"Status: {response.status_code}")
                return False
            
            profiles = response.json()
            if not isinstance(profiles, list) or len(profiles) == 0:
                self.log_test("Get All Profiles", False, "No profiles returned")
                return False
            
            self.log_test("Get All Profiles", True, f"✅ Retrieved {len(profiles)} profiles")
            
            # Test GET single profile
            if self.test_profiles:
                profile_id = self.test_profiles[0]["id"]
                response = self.session.get(f"{API_BASE}/admin/profiles/{profile_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("id") == profile_id:
                        self.log_test("Get Single Profile", True, "✅ Profile retrieved correctly")
                    else:
                        self.log_test("Get Single Profile", False, "Profile ID mismatch")
                        return False
                else:
                    self.log_test("Get Single Profile", False, f"Status: {response.status_code}")
                    return False
            
            # Test UPDATE profile
            if self.test_profiles:
                profile_id = self.test_profiles[0]["id"]
                update_data = {
                    "venue": "Updated Venue - Timezone Test Location",
                    "language": ["english", "telugu"]
                }
                
                response = self.session.put(f"{API_BASE}/admin/profiles/{profile_id}", json=update_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("venue") == update_data["venue"]:
                        self.log_test("Update Profile", True, "✅ Profile updated successfully")
                    else:
                        self.log_test("Update Profile", False, "Update not reflected")
                        return False
                else:
                    self.log_test("Update Profile", False, f"Status: {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            self.log_test("Profile CRUD Operations", False, f"Exception: {str(e)}")
            return False
    
    def test_greeting_submission(self):
        """Test guest greeting submission works with timezone fix"""
        print("\n💬 Testing Guest Greeting Submission...")
        
        if not self.test_profiles:
            self.log_test("Greeting Submission", False, "No test profiles available")
            return False
        
        profile = self.test_profiles[0]
        slug = profile["slug"]
        
        greeting_data = {
            "guest_name": "Anita Desai",
            "message": "Heartiest congratulations on your wedding! May your journey together be filled with love, joy, and countless beautiful memories. Wishing you both a lifetime of happiness!"
        }
        
        try:
            # Submit greeting via public API
            public_session = requests.Session()
            response = public_session.post(f"{API_BASE}/invite/{slug}/greetings", json=greeting_data)
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("guest_name") == greeting_data["guest_name"] and 
                    "id" in data and "created_at" in data):
                    self.log_test("Greeting Submission", True, 
                                f"✅ Greeting submitted by {data['guest_name']}")
                    return True
                else:
                    self.log_test("Greeting Submission", False, "Invalid response data")
                    return False
            elif response.status_code == 410:
                self.log_test("Greeting Submission", False, 
                            "❌ CRITICAL: Greeting submission blocked - link shows expired")
                return False
            else:
                self.log_test("Greeting Submission", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Greeting Submission", False, f"Exception: {str(e)}")
            return False
    
    def run_timezone_fix_tests(self):
        """Run all timezone fix tests as specified in review request"""
        print("🚀 Starting TIMEZONE FIX Testing for Wedding Invitation Platform")
        print("=" * 70)
        
        test_results = []
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ Cannot proceed without authentication")
            return False
        
        # CRITICAL TIMEZONE FIX TESTS
        print("\n🎯 PRIORITY TESTS - TIMEZONE FIX:")
        test_results.append(self.test_profile_creation_default_expiry())
        test_results.append(self.test_immediate_public_access())
        test_results.append(self.test_multiple_expiry_options())
        test_results.append(self.test_timezone_aware_comparison())
        
        print("\n🔍 VERIFICATION TESTS:")
        test_results.append(self.test_profile_crud_operations())
        test_results.append(self.test_greeting_submission())
        
        # Summary
        passed = sum(test_results)
        total = len(test_results)
        
        print("\n" + "=" * 70)
        print(f"🏁 TIMEZONE FIX TEST SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TIMEZONE FIX TESTS PASSED! No 'Link Expired' errors for fresh profiles.")
            return True
        else:
            failed = total - passed
            print(f"⚠️  {failed} tests failed. Timezone fix needs attention!")
            return False

def main():
    """Main test execution"""
    tester = TimezoneFixTester()
    success = tester.run_timezone_fix_tests()
    
    if success:
        print("\n✅ Timezone fix testing completed successfully!")
        exit(0)
    else:
        print("\n❌ Timezone fix testing completed with failures!")
        exit(1)

if __name__ == "__main__":
    main()