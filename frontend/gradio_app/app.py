# ============ frontend/gradio_app/app.py ============
import gradio as gr
import sys
import os
from pathlib import Path

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent / "shared"))
from api_client import VoiceAPIClient

# Import components
from components.tts_interface import create_tts_interface
from components.vc_interface import create_vc_interface
from styles.theme import get_custom_theme


class VoiceAppGradio:
    def __init__(self, backend_url="http://localhost:8000"):
        self.client = VoiceAPIClient(backend_url)
        self.theme = get_custom_theme()

    def create_app(self):
        """Create the main Gradio application"""
        with gr.Blocks(
            theme=self.theme,
            title="Voice App - AI Speech Synthesis",
            css=self.load_custom_css(),
        ) as app:

            gr.Markdown(
                """
            # 🎙️ Voice App - AI Speech Lab

            **Professional Text-to-Speech & Voice Conversion Tool**

            Choose your operation:
            """
            )

            with gr.Tabs():
                with gr.TabItem("🎤 Text-to-Speech", id="tts_tab"):
                    create_tts_interface(self.client)

                with gr.TabItem("🎭 Voice Conversion", id="vc_tab"):
                    create_vc_interface(self.client)

                with gr.TabItem("ℹ️ System Info", id="info_tab"):
                    self.create_info_tab()

        return app

    def create_info_tab(self):
        """Create system information tab"""
        with gr.Column():
            gr.Markdown(
                """
            ## System Status
            """
            )

            status_btn = gr.Button("🔍 Check Backend Status", variant="secondary")
            status_output = gr.JSON(label="Backend Health")

            def check_status():
                return self.client.health_check()

            status_btn.click(check_status, outputs=status_output)

            gr.Markdown(
                """
            ## Usage Guidelines

            ### Text-to-Speech
            - Enter text in the input box (max 1000 characters)
            - Select speaker and language preferences
            - Adjust speed as needed (0.5x - 2.0x)
            - Click "Generate" to synthesize speech

            ### Voice Conversion
            - Upload source audio file (WAV, MP3, OGG, M4A, FLAC)
            - Select target speaker from available profiles
            - Toggle pitch preservation as needed
            - Click "Convert" to process

            ### Supported Formats
            - **Input:** WAV, MP3, OGG, M4A, FLAC (max 50MB)
            - **Output:** WAV (22kHz, 16-bit)

            ### Performance Notes
            - TTS processing: ~3-10 seconds per sentence
            - VC processing: ~5-15 seconds per audio file
            - GPU acceleration recommended for optimal performance
            """
            )

    def load_custom_css(self):
        """Load custom CSS for enhanced styling"""
        css_path = Path(__file__).parent / "styles" / "custom.css"
        if css_path.exists():
            return css_path.read_text()
        return ""


def main():
    """Main entry point for Gradio app"""
    import argparse

    parser = argparse.ArgumentParser(description="Voice App Gradio Interface")
    parser.add_argument(
        "--backend-url", default="http://localhost:8000", help="Backend API URL"
    )
    parser.add_argument("--port", type=int, default=7860, help="Gradio server port")
    parser.add_argument("--share", action="store_true", help="Create shareable link")

    args = parser.parse_args()

    # Create and launch app
    app_instance = VoiceAppGradio(args.backend_url)
    app = app_instance.create_app()

    print(f"🚀 Starting Gradio app on port {args.port}")
    print(f"📡 Backend URL: {args.backend_url}")

    app.launch(
        server_port=args.port, share=args.share, server_name="0.0.0.0", show_error=True
    )


if __name__ == "__main__":
    main()
