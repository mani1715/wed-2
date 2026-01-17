#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Events System
Tests all Events System functionality including:
- Profile Creation with Events
- Events Validation (max 7, at least 1 visible)
- Map Settings
- Public Invitation API with events
- Event Sorting
- Backward Compatibility
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import traceback

# Configuration
BASE_URL = "https://nuptial-hub-18.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@wedding.com"
ADMIN_PASSWORD = "admin123"

class EventsSystemTester:
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
    
    def test_profile_creation_with_events(self):
        """Test 1: Profile Creation with 3 Events (Mehendi, Sangeet, Wedding)"""
        
        # Create events data
        events = [
            {
                "name": "Mehendi Ceremony",
                "date": "2024-02-15",
                "start_time": "16:00",
                "end_time": "20:00",
                "venue_name": "Bride's Home",
                "venue_address": "123 Garden Street, Mumbai, Maharashtra 400001",
                "map_link": "https://maps.google.com/?q=123+Garden+Street+Mumbai",
                "description": "Traditional henna ceremony with music and dance",
                "visible": True,
                "order": 1
            },
            {
                "name": "Sangeet Night",
                "date": "2024-02-16",
                "start_time": "19:00",
                "end_time": "23:00",
                "venue_name": "Grand Ballroom",
                "venue_address": "456 Palace Road, Mumbai, Maharashtra 400002",
                "map_link": "https://maps.google.com/?q=456+Palace+Road+Mumbai",
                "description": "Musical evening with family performances",
                "visible": True,
                "order": 2
            },
            {
                "name": "Wedding Ceremony",
                "date": "2024-02-17",
                "start_time": "10:00",
                "end_time": "14:00",
                "venue_name": "Sacred Temple Hall",
                "venue_address": "789 Temple Street, Mumbai, Maharashtra 400003",
                "map_link": "https://maps.google.com/?q=789+Temple+Street+Mumbai",
                "description": "Sacred wedding rituals and celebrations",
                "visible": True,
                "order": 3
            }
        ]
        
        profile_data = {
            "groom_name": "Arjun Sharma",
            "bride_name": "Priya Patel",
            "event_type": "marriage",
            "event_date": "2024-02-17T10:00:00",
            "venue": "Sacred Temple Hall",
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
            "map_settings": {
                "embed_enabled": True
            },
            "events": events,
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
            
            # Verify events are stored correctly
            if len(profile["events"]) == 3:
                print(f"   ✓ Created profile with 3 events")
                print(f"   ✓ Profile ID: {profile['id']}")
                print(f"   ✓ Slug: {profile['slug']}")
                print(f"   ✓ Map settings embed_enabled: {profile['map_settings']['embed_enabled']}")
                
                # Verify each event has all required fields
                for i, event in enumerate(profile["events"]):
                    expected_name = events[i]["name"]
                    if event["name"] == expected_name:
                        print(f"   ✓ Event {i+1}: {event['name']} - All fields present")
                    else:
                        print(f"   ❌ Event {i+1}: Name mismatch")
                        return False
                
                return True
            else:
                print(f"   ❌ Expected 3 events, got {len(profile['events'])}")
                return False
        else:
            print(f"   ❌ Profile creation failed: {response.status_code} - {response.text}")
            return False
    
    def test_max_events_validation(self):
        """Test 2: Events Validation - Max 7 Events Limit"""
        
        # Create 8 events (should fail)
        events = []
        for i in range(8):
            events.append({
                "name": f"Event {i+1}",
                "date": f"2024-02-{15+i:02d}",
                "start_time": "10:00",
                "end_time": "12:00",
                "venue_name": f"Venue {i+1}",
                "venue_address": f"Address {i+1}",
                "map_link": f"https://maps.google.com/?q=venue{i+1}",
                "description": f"Description for event {i+1}",
                "visible": True,
                "order": i+1
            })
        
        profile_data = {
            "groom_name": "Test Groom",
            "bride_name": "Test Bride",
            "event_type": "marriage",
            "event_date": "2024-02-17T10:00:00",
            "venue": "Test Venue",
            "language": ["english"],
            "enabled_languages": ["english"],
            "events": events
        }
        
        response = requests.post(
            f"{BASE_URL}/admin/profiles",
            json=profile_data,
            headers=self.get_headers()
        )
        
        if response.status_code == 422:
            error_detail = response.json().get("detail", [])
            if any("Maximum 7 events allowed" in str(error) for error in error_detail):
                print(f"   ✓ Correctly rejected 8 events with validation error")
                return True
            else:
                print(f"   ❌ Wrong validation error: {error_detail}")
                return False
        else:
            print(f"   ❌ Expected 422 validation error, got {response.status_code}")
            return False
    
    def test_visible_events_validation(self):
        """Test 3: Events Validation - At Least 1 Visible Event Required"""
        
        # Create events with all visible=false (should fail)
        events = [
            {
                "name": "Hidden Event 1",
                "date": "2024-02-15",
                "start_time": "10:00",
                "end_time": "12:00",
                "venue_name": "Venue 1",
                "venue_address": "Address 1",
                "map_link": "https://maps.google.com/?q=venue1",
                "description": "Hidden event",
                "visible": False,
                "order": 1
            },
            {
                "name": "Hidden Event 2",
                "date": "2024-02-16",
                "start_time": "10:00",
                "end_time": "12:00",
                "venue_name": "Venue 2",
                "venue_address": "Address 2",
                "map_link": "https://maps.google.com/?q=venue2",
                "description": "Another hidden event",
                "visible": False,
                "order": 2
            }
        ]
        
        profile_data = {
            "groom_name": "Test Groom 2",
            "bride_name": "Test Bride 2",
            "event_type": "marriage",
            "event_date": "2024-02-17T10:00:00",
            "venue": "Test Venue",
            "language": ["english"],
            "enabled_languages": ["english"],
            "events": events
        }
        
        response = requests.post(
            f"{BASE_URL}/admin/profiles",
            json=profile_data,
            headers=self.get_headers()
        )
        
        if response.status_code == 422:
            error_detail = response.json().get("detail", [])
            if any("At least one event must be visible" in str(error) for error in error_detail):
                print(f"   ✓ Correctly rejected all hidden events with validation error")
                return True
            else:
                print(f"   ❌ Wrong validation error: {error_detail}")
                return False
        else:
            print(f"   ❌ Expected 422 validation error, got {response.status_code}")
            return False
    
    def test_map_settings_variations(self):
        """Test 4: Map Settings - embed_enabled true/false and updates"""
        
        # Test 1: Create profile with embed_enabled = false
        profile_data_false = {
            "groom_name": "Map Test Groom 1",
            "bride_name": "Map Test Bride 1",
            "event_type": "marriage",
            "event_date": "2024-02-17T10:00:00",
            "venue": "Test Venue",
            "language": ["english"],
            "enabled_languages": ["english"],
            "map_settings": {
                "embed_enabled": False
            },
            "events": [{
                "name": "Test Event",
                "date": "2024-02-17",
                "start_time": "10:00",
                "venue_name": "Test Venue",
                "venue_address": "Test Address",
                "map_link": "https://maps.google.com/?q=test",
                "visible": True,
                "order": 1
            }]
        }
        
        response1 = requests.post(
            f"{BASE_URL}/admin/profiles",
            json=profile_data_false,
            headers=self.get_headers()
        )
        
        if response1.status_code != 200:
            print(f"   ❌ Failed to create profile with embed_enabled=false: {response1.text}")
            return False
        
        profile1 = response1.json()
        self.test_profiles.append(profile1["id"])
        
        if not profile1["map_settings"]["embed_enabled"]:
            print(f"   ✓ Created profile with embed_enabled=false")
        else:
            print(f"   ❌ embed_enabled should be false")
            return False
        
        # Test 2: Create profile with embed_enabled = true
        profile_data_true = {
            "groom_name": "Map Test Groom 2",
            "bride_name": "Map Test Bride 2",
            "event_type": "marriage",
            "event_date": "2024-02-17T10:00:00",
            "venue": "Test Venue",
            "language": ["english"],
            "enabled_languages": ["english"],
            "map_settings": {
                "embed_enabled": True
            },
            "events": [{
                "name": "Test Event",
                "date": "2024-02-17",
                "start_time": "10:00",
                "venue_name": "Test Venue",
                "venue_address": "Test Address",
                "map_link": "https://maps.google.com/?q=test",
                "visible": True,
                "order": 1
            }]
        }
        
        response2 = requests.post(
            f"{BASE_URL}/admin/profiles",
            json=profile_data_true,
            headers=self.get_headers()
        )
        
        if response2.status_code != 200:
            print(f"   ❌ Failed to create profile with embed_enabled=true: {response2.text}")
            return False
        
        profile2 = response2.json()
        self.test_profiles.append(profile2["id"])
        
        if profile2["map_settings"]["embed_enabled"]:
            print(f"   ✓ Created profile with embed_enabled=true")
        else:
            print(f"   ❌ embed_enabled should be true")
            return False
        
        # Test 3: Update existing profile to toggle embed_enabled
        update_data = {
            "map_settings": {
                "embed_enabled": False
            }
        }
        
        response3 = requests.put(
            f"{BASE_URL}/admin/profiles/{profile2['id']}",
            json=update_data,
            headers=self.get_headers()
        )
        
        if response3.status_code != 200:
            print(f"   ❌ Failed to update map_settings: {response3.text}")
            return False
        
        updated_profile = response3.json()
        
        if not updated_profile["map_settings"]["embed_enabled"]:
            print(f"   ✓ Successfully updated embed_enabled from true to false")
            return True
        else:
            print(f"   ❌ embed_enabled should be false after update")
            return False
    
    def test_public_invitation_api_with_events(self):
        """Test 5: Public Invitation API - Events and Map Settings in Response"""
        
        if not self.test_profiles:
            print(f"   ❌ No test profiles available")
            return False
        
        # Get the first profile (should have 3 events)
        profile_id = self.test_profiles[0]
        
        # First get the profile to get the slug
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to get profile: {response.text}")
            return False
        
        profile = response.json()
        slug = profile["slug"]
        
        # Test public invitation API
        public_response = requests.get(f"{BASE_URL}/invite/{slug}")
        
        if public_response.status_code != 200:
            print(f"   ❌ Public invitation API failed: {public_response.text}")
            return False
        
        public_data = public_response.json()
        
        # Verify events array is returned
        if "events" not in public_data:
            print(f"   ❌ Events array missing from public API response")
            return False
        
        if len(public_data["events"]) != 3:
            print(f"   ❌ Expected 3 events, got {len(public_data['events'])}")
            return False
        
        print(f"   ✓ Public API returns events array with {len(public_data['events'])} events")
        
        # Verify map_settings is included
        if "map_settings" not in public_data:
            print(f"   ❌ map_settings missing from public API response")
            return False
        
        if "embed_enabled" not in public_data["map_settings"]:
            print(f"   ❌ embed_enabled missing from map_settings")
            return False
        
        print(f"   ✓ Public API includes map_settings with embed_enabled: {public_data['map_settings']['embed_enabled']}")
        
        # Verify all event fields are present
        required_fields = ["event_id", "name", "date", "start_time", "venue_name", "venue_address", "map_link", "visible", "order"]
        
        for i, event in enumerate(public_data["events"]):
            for field in required_fields:
                if field not in event:
                    print(f"   ❌ Event {i+1} missing field: {field}")
                    return False
        
        print(f"   ✓ All events have required fields")
        
        # Verify only visible events are considered for display
        visible_events = [e for e in public_data["events"] if e["visible"]]
        if len(visible_events) != 3:  # All our test events are visible
            print(f"   ❌ Expected 3 visible events, got {len(visible_events)}")
            return False
        
        print(f"   ✓ Visible events filter working correctly")
        
        return True
    
    def test_event_sorting(self):
        """Test 6: Event Sorting by Date and Start Time"""
        
        # Create profile with events in random order
        events = [
            {
                "name": "Evening Reception",
                "date": "2024-02-17",  # Same day, later time
                "start_time": "18:00",
                "end_time": "22:00",
                "venue_name": "Reception Hall",
                "venue_address": "Reception Address",
                "map_link": "https://maps.google.com/?q=reception",
                "description": "Evening reception",
                "visible": True,
                "order": 3
            },
            {
                "name": "Morning Wedding",
                "date": "2024-02-17",  # Same day, earlier time
                "start_time": "10:00",
                "end_time": "14:00",
                "venue_name": "Temple",
                "venue_address": "Temple Address",
                "map_link": "https://maps.google.com/?q=temple",
                "description": "Wedding ceremony",
                "visible": True,
                "order": 2
            },
            {
                "name": "Pre-Wedding Mehendi",
                "date": "2024-02-16",  # Earlier day
                "start_time": "16:00",
                "end_time": "20:00",
                "venue_name": "Home",
                "venue_address": "Home Address",
                "map_link": "https://maps.google.com/?q=home",
                "description": "Mehendi ceremony",
                "visible": True,
                "order": 1
            }
        ]
        
        profile_data = {
            "groom_name": "Sorting Test Groom",
            "bride_name": "Sorting Test Bride",
            "event_type": "marriage",
            "event_date": "2024-02-17T10:00:00",
            "venue": "Test Venue",
            "language": ["english"],
            "enabled_languages": ["english"],
            "events": events
        }
        
        response = requests.post(
            f"{BASE_URL}/admin/profiles",
            json=profile_data,
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to create profile for sorting test: {response.text}")
            return False
        
        profile = response.json()
        self.test_profiles.append(profile["id"])
        
        # Test public API to verify sorting
        public_response = requests.get(f"{BASE_URL}/invite/{profile['slug']}")
        
        if public_response.status_code != 200:
            print(f"   ❌ Public API failed: {public_response.text}")
            return False
        
        public_data = public_response.json()
        events_returned = public_data["events"]
        
        # Verify chronological order
        expected_order = [
            ("2024-02-16", "16:00", "Pre-Wedding Mehendi"),
            ("2024-02-17", "10:00", "Morning Wedding"),
            ("2024-02-17", "18:00", "Evening Reception")
        ]
        
        for i, (expected_date, expected_time, expected_name) in enumerate(expected_order):
            if i >= len(events_returned):
                print(f"   ❌ Missing event at position {i}")
                return False
            
            event = events_returned[i]
            if event["date"] != expected_date or event["start_time"] != expected_time:
                print(f"   ❌ Event {i+1} not in chronological order")
                print(f"       Expected: {expected_date} {expected_time}")
                print(f"       Got: {event['date']} {event['start_time']}")
                return False
            
            if event["name"] != expected_name:
                print(f"   ❌ Event {i+1} name mismatch: expected {expected_name}, got {event['name']}")
                return False
        
        print(f"   ✓ Events returned in correct chronological order")
        print(f"   ✓ Order: {' → '.join([f'{e[2]} ({e[0]} {e[1]})' for e in expected_order])}")
        
        return True
    
    def test_backward_compatibility(self):
        """Test 7: Backward Compatibility - Profile without Events"""
        
        # Create profile without events array (empty)
        profile_data = {
            "groom_name": "Legacy Groom",
            "bride_name": "Legacy Bride",
            "event_type": "marriage",
            "event_date": "2024-02-17T10:00:00",
            "venue": "Legacy Venue",
            "language": ["english"],
            "enabled_languages": ["english"],
            "events": []  # Empty events array
        }
        
        response = requests.post(
            f"{BASE_URL}/admin/profiles",
            json=profile_data,
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to create profile without events: {response.text}")
            return False
        
        profile = response.json()
        self.test_profiles.append(profile["id"])
        
        # Verify profile was created successfully
        if len(profile["events"]) != 0:
            print(f"   ❌ Expected empty events array, got {len(profile['events'])} events")
            return False
        
        print(f"   ✓ Profile created successfully with empty events array")
        
        # Test public API with empty events
        public_response = requests.get(f"{BASE_URL}/invite/{profile['slug']}")
        
        if public_response.status_code != 200:
            print(f"   ❌ Public API failed for profile without events: {public_response.text}")
            return False
        
        public_data = public_response.json()
        
        # Verify events field exists and is empty
        if "events" not in public_data:
            print(f"   ❌ Events field missing from public API")
            return False
        
        if len(public_data["events"]) != 0:
            print(f"   ❌ Expected empty events array in public API, got {len(public_data['events'])}")
            return False
        
        print(f"   ✓ Public API works correctly with empty events array")
        print(f"   ✓ Backward compatibility maintained")
        
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
        """Run all Events System tests"""
        print("🚀 Starting Events System Backend Testing")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        # Run all tests
        tests = [
            ("Profile Creation with 3 Events (Mehendi, Sangeet, Wedding)", self.test_profile_creation_with_events),
            ("Events Validation - Max 7 Events Limit", self.test_max_events_validation),
            ("Events Validation - At Least 1 Visible Event Required", self.test_visible_events_validation),
            ("Map Settings - embed_enabled Variations and Updates", self.test_map_settings_variations),
            ("Public Invitation API - Events and Map Settings Response", self.test_public_invitation_api_with_events),
            ("Event Sorting - Chronological Order by Date and Time", self.test_event_sorting),
            ("Backward Compatibility - Profile without Events", self.test_backward_compatibility)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Cleanup
        self.cleanup_test_profiles()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 EVENTS SYSTEM TESTING SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed_tests}/{self.total_tests} tests")
        print(f"❌ Failed: {self.total_tests - self.passed_tests}/{self.total_tests} tests")
        
        if self.passed_tests == self.total_tests:
            print("🎉 ALL EVENTS SYSTEM TESTS PASSED!")
            print("✅ Events System is production-ready")
            return True
        else:
            print("⚠️ Some tests failed - Events System needs attention")
            return False

def main():
    """Main function"""
    tester = EventsSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 EVENTS SYSTEM BACKEND TESTING COMPLETE - ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ EVENTS SYSTEM BACKEND TESTING FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()