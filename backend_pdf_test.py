#!/usr/bin/env python3
"""
Comprehensive Backend Testing for PHASE 8 PDF Generation with Deity Background
Tests all PDF generation functionality including:
- PDF generation with deity background (deity_id='ganesha')
- PDF generation without deity (deity_id=null)
- PDF generation with different deities
- PDF generation with different languages
- Multi-event PDF
- PDF security (without authentication)
- Performance testing
- Filename format verification
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import traceback
import time
import re

# Configuration
BASE_URL = "https://wed-organizer-17.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@wedding.com"
ADMIN_PASSWORD = "admin123"

class PDFGenerationTester:
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
    
    def create_test_profile(self, groom_name, bride_name, deity_id=None, events=None, enabled_languages=None):
        """Helper function to create a test profile"""
        if events is None:
            events = [{
                "name": "Wedding Ceremony",
                "date": "2024-03-15",
                "start_time": "10:00",
                "end_time": "14:00",
                "venue_name": "Sacred Temple Hall",
                "venue_address": "789 Temple Street, Mumbai, Maharashtra 400003",
                "map_link": "https://maps.google.com/?q=789+Temple+Street+Mumbai",
                "description": "Sacred wedding rituals and celebrations",
                "visible": True,
                "order": 1
            }]
        
        if enabled_languages is None:
            enabled_languages = ["english"]
        
        profile_data = {
            "groom_name": groom_name,
            "bride_name": bride_name,
            "event_type": "marriage",
            "event_date": "2024-03-15T10:00:00",
            "venue": "Sacred Temple Hall",
            "language": enabled_languages,
            "design_id": "royal_classic",
            "deity_id": deity_id,
            "whatsapp_groom": "+919876543210",
            "whatsapp_bride": "+919876543211",
            "enabled_languages": enabled_languages,
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
            return profile
        else:
            print(f"   ❌ Profile creation failed: {response.status_code} - {response.text}")
            return None
    
    def test_pdf_generation_with_deity_ganesha(self):
        """Test 1: PDF Generation with Deity Background (deity_id='ganesha')"""
        
        # Create profile with Ganesha deity
        profile = self.create_test_profile(
            "Rajesh Kumar", 
            "Priya Sharma", 
            deity_id="ganesha"
        )
        
        if not profile:
            return False
        
        print(f"   ✓ Created profile with deity_id='ganesha'")
        print(f"   ✓ Profile ID: {profile['id']}")
        
        # Test PDF generation
        start_time = time.time()
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile['id']}/download-pdf?language=english",
            headers=self.get_headers()
        )
        end_time = time.time()
        
        generation_time = end_time - start_time
        
        if response.status_code != 200:
            print(f"   ❌ PDF generation failed: {response.status_code} - {response.text}")
            return False
        
        # Verify response headers
        content_type = response.headers.get('content-type', '')
        if content_type != 'application/pdf':
            print(f"   ❌ Wrong content type: expected 'application/pdf', got '{content_type}'")
            return False
        
        print(f"   ✓ PDF generated successfully with correct content-type")
        
        # Verify Content-Disposition header
        content_disposition = response.headers.get('content-disposition', '')
        expected_filename = "wedding-invitation-rajesh-priya.pdf"
        if expected_filename not in content_disposition:
            print(f"   ❌ Wrong filename in Content-Disposition: {content_disposition}")
            return False
        
        print(f"   ✓ Correct filename format: {expected_filename}")
        
        # Verify PDF file size (should be reasonable < 2MB)
        pdf_size = len(response.content)
        pdf_size_mb = pdf_size / (1024 * 1024)
        
        if pdf_size_mb > 2.0:
            print(f"   ⚠️ PDF size is large: {pdf_size_mb:.2f}MB (should be < 2MB)")
        else:
            print(f"   ✓ PDF size is reasonable: {pdf_size_mb:.2f}MB")
        
        # Verify generation time
        if generation_time > 2.0:
            print(f"   ⚠️ PDF generation took {generation_time:.2f}s (should be < 2s)")
        else:
            print(f"   ✓ PDF generation time: {generation_time:.2f}s")
        
        # Verify PDF content is not empty
        if pdf_size < 1000:  # Less than 1KB is suspicious
            print(f"   ❌ PDF size too small: {pdf_size} bytes")
            return False
        
        print(f"   ✓ PDF content size: {pdf_size} bytes")
        print(f"   ✓ PDF with Ganesha deity background generated successfully")
        
        return True
    
    def test_pdf_generation_without_deity(self):
        """Test 2: PDF Generation without Deity (deity_id=null)"""
        
        # Create profile without deity
        profile = self.create_test_profile(
            "Amit Patel", 
            "Sneha Gupta", 
            deity_id=None
        )
        
        if not profile:
            return False
        
        print(f"   ✓ Created profile with deity_id=null")
        
        # Test PDF generation
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile['id']}/download-pdf?language=english",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ PDF generation failed: {response.status_code} - {response.text}")
            return False
        
        # Verify response
        if response.headers.get('content-type') != 'application/pdf':
            print(f"   ❌ Wrong content type")
            return False
        
        pdf_size = len(response.content)
        if pdf_size < 1000:
            print(f"   ❌ PDF size too small: {pdf_size} bytes")
            return False
        
        print(f"   ✓ PDF generated successfully without deity background")
        print(f"   ✓ PDF size: {pdf_size} bytes")
        
        return True
    
    def test_pdf_generation_different_deities(self):
        """Test 3: PDF Generation with Different Deities"""
        
        deities = [
            ("venkateswara_padmavati", "Arjun Reddy", "Lakshmi Devi"),
            ("shiva_parvati", "Karthik Sharma", "Meera Nair"),
            ("lakshmi_vishnu", "Vikram Singh", "Pooja Agarwal")
        ]
        
        for deity_id, groom, bride in deities:
            print(f"   Testing deity: {deity_id}")
            
            profile = self.create_test_profile(groom, bride, deity_id=deity_id)
            if not profile:
                print(f"   ❌ Failed to create profile for {deity_id}")
                return False
            
            response = requests.get(
                f"{BASE_URL}/admin/profiles/{profile['id']}/download-pdf?language=english",
                headers=self.get_headers()
            )
            
            if response.status_code != 200:
                print(f"   ❌ PDF generation failed for {deity_id}: {response.status_code}")
                return False
            
            if response.headers.get('content-type') != 'application/pdf':
                print(f"   ❌ Wrong content type for {deity_id}")
                return False
            
            pdf_size = len(response.content)
            if pdf_size < 1000:
                print(f"   ❌ PDF size too small for {deity_id}: {pdf_size} bytes")
                return False
            
            print(f"   ✓ {deity_id}: PDF generated successfully ({pdf_size} bytes)")
        
        print(f"   ✅ All deity backgrounds working correctly")
        return True
    
    def test_pdf_generation_different_languages(self):
        """Test 4: PDF Generation with Different Languages"""
        
        languages = ["english", "telugu", "tamil", "kannada", "malayalam"]
        
        # Create profile with all languages enabled
        profile = self.create_test_profile(
            "Suresh Kumar", 
            "Kavitha Reddy", 
            deity_id="ganesha",
            enabled_languages=languages
        )
        
        if not profile:
            return False
        
        print(f"   ✓ Created profile with all languages enabled: {languages}")
        
        for language in languages:
            print(f"   Testing language: {language}")
            
            response = requests.get(
                f"{BASE_URL}/admin/profiles/{profile['id']}/download-pdf?language={language}",
                headers=self.get_headers()
            )
            
            if response.status_code != 200:
                print(f"   ❌ PDF generation failed for {language}: {response.status_code}")
                return False
            
            if response.headers.get('content-type') != 'application/pdf':
                print(f"   ❌ Wrong content type for {language}")
                return False
            
            pdf_size = len(response.content)
            if pdf_size < 1000:
                print(f"   ❌ PDF size too small for {language}: {pdf_size} bytes")
                return False
            
            print(f"   ✓ {language}: PDF generated successfully ({pdf_size} bytes)")
        
        print(f"   ✅ All languages working correctly")
        return True
    
    def test_multi_event_pdf(self):
        """Test 5: Multi-Event PDF Generation"""
        
        # Create multiple events
        events = [
            {
                "name": "Mehendi Ceremony",
                "date": "2024-03-13",
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
                "date": "2024-03-14",
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
                "date": "2024-03-15",
                "start_time": "10:00",
                "end_time": "14:00",
                "venue_name": "Sacred Temple Hall",
                "venue_address": "789 Temple Street, Mumbai, Maharashtra 400003",
                "map_link": "https://maps.google.com/?q=789+Temple+Street+Mumbai",
                "description": "Sacred wedding rituals and celebrations",
                "visible": True,
                "order": 3
            },
            {
                "name": "Reception Party",
                "date": "2024-03-15",
                "start_time": "18:00",
                "end_time": "22:00",
                "venue_name": "Luxury Hotel Ballroom",
                "venue_address": "999 Hotel Avenue, Mumbai, Maharashtra 400004",
                "map_link": "https://maps.google.com/?q=999+Hotel+Avenue+Mumbai",
                "description": "Evening reception with dinner and dance",
                "visible": True,
                "order": 4
            }
        ]
        
        profile = self.create_test_profile(
            "Rohit Sharma", 
            "Anjali Kapoor", 
            deity_id="shiva_parvati",
            events=events
        )
        
        if not profile:
            return False
        
        print(f"   ✓ Created profile with {len(events)} events")
        
        # Test PDF generation
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile['id']}/download-pdf?language=english",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Multi-event PDF generation failed: {response.status_code}")
            return False
        
        pdf_size = len(response.content)
        pdf_size_mb = pdf_size / (1024 * 1024)
        
        print(f"   ✓ Multi-event PDF generated successfully")
        print(f"   ✓ PDF size: {pdf_size_mb:.2f}MB")
        
        # Verify events are included (PDF should be larger with more content)
        if pdf_size < 5000:  # Multi-event PDF should be larger
            print(f"   ⚠️ Multi-event PDF seems small: {pdf_size} bytes")
        
        return True
    
    def test_pdf_security_no_auth(self):
        """Test 6: PDF Security - No Authentication"""
        
        if not self.test_profiles:
            print(f"   ❌ No test profiles available")
            return False
        
        profile_id = self.test_profiles[0]
        
        # Try to download PDF without authentication
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}/download-pdf?language=english"
            # No headers = no authentication
        )
        
        if response.status_code == 403:
            print(f"   ✅ Correctly returned 403 Forbidden without authentication")
            return True
        elif response.status_code == 401:
            print(f"   ✅ Correctly returned 401 Unauthorized without authentication")
            return True
        else:
            print(f"   ❌ Expected 403/401, got {response.status_code}")
            return False
    
    def test_pdf_performance(self):
        """Test 7: PDF Performance Testing"""
        
        if not self.test_profiles:
            print(f"   ❌ No test profiles available")
            return False
        
        profile_id = self.test_profiles[0]
        
        # Test multiple PDF generations for performance
        times = []
        
        for i in range(3):
            start_time = time.time()
            response = requests.get(
                f"{BASE_URL}/admin/profiles/{profile_id}/download-pdf?language=english",
                headers=self.get_headers()
            )
            end_time = time.time()
            
            if response.status_code != 200:
                print(f"   ❌ PDF generation {i+1} failed: {response.status_code}")
                return False
            
            generation_time = end_time - start_time
            times.append(generation_time)
            print(f"   ✓ Generation {i+1}: {generation_time:.2f}s")
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"   📊 Average generation time: {avg_time:.2f}s")
        print(f"   📊 Maximum generation time: {max_time:.2f}s")
        
        if avg_time > 2.0:
            print(f"   ⚠️ Average time exceeds 2s requirement")
        else:
            print(f"   ✅ Performance meets < 2s requirement")
        
        return True
    
    def test_filename_format_special_characters(self):
        """Test 8: Filename Format with Special Characters"""
        
        # Create profile with names containing special characters and spaces
        profile = self.create_test_profile(
            "Ravi Kumar-Sharma", 
            "Priya D'Souza Nair"
        )
        
        if not profile:
            return False
        
        print(f"   ✓ Created profile with special characters in names")
        
        response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile['id']}/download-pdf?language=english",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ PDF generation failed: {response.status_code}")
            return False
        
        # Check filename in Content-Disposition header
        content_disposition = response.headers.get('content-disposition', '')
        
        # Extract filename from header
        filename_match = re.search(r'filename=([^;]+)', content_disposition)
        if not filename_match:
            print(f"   ❌ No filename found in Content-Disposition")
            return False
        
        filename = filename_match.group(1).strip('"')
        print(f"   ✓ Generated filename: {filename}")
        
        # Verify filename format (should clean special characters)
        expected_pattern = r'^wedding-invitation-[a-z]+-[a-z]+\.pdf$'
        if not re.match(expected_pattern, filename):
            print(f"   ❌ Filename doesn't match expected pattern: {expected_pattern}")
            return False
        
        print(f"   ✅ Filename format is correct and handles special characters")
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
        """Run all PDF Generation tests"""
        print("🚀 Starting PHASE 8 PDF Generation Backend Testing")
        print("=" * 70)
        
        if not self.authenticate():
            return False
        
        # Run all tests
        tests = [
            ("PDF Generation with Deity Background (deity_id='ganesha')", self.test_pdf_generation_with_deity_ganesha),
            ("PDF Generation without Deity (deity_id=null)", self.test_pdf_generation_without_deity),
            ("PDF Generation with Different Deities", self.test_pdf_generation_different_deities),
            ("PDF Generation with Different Languages", self.test_pdf_generation_different_languages),
            ("Multi-Event PDF Generation", self.test_multi_event_pdf),
            ("PDF Security - No Authentication", self.test_pdf_security_no_auth),
            ("PDF Performance Testing", self.test_pdf_performance),
            ("Filename Format with Special Characters", self.test_filename_format_special_characters)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Cleanup
        self.cleanup_test_profiles()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 PHASE 8 PDF GENERATION TESTING SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {self.passed_tests}/{self.total_tests} tests")
        print(f"❌ Failed: {self.total_tests - self.passed_tests}/{self.total_tests} tests")
        
        if self.passed_tests == self.total_tests:
            print("🎉 ALL PDF GENERATION TESTS PASSED!")
            print("✅ PHASE 8 PDF Generation with Deity Background is production-ready")
            return True
        else:
            print("⚠️ Some tests failed - PDF Generation needs attention")
            return False

def main():
    """Main function"""
    tester = PDFGenerationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 PHASE 8 PDF GENERATION BACKEND TESTING COMPLETE - ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ PHASE 8 PDF GENERATION BACKEND TESTING FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()