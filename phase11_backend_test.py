#!/usr/bin/env python3
"""
PHASE 11 Backend Testing - Guest Interaction & Experience Polish
Tests all PHASE 11 functionality including:
- Greetings Moderation System (pending/approved/rejected status)
- Contact Information (E.164 phone validation)
- Calendar & QR Code generation
- Sections Enabled toggles
- Admin greeting management endpoints
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import traceback
import re

# Configuration
BASE_URL = "https://marriage-site-2.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@wedding.com"
ADMIN_PASSWORD = "admin123"

class Phase11Tester:
    def __init__(self):
        self.token = None
        self.test_profiles = []
        self.test_greetings = []
        self.passed_tests = 0
        self.total_tests = 0
        
    def authenticate(self):
        """Authenticate as admin"""
        print("🔐 Authenticating as admin...")
        
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            print(f"✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def run_test(self, test_name, test_func):
        """Run a single test with error handling"""
        self.total_tests += 1
        print(f"\n🧪 TEST {self.total_tests}: {test_name}")
        
        try:
            result = test_func()
            if result:
                self.passed_tests += 1
                print(f"✅ PASSED: {test_name}")
            else:
                print(f"❌ FAILED: {test_name}")
            return result
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {str(e)}")
            traceback.print_exc()
            return False
    
    def test_profile_creation_with_contact_info(self):
        """Test 1: Profile Creation with Contact Information and E.164 Validation"""
        
        # Test valid E.164 phone numbers
        profile_data = {
            "groom_name": "Rajesh Kumar",
            "bride_name": "Priya Sharma",
            "event_type": "marriage",
            "event_date": "2024-03-15T10:00:00",
            "venue": "Grand Palace Hall",
            "city": "Mumbai",
            "invitation_message": "Join us in celebrating our special day",
            "language": ["english", "telugu"],
            "design_id": "royal_classic",
            "deity_id": "ganesha",
            "whatsapp_groom": "+919876543210",
            "whatsapp_bride": "+919876543211",
            "enabled_languages": ["english", "telugu"],
            "contact_info": {
                "groom_phone": "+919876543210",
                "bride_phone": "+919876543211", 
                "emergency_phone": "+919876543212",
                "email": "rajesh.priya@wedding.com"
            },
            "sections_enabled": {
                "opening": True,
                "welcome": True,
                "couple": True,
                "photos": True,
                "video": False,
                "events": True,
                "greetings": True,
                "contact": True,
                "calendar": True,
                "countdown": True,
                "qr": True,
                "footer": True
            },
            "events": [{
                "name": "Wedding Ceremony",
                "date": "2024-03-15",
                "start_time": "10:00",
                "end_time": "14:00",
                "venue_name": "Grand Palace Hall",
                "venue_address": "123 Palace Road, Mumbai, Maharashtra 400001",
                "map_link": "https://maps.google.com/?q=123+Palace+Road+Mumbai",
                "description": "Sacred wedding ceremony",
                "visible": True,
                "order": 1
            }],
            "link_expiry_type": "days",
            "link_expiry_value": 30
        }
        
        response = requests.post(
            f"{BASE_URL}/admin/profiles",
            json=profile_data,
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            profile = response.json()
            self.test_profiles.append(profile["id"])
            
            # Verify contact_info is stored correctly
            contact_info = profile.get("contact_info", {})
            if (contact_info.get("groom_phone") == "+919876543210" and
                contact_info.get("bride_phone") == "+919876543211" and
                contact_info.get("emergency_phone") == "+919876543212" and
                contact_info.get("email") == "rajesh.priya@wedding.com"):
                print(f"   ✓ Contact info stored correctly")
            else:
                print(f"   ❌ Contact info not stored correctly: {contact_info}")
                return False
            
            # Verify sections_enabled includes new PHASE 11 toggles
            sections = profile.get("sections_enabled", {})
            phase11_sections = ["contact", "calendar", "countdown", "qr"]
            for section in phase11_sections:
                if section not in sections:
                    print(f"   ❌ Missing section toggle: {section}")
                    return False
                if sections[section] != True:
                    print(f"   ❌ Section {section} should be enabled")
                    return False
            
            print(f"   ✓ All PHASE 11 section toggles present and enabled")
            print(f"   ✓ Profile ID: {profile['id']}")
            print(f"   ✓ Slug: {profile['slug']}")
            
            return True
        else:
            print(f"   ❌ Profile creation failed: {response.status_code} - {response.text}")
            return False
    
    def test_invalid_phone_validation(self):
        """Test 2: E.164 Phone Format Validation"""
        
        # Test invalid phone numbers
        invalid_phones = [
            "9876543210",      # Missing country code
            "+91 9876543210",  # Space in number
            "+91-9876543210",  # Dash in number
            "919876543210",    # Missing + sign
            "+91987654321",    # Too short
            "+9198765432100",  # Too long
            "+abc9876543210"   # Invalid characters
        ]
        
        for invalid_phone in invalid_phones:
            profile_data = {
                "groom_name": "Test Groom",
                "bride_name": "Test Bride",
                "event_type": "marriage",
                "event_date": "2024-03-15T10:00:00",
                "venue": "Test Venue",
                "language": ["english"],
                "enabled_languages": ["english"],
                "contact_info": {
                    "groom_phone": invalid_phone,
                    "email": "test@example.com"
                },
                "events": [{
                    "name": "Test Event",
                    "date": "2024-03-15",
                    "start_time": "10:00",
                    "venue_name": "Test Venue",
                    "venue_address": "Test Address",
                    "visible": True,
                    "order": 1
                }]
            }
            
            response = requests.post(
                f"{BASE_URL}/admin/profiles",
                json=profile_data,
                headers=self.get_headers()
            )
            
            if response.status_code != 422:
                print(f"   ❌ Invalid phone {invalid_phone} should be rejected with 422")
                return False
        
        print(f"   ✓ All invalid phone formats correctly rejected")
        return True
    
    def test_greeting_submission_with_moderation(self):
        """Test 3: Greeting Submission with Moderation (Default Pending Status)"""
        
        if not self.test_profiles:
            print(f"   ❌ No test profiles available")
            return False
        
        profile_id = self.test_profiles[0]
        
        # Get profile slug
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to get profile: {response.text}")
            return False
        
        profile = response.json()
        slug = profile["slug"]
        
        # Submit multiple greetings
        greetings_data = [
            {
                "guest_name": "Amit Patel",
                "message": "Congratulations on your wedding! Wishing you both a lifetime of happiness and love. 🎉❤️"
            },
            {
                "guest_name": "Sunita Reddy", 
                "message": "So happy for you both! May your marriage be filled with joy and blessings."
            },
            {
                "guest_name": "Vikram Singh",
                "message": "Best wishes for your new journey together! 🥳🎊"
            }
        ]
        
        for greeting_data in greetings_data:
            response = requests.post(
                f"{BASE_URL}/invite/{slug}/greetings",
                json=greeting_data
            )
            
            if response.status_code != 200:
                print(f"   ❌ Greeting submission failed: {response.text}")
                return False
            
            greeting = response.json()
            self.test_greetings.append(greeting["id"])
            
            # Verify default status is 'pending'
            if greeting["approval_status"] != "pending":
                print(f"   ❌ Greeting should have 'pending' status, got: {greeting['approval_status']}")
                return False
        
        print(f"   ✓ Submitted {len(greetings_data)} greetings with 'pending' status")
        return True
    
    def test_emoji_spam_validation(self):
        """Test 4: Emoji Spam Validation (Max 10 Emojis)"""
        
        if not self.test_profiles:
            print(f"   ❌ No test profiles available")
            return False
        
        profile_id = self.test_profiles[0]
        
        # Get profile slug
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}",
            headers=self.get_headers()
        )
        
        profile = response.json()
        slug = profile["slug"]
        
        # Test message with more than 10 emojis (should be rejected)
        spam_message = "Congratulations! 🎉🎊🥳❤️💕🌟✨🎈🎁🎂🍰🎵"  # 12 emojis
        
        greeting_data = {
            "guest_name": "Emoji Spammer",
            "message": spam_message
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{slug}/greetings",
            json=greeting_data
        )
        
        if response.status_code == 422:
            error_detail = response.json().get("detail", [])
            if any("emoji" in str(error).lower() for error in error_detail):
                print(f"   ✓ Emoji spam correctly rejected")
            else:
                print(f"   ❌ Wrong validation error for emoji spam: {error_detail}")
                return False
        else:
            print(f"   ❌ Emoji spam should be rejected with 422, got: {response.status_code}")
            return False
        
        # Test message with exactly 10 emojis (should be accepted)
        valid_message = "Congratulations! 🎉🎊🥳❤️💕🌟✨🎈🎁🎂"  # 10 emojis
        
        greeting_data = {
            "guest_name": "Valid Emoji User",
            "message": valid_message
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{slug}/greetings",
            json=greeting_data
        )
        
        if response.status_code == 200:
            greeting = response.json()
            self.test_greetings.append(greeting["id"])
            print(f"   ✓ Message with 10 emojis accepted")
            return True
        else:
            print(f"   ❌ Valid emoji message should be accepted: {response.text}")
            return False
    
    def test_admin_greeting_management(self):
        """Test 5: Admin Greeting Management Endpoints"""
        
        if not self.test_profiles or not self.test_greetings:
            print(f"   ❌ No test profiles or greetings available")
            return False
        
        profile_id = self.test_profiles[0]
        
        # Test 1: Get all greetings for profile
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}/greetings",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to get greetings: {response.text}")
            return False
        
        all_greetings = response.json()
        if len(all_greetings) < 3:
            print(f"   ❌ Expected at least 3 greetings, got {len(all_greetings)}")
            return False
        
        print(f"   ✓ Retrieved {len(all_greetings)} greetings")
        
        # Test 2: Filter greetings by status (pending)
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}/greetings?status=pending",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to filter pending greetings: {response.text}")
            return False
        
        pending_greetings = response.json()
        if len(pending_greetings) < 3:
            print(f"   ❌ Expected at least 3 pending greetings, got {len(pending_greetings)}")
            return False
        
        print(f"   ✓ Filtered {len(pending_greetings)} pending greetings")
        
        # Test 3: Approve a greeting
        greeting_id = self.test_greetings[0]
        response = requests.put(
            f"{BASE_URL}/admin/greetings/{greeting_id}/approve",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to approve greeting: {response.text}")
            return False
        
        print(f"   ✓ Approved greeting {greeting_id}")
        
        # Test 4: Reject a greeting
        greeting_id = self.test_greetings[1]
        response = requests.put(
            f"{BASE_URL}/admin/greetings/{greeting_id}/reject",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to reject greeting: {response.text}")
            return False
        
        print(f"   ✓ Rejected greeting {greeting_id}")
        
        # Test 5: Delete a greeting
        greeting_id = self.test_greetings[2]
        response = requests.delete(
            f"{BASE_URL}/admin/greetings/{greeting_id}",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to delete greeting: {response.text}")
            return False
        
        print(f"   ✓ Deleted greeting {greeting_id}")
        
        # Test 6: Verify status filters work
        for status in ["approved", "rejected"]:
            response = requests.get(
                f"{BASE_URL}/admin/profiles/{profile_id}/greetings?status={status}",
                headers=self.get_headers()
            )
            
            if response.status_code != 200:
                print(f"   ❌ Failed to filter {status} greetings: {response.text}")
                return False
            
            filtered_greetings = response.json()
            if len(filtered_greetings) < 1:
                print(f"   ❌ Expected at least 1 {status} greeting")
                return False
            
            # Verify all returned greetings have correct status
            for greeting in filtered_greetings:
                if greeting["approval_status"] != status:
                    print(f"   ❌ Greeting has wrong status: expected {status}, got {greeting['approval_status']}")
                    return False
        
        print(f"   ✓ All greeting status filters working correctly")
        return True
    
    def test_public_invitation_approved_greetings_only(self):
        """Test 6: Public Invitation Returns Only Approved Greetings (Last 20)"""
        
        if not self.test_profiles:
            print(f"   ❌ No test profiles available")
            return False
        
        profile_id = self.test_profiles[0]
        
        # Get profile slug
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}",
            headers=self.get_headers()
        )
        
        profile = response.json()
        slug = profile["slug"]
        
        # Test public invitation API
        response = requests.get(f"{BASE_URL}/invite/{slug}")
        
        if response.status_code != 200:
            print(f"   ❌ Public invitation API failed: {response.text}")
            return False
        
        public_data = response.json()
        
        # Verify greetings array exists
        if "greetings" not in public_data:
            print(f"   ❌ Greetings array missing from public API")
            return False
        
        greetings = public_data["greetings"]
        
        # Verify only approved greetings are returned
        for greeting in greetings:
            if greeting["approval_status"] != "approved":
                print(f"   ❌ Non-approved greeting in public API: {greeting['approval_status']}")
                return False
        
        # Verify contact_info is included
        if "contact_info" not in public_data:
            print(f"   ❌ Contact info missing from public API")
            return False
        
        contact_info = public_data["contact_info"]
        if not contact_info.get("groom_phone") or not contact_info.get("email"):
            print(f"   ❌ Contact info incomplete: {contact_info}")
            return False
        
        print(f"   ✓ Public API returns only approved greetings ({len(greetings)} greetings)")
        print(f"   ✓ Contact info included in public API")
        
        return True
    
    def test_calendar_ics_generation(self):
        """Test 7: Calendar .ics File Generation"""
        
        if not self.test_profiles:
            print(f"   ❌ No test profiles available")
            return False
        
        profile_id = self.test_profiles[0]
        
        # Get profile slug
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}",
            headers=self.get_headers()
        )
        
        profile = response.json()
        slug = profile["slug"]
        
        # Test calendar endpoint
        response = requests.get(f"{BASE_URL}/invite/{slug}/calendar")
        
        if response.status_code != 200:
            print(f"   ❌ Calendar endpoint failed: {response.status_code} - {response.text}")
            return False
        
        # Verify content type is calendar
        content_type = response.headers.get("content-type", "")
        if "calendar" not in content_type.lower():
            print(f"   ❌ Wrong content type for calendar: {content_type}")
            return False
        
        # Verify .ics content
        ics_content = response.text
        
        # Check for required .ics components
        required_components = [
            "BEGIN:VCALENDAR",
            "END:VCALENDAR", 
            "BEGIN:VEVENT",
            "END:VEVENT",
            "SUMMARY:",
            "DTSTART:",
            "DTEND:",
            "LOCATION:"
        ]
        
        for component in required_components:
            if component not in ics_content:
                print(f"   ❌ Missing .ics component: {component}")
                return False
        
        # Verify event details are included
        if "Wedding Ceremony" not in ics_content:
            print(f"   ❌ Event name not found in .ics file")
            return False
        
        if "Grand Palace Hall" not in ics_content:
            print(f"   ❌ Venue not found in .ics file")
            return False
        
        print(f"   ✓ Calendar .ics file generated successfully")
        print(f"   ✓ Contains all required components and event details")
        
        return True
    
    def test_qr_code_generation(self):
        """Test 8: QR Code PNG Generation"""
        
        if not self.test_profiles:
            print(f"   ❌ No test profiles available")
            return False
        
        profile_id = self.test_profiles[0]
        
        # Get profile slug
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}",
            headers=self.get_headers()
        )
        
        profile = response.json()
        slug = profile["slug"]
        
        # Test QR code endpoint
        response = requests.get(f"{BASE_URL}/invite/{slug}/qr")
        
        if response.status_code != 200:
            print(f"   ❌ QR code endpoint failed: {response.status_code} - {response.text}")
            return False
        
        # Verify content type is PNG image
        content_type = response.headers.get("content-type", "")
        if "image/png" not in content_type:
            print(f"   ❌ Wrong content type for QR code: {content_type}")
            return False
        
        # Verify response has image data
        if len(response.content) < 100:  # PNG should be larger than 100 bytes
            print(f"   ❌ QR code image too small: {len(response.content)} bytes")
            return False
        
        # Verify PNG signature (first 8 bytes)
        png_signature = b'\x89PNG\r\n\x1a\n'
        if not response.content.startswith(png_signature):
            print(f"   ❌ Invalid PNG signature")
            return False
        
        print(f"   ✓ QR code PNG generated successfully")
        print(f"   ✓ Image size: {len(response.content)} bytes")
        
        return True
    
    def test_sections_enabled_toggles(self):
        """Test 9: Sections Enabled Toggles CRUD Operations"""
        
        # Test profile update with different section combinations
        if not self.test_profiles:
            print(f"   ❌ No test profiles available")
            return False
        
        profile_id = self.test_profiles[0]
        
        # Test 1: Disable some PHASE 11 sections
        update_data = {
            "sections_enabled": {
                "opening": True,
                "welcome": True,
                "couple": True,
                "photos": True,
                "video": False,
                "events": True,
                "greetings": True,
                "contact": False,  # Disable contact
                "calendar": False, # Disable calendar
                "countdown": True,
                "qr": False,       # Disable QR
                "footer": True
            }
        }
        
        response = requests.put(
            f"{BASE_URL}/admin/profiles/{profile_id}",
            json=update_data,
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to update sections: {response.text}")
            return False
        
        updated_profile = response.json()
        sections = updated_profile["sections_enabled"]
        
        # Verify updates
        if (sections["contact"] != False or 
            sections["calendar"] != False or 
            sections["qr"] != False or
            sections["countdown"] != True):
            print(f"   ❌ Section toggles not updated correctly: {sections}")
            return False
        
        print(f"   ✓ Successfully disabled contact, calendar, and qr sections")
        
        # Test 2: Enable all sections
        update_data = {
            "sections_enabled": {
                "opening": True,
                "welcome": True,
                "couple": True,
                "photos": True,
                "video": True,
                "events": True,
                "greetings": True,
                "contact": True,
                "calendar": True,
                "countdown": True,
                "qr": True,
                "footer": True
            }
        }
        
        response = requests.put(
            f"{BASE_URL}/admin/profiles/{profile_id}",
            json=update_data,
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to enable all sections: {response.text}")
            return False
        
        updated_profile = response.json()
        sections = updated_profile["sections_enabled"]
        
        # Verify all PHASE 11 sections are enabled
        phase11_sections = ["contact", "calendar", "countdown", "qr"]
        for section in phase11_sections:
            if not sections.get(section, False):
                print(f"   ❌ Section {section} should be enabled")
                return False
        
        print(f"   ✓ Successfully enabled all PHASE 11 sections")
        
        # Test 3: Verify public API respects section toggles
        profile = updated_profile
        slug = profile["slug"]
        
        response = requests.get(f"{BASE_URL}/invite/{slug}")
        
        if response.status_code != 200:
            print(f"   ❌ Public API failed: {response.text}")
            return False
        
        public_data = response.json()
        public_sections = public_data["sections_enabled"]
        
        # Verify sections match
        for section in phase11_sections:
            if public_sections.get(section) != sections.get(section):
                print(f"   ❌ Section {section} mismatch in public API")
                return False
        
        print(f"   ✓ Public API correctly reflects section toggles")
        
        return True
    
    def cleanup_test_data(self):
        """Clean up test profiles and greetings"""
        print(f"\n🧹 Cleaning up {len(self.test_profiles)} test profiles...")
        
        for profile_id in self.test_profiles:
            try:
                response = requests.delete(
                    f"{BASE_URL}/admin/profiles/{profile_id}",
                    headers=self.get_headers()
                )
                if response.status_code == 200:
                    print(f"   ✓ Deleted profile {profile_id}")
                else:
                    print(f"   ⚠️ Failed to delete profile {profile_id}: {response.status_code}")
            except Exception as e:
                print(f"   ⚠️ Error deleting profile {profile_id}: {str(e)}")
    
    def run_all_tests(self):
        """Run all PHASE 11 tests"""
        print("🚀 Starting PHASE 11 Backend Testing")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        # Run all tests
        tests = [
            ("Profile Creation with Contact Information and E.164 Validation", self.test_profile_creation_with_contact_info),
            ("E.164 Phone Format Validation", self.test_invalid_phone_validation),
            ("Greeting Submission with Moderation (Default Pending Status)", self.test_greeting_submission_with_moderation),
            ("Emoji Spam Validation (Max 10 Emojis)", self.test_emoji_spam_validation),
            ("Admin Greeting Management Endpoints", self.test_admin_greeting_management),
            ("Public Invitation Returns Only Approved Greetings", self.test_public_invitation_approved_greetings_only),
            ("Calendar .ics File Generation", self.test_calendar_ics_generation),
            ("QR Code PNG Generation", self.test_qr_code_generation),
            ("Sections Enabled Toggles CRUD Operations", self.test_sections_enabled_toggles)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 PHASE 11 TESTING SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed_tests}/{self.total_tests} tests")
        print(f"❌ Failed: {self.total_tests - self.passed_tests}/{self.total_tests} tests")
        
        if self.passed_tests == self.total_tests:
            print("🎉 ALL PHASE 11 TESTS PASSED!")
            print("✅ PHASE 11 Guest Interaction & Experience Polish is production-ready")
            return True
        else:
            print("⚠️ Some tests failed - PHASE 11 needs attention")
            return False

def main():
    """Main function"""
    tester = Phase11Tester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 PHASE 11 BACKEND TESTING COMPLETE - ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ PHASE 11 BACKEND TESTING FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()