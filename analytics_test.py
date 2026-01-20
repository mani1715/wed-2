#!/usr/bin/env python3
"""
PHASE 9 Enhanced Analytics System Testing
Tests all analytics functionality including:
- View tracking with device types and session management
- Language tracking
- Interaction tracking (map clicks, RSVP clicks, music play/pause)
- Detailed analytics retrieval
- Analytics summary with date range filters
- Edge cases and error handling
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta
import sys
import traceback

# Configuration
BASE_URL = "https://blissful-union-4.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@wedding.com"
ADMIN_PASSWORD = "admin123"

class AnalyticsSystemTester:
    def __init__(self):
        self.token = None
        self.test_profiles = []
        self.test_profile_id = None
        self.test_slug = None
        self.session_id = str(uuid.uuid4())
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
    
    def test_create_test_profile(self):
        """Test 1: Create a test wedding profile with realistic Indian names"""
        
        profile_data = {
            "groom_name": "Arjun Krishnamurthy",
            "bride_name": "Meera Raghavan",
            "event_type": "marriage",
            "event_date": "2024-03-15T10:00:00",
            "venue": "Sri Venkateswara Temple",
            "language": ["english", "telugu"],
            "design_id": "temple_divine",
            "deity_id": "venkateswara_padmavati",
            "whatsapp_groom": "+919876543210",
            "whatsapp_bride": "+919876543211",
            "enabled_languages": ["english", "telugu", "tamil"],
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
            "background_music": {
                "enabled": True,
                "file_url": "https://example.com/wedding-music.mp3"
            },
            "events": [
                {
                    "name": "Mehendi Ceremony",
                    "date": "2024-03-13",
                    "start_time": "16:00",
                    "end_time": "20:00",
                    "venue_name": "Bride's Home",
                    "venue_address": "123 Temple Street, Chennai, Tamil Nadu 600001",
                    "map_link": "https://maps.google.com/?q=123+Temple+Street+Chennai",
                    "description": "Traditional henna ceremony with music and dance",
                    "visible": True,
                    "order": 1
                },
                {
                    "name": "Wedding Ceremony",
                    "date": "2024-03-15",
                    "start_time": "10:00",
                    "end_time": "14:00",
                    "venue_name": "Sri Venkateswara Temple",
                    "venue_address": "456 Temple Road, Chennai, Tamil Nadu 600002",
                    "map_link": "https://maps.google.com/?q=456+Temple+Road+Chennai",
                    "description": "Sacred wedding rituals and celebrations",
                    "visible": True,
                    "order": 2
                }
            ],
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
            self.test_profile_id = profile["id"]
            self.test_slug = profile["slug"]
            self.test_profiles.append(profile["id"])
            
            print(f"   ✓ Created test profile: {profile['groom_name']} & {profile['bride_name']}")
            print(f"   ✓ Profile ID: {self.test_profile_id}")
            print(f"   ✓ Slug: {self.test_slug}")
            return True
        else:
            print(f"   ❌ Profile creation failed: {response.status_code} - {response.text}")
            return False
    
    def test_view_tracking_mobile(self):
        """Test 2: View tracking with mobile device type"""
        
        if not self.test_slug:
            print("   ❌ No test profile available")
            return False
        
        view_data = {
            "device_type": "mobile",
            "session_id": self.session_id
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{self.test_slug}/view",
            json=view_data
        )
        
        if response.status_code == 204:
            print(f"   ✓ Mobile view tracked successfully (204 status)")
            return True
        else:
            print(f"   ❌ Mobile view tracking failed: {response.status_code} - {response.text}")
            return False
    
    def test_view_tracking_desktop(self):
        """Test 3: View tracking with desktop device type"""
        
        if not self.test_slug:
            print("   ❌ No test profile available")
            return False
        
        view_data = {
            "device_type": "desktop",
            "session_id": str(uuid.uuid4())  # Different session
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{self.test_slug}/view",
            json=view_data
        )
        
        if response.status_code == 204:
            print(f"   ✓ Desktop view tracked successfully (204 status)")
            return True
        else:
            print(f"   ❌ Desktop view tracking failed: {response.status_code} - {response.text}")
            return False
    
    def test_view_tracking_tablet(self):
        """Test 4: View tracking with tablet device type"""
        
        if not self.test_slug:
            print("   ❌ No test profile available")
            return False
        
        view_data = {
            "device_type": "tablet",
            "session_id": str(uuid.uuid4())  # Different session
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{self.test_slug}/view",
            json=view_data
        )
        
        if response.status_code == 204:
            print(f"   ✓ Tablet view tracked successfully (204 status)")
            return True
        else:
            print(f"   ❌ Tablet view tracking failed: {response.status_code} - {response.text}")
            return False
    
    def test_unique_visitor_tracking(self):
        """Test 5: Unique visitor tracking with same session_id within 24hrs"""
        
        if not self.test_slug:
            print("   ❌ No test profile available")
            return False
        
        # Use same session_id as first mobile view (should not increment unique_views)
        view_data = {
            "device_type": "mobile",
            "session_id": self.session_id  # Same session as first test
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{self.test_slug}/view",
            json=view_data
        )
        
        if response.status_code == 204:
            print(f"   ✓ Repeat session view tracked (should not increment unique_views)")
            return True
        else:
            print(f"   ❌ Repeat session view tracking failed: {response.status_code} - {response.text}")
            return False
    
    def test_language_tracking_english(self):
        """Test 6: Language tracking - English"""
        
        if not self.test_slug:
            print("   ❌ No test profile available")
            return False
        
        language_data = {
            "language_code": "english"
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{self.test_slug}/track-language",
            json=language_data
        )
        
        if response.status_code == 204:
            print(f"   ✓ English language tracking successful (204 status)")
            return True
        else:
            print(f"   ❌ English language tracking failed: {response.status_code} - {response.text}")
            return False
    
    def test_language_tracking_telugu(self):
        """Test 7: Language tracking - Telugu"""
        
        if not self.test_slug:
            print("   ❌ No test profile available")
            return False
        
        language_data = {
            "language_code": "telugu"
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{self.test_slug}/track-language",
            json=language_data
        )
        
        if response.status_code == 204:
            print(f"   ✓ Telugu language tracking successful (204 status)")
            return True
        else:
            print(f"   ❌ Telugu language tracking failed: {response.status_code} - {response.text}")
            return False
    
    def test_language_tracking_tamil(self):
        """Test 8: Language tracking - Tamil"""
        
        if not self.test_slug:
            print("   ❌ No test profile available")
            return False
        
        language_data = {
            "language_code": "tamil"
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{self.test_slug}/track-language",
            json=language_data
        )
        
        if response.status_code == 204:
            print(f"   ✓ Tamil language tracking successful (204 status)")
            return True
        else:
            print(f"   ❌ Tamil language tracking failed: {response.status_code} - {response.text}")
            return False
    
    def test_interaction_tracking_map_click(self):
        """Test 9: Interaction tracking - Map click"""
        
        if not self.test_slug:
            print("   ❌ No test profile available")
            return False
        
        interaction_data = {
            "interaction_type": "map_click"
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{self.test_slug}/track-interaction",
            json=interaction_data
        )
        
        if response.status_code == 204:
            print(f"   ✓ Map click interaction tracked successfully (204 status)")
            return True
        else:
            print(f"   ❌ Map click interaction tracking failed: {response.status_code} - {response.text}")
            return False
    
    def test_interaction_tracking_rsvp_click(self):
        """Test 10: Interaction tracking - RSVP click"""
        
        if not self.test_slug:
            print("   ❌ No test profile available")
            return False
        
        interaction_data = {
            "interaction_type": "rsvp_click"
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{self.test_slug}/track-interaction",
            json=interaction_data
        )
        
        if response.status_code == 204:
            print(f"   ✓ RSVP click interaction tracked successfully (204 status)")
            return True
        else:
            print(f"   ❌ RSVP click interaction tracking failed: {response.status_code} - {response.text}")
            return False
    
    def test_interaction_tracking_music_play(self):
        """Test 11: Interaction tracking - Music play"""
        
        if not self.test_slug:
            print("   ❌ No test profile available")
            return False
        
        interaction_data = {
            "interaction_type": "music_play"
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{self.test_slug}/track-interaction",
            json=interaction_data
        )
        
        if response.status_code == 204:
            print(f"   ✓ Music play interaction tracked successfully (204 status)")
            return True
        else:
            print(f"   ❌ Music play interaction tracking failed: {response.status_code} - {response.text}")
            return False
    
    def test_interaction_tracking_music_pause(self):
        """Test 12: Interaction tracking - Music pause"""
        
        if not self.test_slug:
            print("   ❌ No test profile available")
            return False
        
        interaction_data = {
            "interaction_type": "music_pause"
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{self.test_slug}/track-interaction",
            json=interaction_data
        )
        
        if response.status_code == 204:
            print(f"   ✓ Music pause interaction tracked successfully (204 status)")
            return True
        else:
            print(f"   ❌ Music pause interaction tracking failed: {response.status_code} - {response.text}")
            return False
    
    def test_get_detailed_analytics(self):
        """Test 13: Get detailed analytics (admin only)"""
        
        if not self.test_profile_id:
            print("   ❌ No test profile available")
            return False
        
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{self.test_profile_id}/analytics",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            analytics = response.json()
            
            # Verify all required fields are present
            required_fields = [
                "profile_id", "total_views", "unique_views", "mobile_views", 
                "desktop_views", "tablet_views", "first_viewed_at", "last_viewed_at",
                "daily_views", "hourly_distribution", "language_views",
                "map_clicks", "rsvp_clicks", "music_plays", "music_pauses"
            ]
            
            for field in required_fields:
                if field not in analytics:
                    print(f"   ❌ Missing field in analytics: {field}")
                    return False
            
            print(f"   ✓ Analytics retrieved successfully")
            print(f"   ✓ Total views: {analytics['total_views']}")
            print(f"   ✓ Unique views: {analytics['unique_views']}")
            print(f"   ✓ Mobile views: {analytics['mobile_views']}")
            print(f"   ✓ Desktop views: {analytics['desktop_views']}")
            print(f"   ✓ Tablet views: {analytics['tablet_views']}")
            print(f"   ✓ Map clicks: {analytics['map_clicks']}")
            print(f"   ✓ RSVP clicks: {analytics['rsvp_clicks']}")
            print(f"   ✓ Music plays: {analytics['music_plays']}")
            print(f"   ✓ Music pauses: {analytics['music_pauses']}")
            print(f"   ✓ Language views: {analytics['language_views']}")
            
            # Verify expected values based on our tests
            if analytics['total_views'] >= 4:  # At least 4 views tracked
                print(f"   ✓ Total views count is correct")
            else:
                print(f"   ❌ Expected at least 4 total views, got {analytics['total_views']}")
                return False
            
            if analytics['unique_views'] >= 3:  # At least 3 unique sessions
                print(f"   ✓ Unique views count is correct")
            else:
                print(f"   ❌ Expected at least 3 unique views, got {analytics['unique_views']}")
                return False
            
            return True
        else:
            print(f"   ❌ Analytics retrieval failed: {response.status_code} - {response.text}")
            return False
    
    def test_analytics_summary_7d(self):
        """Test 14: Analytics summary with 7d date range"""
        
        if not self.test_profile_id:
            print("   ❌ No test profile available")
            return False
        
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{self.test_profile_id}/analytics/summary?date_range=7d",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            summary = response.json()
            
            # Verify required fields
            required_fields = ["total_views", "unique_visitors", "most_viewed_language", "peak_hour", "device_breakdown"]
            
            for field in required_fields:
                if field not in summary:
                    print(f"   ❌ Missing field in summary: {field}")
                    return False
            
            print(f"   ✓ 7d summary retrieved successfully")
            print(f"   ✓ Total views: {summary['total_views']}")
            print(f"   ✓ Unique visitors: {summary['unique_visitors']}")
            print(f"   ✓ Most viewed language: {summary['most_viewed_language']}")
            print(f"   ✓ Peak hour: {summary['peak_hour']}")
            print(f"   ✓ Device breakdown: {summary['device_breakdown']}")
            
            return True
        else:
            print(f"   ❌ 7d summary retrieval failed: {response.status_code} - {response.text}")
            return False
    
    def test_analytics_summary_30d(self):
        """Test 15: Analytics summary with 30d date range"""
        
        if not self.test_profile_id:
            print("   ❌ No test profile available")
            return False
        
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{self.test_profile_id}/analytics/summary?date_range=30d",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            summary = response.json()
            print(f"   ✓ 30d summary retrieved successfully")
            return True
        else:
            print(f"   ❌ 30d summary retrieval failed: {response.status_code} - {response.text}")
            return False
    
    def test_analytics_summary_all(self):
        """Test 16: Analytics summary with 'all' date range"""
        
        if not self.test_profile_id:
            print("   ❌ No test profile available")
            return False
        
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{self.test_profile_id}/analytics/summary?date_range=all",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            summary = response.json()
            print(f"   ✓ All-time summary retrieved successfully")
            return True
        else:
            print(f"   ❌ All-time summary retrieval failed: {response.status_code} - {response.text}")
            return False
    
    def test_analytics_no_views(self):
        """Test 17: Analytics for profile with no views (should return zeros)"""
        
        # Create a new profile for this test
        profile_data = {
            "groom_name": "Test Groom No Views",
            "bride_name": "Test Bride No Views",
            "event_type": "marriage",
            "event_date": "2024-03-20T10:00:00",
            "venue": "Test Venue",
            "language": ["english"],
            "enabled_languages": ["english"],
            "events": [{
                "name": "Test Event",
                "date": "2024-03-20",
                "start_time": "10:00",
                "venue_name": "Test Venue",
                "venue_address": "Test Address",
                "map_link": "https://maps.google.com/?q=test",
                "visible": True,
                "order": 1
            }]
        }
        
        response = requests.post(
            f"{BASE_URL}/admin/profiles",
            json=profile_data,
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to create test profile: {response.text}")
            return False
        
        profile = response.json()
        no_views_profile_id = profile["id"]
        self.test_profiles.append(no_views_profile_id)
        
        # Get analytics for profile with no views
        analytics_response = requests.get(
            f"{BASE_URL}/admin/profiles/{no_views_profile_id}/analytics",
            headers=self.get_headers()
        )
        
        if analytics_response.status_code == 200:
            analytics = analytics_response.json()
            
            # Verify all counts are zero
            if (analytics['total_views'] == 0 and 
                analytics['unique_views'] == 0 and
                analytics['mobile_views'] == 0 and
                analytics['desktop_views'] == 0 and
                analytics['tablet_views'] == 0 and
                analytics['map_clicks'] == 0 and
                analytics['rsvp_clicks'] == 0 and
                analytics['music_plays'] == 0 and
                analytics['music_pauses'] == 0):
                
                print(f"   ✓ Profile with no views returns zeros correctly")
                return True
            else:
                print(f"   ❌ Profile with no views should return all zeros")
                return False
        else:
            print(f"   ❌ Analytics retrieval failed: {analytics_response.status_code}")
            return False
    
    def test_invalid_slug_404(self):
        """Test 18: Invalid slug returns 404"""
        
        invalid_slug = "invalid-slug-12345"
        
        # Test view tracking with invalid slug
        view_data = {
            "device_type": "mobile",
            "session_id": str(uuid.uuid4())
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{invalid_slug}/view",
            json=view_data
        )
        
        if response.status_code == 404:
            print(f"   ✓ Invalid slug correctly returns 404 for view tracking")
            return True
        else:
            print(f"   ❌ Expected 404 for invalid slug, got {response.status_code}")
            return False
    
    def test_analytics_without_auth_403(self):
        """Test 19: Analytics without auth token returns 403"""
        
        if not self.test_profile_id:
            print("   ❌ No test profile available")
            return False
        
        # Try to get analytics without auth header
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{self.test_profile_id}/analytics"
        )
        
        if response.status_code == 403:
            print(f"   ✓ Analytics without auth correctly returns 403")
            return True
        else:
            print(f"   ❌ Expected 403 for no auth, got {response.status_code}")
            return False
    
    def test_invalid_device_type_422(self):
        """Test 20: Invalid device_type returns 422"""
        
        if not self.test_slug:
            print("   ❌ No test profile available")
            return False
        
        view_data = {
            "device_type": "invalid_device",
            "session_id": str(uuid.uuid4())
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{self.test_slug}/view",
            json=view_data
        )
        
        if response.status_code == 422:
            print(f"   ✓ Invalid device_type correctly returns 422")
            return True
        else:
            print(f"   ❌ Expected 422 for invalid device_type, got {response.status_code}")
            return False
    
    def test_invalid_interaction_type_422(self):
        """Test 21: Invalid interaction_type returns 422"""
        
        if not self.test_slug:
            print("   ❌ No test profile available")
            return False
        
        interaction_data = {
            "interaction_type": "invalid_interaction"
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{self.test_slug}/track-interaction",
            json=interaction_data
        )
        
        if response.status_code == 422:
            print(f"   ✓ Invalid interaction_type correctly returns 422")
            return True
        else:
            print(f"   ❌ Expected 422 for invalid interaction_type, got {response.status_code}")
            return False
    
    def test_invalid_language_code_422(self):
        """Test 22: Invalid language_code returns 422"""
        
        if not self.test_slug:
            print("   ❌ No test profile available")
            return False
        
        language_data = {
            "language_code": "invalid_language"
        }
        
        response = requests.post(
            f"{BASE_URL}/invite/{self.test_slug}/track-language",
            json=language_data
        )
        
        if response.status_code == 422:
            print(f"   ✓ Invalid language_code correctly returns 422")
            return True
        else:
            print(f"   ❌ Expected 422 for invalid language_code, got {response.status_code}")
            return False
    
    def cleanup_test_profiles(self):
        """Clean up test profiles"""
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
        """Run all Analytics System tests"""
        print("🚀 Starting PHASE 9 Enhanced Analytics System Testing")
        print("=" * 70)
        
        if not self.authenticate():
            return False
        
        # Run all tests
        tests = [
            ("Create Test Profile with Realistic Indian Names", self.test_create_test_profile),
            ("View Tracking - Mobile Device", self.test_view_tracking_mobile),
            ("View Tracking - Desktop Device", self.test_view_tracking_desktop),
            ("View Tracking - Tablet Device", self.test_view_tracking_tablet),
            ("Unique Visitor Tracking - Same Session ID", self.test_unique_visitor_tracking),
            ("Language Tracking - English", self.test_language_tracking_english),
            ("Language Tracking - Telugu", self.test_language_tracking_telugu),
            ("Language Tracking - Tamil", self.test_language_tracking_tamil),
            ("Interaction Tracking - Map Click", self.test_interaction_tracking_map_click),
            ("Interaction Tracking - RSVP Click", self.test_interaction_tracking_rsvp_click),
            ("Interaction Tracking - Music Play", self.test_interaction_tracking_music_play),
            ("Interaction Tracking - Music Pause", self.test_interaction_tracking_music_pause),
            ("Get Detailed Analytics (Admin Only)", self.test_get_detailed_analytics),
            ("Analytics Summary - 7d Date Range", self.test_analytics_summary_7d),
            ("Analytics Summary - 30d Date Range", self.test_analytics_summary_30d),
            ("Analytics Summary - All Time", self.test_analytics_summary_all),
            ("Analytics for Profile with No Views", self.test_analytics_no_views),
            ("Invalid Slug Returns 404", self.test_invalid_slug_404),
            ("Analytics without Auth Returns 403", self.test_analytics_without_auth_403),
            ("Invalid Device Type Returns 422", self.test_invalid_device_type_422),
            ("Invalid Interaction Type Returns 422", self.test_invalid_interaction_type_422),
            ("Invalid Language Code Returns 422", self.test_invalid_language_code_422)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Cleanup
        self.cleanup_test_profiles()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 PHASE 9 ENHANCED ANALYTICS SYSTEM TESTING SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {self.passed_tests}/{self.total_tests} tests")
        print(f"❌ Failed: {self.total_tests - self.passed_tests}/{self.total_tests} tests")
        
        if self.passed_tests == self.total_tests:
            print("🎉 ALL ANALYTICS SYSTEM TESTS PASSED!")
            print("✅ Phase 9 Enhanced Analytics System is production-ready")
            return True
        else:
            print("⚠️ Some tests failed - Analytics System needs attention")
            return False

def main():
    """Main function"""
    tester = AnalyticsSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 PHASE 9 ENHANCED ANALYTICS SYSTEM TESTING COMPLETE - ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ PHASE 9 ENHANCED ANALYTICS SYSTEM TESTING FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()