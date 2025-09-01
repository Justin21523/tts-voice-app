# ============ scripts/download_models.py ============
#!/usr/bin/env python3
"""
Model Download and Setup Script for Voice App
Creates directories and provides download guidance
"""

import os
import sys
from pathlib import Path
import json


class ModelSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.load_config()

    def load_config(self):
        """Load configuration from .env file"""
        env_file = self.project_root / "backend" / ".env"
        self.cache_root = os.getenv(
            "AI_CACHE_ROOT", str(Path.home() / ".cache" / "voice-app")
        )

        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        key, _, value = line.partition("=")
                        if key.strip() == "AI_CACHE_ROOT":
                            self.cache_root = value.strip()
                            break

    def create_directories(self):
        """Create necessary model directories"""
        print("📁 Creating model directories...")

        directories = [
            f"{self.cache_root}/models/tts",
            f"{self.cache_root}/models/vc",
            f"{self.cache_root}/voice/speakers",
            f"{self.cache_root}/outputs/voice-app",
            f"{self.cache_root}/hf/transformers",
            f"{self.cache_root}/hf/datasets",
            f"{self.cache_root}/hf/hub",
            f"{self.cache_root}/torch",
        ]

        for directory in directories:
            path = Path(directory)
            path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {path}")

        print(f"\n✅ Model cache root: {self.cache_root}")

    def create_speaker_profiles(self):
        """Create example speaker profiles"""
        print("\n👤 Creating example speaker profiles...")

        speakers_dir = Path(f"{self.cache_root}/voice/speakers")

        example_profiles = [
            {
                "id": "default",
                "name": "Default Speaker",
                "description": "Default XTTS speaker",
                "language": "en",
                "gender": "neutral",
                "created_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": "female_en",
                "name": "English Female",
                "description": "Female English speaker",
                "language": "en",
                "gender": "female",
                "created_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": "male_zh",
                "name": "Chinese Male",
                "description": "Male Chinese speaker",
                "language": "zh",
                "gender": "male",
                "created_at": "2024-01-01T00:00:00Z",
            },
        ]

        for profile in example_profiles:
            profile_file = speakers_dir / f"{profile['id']}.json"
            if not profile_file.exists():
                with open(profile_file, "w") as f:
                    json.dump(profile, f, indent=2)
                print(f"  ✅ {profile['name']} ({profile['id']})")

    def show_download_instructions(self):
        """Show model download instructions"""
        print("\n" + "=" * 60)
        print("📥 Model Download Instructions")
        print("=" * 60)

        print("\n🎤 TTS Models (XTTS):")
        print("The TTS models will be automatically downloaded when first used.")
        print("XTTS uses Hugging Face models that download on-demand.")
        print(f"Cache location: {self.cache_root}/hf/")

        print("\n🎭 Voice Conversion Models (RVC):")
        print("RVC models need to be manually downloaded and placed in:")
        print(f"  {self.cache_root}/models/vc/")

        print("\nRecommended RVC models:")
        print(
            "• Download from: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI"
        )
        print("• Or use Hugging Face RVC model repositories")
        print("• Place .pth files in the vc directory")

        print("\n📋 Manual Setup Steps:")
        print("1. Download your preferred RVC models")
        print("2. Place them in the vc directory")
        print("3. Create speaker profiles in the speakers directory")
        print("4. Start the backend: python backend/api/main.py")
        print("5. Test with: python scripts/test_api.py")

        print(f"\n💾 All models will be cached in: {self.cache_root}")
        print("This keeps your project repo lightweight!")

    def check_models(self):
        """Check what models are available"""
        print("\n🔍 Checking available models...")

        # Check TTS models (HuggingFace cache)
        hf_cache = Path(f"{self.cache_root}/hf")
        if hf_cache.exists() and any(hf_cache.iterdir()):
            print("  ✅ HuggingFace cache directory exists")
            try:
                model_count = len(list(hf_cache.glob("**/*.bin"))) + len(
                    list(hf_cache.glob("**/*.safetensors"))
                )
                print(f"  📊 Found {model_count} cached model files")
            except:
                pass
        else:
            print("  📦 HuggingFace cache is empty (models will download on first use)")

        # Check VC models
        vc_dir = Path(f"{self.cache_root}/models/vc")
        vc_models = list(vc_dir.glob("*.pth")) + list(vc_dir.glob("*.ckpt"))
        if vc_models:
            print(f"  🎭 Found {len(vc_models)} VC model files:")
            for model in vc_models[:5]:  # Show first 5
                print(f"    - {model.name}")
        else:
            print("  📦 No VC models found (manual download required)")

        # Check speaker profiles
        speakers_dir = Path(f"{self.cache_root}/voice/speakers")
        profiles = list(speakers_dir.glob("*.json"))
        print(f"  👤 Found {len(profiles)} speaker profiles:")
        for profile in profiles:
            try:
                with open(profile, "r") as f:
                    data = json.load(f)
                    name = data.get("name", profile.stem)
                    lang = data.get("language", "unknown")
                    print(f"    - {name} ({lang})")
            except:
                print(f"    - {profile.stem} (invalid)")

    def cleanup_cache(self):
        """Clean up model cache"""
        print("\n🧹 Cache cleanup options:")
        print("1. Clear HuggingFace cache")
        print("2. Clear VC models")
        print("3. Clear speaker profiles")
        print("4. Clear all")
        print("5. Cancel")

        choice = input("\nSelect option (1-5): ").strip()

        if choice == "1":
            self._clear_directory(f"{self.cache_root}/hf", "HuggingFace cache")
        elif choice == "2":
            self._clear_directory(f"{self.cache_root}/models/vc", "VC models")
        elif choice == "3":
            self._clear_directory(
                f"{self.cache_root}/voice/speakers", "speaker profiles"
            )
        elif choice == "4":
            self._clear_directory(self.cache_root, "entire cache")
        elif choice == "5":
            print("Cleanup cancelled")
        else:
            print("Invalid choice")

    def _clear_directory(self, directory, name):
        """Clear a directory"""
        import shutil

        path = Path(directory)
        if path.exists():
            try:
                shutil.rmtree(path)
                path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Cleared {name}")
            except Exception as e:
                print(f"❌ Failed to clear {name}: {e}")
        else:
            print(f"📂 {name} directory doesn't exist")


def main():
    """Main setup function"""
    import argparse

    parser = argparse.ArgumentParser(description="Voice App Model Setup")
    parser.add_argument("--check", action="store_true", help="Check available models")
    parser.add_argument("--cleanup", action="store_true", help="Clean up model cache")
    parser.add_argument(
        "--setup",
        action="store_true",
        default=True,
        help="Setup directories and profiles (default)",
    )

    args = parser.parse_args()

    setup = ModelSetup()

    print("🎙️  Voice App Model Setup")
    print("=" * 30)

    if args.check:
        setup.check_models()
    elif args.cleanup:
        setup.cleanup_cache()
    else:
        # Default setup
        setup.create_directories()
        setup.create_speaker_profiles()
        setup.show_download_instructions()
        setup.check_models()

    return 0


if __name__ == "__main__":
    sys.exit(main())
