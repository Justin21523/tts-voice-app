# ============ frontend/gradio_app/components/tts_interface.py ============
import gradio as gr
import tempfile
import os
from pathlib import Path


def create_tts_interface(client):
    """Create TTS interface components"""
    with gr.Column():
        gr.Markdown("### Text Input")

        # Text input
        text_input = gr.Textbox(
            label="Text to Synthesize",
            placeholder="Enter your text here...",
            lines=6,
            max_lines=10,
            info="Maximum 1000 characters",
        )

        char_count = gr.Markdown("0/1000 characters")

        # Update character count
        def update_char_count(text):
            count = len(text) if text else 0
            return f"{count}/1000 characters"

        text_input.change(update_char_count, inputs=text_input, outputs=char_count)

        # Settings
        with gr.Row():
            speaker_dropdown = gr.Dropdown(
                label="Speaker",
                choices=[("Default", "default")],
                value="default",
                interactive=True,
            )

            language_dropdown = gr.Dropdown(
                label="Language",
                choices=[("Chinese", "zh"), ("English", "en"), ("Japanese", "ja")],
                value="zh",
            )

        speed_slider = gr.Slider(
            label="Speed",
            minimum=0.5,
            maximum=2.0,
            value=1.0,
            step=0.1,
            info="Speech speed multiplier",
        )

        # Generate button
        generate_btn = gr.Button("🎤 Generate Speech", variant="primary", size="lg")

        # Results section
        gr.Markdown("### Results")

        with gr.Column():
            result_info = gr.Markdown("Click 'Generate Speech' to synthesize audio")
            audio_output = gr.Audio(label="Generated Audio", type="filepath")
            download_btn = gr.File(label="Download Audio", visible=False)

        # Load speaker profiles on interface creation
        def load_speakers():
            try:
                result = client.get_profiles()
                if result.get("profiles"):
                    choices = [("Default", "default")]
                    choices.extend([(p["name"], p["id"]) for p in result["profiles"]])
                    return gr.Dropdown(choices=choices, value="default")
            except Exception as e:
                print(f"Failed to load speakers: {e}")
            return gr.Dropdown(choices=[("Default", "default")], value="default")

        # TTS generation function
        def generate_tts(text, speaker_id, language, speed):
            if not text.strip():
                return (
                    "❌ Please enter text to synthesize",
                    None,
                    gr.File(visible=False),
                )

            if len(text) > 1000:
                return (
                    "❌ Text too long (max 1000 characters)",
                    None,
                    gr.File(visible=False),
                )

            try:
                # Call TTS API
                result = client.text_to_speech(
                    text=text, speaker_id=speaker_id, language=language, speed=speed
                )

                if result.get("error"):
                    return f"❌ Error: {result['error']}", None, gr.File(visible=False)

                # Download audio file
                audio_url = result.get("audio_url")
                if not audio_url:
                    return "❌ No audio URL in response", None, gr.File(visible=False)

                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                temp_file.close()

                success = client.download_audio(audio_url, temp_file.name)
                if not success:
                    return "❌ Failed to download audio", None, gr.File(visible=False)

                # Format result info
                duration = result.get("duration", 0)
                processing_time = result.get("processing_time", 0)

                info_text = f"""✅ **Generation Successful**

**Statistics:**
- Duration: {duration:.1f}s
- Processing Time: {processing_time:.1f}s
- Speed: {speed}x
- Language: {language.upper()}
"""

                return (
                    info_text,
                    temp_file.name,
                    gr.File(value=temp_file.name, visible=True),
                )

            except Exception as e:
                return f"❌ Generation failed: {str(e)}", None, gr.File(visible=False)

        # Connect event handlers
        generate_btn.click(
            generate_tts,
            inputs=[text_input, speaker_dropdown, language_dropdown, speed_slider],
            outputs=[result_info, audio_output, download_btn],
        )
