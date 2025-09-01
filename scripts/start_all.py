# ============ scripts/start_all.py ============
#!/usr/bin/env python3
"""
Start all frontends for Voice App
Launches React, Gradio, and PyQt applications
"""

import sys
import os
import subprocess
import time
import signal
import platform
from pathlib import Path
from typing import List, Dict


class ProcessManager:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.frontend_configs = {
            "react": {
                "name": "React Web App",
                "port": 3000,
                "path": "frontend/react_app",
                "command": ["npm", "start"],
                "url": "http://localhost:3000",
            },
            "gradio": {
                "name": "Gradio Interface",
                "port": 7860,
                "path": "frontend/gradio_app",
                "command": [sys.executable, "app.py", "--port", "7860"],
                "url": "http://localhost:7860",
            },
        }

    def check_dependencies(self) -> Dict[str, bool]:
        """Check if all required dependencies are available"""
        results = {}

        # Check Node.js for React
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
            subprocess.run(["npm", "--version"], capture_output=True, check=True)
            results["node"] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            results["node"] = False

        # Check Python modules for Gradio
        try:
            import gradio

            results["gradio"] = True
        except ImportError:
            results["gradio"] = False

        # Check PyQt6
        try:
            from PyQt6.QtWidgets import QApplication

            results["pyqt"] = True
        except ImportError:
            results["pyqt"] = False

        return results

    def install_react_deps(self):
        """Install React dependencies if needed"""
        react_path = Path("frontend/react_app")
        if not (react_path / "node_modules").exists():
            print("📦 Installing React dependencies...")
            try:
                subprocess.run(["npm", "install"], cwd=react_path, check=True)
                print("✅ React dependencies installed")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install React deps: {e}")
                return False
        return True

    def start_frontend(self, frontend_type: str) -> bool:
        """Start a specific frontend"""
        if frontend_type not in self.frontend_configs:
            print(f"❌ Unknown frontend type: {frontend_type}")
            return False

        config = self.frontend_configs[frontend_type]
        frontend_path = Path(config["path"])

        if not frontend_path.exists():
            print(f"❌ Frontend path not found: {frontend_path}")
            return False

        print(f"🚀 Starting {config['name']}...")

        try:
            # Special handling for React
            if frontend_type == "react":
                if not self.install_react_deps():
                    return False

            # Start process
            process = subprocess.Popen(
                config["command"],
                cwd=frontend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.processes.append(process)

            # Wait a moment and check if process is still running
            time.sleep(2)
            if process.poll() is None:
                print(f"✅ {config['name']} started successfully")
                print(f"🌐 Access at: {config['url']}")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ {config['name']} failed to start")
                if stderr:
                    print(f"Error: {stderr[:200]}...")
                return False

        except Exception as e:
            print(f"❌ Failed to start {config['name']}: {e}")
            return False

    def start_pyqt_app(self):
        """Start PyQt desktop application"""
        print("🖥️  Starting PyQt Desktop App...")

        try:
            # Import and run PyQt app directly
            sys.path.append(str(Path("frontend/pyqt_app")))
            from main import main as pyqt_main

            # Run in separate process to avoid blocking
            import threading

            def run_pyqt():
                try:
                    pyqt_main()
                except Exception as e:
                    print(f"PyQt Error: {e}")

            pyqt_thread = threading.Thread(target=run_pyqt, daemon=True)
            pyqt_thread.start()

            print("✅ PyQt Desktop App started")
            return True

        except Exception as e:
            print(f"❌ Failed to start PyQt app: {e}")
            return False

    def stop_all(self):
        """Stop all running processes"""
        print("\n🛑 Stopping all frontends...")

        for process in self.processes:
            try:
                if process.poll() is None:  # Still running
                    if platform.system() == "Windows":
                        process.terminate()
                    else:
                        process.send_signal(signal.SIGTERM)

                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()

            except Exception as e:
                print(f"Warning: Error stopping process: {e}")

        self.processes.clear()
        print("✅ All processes stopped")

    def show_status(self):
        """Show status of all frontends"""
        deps = self.check_dependencies()

        print("\n" + "=" * 50)
        print("🎙️  Voice App Frontend Status")
        print("=" * 50)

        print("\nDependency Status:")
        print(f"📦 Node.js/NPM:  {'✅ Available' if deps['node'] else '❌ Missing'}")
        print(f"🐍 Gradio:       {'✅ Available' if deps['gradio'] else '❌ Missing'}")
        print(f"🖥️  PyQt6:        {'✅ Available' if deps['pyqt'] else '❌ Missing'}")

        print(f"\nRunning Processes: {len(self.processes)}")
        print("\nFrontend URLs:")
        for config in self.frontend_configs.values():
            print(f"• {config['name']}: {config['url']}")

        print("\n" + "=" * 50)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Voice App Frontend Launcher")
    parser.add_argument(
        "--frontends",
        nargs="+",
        choices=["react", "gradio", "pyqt", "all"],
        default=["all"],
        help="Frontends to start (default: all)",
    )
    parser.add_argument("--status", action="store_true", help="Show status and exit")
    parser.add_argument(
        "--backend-check",
        action="store_true",
        help="Check backend health before starting",
    )

    args = parser.parse_args()

    manager = ProcessManager()

    if args.status:
        manager.show_status()
        return

    # Backend health check
    if args.backend_check:
        print("🔍 Checking backend health...")
        try:
            import sys

            sys.path.append(str(Path("frontend/shared")))
            from api_client import VoiceAPIClient

            client = VoiceAPIClient()
            health = client.health_check()

            if health.get("status") == "healthy":
                print("✅ Backend is healthy")
            else:
                print("⚠️  Backend health check failed")
                print("💡 Make sure backend is running: python backend/api/main.py")

        except Exception as e:
            print(f"❌ Backend check failed: {e}")
            print("💡 Make sure backend is running: python backend/api/main.py")

    # Determine which frontends to start
    frontends = args.frontends
    if "all" in frontends:
        frontends = ["react", "gradio", "pyqt"]

    print("🎙️  Voice App Frontend Launcher")
    print("=" * 40)

    manager.show_status()

    started_count = 0

    # Start specified frontends
    for frontend in frontends:
        if frontend == "pyqt":
            if manager.start_pyqt_app():
                started_count += 1
        elif frontend in ["react", "gradio"]:
            if manager.start_frontend(frontend):
                started_count += 1

    if started_count == 0:
        print("❌ No frontends started successfully")
        return 1

    print(f"\n✅ Started {started_count} frontend(s)")
    print("\n📖 Usage Instructions:")
    print("• React App: Modern web interface with drag & drop")
    print("• Gradio App: Research-friendly interface with instant preview")
    print("• PyQt App: Native desktop app with offline caching")
    print("\n🛑 Press Ctrl+C to stop all frontends")

    # Keep running until interrupted
    try:
        while True:
            time.sleep(1)
            # Check if processes are still alive
            alive_processes = [p for p in manager.processes if p.poll() is None]
            if len(alive_processes) == 0 and started_count > 0:
                print("\n⚠️  All processes have stopped")
                break

    except KeyboardInterrupt:
        pass
    finally:
        manager.stop_all()

    return 0


if __name__ == "__main__":
    sys.exit(main())
