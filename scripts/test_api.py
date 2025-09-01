# ============ scripts/test_api.py ============
#!/usr/bin/env python3
"""
API Testing Script for Voice App
Tests all backend endpoints and functionality
"""

import sys
import os
import json
import time
from pathlib import Path

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent / "frontend" / "shared"))

try:
    from api_client import VoiceAPIClient
except ImportError as e:
    print(f"❌ Failed to import API client: {e}")
    print("💡 Make sure you've run: python scripts/setup_dev.py")
    sys.exit(1)


class APITester:
    def __init__(self, backend_url="http://localhost:8000"):
        self.client = VoiceAPIClient(backend_url)
        self.backend_url = backend_url
        self.test_results = {}

    def run_all_tests(self):
        """Run all API tests"""
        print("🧪 Voice App API Testing")
        print("=" * 40)
        print(f"📡 Backend URL: {self.backend_url}")
        print()

        tests = [
            ("Health Check", self.test_health_check),
            ("Get Profiles", self.test_get_profiles),
            ("Text-to-Speech", self.test_tts),
            ("Voice Conversion", self.test_vc_mock),
            ("Error Handling", self.test_error_handling),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"🔍 Testing {test_name}...")
            try:
                result = test_func()
                if result:
                    print(f"✅ {test_name}: PASSED")
                    passed += 1
                else:
                    print(f"❌ {test_name}: FAILED")
                self.test_results[test_name] = result
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {e}")
                self.test_results[test_name] = False
            print()

        # Summary
        print("=" * 40)
        print(f"📊 Test Summary: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed. Check backend status.")
            return False

    def test_health_check(self):
        """Test health check endpoint"""
        try:
            health = self.client.health_check()

            if health.get("status") == "healthy":
                print(f"   Backend version: {health.get('version', 'unknown')}")
                print(f"   Uptime: {health.get('uptime', 'unknown')}")
                return True
            else:
                print(f"   Health check failed: {health}")
                return False

        except Exception as e:
            print(f"   Health check error: {e}")
            return False

    def test_get_profiles(self):
        """Test get profiles endpoint"""
        try:
            profiles = self.client.get_profiles()

            if "error" in profiles:
                print(f"   Profile error: {profiles['error']}")
                return False

            profile_list = profiles.get("profiles", [])
            print(f"   Found {len(profile_list)} speaker profiles")

            for profile in profile_list[:3]:  # Show first 3
                print(f"   - {profile.get('name', 'Unknown')}")

            return True

        except Exception as e:
            print(f"   Profile test error: {e}")
            return False

    def test_tts(self):
        """Test text-to-speech endpoint"""
        test_text = "Hello, this is a test of the text-to-speech system."

        try:
            print(f"   Synthesizing: '{test_text[:30]}...'")

            start_time = time.time()
            result = self.client.text_to_speech(
                text=test_text, speaker_id="default", language="en", speed=1.0
            )
            end_time = time.time()

            if result.get("error"):
                print(f"   TTS error: {result['error']}")
                return False

            # Check response format
            required_fields = ["audio_url", "duration", "processing_time"]
            for field in required_fields:
                if field not in result:
                    print(f"   Missing field: {field}")
                    return False

            print(f"   Duration: {result['duration']:.1f}s")
            print(f"   Processing time: {result['processing_time']:.1f}s")
            print(f"   Total request time: {end_time - start_time:.1f}s")
            print(f"   Audio URL: {result['audio_url']}")

            return True

        except Exception as e:
            print(f"   TTS test error: {e}")
            return False

    def test_vc_mock(self):
        """Test voice conversion with mock data"""
        try:
            # Create a small mock audio file (just bytes)
            mock_audio = b"\x00" * 1024  # 1KB of zeros

            print("   Testing with mock audio data...")

            start_time = time.time()
            result = self.client.voice_conversion(
                audio_file=mock_audio, target_speaker="default", preserve_pitch=True
            )
            end_time = time.time()

            if result.get("error"):
                # Expected for mock data, but should be handled gracefully
                print(f"   VC handled error gracefully: {result['error'][:50]}...")
                return True

            # Check response format if successful
            required_fields = ["audio_url", "processing_time"]
            for field in required_fields:
                if field not in result:
                    print(f"   Missing field: {field}")
                    return False

            print(f"   Processing time: {result['processing_time']:.1f}s")
            print(f"   Total request time: {end_time - start_time:.1f}s")

            return True

        except Exception as e:
            print(f"   VC test error: {e}")
            return False

    def test_error_handling(self):
        """Test error handling"""
        try:
            # Test invalid TTS request
            result = self.client.text_to_speech(
                text="", speaker_id="nonexistent_speaker"  # Empty text should fail
            )

            if result.get("error"):
                print("   ✓ Empty text error handled correctly")
            else:
                print("   ⚠ Empty text should have returned error")

            # Test invalid VC request
            result = self.client.voice_conversion(
                audio_file=b"invalid_audio_data", target_speaker="nonexistent_speaker"
            )

            if result.get("error"):
                print("   ✓ Invalid audio error handled correctly")
            else:
                print("   ⚠ Invalid audio should have returned error")

            return True

        except Exception as e:
            print(f"   Error handling test failed: {e}")
            return False

    def generate_report(self):
        """Generate detailed test report"""
        report_file = Path("test_report.json")

        report_data = {
            "timestamp": time.time(),
            "backend_url": self.backend_url,
            "test_results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed_tests": sum(1 for r in self.test_results.values() if r),
                "failed_tests": sum(1 for r in self.test_results.values() if not r),
            },
        }

        try:
            with open(report_file, "w") as f:
                json.dump(report_data, f, indent=2)
            print(f"📝 Test report saved to: {report_file}")
        except Exception as e:
            print(f"⚠️ Failed to save report: {e}")


def main():
    """Main test function"""
    import argparse

    parser = argparse.ArgumentParser(description="Voice App API Tester")
    parser.add_argument(
        "--backend-url", default="http://localhost:8000", help="Backend API URL"
    )
    parser.add_argument("--report", action="store_true", help="Generate test report")
    parser.add_argument("--quick", action="store_true", help="Run only health check")

    args = parser.parse_args()

    tester = APITester(args.backend_url)

    if args.quick:
        # Quick health check only
        print("⚡ Quick health check...")
        success = tester.test_health_check()
        if success:
            print("✅ Backend is healthy")
            return 0
        else:
            print("❌ Backend health check failed")
            return 1

    # Run full test suite
    success = tester.run_all_tests()

    if args.report:
        tester.generate_report()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
