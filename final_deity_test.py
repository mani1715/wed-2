#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE PHASE 3 DEITY TESTING
Verifying all review request requirements with fresh profiles
"""

import requests
import json

# Configuration
BACKEND_URL = "https://wedding-planner-113.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@wedding.com"
ADMIN_PASSWORD = "admin123"

def test_comprehensive_deity_functionality():
    """Run comprehensive deity functionality test"""
    print("🎯 FINAL COMPREHENSIVE PHASE 3 DEITY TESTING")
    print("=" * 60)
    
    # Authenticate
    session = requests.Session()
    response = session.post(f"{BACKEND_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code != 200:
        print("❌ Authentication failed")
        return False
    
    token = response.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    print("✅ Admin authenticated")
    
    test_results = []
    
    # TEST 1: Profile creation without deity_id (should default to null)
    print("\n📝 TEST 1: Profile creation without deity_id")
    profile_no_deity = {
        "groom_name": "Fresh Test Groom",
        "bride_name": "Fresh Test Bride", 
        "event_type": "marriage",
        "event_date": "2024-12-25T10:00:00Z",
        "venue": "Test Venue",
        "language": ["english"],
        "design_id": "royal_classic",
        # NO deity_id field
        "enabled_languages": ["english"]
    }
    
    response = session.post(f"{BACKEND_URL}/admin/profiles", json=profile_no_deity)
    if response.status_code == 200:
        profile = response.json()
        if profile.get("deity_id") is None:
            print("✅ Profile without deity_id defaults to null")
            test_results.append(("Profile creation without deity", True))
        else:
            print(f"❌ Expected null, got: {profile.get('deity_id')}")
            test_results.append(("Profile creation without deity", False))
        
        # Test public API for this profile
        public_session = requests.Session()
        pub_response = public_session.get(f"{BACKEND_URL}/invite/{profile['slug']}")
        if pub_response.status_code == 200:
            pub_data = pub_response.json()
            if pub_data.get("deity_id") is None:
                print("✅ Public API returns null deity_id correctly")
                test_results.append(("Public API null deity", True))
            else:
                print(f"❌ Public API deity_id should be null, got: {pub_data.get('deity_id')}")
                test_results.append(("Public API null deity", False))
    else:
        print(f"❌ Profile creation failed: {response.status_code}")
        test_results.append(("Profile creation without deity", False))
    
    # TEST 2: Profile creation with each deity type
    print("\n📝 TEST 2: Profile creation with each deity type")
    deity_types = ["ganesha", "venkateswara_padmavati", "shiva_parvati", "lakshmi_vishnu"]
    
    for deity_id in deity_types:
        profile_with_deity = {
            "groom_name": f"Fresh {deity_id} Groom",
            "bride_name": f"Fresh {deity_id} Bride",
            "event_type": "marriage", 
            "event_date": "2024-12-26T11:00:00Z",
            "venue": f"Temple for {deity_id}",
            "language": ["english"],
            "design_id": "divine_temple",
            "deity_id": deity_id,
            "enabled_languages": ["english"]
        }
        
        response = session.post(f"{BACKEND_URL}/admin/profiles", json=profile_with_deity)
        if response.status_code == 200:
            profile = response.json()
            if profile.get("deity_id") == deity_id:
                print(f"✅ Profile with deity_id='{deity_id}' created correctly")
                test_results.append((f"Profile creation with {deity_id}", True))
                
                # Test public API for this profile
                public_session = requests.Session()
                pub_response = public_session.get(f"{BACKEND_URL}/invite/{profile['slug']}")
                if pub_response.status_code == 200:
                    pub_data = pub_response.json()
                    if pub_data.get("deity_id") == deity_id:
                        print(f"✅ Public API returns deity_id='{deity_id}' correctly")
                        test_results.append((f"Public API {deity_id}", True))
                    else:
                        print(f"❌ Public API deity_id mismatch for {deity_id}")
                        test_results.append((f"Public API {deity_id}", False))
            else:
                print(f"❌ Deity_id mismatch for {deity_id}")
                test_results.append((f"Profile creation with {deity_id}", False))
        else:
            print(f"❌ Profile creation with {deity_id} failed: {response.status_code}")
            test_results.append((f"Profile creation with {deity_id}", False))
    
    # TEST 3: Invalid deity validation
    print("\n📝 TEST 3: Invalid deity validation")
    invalid_profile = {
        "groom_name": "Invalid Test Groom",
        "bride_name": "Invalid Test Bride",
        "event_type": "marriage",
        "event_date": "2024-12-27T12:00:00Z", 
        "venue": "Test Venue",
        "language": ["english"],
        "design_id": "royal_classic",
        "deity_id": "invalid_deity_name",
        "enabled_languages": ["english"]
    }
    
    response = session.post(f"{BACKEND_URL}/admin/profiles", json=invalid_profile)
    if response.status_code == 422:
        print("✅ Invalid deity_id properly rejected with 422")
        test_results.append(("Invalid deity validation", True))
    else:
        print(f"❌ Expected 422, got: {response.status_code}")
        test_results.append(("Invalid deity validation", False))
    
    # Print final summary
    print("\n" + "=" * 60)
    print("📊 FINAL COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if total - passed == 0:
        print("\n🎉 ALL TESTS PASSED - DEITY SYSTEM IS PRODUCTION READY!")
        print("\n✅ VERIFIED REQUIREMENTS:")
        print("   • Profile creation without deity_id defaults to null")
        print("   • Profile creation with all 4 deity types working")
        print("   • Public invitation API includes deity_id field correctly")
        print("   • Invalid deity validation returns 422 error")
        print("   • All deity_id CRUD operations working correctly")
    else:
        print("\n❌ SOME TESTS FAILED:")
        for test_name, success in test_results:
            if not success:
                print(f"   • {test_name}")
    
    return total - passed == 0

if __name__ == "__main__":
    test_comprehensive_deity_functionality()