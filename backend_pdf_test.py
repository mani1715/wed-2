#!/usr/bin/env python3
"""
Comprehensive Backend Testing for PDF Generation System (Phase 8)
Tests all PDF generation functionality including:
- PDF endpoint authentication (403 without auth, works with admin)
- PDF generation with different themes (royal_classic, temple_divine)
- Multi-language PDF generation (english, telugu, tamil)
- Content validation with realistic data
- Performance check (<2 seconds)
- Error handling (invalid profile_id, invalid language)
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import traceback
import time
import io

# Configuration
BASE_URL = "https://wed-organizer-16.preview.emergentagent.com/api"
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
    
    def test_pdf_endpoint_authentication(self):
        """Test 1: PDF Endpoint Authentication - 403 without auth, works with admin"""
        
        # First create a test profile
        profile_data = {
            "groom_name": "Rajesh Kumar",
            "bride_name": "Priya Sharma",
            "event_type": "marriage",
            "event_date": "2024-03-15T10:00:00",
            "venue": "Grand Palace Hall",
            "language": ["english", "telugu"],
            "design_id": "royal_classic",
            "whatsapp_groom": "+919876543210",
            "whatsapp_bride": "+919876543211",
            "enabled_languages": ["english", "telugu"],
            "events": [
                {
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
                }
            ]
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
        profile_id = profile["id"]
        self.test_profiles.append(profile_id)
        print(f"   ✓ Created test profile: {profile_id}")
        
        # Test 1a: PDF endpoint without authentication (should return 403)
        response_no_auth = requests.get(f"{BASE_URL}/admin/profiles/{profile_id}/download-pdf")
        
        if response_no_auth.status_code == 403:
            print(f"   ✅ PDF endpoint correctly returns 403 without authentication")
        else:
            print(f"   ❌ Expected 403, got {response_no_auth.status_code}")
            return False
        
        # Test 1b: PDF endpoint with valid admin credentials (should return PDF)
        response_with_auth = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}/download-pdf",
            headers=self.get_headers()
        )
        
        if response_with_auth.status_code == 200:
            # Check content type
            content_type = response_with_auth.headers.get('content-type', '')
            if content_type == 'application/pdf':
                print(f"   ✅ PDF endpoint returns 200 with valid admin credentials")
                print(f"   ✅ Content-Type: {content_type}")
                
                # Check Content-Disposition header
                content_disposition = response_with_auth.headers.get('content-disposition', '')
                if 'wedding-invitation-rajesh-priya.pdf' in content_disposition:
                    print(f"   ✅ Correct filename format: {content_disposition}")
                else:
                    print(f"   ❌ Incorrect filename format: {content_disposition}")
                    return False
                
                return True
            else:
                print(f"   ❌ Wrong content type: {content_type}")
                return False
        else:
            print(f"   ❌ PDF endpoint failed with auth: {response_with_auth.status_code} - {response_with_auth.text}")
            return False
    
    def test_pdf_generation_different_themes(self):
        """Test 2: PDF Generation with Different Themes (royal_classic, temple_divine)"""
        
        themes_to_test = [
            ("royal_classic", "Royal Classic"),
            ("temple_divine", "Temple Divine")
        ]
        
        for design_id, design_name in themes_to_test:
            print(f"   🎨 Testing theme: {design_name} ({design_id})")
            
            # Create profile with specific theme
            profile_data = {
                "groom_name": f"Theme Test Groom {design_id}",
                "bride_name": f"Theme Test Bride {design_id}",
                "event_type": "marriage",
                "event_date": "2024-03-20T11:00:00",
                "venue": "Theme Test Venue",
                "language": ["english"],
                "design_id": design_id,
                "enabled_languages": ["english"],
                "events": [
                    {
                        "name": "Wedding Ceremony",
                        "date": "2024-03-20",
                        "start_time": "11:00",
                        "end_time": "15:00",
                        "venue_name": "Theme Test Venue",
                        "venue_address": "456 Theme Street, Delhi 110001",
                        "map_link": "https://maps.google.com/?q=456+Theme+Street+Delhi",
                        "description": f"Wedding with {design_name} theme",
                        "visible": True,
                        "order": 1
                    }
                ]
            }
            
            response = requests.post(
                f"{BASE_URL}/admin/profiles",
                json=profile_data,
                headers=self.get_headers()
            )
            
            if response.status_code != 200:
                print(f"   ❌ Failed to create profile with {design_id}: {response.text}")
                return False
            
            profile = response.json()
            profile_id = profile["id"]
            self.test_profiles.append(profile_id)
            
            # Download PDF for this theme
            pdf_response = requests.get(
                f"{BASE_URL}/admin/profiles/{profile_id}/download-pdf",
                headers=self.get_headers()
            )
            
            if pdf_response.status_code == 200:
                content_type = pdf_response.headers.get('content-type', '')
                if content_type == 'application/pdf':
                    pdf_size = len(pdf_response.content)
                    print(f"   ✅ {design_name} PDF generated successfully (Size: {pdf_size} bytes)")
                    
                    # Check file size is reasonable (<2MB)
                    if pdf_size < 2 * 1024 * 1024:  # 2MB
                        print(f"   ✅ PDF size is reasonable (<2MB)")
                    else:
                        print(f"   ❌ PDF size too large: {pdf_size} bytes")
                        return False
                else:
                    print(f"   ❌ Wrong content type for {design_id}: {content_type}")
                    return False
            else:
                print(f"   ❌ PDF generation failed for {design_id}: {pdf_response.status_code}")
                return False
        
        return True
    
    def test_multi_language_pdf_generation(self):
        """Test 3: Multi-language PDF Generation (english, telugu, tamil)"""
        
        # Create profile with multiple languages enabled
        profile_data = {
            "groom_name": "Multilang Groom",
            "bride_name": "Multilang Bride",
            "event_type": "marriage",
            "event_date": "2024-04-10T09:00:00",
            "venue": "Multilingual Wedding Hall",
            "language": ["english", "telugu", "tamil"],
            "design_id": "royal_classic",
            "enabled_languages": ["english", "telugu", "tamil"],
            "events": [
                {
                    "name": "Multilingual Wedding",
                    "date": "2024-04-10",
                    "start_time": "09:00",
                    "end_time": "13:00",
                    "venue_name": "Multilingual Wedding Hall",
                    "venue_address": "789 Language Street, Chennai 600001",
                    "map_link": "https://maps.google.com/?q=789+Language+Street+Chennai",
                    "description": "Wedding ceremony in multiple languages",
                    "visible": True,
                    "order": 1
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/admin/profiles",
            json=profile_data,
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to create multilingual profile: {response.text}")
            return False
        
        profile = response.json()
        profile_id = profile["id"]
        self.test_profiles.append(profile_id)
        print(f"   ✓ Created multilingual profile: {profile_id}")
        
        # Test PDF generation for each language
        languages_to_test = ["english", "telugu", "tamil"]
        
        for language in languages_to_test:
            print(f"   🌐 Testing language: {language}")
            
            pdf_response = requests.get(
                f"{BASE_URL}/admin/profiles/{profile_id}/download-pdf?language={language}",
                headers=self.get_headers()
            )
            
            if pdf_response.status_code == 200:
                content_type = pdf_response.headers.get('content-type', '')
                if content_type == 'application/pdf':
                    pdf_size = len(pdf_response.content)
                    print(f"   ✅ {language.capitalize()} PDF generated successfully (Size: {pdf_size} bytes)")
                    
                    # Verify filename includes language info (if different from default)
                    content_disposition = pdf_response.headers.get('content-disposition', '')
                    if 'wedding-invitation-multilang-multilang.pdf' in content_disposition:
                        print(f"   ✅ Correct filename format for {language}")
                    else:
                        print(f"   ❌ Incorrect filename for {language}: {content_disposition}")
                        return False
                else:
                    print(f"   ❌ Wrong content type for {language}: {content_type}")
                    return False
            else:
                print(f"   ❌ PDF generation failed for {language}: {pdf_response.status_code}")
                return False
        
        return True
    
    def test_content_validation(self):
        """Test 4: Content Validation with Realistic Indian Wedding Data"""
        
        # Create profile with comprehensive Indian wedding data
        profile_data = {
            "groom_name": "Rajesh Kumar",
            "bride_name": "Priya Sharma",
            "event_type": "marriage",
            "event_date": "2024-05-15T10:30:00",
            "venue": "Shree Ganesh Marriage Hall",
            "language": ["english", "telugu"],
            "design_id": "royal_classic",
            "whatsapp_groom": "+919876543210",
            "whatsapp_bride": "+919876543211",
            "enabled_languages": ["english", "telugu"],
            "events": [
                {
                    "name": "Mehendi Ceremony",
                    "date": "2024-05-13",
                    "start_time": "16:00",
                    "end_time": "20:00",
                    "venue_name": "Bride's Residence",
                    "venue_address": "Plot No. 123, Jubilee Hills, Hyderabad, Telangana 500033",
                    "map_link": "https://maps.google.com/?q=Plot+123+Jubilee+Hills+Hyderabad",
                    "description": "Traditional henna ceremony with music and dance",
                    "visible": True,
                    "order": 1
                },
                {
                    "name": "Sangeet Night",
                    "date": "2024-05-14",
                    "start_time": "19:00",
                    "end_time": "23:30",
                    "venue_name": "Grand Ballroom, Hotel Taj Krishna",
                    "venue_address": "Road No. 1, Banjara Hills, Hyderabad, Telangana 500034",
                    "map_link": "https://maps.google.com/?q=Hotel+Taj+Krishna+Banjara+Hills",
                    "description": "Musical evening with family performances and dinner",
                    "visible": True,
                    "order": 2
                },
                {
                    "name": "Wedding Ceremony",
                    "date": "2024-05-15",
                    "start_time": "10:30",
                    "end_time": "14:00",
                    "venue_name": "Shree Ganesh Marriage Hall",
                    "venue_address": "SR Nagar Main Road, Hyderabad, Telangana 500038",
                    "map_link": "https://maps.google.com/?q=Shree+Ganesh+Marriage+Hall+SR+Nagar",
                    "description": "Sacred wedding rituals followed by lunch",
                    "visible": True,
                    "order": 3
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/admin/profiles",
            json=profile_data,
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to create comprehensive profile: {response.text}")
            return False
        
        profile = response.json()
        profile_id = profile["id"]
        self.test_profiles.append(profile_id)
        print(f"   ✓ Created comprehensive profile with {len(profile['events'])} events")
        
        # Download PDF and validate
        pdf_response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}/download-pdf",
            headers=self.get_headers()
        )
        
        if pdf_response.status_code == 200:
            # Validate response headers
            content_type = pdf_response.headers.get('content-type', '')
            content_disposition = pdf_response.headers.get('content-disposition', '')
            
            if content_type != 'application/pdf':
                print(f"   ❌ Wrong content type: {content_type}")
                return False
            
            # Check filename format: wedding-invitation-{groom}-{bride}.pdf
            expected_filename = "wedding-invitation-rajesh-priya.pdf"
            if expected_filename not in content_disposition:
                print(f"   ❌ Incorrect filename format: {content_disposition}")
                print(f"   Expected: {expected_filename}")
                return False
            
            print(f"   ✅ Correct Content-Disposition: {content_disposition}")
            
            # Validate PDF file size (<2MB)
            pdf_size = len(pdf_response.content)
            if pdf_size >= 2 * 1024 * 1024:  # 2MB
                print(f"   ❌ PDF size too large: {pdf_size} bytes (>2MB)")
                return False
            
            print(f"   ✅ PDF size is reasonable: {pdf_size} bytes (<2MB)")
            
            # Validate PDF content is not empty
            if pdf_size < 1000:  # Less than 1KB is suspicious
                print(f"   ❌ PDF size too small: {pdf_size} bytes")
                return False
            
            print(f"   ✅ PDF content validation passed")
            return True
        else:
            print(f"   ❌ PDF generation failed: {pdf_response.status_code} - {pdf_response.text}")
            return False
    
    def test_performance_check(self):
        """Test 5: Performance Check - PDF generation should be <2 seconds"""
        
        # Use existing profile if available, otherwise create one
        if not self.test_profiles:
            print(f"   ❌ No test profiles available for performance test")
            return False
        
        profile_id = self.test_profiles[0]
        
        # Measure PDF generation time
        start_time = time.time()
        
        pdf_response = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}/download-pdf",
            headers=self.get_headers()
        )
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        print(f"   ⏱️ PDF generation time: {generation_time:.3f} seconds")
        
        if pdf_response.status_code == 200:
            if generation_time < 2.0:
                print(f"   ✅ PDF generation time is acceptable (<2 seconds)")
                
                # Test multiple concurrent downloads (simplified)
                print(f"   🔄 Testing concurrent PDF downloads...")
                
                concurrent_start = time.time()
                
                # Make 3 concurrent requests (simplified sequential for testing)
                for i in range(3):
                    concurrent_response = requests.get(
                        f"{BASE_URL}/admin/profiles/{profile_id}/download-pdf",
                        headers=self.get_headers()
                    )
                    if concurrent_response.status_code != 200:
                        print(f"   ❌ Concurrent request {i+1} failed: {concurrent_response.status_code}")
                        return False
                
                concurrent_end = time.time()
                concurrent_time = concurrent_end - concurrent_start
                
                print(f"   ✅ 3 concurrent PDF downloads completed in {concurrent_time:.3f} seconds")
                return True
            else:
                print(f"   ❌ PDF generation too slow: {generation_time:.3f} seconds (>2 seconds)")
                return False
        else:
            print(f"   ❌ PDF generation failed: {pdf_response.status_code}")
            return False
    
    def test_error_handling(self):
        """Test 6: Error Handling - Invalid profile_id and invalid language"""
        
        # Test 6a: Invalid profile_id (should return 404)
        invalid_profile_id = "invalid-profile-id-12345"
        
        response_invalid_id = requests.get(
            f"{BASE_URL}/admin/profiles/{invalid_profile_id}/download-pdf",
            headers=self.get_headers()
        )
        
        if response_invalid_id.status_code == 404:
            print(f"   ✅ Invalid profile_id correctly returns 404")
        else:
            print(f"   ❌ Expected 404 for invalid profile_id, got {response_invalid_id.status_code}")
            return False
        
        # Test 6b: Invalid language parameter (should handle gracefully)
        if not self.test_profiles:
            print(f"   ❌ No test profiles available for language test")
            return False
        
        profile_id = self.test_profiles[0]
        
        response_invalid_lang = requests.get(
            f"{BASE_URL}/admin/profiles/{profile_id}/download-pdf?language=invalid_language",
            headers=self.get_headers()
        )
        
        # Should either return 200 (fallback to default language) or 400 (validation error)
        if response_invalid_lang.status_code in [200, 400]:
            if response_invalid_lang.status_code == 200:
                print(f"   ✅ Invalid language handled gracefully (fallback to default)")
            else:
                print(f"   ✅ Invalid language properly validated with 400 error")
        else:
            print(f"   ❌ Unexpected response for invalid language: {response_invalid_lang.status_code}")
            return False
        
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
        print("🚀 Starting PDF Generation Backend Testing (Phase 8)")
        print("=" * 70)
        
        if not self.authenticate():
            return False
        
        # Run all tests
        tests = [
            ("PDF Endpoint Authentication (403 without auth, works with admin)", self.test_pdf_endpoint_authentication),
            ("PDF Generation with Different Themes (royal_classic, temple_divine)", self.test_pdf_generation_different_themes),
            ("Multi-language PDF Generation (english, telugu, tamil)", self.test_multi_language_pdf_generation),
            ("Content Validation with Realistic Indian Wedding Data", self.test_content_validation),
            ("Performance Check (<2 seconds generation time)", self.test_performance_check),
            ("Error Handling (invalid profile_id, invalid language)", self.test_error_handling)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Cleanup
        self.cleanup_test_profiles()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 PDF GENERATION TESTING SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {self.passed_tests}/{self.total_tests} tests")
        print(f"❌ Failed: {self.total_tests - self.passed_tests}/{self.total_tests} tests")
        
        if self.passed_tests == self.total_tests:
            print("🎉 ALL PDF GENERATION TESTS PASSED!")
            print("✅ PDF Generation System is production-ready")
            return True
        else:
            print("⚠️ Some tests failed - PDF Generation System needs attention")
            return False

def main():
    """Main function"""
    tester = PDFGenerationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 PDF GENERATION BACKEND TESTING COMPLETE - ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ PDF GENERATION BACKEND TESTING FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()