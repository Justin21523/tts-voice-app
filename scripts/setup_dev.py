# ============ scripts/setup_dev.py ============
#!/usr/bin/env python3
"""
Development environment setup script for Voice App
Installs all dependencies and sets up the development environment
"""

import sys
import os
import subprocess
import platform
from pathlib import Path


class DevSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.python_exe = sys.executable

    def check_system_requirements(self):
        """Check system requirements"""
        print("🔍 Checking system requirements...")

        requirements = {
            "python": self.check_python(),
            "node": self.check_node(),
            "ffmpeg": self.check_ffmpeg(),
        }

        for req, status in requirements.items():
            status_icon = "✅" if status else "❌"
            print(
                f"  {status_icon} {req.upper()}: {'Available' if status else 'Missing'}"
            )

        return all(requirements.values())

    def check_python(self):
        """Check Python version"""
        try:
            version = sys.version_info
            return version.major == 3 and version.minor >= 8
        except:
            return False

    def check_node(self):
        """Check Node.js availability"""
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True
            )
            version = result.stdout.strip().replace("v", "")
            major_version = int(version.split(".")[0])
            return major_version >= 14
        except:
            return False

    def check_ffmpeg(self):
        """Check FFmpeg availability"""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except:
            return False

    def install_python_deps(self):
        """Install Python dependencies"""
        print("\n📦 Installing Python dependencies...")

        # Backend dependencies
        backend_req = self.project_root / "backend" / "requirements.txt"
        if backend_req.exists():
            print("  Installing backend dependencies...")
            try:
                subprocess.run(
                    [self.python_exe, "-m", "pip", "install", "-r", str(backend_req)],
                    check=True,
                )
                print("  ✅ Backend dependencies installed")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Failed to install backend deps: {e}")
                return False

        # Gradio dependencies
        gradio_req = self.project_root / "frontend" / "gradio_app" / "requirements.txt"
        if gradio_req.exists():
            print("  Installing Gradio dependencies...")
            try:
                subprocess.run(
                    [self.python_exe, "-m", "pip", "install", "-r", str(gradio_req)],
                    check=True,
                )
                print("  ✅ Gradio dependencies installed")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Failed to install Gradio deps: {e}")
                return False

        # PyQt dependencies
        pyqt_req = self.project_root / "frontend" / "pyqt_app" / "requirements.txt"
        if pyqt_req.exists():
            print("  Installing PyQt dependencies...")
            try:
                subprocess.run(
                    [self.python_exe, "-m", "pip", "install", "-r", str(pyqt_req)],
                    check=True,
                )
                print("  ✅ PyQt dependencies installed")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Failed to install PyQt deps: {e}")
                return False

        return True

    def install_react_deps(self):
        """Install React dependencies"""
        print("\n🌐 Installing React dependencies...")

        react_path = self.project_root / "frontend" / "react_app"
        if not react_path.exists():
            print("  ❌ React app directory not found")
            return False

        try:
            subprocess.run(["npm", "install"], cwd=react_path, check=True)
            print("  ✅ React dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install React deps: {e}")
            return False

    def create_directories(self):
        """Create necessary directories"""
        print("\n📁 Creating directories...")

        directories = ["data/speakers", "data/outputs", "data/cache", "logs"]

        for dir_path in directories:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {dir_path}")

    def setup_env_file(self):
        """Setup environment file"""
        print("\n⚙️  Setting up environment...")

        env_example = self.project_root / "backend" / ".env.example"
        env_file = self.project_root / "backend" / ".env"

        if env_example.exists() and not env_file.exists():
            try:
                import shutil

                shutil.copy2(env_example, env_file)
                print("  ✅ .env file created from template")

                # Update cache path for current system
                if platform.system() == "Windows":
                    cache_path = str(
                        Path.home() / "AppData" / "Local" / "VoiceApp" / "cache"
                    )
                else:
                    cache_path = str(Path.home() / ".cache" / "voice-app")

                # Update .env file
                env_content = env_file.read_text()
                env_content = env_content.replace(
                    "AI_CACHE_ROOT=/mnt/ai_warehouse/cache",
                    f"AI_CACHE_ROOT={cache_path}",
                )
                env_file.write_text(env_content)
                print(f"  ✅ Cache path set to: {cache_path}")

            except Exception as e:
                print(f"  ❌ Failed to setup .env: {e}")
                return False

        return True

    def run_tests(self):
        """Run basic tests"""
        print("\n🧪 Running basic tests...")

        try:
            # Test API client import
            sys.path.append(str(self.project_root / "frontend" / "shared"))
            from api_client import VoiceAPIClient

            client = VoiceAPIClient()
            print("  ✅ API client import successful")

            # Test basic functionality
            health = client.health_check()
            if "error" in health:
                print("  ⚠️  Backend not running (this is OK for setup)")
            else:
                print("  ✅ Backend health check successful")

            return True

        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            return False

    def show_next_steps(self):
        """Show next steps after setup"""
        print("\n" + "=" * 50)
        print("🎉 Development environment setup complete!")
        print("=" * 50)

        print("\n📋 Next Steps:")
        print("1. Start the backend:")
        print("   cd backend && python -m api.main")

        print("\n2. Start frontends:")
        print("   python scripts/start_all.py")

        print("\n3. Or start individual frontends:")
        print("   • React:  cd frontend/react_app && npm start")
        print("   • Gradio: cd frontend/gradio_app && python app.py")
        print("   • PyQt:   cd frontend/pyqt_app && python main.py")

        print("\n4. Access the applications:")
        print("   • React App: http://localhost:3000")
        print("   • Gradio App: http://localhost:7860")
        print("   • PyQt App: Desktop application window")

        print("\n🔧 Troubleshooting:")
        print("   • Check logs in the 'logs' directory")
        print("   • Ensure backend is running before starting frontends")
        print("   • Run 'python scripts/test_api.py' to test API connectivity")

        print("\n📚 Documentation:")
        print("   • API docs: docs/API.md")
        print("   • Setup guide: docs/SETUP.md")
        print("   • Development guide: docs/DEVELOPMENT.md")


def main():
    """Main setup function"""
    print("🎙️  Voice App Development Setup")
    print("=" * 40)

    setup = DevSetup()

    # Check system requirements
    if not setup.check_system_requirements():
        print("\n❌ System requirements not met")
        print("📖 Please install missing requirements:")
        print("   • Python 3.8+")
        print("   • Node.js 14+")
        print("   • FFmpeg")
        return 1

    print("✅ System requirements satisfied")

    # Run setup steps
    steps = [
        ("Creating directories", setup.create_directories),
        ("Installing Python dependencies", setup.install_python_deps),
        ("Installing React dependencies", setup.install_react_deps),
        ("Setting up environment", setup.setup_env_file),
        ("Running tests", setup.run_tests),
    ]

    for step_name, step_func in steps:
        print(f"\n⚙️  {step_name}...")
        if not step_func():
            print(f"❌ {step_name} failed")
            return 1
        print(f"✅ {step_name} completed")

    setup.show_next_steps()
    return 0


if __name__ == "__main__":
    main()
