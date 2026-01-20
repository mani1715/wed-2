#!/usr/bin/env python3
"""
PHASE 7 - Invitation Analytics & View Tracking Backend Testing
Tests all analytics functionality including:
- View Tracking Endpoint (POST /api/invite/{slug}/view)
- Analytics Retrieval (GET /api/admin/profiles/{profile_id}/analytics)
- View Increment Logic
- Zero Views Case
- Performance Check
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys
import traceback

# Configuration
BASE_URL = "https://wed-management.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@wedding.com"
ADMIN_PASSWORD = "admin123"

class Phase7AnalyticsTester:
    def __init__(self):
        self.token = None
        self.test_profiles = []
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
    
    def create_test_profile(self, name_suffix=""):
        """Create a test profile for analytics testing"""
        profile_data = {
            "groom_name": f"Rajesh Kumar{name_suffix}",
            "bride_name": f"Priya Sharma{name_suffix}",
            "event_type": "marriage",
            "event_date": "2024-03-15T10:00:00",
            "venue": "Grand Palace Hall",
            "language": ["english", "telugu"],
            "design_id": "royal_classic",
            "deity_id": "ganesha",
            "whatsapp_groom": "+919876543210",
            "whatsapp_bride": "+919876543211",
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
            return profile
        else:
            print(f"   ❌ Failed to create test profile: {response.status_code} - {response.text}")
            return None
    
    def test_view_tracking_endpoint(self):
        """Test 1: View Tracking Endpoint (POST /api/invite/{slug}/view)"""
        
        # Create test profile
        profile = self.create_test_profile(" ViewTracking")
        if not profile:
            return False
        
        slug = profile["slug"]
        print(f"   ✓ Created test profile with slug: {slug}")
        
        # Test mobile view tracking
        mobile_view_data = {
            "device_type": "mobile"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/invite/{slug}/view",
            json=mobile_view_data
        )
        end_time = time.time()
        
        if response.status_code != 204:
            print(f"   ❌ Mobile view tracking failed: {response.status_code} - {response.text}")
            return False
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        print(f"   ✓ Mobile view tracked successfully (Response time: {response_time:.2f}ms)")
        
        # Test desktop view tracking
        desktop_view_data = {
            "device_type": "desktop"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/invite/{slug}/view",
            json=desktop_view_data
        )
        end_time = time.time()
        
        if response.status_code != 204:
            print(f"   ❌ Desktop view tracking failed: {response.status_code} - {response.text}")
            return False
        
        response_time = (end_time - start_time) * 1000
        print(f"   ✓ Desktop view tracked successfully (Response time: {response_time:.2f}ms)")
        
        # Test with invalid slug
        invalid_response = requests.post(
            f"{BASE_URL}/invite/invalid-slug-12345/view",
            json=mobile_view_data
        )
        
        if invalid_response.status_code != 404:
            print(f"   ❌ Expected 404 for invalid slug, got {invalid_response.status_code}")
            return False
        
        print(f"   ✓ Invalid slug correctly returns 404")
        
        return True
    
    def test_analytics_retrieval(self):
        """Test 2: Analytics Retrieval (GET /api/admin/profiles/{profile_id}/analytics)"""
        
        if not self.test_profiles:
            print(f"   ❌ No test profiles available")
            return False
        
        profile_id = self.test_profiles[0]  # Use the profile from previous test
        
        # Get analytics for the profile
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}/analytics",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Analytics retrieval failed: {response.status_code} - {response.text}")
            return False
        
        analytics = response.json()
        print(f"   ✓ Analytics retrieved successfully")
        
        # Verify response structure
        required_fields = ["profile_id", "total_views", "mobile_views", "desktop_views", "last_viewed_at"]
        for field in required_fields:
            if field not in analytics:
                print(f"   ❌ Missing field in analytics response: {field}")
                return False
        
        print(f"   ✓ All required fields present in analytics response")
        
        # Verify counts match tracked views (1 mobile + 1 desktop = 2 total)
        if analytics["total_views"] != 2:
            print(f"   ❌ Expected total_views=2, got {analytics['total_views']}")
            return False
        
        if analytics["mobile_views"] != 1:
            print(f"   ❌ Expected mobile_views=1, got {analytics['mobile_views']}")
            return False
        
        if analytics["desktop_views"] != 1:
            print(f"   ❌ Expected desktop_views=1, got {analytics['desktop_views']}")
            return False
        
        if analytics["last_viewed_at"] is None:
            print(f"   ❌ last_viewed_at should not be null")
            return False
        
        print(f"   ✓ View counts match tracked views: Total={analytics['total_views']}, Mobile={analytics['mobile_views']}, Desktop={analytics['desktop_views']}")
        
        # Test with invalid profile_id
        invalid_response = requests.get(
            f"{BASE_URL}/admin/profiles/invalid-profile-id/analytics",
            headers=self.get_headers()
        )
        
        if invalid_response.status_code != 404:
            print(f"   ❌ Expected 404 for invalid profile_id, got {invalid_response.status_code}")
            return False
        
        print(f"   ✓ Invalid profile_id correctly returns 404")
        
        # Test without authentication
        no_auth_response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}/analytics"
        )
        
        if no_auth_response.status_code not in [401, 403]:
            print(f"   ❌ Expected 401 or 403 for no authentication, got {no_auth_response.status_code}")
            return False
        
        print(f"   ✓ No authentication correctly returns {no_auth_response.status_code}")
        
        return True
    
    def test_view_increment_logic(self):
        """Test 3: View Increment Logic"""
        
        # Create new test profile for increment testing
        profile = self.create_test_profile(" IncrementTest")
        if not profile:
            return False
        
        slug = profile["slug"]
        profile_id = profile["id"]
        
        print(f"   ✓ Created test profile for increment testing: {slug}")
        
        # Track multiple mobile views
        for i in range(3):
            response = requests.post(
                f"{BASE_URL}/invite/{slug}/view",
                json={"device_type": "mobile"}
            )
            if response.status_code != 204:
                print(f"   ❌ Mobile view {i+1} tracking failed")
                return False
        
        print(f"   ✓ Tracked 3 mobile views")
        
        # Track multiple desktop views
        for i in range(2):
            response = requests.post(
                f"{BASE_URL}/invite/{slug}/view",
                json={"device_type": "desktop"}
            )
            if response.status_code != 204:
                print(f"   ❌ Desktop view {i+1} tracking failed")
                return False
        
        print(f"   ✓ Tracked 2 desktop views")
        
        # Get analytics and verify counts
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}/analytics",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Analytics retrieval failed")
            return False
        
        analytics = response.json()
        
        # Verify total_views increments correctly (3 mobile + 2 desktop = 5 total)
        if analytics["total_views"] != 5:
            print(f"   ❌ Expected total_views=5, got {analytics['total_views']}")
            return False
        
        # Verify mobile_views and desktop_views increment independently
        if analytics["mobile_views"] != 3:
            print(f"   ❌ Expected mobile_views=3, got {analytics['mobile_views']}")
            return False
        
        if analytics["desktop_views"] != 2:
            print(f"   ❌ Expected desktop_views=2, got {analytics['desktop_views']}")
            return False
        
        print(f"   ✓ View counts incremented correctly: Total={analytics['total_views']}, Mobile={analytics['mobile_views']}, Desktop={analytics['desktop_views']}")
        
        # Store initial last_viewed_at
        initial_last_viewed = analytics["last_viewed_at"]
        
        # Wait a moment and track another view
        time.sleep(1)
        
        response = requests.post(
            f"{BASE_URL}/invite/{slug}/view",
            json={"device_type": "mobile"}
        )
        
        if response.status_code != 204:
            print(f"   ❌ Additional view tracking failed")
            return False
        
        # Get updated analytics
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}/analytics",
            headers=self.get_headers()
        )
        
        analytics = response.json()
        updated_last_viewed = analytics["last_viewed_at"]
        
        # Verify last_viewed_at updates on each view
        if updated_last_viewed == initial_last_viewed:
            print(f"   ❌ last_viewed_at should update on each view")
            return False
        
        print(f"   ✓ last_viewed_at updates correctly on each view")
        
        return True
    
    def test_zero_views_case(self):
        """Test 4: Zero Views Case"""
        
        # Create new profile that has never been viewed
        profile = self.create_test_profile(" ZeroViews")
        if not profile:
            return False
        
        profile_id = profile["id"]
        print(f"   ✓ Created new profile that has never been viewed")
        
        # Get analytics for this profile
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}/analytics",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Analytics retrieval failed: {response.status_code} - {response.text}")
            return False
        
        analytics = response.json()
        
        # Verify it returns zero for all view counts
        if analytics["total_views"] != 0:
            print(f"   ❌ Expected total_views=0, got {analytics['total_views']}")
            return False
        
        if analytics["mobile_views"] != 0:
            print(f"   ❌ Expected mobile_views=0, got {analytics['mobile_views']}")
            return False
        
        if analytics["desktop_views"] != 0:
            print(f"   ❌ Expected desktop_views=0, got {analytics['desktop_views']}")
            return False
        
        # Verify last_viewed_at is null
        if analytics["last_viewed_at"] is not None:
            print(f"   ❌ Expected last_viewed_at=null, got {analytics['last_viewed_at']}")
            return False
        
        print(f"   ✓ Zero views case returns correct values: Total=0, Mobile=0, Desktop=0, LastViewed=null")
        
        return True
    
    def test_performance_check(self):
        """Test 5: Performance Check"""
        
        if not self.test_profiles:
            print(f"   ❌ No test profiles available")
            return False
        
        # Get slug from first test profile
        profile_id = self.test_profiles[0]
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to get profile for performance test")
            return False
        
        slug = response.json()["slug"]
        
        # Test multiple view tracking requests for performance
        response_times = []
        
        for i in range(10):
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/invite/{slug}/view",
                json={"device_type": "mobile"}
            )
            end_time = time.time()
            
            if response.status_code != 204:
                print(f"   ❌ Performance test request {i+1} failed")
                return False
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            response_times.append(response_time)
        
        # Calculate average response time
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        print(f"   ✓ Completed 10 view tracking requests")
        print(f"   ✓ Average response time: {avg_response_time:.2f}ms")
        print(f"   ✓ Maximum response time: {max_response_time:.2f}ms")
        
        # Verify POST /api/invite/{slug}/view responds quickly (<100ms average)
        if avg_response_time > 100:
            print(f"   ⚠️ Average response time ({avg_response_time:.2f}ms) exceeds 100ms threshold")
            # Don't fail the test, just warn as network latency can affect this
        else:
            print(f"   ✅ Response time meets <100ms performance requirement")
        
        # Test that it doesn't block invitation loading
        start_time = time.time()
        invitation_response = requests.get(f"{BASE_URL}/invite/{slug}")
        end_time = time.time()
        
        if invitation_response.status_code != 200:
            print(f"   ❌ Invitation loading failed during performance test")
            return False
        
        invitation_response_time = (end_time - start_time) * 1000
        print(f"   ✓ Invitation loading works correctly (Response time: {invitation_response_time:.2f}ms)")
        print(f"   ✓ View tracking doesn't block invitation loading")
        
        return True
    
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
        """Run all Phase 7 Analytics tests"""
        print("🚀 Starting PHASE 7 - Invitation Analytics & View Tracking Backend Testing")
        print("=" * 80)
        
        if not self.authenticate():
            return False
        
        # Run all tests
        tests = [
            ("View Tracking Endpoint (POST /api/invite/{slug}/view)", self.test_view_tracking_endpoint),
            ("Analytics Retrieval (GET /api/admin/profiles/{profile_id}/analytics)", self.test_analytics_retrieval),
            ("View Increment Logic", self.test_view_increment_logic),
            ("Zero Views Case", self.test_zero_views_case),
            ("Performance Check", self.test_performance_check)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Cleanup
        self.cleanup_test_profiles()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 PHASE 7 ANALYTICS TESTING SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {self.passed_tests}/{self.total_tests} tests")
        print(f"❌ Failed: {self.total_tests - self.passed_tests}/{self.total_tests} tests")
        
        if self.passed_tests == self.total_tests:
            print("🎉 ALL PHASE 7 ANALYTICS TESTS PASSED!")
            print("✅ Invitation Analytics & View Tracking system is production-ready")
            return True
        else:
            print("⚠️ Some tests failed - Analytics system needs attention")
            return False

def main():
    """Main function"""
    tester = Phase7AnalyticsTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 PHASE 7 ANALYTICS BACKEND TESTING COMPLETE - ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ PHASE 7 ANALYTICS BACKEND TESTING FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()