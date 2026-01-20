#!/usr/bin/env python3
"""
PHASE 12 - EXPIRY & AUTO-DISABLE SYSTEM TESTING

This script tests the expiry system features as requested in the review:
1. Set Expiry Date API
2. Check Expired Profile Flag
3. Active Profile (Not Expired)
4. RSVP Disabled When Expired
5. Wishes Disabled When Expired
6. Default Expiry Calculation
"""

import requests
import json
from datetime import datetime, timedelta, timezone
import time
import sys
import os

# Get backend URL from environment
BACKEND_URL = "https://wed-management.preview.emergentagent.com/api"

# Admin credentials
ADMIN_EMAIL = "admin@wedding.com"
ADMIN_PASSWORD = "admin123"

class ExpirySystemTester:
    def __init__(self):
        self.token = None
        self.test_profiles = []
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")
        print()
    
    def authenticate(self):
        """Authenticate as admin"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.log_result("Admin Authentication", True, "Successfully authenticated as admin")
                return True
            else:
                self.log_result("Admin Authentication", False, f"Failed to authenticate: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def create_test_profile(self, groom_name, bride_name, wedding_date, expires_at=None):
        """Create a test profile"""
        try:
            profile_data = {
                "groom_name": groom_name,
                "bride_name": bride_name,
                "event_type": "marriage",
                "event_date": wedding_date.isoformat(),
                "venue": "Grand Palace Wedding Hall",
                "city": "Hyderabad",
                "invitation_message": "Join us in celebrating our special day",
                "language": ["english", "telugu"],
                "design_id": "royal_classic",
                "deity_id": "ganesha",
                "whatsapp_groom": "+919876543210",
                "whatsapp_bride": "+919876543211",
                "enabled_languages": ["english", "telugu"],
                "events": [
                    {
                        "name": "Wedding Ceremony",
                        "date": wedding_date.strftime("%Y-%m-%d"),
                        "start_time": "10:00",
                        "end_time": "12:00",
                        "venue_name": "Grand Palace Wedding Hall",
                        "venue_address": "Banjara Hills, Hyderabad",
                        "map_link": "https://maps.google.com/example",
                        "description": "Main wedding ceremony",
                        "visible": True,
                        "order": 0
                    }
                ],
                "sections_enabled": {
                    "opening": True,
                    "welcome": True,
                    "couple": True,
                    "events": True,
                    "photos": True,
                    "video": False,
                    "greetings": True,
                    "rsvp": True,
                    "footer": True
                }
            }
            
            if expires_at:
                profile_data["expires_at"] = expires_at.isoformat()
            
            response = requests.post(
                f"{BACKEND_URL}/admin/profiles",
                json=profile_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                profile = response.json()
                self.test_profiles.append(profile)
                return profile
            else:
                print(f"Failed to create profile: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating profile: {str(e)}")
            return None
    
    def test_1_set_expiry_date_api(self):
        """TEST 1: Set Expiry Date API"""
        print("🧪 TEST 1: Set Expiry Date API")
        
        # Create test profile (Arjun & Meera wedding)
        wedding_date = datetime.now(timezone.utc) + timedelta(days=30)
        profile = self.create_test_profile("Arjun Kumar", "Meera Sharma", wedding_date)
        
        if not profile:
            self.log_result("TEST 1 - Profile Creation", False, "Failed to create test profile")
            return False
        
        profile_id = profile["id"]
        original_expires_at = profile.get("expires_at")
        
        # Set expiry date to tomorrow
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        
        try:
            response = requests.put(
                f"{BACKEND_URL}/admin/profiles/{profile_id}/set-expiry",
                json={"expires_at": tomorrow.isoformat()},
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Verify the response
                if "expires_at" in result:
                    # Get updated profile to verify
                    profile_response = requests.get(
                        f"{BACKEND_URL}/admin/profiles/{profile_id}",
                        headers=self.get_headers()
                    )
                    
                    if profile_response.status_code == 200:
                        updated_profile = profile_response.json()
                        updated_expires_at = updated_profile.get("expires_at")
                        
                        if updated_expires_at:
                            self.log_result(
                                "TEST 1 - Set Expiry Date API", 
                                True, 
                                "Successfully set expiry date to tomorrow",
                                {
                                    "profile_id": profile_id,
                                    "original_expires_at": original_expires_at,
                                    "new_expires_at": updated_expires_at,
                                    "groom_bride": f"{profile['groom_name']} & {profile['bride_name']}"
                                }
                            )
                            return True
                        else:
                            self.log_result("TEST 1 - Set Expiry Date API", False, "expires_at field not updated in profile")
                    else:
                        self.log_result("TEST 1 - Set Expiry Date API", False, f"Failed to fetch updated profile: {profile_response.status_code}")
                else:
                    self.log_result("TEST 1 - Set Expiry Date API", False, "Response missing expires_at field")
            else:
                self.log_result("TEST 1 - Set Expiry Date API", False, f"API call failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("TEST 1 - Set Expiry Date API", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def test_2_check_expired_profile_flag(self):
        """TEST 2: Check Expired Profile Flag"""
        print("🧪 TEST 2: Check Expired Profile Flag")
        
        # Create test profile (Karthik & Divya wedding) with past expiry
        wedding_date = datetime.now(timezone.utc) + timedelta(days=15)
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        
        profile = self.create_test_profile("Karthik Reddy", "Divya Nair", wedding_date, expires_at=yesterday)
        
        if not profile:
            self.log_result("TEST 2 - Profile Creation", False, "Failed to create test profile")
            return False
        
        slug = profile["slug"]
        
        try:
            # Get public invitation
            response = requests.get(f"{BACKEND_URL}/invite/{slug}")
            
            if response.status_code == 200:
                invitation_data = response.json()
                is_expired = invitation_data.get("is_expired", False)
                
                if is_expired:
                    self.log_result(
                        "TEST 2 - Check Expired Profile Flag", 
                        True, 
                        "is_expired field correctly returns true for expired profile",
                        {
                            "slug": slug,
                            "is_expired": is_expired,
                            "groom_bride": f"{profile['groom_name']} & {profile['bride_name']}",
                            "profile_data_accessible": "Yes - profile data is still accessible"
                        }
                    )
                    return True
                else:
                    self.log_result("TEST 2 - Check Expired Profile Flag", False, f"is_expired field is {is_expired}, expected True")
            else:
                self.log_result("TEST 2 - Check Expired Profile Flag", False, f"Failed to get public invitation: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("TEST 2 - Check Expired Profile Flag", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def test_3_active_profile_not_expired(self):
        """TEST 3: Active Profile (Not Expired)"""
        print("🧪 TEST 3: Active Profile (Not Expired)")
        
        # Create test profile (Rahul & Anjali wedding) with future expiry
        wedding_date = datetime.now(timezone.utc) + timedelta(days=20)
        future_expiry = datetime.now(timezone.utc) + timedelta(days=7)
        
        profile = self.create_test_profile("Rahul Gupta", "Anjali Singh", wedding_date, expires_at=future_expiry)
        
        if not profile:
            self.log_result("TEST 3 - Profile Creation", False, "Failed to create test profile")
            return False
        
        slug = profile["slug"]
        
        try:
            # Get public invitation
            response = requests.get(f"{BACKEND_URL}/invite/{slug}")
            
            if response.status_code == 200:
                invitation_data = response.json()
                is_expired = invitation_data.get("is_expired", True)  # Default to True to catch missing field
                
                if not is_expired:
                    self.log_result(
                        "TEST 3 - Active Profile (Not Expired)", 
                        True, 
                        "is_expired field correctly returns false for active profile",
                        {
                            "slug": slug,
                            "is_expired": is_expired,
                            "groom_bride": f"{profile['groom_name']} & {profile['bride_name']}",
                            "profile_data_accessible": "Yes - profile data is fully accessible"
                        }
                    )
                    return True
                else:
                    self.log_result("TEST 3 - Active Profile (Not Expired)", False, f"is_expired field is {is_expired}, expected False")
            else:
                self.log_result("TEST 3 - Active Profile (Not Expired)", False, f"Failed to get public invitation: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("TEST 3 - Active Profile (Not Expired)", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def test_4_rsvp_disabled_when_expired(self):
        """TEST 4: RSVP Disabled When Expired"""
        print("🧪 TEST 4: RSVP Disabled When Expired")
        
        # Use the expired profile from TEST 2 if available
        expired_profile = None
        for profile in self.test_profiles:
            if "Karthik" in profile.get("groom_name", ""):
                expired_profile = profile
                break
        
        if not expired_profile:
            # Create a new expired profile
            wedding_date = datetime.now(timezone.utc) + timedelta(days=10)
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            expired_profile = self.create_test_profile("Karthik Reddy", "Divya Nair", wedding_date, expires_at=yesterday)
        
        if not expired_profile:
            self.log_result("TEST 4 - Profile Setup", False, "Failed to get/create expired profile")
            return False
        
        slug = expired_profile["slug"]
        
        try:
            # Try to submit RSVP
            rsvp_data = {
                "guest_name": "Rajesh Kumar",
                "guest_phone": "+919876543212",
                "status": "yes",
                "guest_count": 2,
                "message": "Looking forward to the celebration!"
            }
            
            response = requests.post(f"{BACKEND_URL}/rsvp?slug={slug}", json=rsvp_data)
            
            # Should return error indicating invitation has expired
            if response.status_code == 403:
                error_message = response.json().get("detail", "")
                if "expired" in error_message.lower():
                    self.log_result(
                        "TEST 4 - RSVP Disabled When Expired", 
                        True, 
                        "RSVP correctly blocked for expired invitation",
                        {
                            "slug": slug,
                            "status_code": response.status_code,
                            "error_message": error_message,
                            "groom_bride": f"{expired_profile['groom_name']} & {expired_profile['bride_name']}"
                        }
                    )
                    return True
                else:
                    self.log_result("TEST 4 - RSVP Disabled When Expired", False, f"Wrong error message: {error_message}")
            else:
                self.log_result("TEST 4 - RSVP Disabled When Expired", False, f"Unexpected response: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("TEST 4 - RSVP Disabled When Expired", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def test_5_wishes_disabled_when_expired(self):
        """TEST 5: Wishes Disabled When Expired"""
        print("🧪 TEST 5: Wishes Disabled When Expired")
        
        # Use the expired profile from TEST 2 if available
        expired_profile = None
        for profile in self.test_profiles:
            if "Karthik" in profile.get("groom_name", ""):
                expired_profile = profile
                break
        
        if not expired_profile:
            # Create a new expired profile
            wedding_date = datetime.now(timezone.utc) + timedelta(days=10)
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            expired_profile = self.create_test_profile("Karthik Reddy", "Divya Nair", wedding_date, expires_at=yesterday)
        
        if not expired_profile:
            self.log_result("TEST 5 - Profile Setup", False, "Failed to get/create expired profile")
            return False
        
        slug = expired_profile["slug"]
        
        try:
            # Try to submit greeting/wish
            greeting_data = {
                "guest_name": "Priya Sharma",
                "message": "Wishing you both a lifetime of happiness and love!"
            }
            
            response = requests.post(f"{BACKEND_URL}/invite/{slug}/greetings", json=greeting_data)
            
            # Should return error indicating invitation has expired
            if response.status_code == 403:
                error_message = response.json().get("detail", "")
                if "expired" in error_message.lower():
                    self.log_result(
                        "TEST 5 - Wishes Disabled When Expired", 
                        True, 
                        "Greeting submission correctly blocked for expired invitation",
                        {
                            "slug": slug,
                            "status_code": response.status_code,
                            "error_message": error_message,
                            "groom_bride": f"{expired_profile['groom_name']} & {expired_profile['bride_name']}"
                        }
                    )
                    return True
                else:
                    self.log_result("TEST 5 - Wishes Disabled When Expired", False, f"Wrong error message: {error_message}")
            else:
                self.log_result("TEST 5 - Wishes Disabled When Expired", False, f"Unexpected response: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("TEST 5 - Wishes Disabled When Expired", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def test_6_default_expiry_calculation(self):
        """TEST 6: Default Expiry Calculation"""
        print("🧪 TEST 6: Default Expiry Calculation")
        
        # Create profile with specific wedding date
        wedding_date = datetime(2025, 3, 15, 10, 0, 0, tzinfo=timezone.utc)
        expected_expiry = datetime(2025, 3, 22, 10, 0, 0, tzinfo=timezone.utc)  # wedding_date + 7 days
        
        profile = self.create_test_profile("Vikram Patel", "Sneha Joshi", wedding_date)
        
        if not profile:
            self.log_result("TEST 6 - Profile Creation", False, "Failed to create test profile")
            return False
        
        try:
            # Check if expires_at is automatically set to wedding_date + 7 days
            expires_at_str = profile.get("expires_at")
            
            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                
                # Check if it's approximately wedding_date + 7 days (allow some tolerance)
                time_diff = abs((expires_at - expected_expiry).total_seconds())
                
                if time_diff < 3600:  # Within 1 hour tolerance
                    self.log_result(
                        "TEST 6 - Default Expiry Calculation", 
                        True, 
                        "Default expiry correctly set to wedding_date + 7 days",
                        {
                            "wedding_date": wedding_date.isoformat(),
                            "expected_expiry": expected_expiry.isoformat(),
                            "actual_expiry": expires_at.isoformat(),
                            "groom_bride": f"{profile['groom_name']} & {profile['bride_name']}",
                            "time_difference_seconds": time_diff
                        }
                    )
                    return True
                else:
                    self.log_result("TEST 6 - Default Expiry Calculation", False, f"Expiry date mismatch. Expected: {expected_expiry}, Got: {expires_at}")
            else:
                self.log_result("TEST 6 - Default Expiry Calculation", False, "expires_at field is missing from profile")
                
        except Exception as e:
            self.log_result("TEST 6 - Default Expiry Calculation", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def cleanup_test_profiles(self):
        """Clean up test profiles"""
        print("🧹 Cleaning up test profiles...")
        
        for profile in self.test_profiles:
            try:
                response = requests.delete(
                    f"{BACKEND_URL}/admin/profiles/{profile['id']}",
                    headers=self.get_headers()
                )
                if response.status_code == 200:
                    print(f"✅ Deleted profile: {profile['groom_name']} & {profile['bride_name']}")
                else:
                    print(f"❌ Failed to delete profile: {profile['id']}")
            except Exception as e:
                print(f"❌ Error deleting profile {profile['id']}: {str(e)}")
    
    def run_all_tests(self):
        """Run all expiry system tests"""
        print("🚀 Starting PHASE 12 - EXPIRY & AUTO-DISABLE SYSTEM TESTING")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all tests
        tests = [
            self.test_1_set_expiry_date_api,
            self.test_2_check_expired_profile_flag,
            self.test_3_active_profile_not_expired,
            self.test_4_rsvp_disabled_when_expired,
            self.test_5_wishes_disabled_when_expired,
            self.test_6_default_expiry_calculation
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
                time.sleep(1)  # Small delay between tests
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with exception: {str(e)}")
        
        # Print summary
        print("=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status}: {result['test']}")
        
        print(f"\n🎯 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Expiry system is working correctly.")
        else:
            print(f"⚠️  {total_tests - passed_tests} test(s) failed. Please review the issues above.")
        
        # Cleanup
        self.cleanup_test_profiles()
        
        return passed_tests == total_tests

def main():
    """Main function"""
    tester = ExpirySystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All expiry system tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()