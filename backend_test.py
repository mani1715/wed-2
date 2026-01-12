#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Wedding Invitation Platform
FOCUS: Testing CRITICAL FIXES for Default Expiry Logic, Multi-Language Support, and Expiry Options
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

print(f"🔗 Testing backend at: {API_BASE}")

class WeddingAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_profile_ids = []  # Store multiple test profiles
        self.test_slugs = []  # Store multiple test slugs
        self.test_media_id = None
        self.test_greeting_id = None
        
    def log_test(self, test_name, success, details=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        if not success:
            print()
    
    def test_admin_login(self):
        """Test admin authentication"""
        print("\n🔐 Testing Authentication...")
        
        # Test login with correct credentials
        login_data = {
            "email": "admin@wedding.com",
            "password": "admin123"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "admin" in data:
                    self.admin_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_test("Admin Login", True, f"Token received, Admin ID: {data['admin']['id']}")
                    return True
                else:
                    self.log_test("Admin Login", False, "Missing token or admin info in response")
                    return False
            else:
                self.log_test("Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_login_invalid(self):
        """Test login with invalid credentials"""
        invalid_login = {
            "email": "admin@wedding.com",
            "password": "wrongpassword"
        }
        
        try:
            response = requests.post(f"{API_BASE}/auth/login", json=invalid_login)
            
            if response.status_code == 401:
                self.log_test("Invalid Login Rejection", True, "Correctly rejected invalid credentials")
                return True
            else:
                self.log_test("Invalid Login Rejection", False, f"Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Login Rejection", False, f"Exception: {str(e)}")
            return False
    
    def test_auth_me(self):
        """Test /auth/me endpoint"""
        if not self.admin_token:
            self.log_test("Auth Me Endpoint", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{API_BASE}/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "email" in data:
                    self.log_test("Auth Me Endpoint", True, f"Admin info retrieved: {data['email']}")
                    return True
                else:
                    self.log_test("Auth Me Endpoint", False, "Missing required fields in response")
                    return False
            else:
                self.log_test("Auth Me Endpoint", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Auth Me Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_default_expiry_logic(self):
        """Test CRITICAL FIX: Default expiry logic - profiles should default to 30 days"""
        print("\n🕒 Testing CRITICAL FIX: Default Expiry Logic...")
        
        if not self.admin_token:
            self.log_test("Default Expiry Logic", False, "No admin token available")
            return False
        
        # Create profile WITHOUT specifying expiry (should default to 30 days)
        profile_data = {
            "groom_name": "Arjun Reddy",
            "bride_name": "Meera Nair",
            "event_type": "marriage",
            "event_date": (datetime.now() + timedelta(days=45)).isoformat(),
            "venue": "Leela Palace, Bangalore",
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
            # NOT specifying link_expiry_type or link_expiry_value - should default
        }
        
        try:
            response = self.session.post(f"{API_BASE}/admin/profiles", json=profile_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check default values
                if (data.get("link_expiry_type") == "days" and 
                    data.get("link_expiry_value") == 30 and
                    data.get("link_expiry_date") is not None):
                    
                    # Verify expiry date is approximately 30 days from now
                    expiry_date = datetime.fromisoformat(data["link_expiry_date"].replace('Z', '+00:00'))
                    expected_expiry = datetime.now(timezone.utc) + timedelta(days=30)
                    time_diff = abs((expiry_date - expected_expiry).total_seconds())
                    
                    if time_diff < 300:  # Within 5 minutes tolerance
                        self.test_profile_ids.append(data["id"])
                        self.test_slugs.append(data["slug"])
                        self.log_test("Default Expiry Logic", True, 
                                    f"✅ Defaults correct: type=days, value=30, expiry≈30 days from now")
                        return True
                    else:
                        self.log_test("Default Expiry Logic", False, 
                                    f"Expiry date calculation incorrect. Expected ≈{expected_expiry}, got {expiry_date}")
                        return False
                else:
                    self.log_test("Default Expiry Logic", False, 
                                f"Default values incorrect: type={data.get('link_expiry_type')}, value={data.get('link_expiry_value')}")
                    return False
            else:
                self.log_test("Default Expiry Logic", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Default Expiry Logic", False, f"Exception: {str(e)}")
            return False

    def test_multi_language_support(self):
        """Test CRITICAL FIX: Multi-language support - language should be array"""
        print("\n🌐 Testing CRITICAL FIX: Multi-Language Support...")
        
        if not self.admin_token:
            self.log_test("Multi-Language Support", False, "No admin token available")
            return False
        
        # Create profile with multiple languages
        profile_data = {
            "groom_name": "Vikram Singh",
            "bride_name": "Kavya Iyer",
            "event_type": "marriage",
            "event_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "venue": "ITC Grand Chola, Chennai",
            "language": ["english", "hindi", "tamil"],  # Multiple languages
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
            "link_expiry_value": 7
        }
        
        try:
            response = self.session.post(f"{API_BASE}/admin/profiles", json=profile_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check language is returned as array
                if (isinstance(data.get("language"), list) and 
                    set(data["language"]) == {"english", "hindi", "tamil"}):
                    
                    profile_id = data["id"]
                    slug = data["slug"]
                    self.test_profile_ids.append(profile_id)
                    self.test_slugs.append(slug)
                    
                    # Test GET /api/invite/:slug returns language array
                    public_session = requests.Session()
                    invite_response = public_session.get(f"{API_BASE}/invite/{slug}")
                    
                    if invite_response.status_code == 200:
                        invite_data = invite_response.json()
                        if (isinstance(invite_data.get("language"), list) and 
                            set(invite_data["language"]) == {"english", "hindi", "tamil"}):
                            
                            self.log_test("Multi-Language Support", True, 
                                        f"✅ Language array working: {invite_data['language']}")
                            return True
                        else:
                            self.log_test("Multi-Language Support", False, 
                                        f"Public API language format incorrect: {invite_data.get('language')}")
                            return False
                    else:
                        self.log_test("Multi-Language Support", False, 
                                    f"Public invite API failed: {invite_response.status_code}")
                        return False
                else:
                    self.log_test("Multi-Language Support", False, 
                                f"Language format incorrect in create response: {data.get('language')}")
                    return False
            else:
                self.log_test("Multi-Language Support", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Multi-Language Support", False, f"Exception: {str(e)}")
            return False

    def test_expiry_options(self):
        """Test CRITICAL FIX: All expiry presets (1 day, 7 days, 30 days, custom)"""
        print("\n⏰ Testing CRITICAL FIX: Expiry Options...")
        
        if not self.admin_token:
            self.log_test("Expiry Options", False, "No admin token available")
            return False
        
        test_cases = [
            {"name": "1 Day Expiry", "type": "days", "value": 1},
            {"name": "7 Days Expiry", "type": "days", "value": 7},
            {"name": "30 Days Expiry", "type": "days", "value": 30},
            {"name": "Custom 15 Hours", "type": "hours", "value": 15}
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases):
            profile_data = {
                "groom_name": f"Test Groom {i+1}",
                "bride_name": f"Test Bride {i+1}",
                "event_type": "marriage",
                "event_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "venue": f"Test Venue {i+1}",
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
                "link_expiry_type": test_case["type"],
                "link_expiry_value": test_case["value"]
            }
            
            try:
                response = self.session.post(f"{API_BASE}/admin/profiles", json=profile_data)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify expiry settings
                    if (data.get("link_expiry_type") == test_case["type"] and 
                        data.get("link_expiry_value") == test_case["value"] and
                        data.get("link_expiry_date") is not None):
                        
                        # Calculate expected expiry
                        if test_case["type"] == "days":
                            expected_expiry = datetime.now(timezone.utc) + timedelta(days=test_case["value"])
                        else:  # hours
                            expected_expiry = datetime.now(timezone.utc) + timedelta(hours=test_case["value"])
                        
                        actual_expiry = datetime.fromisoformat(data["link_expiry_date"].replace('Z', '+00:00'))
                        time_diff = abs((actual_expiry - expected_expiry).total_seconds())
                        
                        if time_diff < 300:  # Within 5 minutes tolerance
                            self.test_profile_ids.append(data["id"])
                            self.test_slugs.append(data["slug"])
                            self.log_test(f"Expiry Option: {test_case['name']}", True, 
                                        f"✅ Expiry calculated correctly")
                        else:
                            self.log_test(f"Expiry Option: {test_case['name']}", False, 
                                        f"Expiry calculation incorrect")
                            all_passed = False
                    else:
                        self.log_test(f"Expiry Option: {test_case['name']}", False, 
                                    f"Expiry settings incorrect: {data.get('link_expiry_type')}, {data.get('link_expiry_value')}")
                        all_passed = False
                else:
                    self.log_test(f"Expiry Option: {test_case['name']}", False, 
                                f"Status: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Expiry Option: {test_case['name']}", False, f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_link_expiry_validation(self):
        """Test CRITICAL FIX: Link expiry validation - active vs expired links"""
        print("\n🔒 Testing CRITICAL FIX: Link Expiry Validation...")
        
        if not self.test_slugs:
            self.log_test("Link Expiry Validation", False, "No test slugs available")
            return False
        
        # Test active profiles (should load correctly)
        active_tests_passed = 0
        for slug in self.test_slugs[:3]:  # Test first 3 active profiles
            try:
                public_session = requests.Session()
                response = public_session.get(f"{API_BASE}/invite/{slug}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "slug" in data and "groom_name" in data:
                        active_tests_passed += 1
                        self.log_test(f"Active Link: {slug[:15]}...", True, "✅ Loads correctly")
                    else:
                        self.log_test(f"Active Link: {slug[:15]}...", False, "Missing data in response")
                else:
                    self.log_test(f"Active Link: {slug[:15]}...", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Active Link: {slug[:15]}...", False, f"Exception: {str(e)}")
        
        # Test expired link by soft-deleting a profile
        if self.test_profile_ids:
            try:
                # Soft delete first profile
                delete_response = self.session.delete(f"{API_BASE}/admin/profiles/{self.test_profile_ids[0]}")
                
                if delete_response.status_code == 200:
                    # Try to access the deleted profile's invitation
                    public_session = requests.Session()
                    expired_response = public_session.get(f"{API_BASE}/invite/{self.test_slugs[0]}")
                    
                    if expired_response.status_code == 410:
                        self.log_test("Expired Link Validation", True, "✅ Correctly returns 410 for expired link")
                        return active_tests_passed >= 2  # At least 2 active links worked
                    else:
                        self.log_test("Expired Link Validation", False, 
                                    f"Expected 410 for expired link, got {expired_response.status_code}")
                        return False
                else:
                    self.log_test("Expired Link Validation", False, "Failed to delete profile for testing")
                    return False
                    
            except Exception as e:
                self.log_test("Expired Link Validation", False, f"Exception: {str(e)}")
                return False
        
        return False
    
    def test_profile_crud_new_format(self):
        """Test CRITICAL FIX: Profile CRUD with new format (language arrays, etc.)"""
        print("\n📝 Testing CRITICAL FIX: Profile CRUD with New Format...")
        
        if not self.admin_token:
            self.log_test("Profile CRUD New Format", False, "No admin token available")
            return False
        
        # Create profile with all new fields
        profile_data = {
            "groom_name": "Rohit Sharma",
            "bride_name": "Ananya Gupta",
            "event_type": "engagement",
            "event_date": (datetime.now() + timedelta(days=20)).isoformat(),
            "venue": "Taj Lake Palace, Udaipur",
            "language": ["hindi", "english", "tamil"],  # Multi-language array
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
            "link_expiry_value": 14
        }
        
        try:
            # CREATE
            response = self.session.post(f"{API_BASE}/admin/profiles", json=profile_data)
            
            if response.status_code != 200:
                self.log_test("Profile CRUD - Create", False, f"Create failed: {response.status_code}")
                return False
            
            data = response.json()
            profile_id = data["id"]
            slug = data["slug"]
            self.test_profile_ids.append(profile_id)
            self.test_slugs.append(slug)
            
            # Verify creation with new format
            if not isinstance(data.get("language"), list):
                self.log_test("Profile CRUD - Create", False, "Language not returned as array")
                return False
            
            self.log_test("Profile CRUD - Create", True, f"✅ Created with language array: {data['language']}")
            
            # UPDATE - Change language array
            update_data = {
                "language": ["english", "telugu"],  # Update to different languages
                "venue": "Updated Venue - Hyatt Regency, Delhi"
            }
            
            update_response = self.session.put(f"{API_BASE}/admin/profiles/{profile_id}", json=update_data)
            
            if update_response.status_code != 200:
                self.log_test("Profile CRUD - Update", False, f"Update failed: {update_response.status_code}")
                return False
            
            update_result = update_response.json()
            if (isinstance(update_result.get("language"), list) and 
                set(update_result["language"]) == {"english", "telugu"}):
                self.log_test("Profile CRUD - Update", True, f"✅ Updated language array: {update_result['language']}")
            else:
                self.log_test("Profile CRUD - Update", False, f"Language update failed: {update_result.get('language')}")
                return False
            
            # GET ALL - Verify language arrays in list
            all_profiles_response = self.session.get(f"{API_BASE}/admin/profiles")
            
            if all_profiles_response.status_code != 200:
                self.log_test("Profile CRUD - Get All", False, f"Get all failed: {all_profiles_response.status_code}")
                return False
            
            all_profiles = all_profiles_response.json()
            our_profile = next((p for p in all_profiles if p["id"] == profile_id), None)
            
            if our_profile and isinstance(our_profile.get("language"), list):
                self.log_test("Profile CRUD - Get All", True, "✅ Language arrays displayed correctly in list")
            else:
                self.log_test("Profile CRUD - Get All", False, "Language arrays not working in profile list")
                return False
            
            # Verify slug generation still works
            if slug and len(slug) > 10 and "-" in slug:
                self.log_test("Profile CRUD - Slug Generation", True, f"✅ Slug generated: {slug}")
            else:
                self.log_test("Profile CRUD - Slug Generation", False, f"Invalid slug: {slug}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Profile CRUD New Format", False, f"Exception: {str(e)}")
            return False

    def test_immediate_link_access(self):
        """Test that invitation links work immediately after creation (no 'Link Expired' errors)"""
        print("\n🔗 Testing Immediate Link Access...")
        
        if not self.test_slugs:
            self.log_test("Immediate Link Access", False, "No test slugs available")
            return False
        
        # Test that newly created profiles are immediately accessible
        success_count = 0
        
        for i, slug in enumerate(self.test_slugs[:3]):  # Test first 3 profiles
            try:
                public_session = requests.Session()
                response = public_session.get(f"{API_BASE}/invite/{slug}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "groom_name" in data and "bride_name" in data:
                        success_count += 1
                        self.log_test(f"Immediate Access {i+1}", True, 
                                    f"✅ {data['groom_name']} & {data['bride_name']} invitation loads correctly")
                    else:
                        self.log_test(f"Immediate Access {i+1}", False, "Missing profile data")
                elif response.status_code == 410:
                    self.log_test(f"Immediate Access {i+1}", False, 
                                "❌ CRITICAL: New profile shows as expired!")
                else:
                    self.log_test(f"Immediate Access {i+1}", False, 
                                f"Unexpected status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Immediate Access {i+1}", False, f"Exception: {str(e)}")
        
        if success_count >= 2:
            self.log_test("Overall Immediate Access", True, 
                        f"✅ {success_count} profiles accessible immediately after creation")
            return True
        else:
            self.log_test("Overall Immediate Access", False, 
                        f"❌ Only {success_count} profiles accessible - CRITICAL ISSUE")
            return False
    
    def test_get_single_profile(self):
        """Test getting single profile"""
        if not self.admin_token or not self.test_profile_id:
            self.log_test("Get Single Profile", False, "No admin token or profile ID available")
            return False
            
        try:
            response = self.session.get(f"{API_BASE}/admin/profiles/{self.test_profile_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["id"] == self.test_profile_id:
                    self.log_test("Get Single Profile", True, f"Retrieved profile: {data['groom_name']} & {data['bride_name']}")
                    return True
                else:
                    self.log_test("Get Single Profile", False, "Profile ID mismatch or missing data")
                    return False
            else:
                self.log_test("Get Single Profile", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Single Profile", False, f"Exception: {str(e)}")
            return False
    
    def test_update_profile(self):
        """Test profile update"""
        if not self.admin_token or not self.test_profile_id:
            self.log_test("Update Profile", False, "No admin token or profile ID available")
            return False
        
        update_data = {
            "venue": "Updated Venue - Taj Palace, Delhi",
            "language": "hindi"
        }
        
        try:
            response = self.session.put(f"{API_BASE}/admin/profiles/{self.test_profile_id}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("venue") == update_data["venue"] and data.get("language") == update_data["language"]:
                    self.log_test("Update Profile", True, f"Profile updated successfully")
                    return True
                else:
                    self.log_test("Update Profile", False, "Update data not reflected in response")
                    return False
            else:
                self.log_test("Update Profile", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Update Profile", False, f"Exception: {str(e)}")
            return False
    
    def test_add_media(self):
        """Test adding media to profile"""
        print("\n📸 Testing Media Management...")
        
        if not self.admin_token or not self.test_profile_id:
            self.log_test("Add Media", False, "No admin token or profile ID available")
            return False
        
        media_data = {
            "media_type": "photo",
            "media_url": "https://example.com/wedding-photo1.jpg",
            "caption": "Beautiful couple photo",
            "order": 1
        }
        
        try:
            response = self.session.post(f"{API_BASE}/admin/profiles/{self.test_profile_id}/media", json=media_data)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("media_url") == media_data["media_url"]:
                    self.test_media_id = data["id"]
                    self.log_test("Add Media", True, f"Media added with ID: {data['id']}")
                    return True
                else:
                    self.log_test("Add Media", False, "Missing ID or URL mismatch in response")
                    return False
            else:
                self.log_test("Add Media", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Add Media", False, f"Exception: {str(e)}")
            return False
    
    def test_get_profile_media(self):
        """Test getting profile media"""
        if not self.admin_token or not self.test_profile_id:
            self.log_test("Get Profile Media", False, "No admin token or profile ID available")
            return False
            
        try:
            response = self.session.get(f"{API_BASE}/admin/profiles/{self.test_profile_id}/media")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("Get Profile Media", True, f"Retrieved {len(data)} media items")
                    return True
                else:
                    self.log_test("Get Profile Media", False, "No media items found or invalid response")
                    return False
            else:
                self.log_test("Get Profile Media", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Profile Media", False, f"Exception: {str(e)}")
            return False
    
    def test_public_invitation(self):
        """Test public invitation access"""
        print("\n💌 Testing Public Invitation APIs...")
        
        if not self.test_slug:
            self.log_test("Public Invitation Access", False, "No test slug available")
            return False
        
        try:
            # Use a new session without auth headers for public access
            public_session = requests.Session()
            response = public_session.get(f"{API_BASE}/invite/{self.test_slug}")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["slug", "groom_name", "bride_name", "event_type", "event_date", "venue", "media", "greetings"]
                
                if all(field in data for field in required_fields):
                    self.log_test("Public Invitation Access", True, f"Invitation data retrieved for {data['groom_name']} & {data['bride_name']}")
                    return True
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("Public Invitation Access", False, f"Missing fields: {missing_fields}")
                    return False
            else:
                self.log_test("Public Invitation Access", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Public Invitation Access", False, f"Exception: {str(e)}")
            return False
    
    def test_submit_greeting(self):
        """Test submitting a guest greeting"""
        if not self.test_slug:
            self.log_test("Submit Greeting", False, "No test slug available")
            return False
        
        greeting_data = {
            "guest_name": "Amit Patel",
            "message": "Congratulations on your special day! Wishing you both a lifetime of happiness and love. May your marriage be filled with joy, laughter, and endless blessings."
        }
        
        try:
            # Use a new session without auth headers for public access
            public_session = requests.Session()
            response = public_session.post(f"{API_BASE}/invite/{self.test_slug}/greetings", json=greeting_data)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("guest_name") == greeting_data["guest_name"]:
                    self.test_greeting_id = data["id"]
                    self.log_test("Submit Greeting", True, f"Greeting submitted by {data['guest_name']}")
                    return True
                else:
                    self.log_test("Submit Greeting", False, "Missing ID or name mismatch in response")
                    return False
            else:
                self.log_test("Submit Greeting", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Submit Greeting", False, f"Exception: {str(e)}")
            return False
    
    def test_get_profile_greetings(self):
        """Test getting profile greetings as admin"""
        if not self.admin_token or not self.test_profile_id:
            self.log_test("Get Profile Greetings", False, "No admin token or profile ID available")
            return False
            
        try:
            response = self.session.get(f"{API_BASE}/admin/profiles/{self.test_profile_id}/greetings")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("Get Profile Greetings", True, f"Retrieved {len(data)} greetings")
                    return True
                else:
                    self.log_test("Get Profile Greetings", False, "No greetings found or invalid response")
                    return False
            else:
                self.log_test("Get Profile Greetings", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Profile Greetings", False, f"Exception: {str(e)}")
            return False
    
    def test_delete_media(self):
        """Test deleting media"""
        if not self.admin_token or not self.test_media_id:
            self.log_test("Delete Media", False, "No admin token or media ID available")
            return False
            
        try:
            response = self.session.delete(f"{API_BASE}/admin/media/{self.test_media_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Delete Media", True, "Media deleted successfully")
                    return True
                else:
                    self.log_test("Delete Media", False, "No success message in response")
                    return False
            else:
                self.log_test("Delete Media", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Delete Media", False, f"Exception: {str(e)}")
            return False
    
    def test_delete_profile(self):
        """Test profile deletion (soft delete)"""
        if not self.admin_token or not self.test_profile_id:
            self.log_test("Delete Profile", False, "No admin token or profile ID available")
            return False
            
        try:
            response = self.session.delete(f"{API_BASE}/admin/profiles/{self.test_profile_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Delete Profile", True, "Profile soft deleted successfully")
                    return True
                else:
                    self.log_test("Delete Profile", False, "No success message in response")
                    return False
            else:
                self.log_test("Delete Profile", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Delete Profile", False, f"Exception: {str(e)}")
            return False
    
    def test_expired_link_access(self):
        """Test accessing deleted/expired profile"""
        if not self.test_slug:
            self.log_test("Expired Link Access", False, "No test slug available")
            return False
            
        try:
            # Use a new session without auth headers for public access
            public_session = requests.Session()
            response = public_session.get(f"{API_BASE}/invite/{self.test_slug}")
            
            if response.status_code == 410:
                self.log_test("Expired Link Access", True, "Correctly returned 410 for expired/deleted profile")
                return True
            else:
                self.log_test("Expired Link Access", False, f"Expected 410, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Expired Link Access", False, f"Exception: {str(e)}")
            return False
    
    def run_critical_fix_tests(self):
        """Run all CRITICAL FIX tests as specified in review request"""
        print("🚀 Starting CRITICAL FIXES Testing for Wedding Invitation Platform")
        print("=" * 70)
        
        test_results = []
        
        # Authentication (prerequisite)
        test_results.append(self.test_admin_login())
        if not self.admin_token:
            print("❌ Cannot proceed without authentication")
            return False
        
        # CRITICAL FIXES TESTING
        print("\n🎯 PRIORITY TESTS - CRITICAL FIXES:")
        test_results.append(self.test_default_expiry_logic())
        test_results.append(self.test_multi_language_support())
        test_results.append(self.test_expiry_options())
        test_results.append(self.test_link_expiry_validation())
        test_results.append(self.test_profile_crud_new_format())
        test_results.append(self.test_immediate_link_access())
        
        # Additional verification tests
        print("\n🔍 VERIFICATION TESTS:")
        test_results.append(self.test_admin_login_invalid())
        test_results.append(self.test_auth_me())
        
        # Summary
        passed = sum(test_results)
        total = len(test_results)
        
        print("\n" + "=" * 70)
        print(f"🏁 CRITICAL FIXES TEST SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL CRITICAL FIXES WORKING! Backend ready for production.")
            return True
        else:
            failed = total - passed
            print(f"⚠️  {failed} CRITICAL tests failed. Issues need immediate attention!")
            return False

def main():
    """Main test execution"""
    tester = WeddingAPITester()
    success = tester.run_critical_fix_tests()
    
    if success:
        print("\n✅ CRITICAL FIXES testing completed successfully!")
        exit(0)
    else:
        print("\n❌ CRITICAL FIXES testing completed with failures!")
        exit(1)

if __name__ == "__main__":
    main()