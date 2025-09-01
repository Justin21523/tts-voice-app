# ============ frontend/gradio_app/components/vc_interface.py ============
import gradio as gr
import tempfile
import os


def create_vc_interface(client):
    """Create Voice Conversion interface components"""
    with gr.Column():
        gr.Markdown("### Audio Upload")

        # Audio input
        audio_input = gr.Audio(
            label="Source Audio",
            type="filepath",
            info="Upload WAV, MP3, OGG, M4A, or FLAC file (max 50MB)",
        )

        # Settings
        with gr.Row():
            target_speaker_dropdown = gr.Dropdown(
                label="Target Speaker",
                choices=[],
                value=None,
                info="Select the voice you want to convert to",
            )

        preserve_pitch_checkbox = gr.Checkbox(
            label="Preserve Pitch",
            value=True,
            info="Maintain original pitch characteristics",
        )

        # Convert button
        convert_btn = gr.Button("🎭 Convert Voice", variant="primary", size="lg")

        # Results section
        gr.Markdown("### Results")

        with gr.Column():
            result_info = gr.Markdown(
                "Upload audio and click 'Convert Voice' to process"
            )
            audio_output = gr.Audio(label="Converted Audio", type="filepath")
            download_btn = gr.File(label="Download Audio", visible=False)

        # Load speaker profiles
        def load_target_speakers():
            try:
                result = client.get_profiles()
                if result.get("profiles"):
                    choices = [(p["name"], p["id"]) for p in result["profiles"]]
                    return gr.Dropdown(
                        choices=choices, value=choices[0][1] if choices else None
                    )
            except Exception as e:
                print(f"Failed to load target speakers: {e}")
            return gr.Dropdown(choices=[], value=None)

        # Voice conversion function
        def convert_voice(audio_file, target_speaker, preserve_pitch):
            if not audio_file:
                return "❌ Please upload an audio file", None, gr.File(visible=False)

            if not target_speaker:
                return "❌ Please select a target speaker", None, gr.File(visible=False)

            try:
                # Call VC API
                result = client.voice_conversion(
                    audio_file=audio_file,
                    target_speaker=target_speaker,
                    preserve_pitch=preserve_pitch,
                )

                if result.get("error"):
                    return f"❌ Error: {result['error']}", None, gr.File(visible=False)

                # Download converted audio
                audio_url = result.get("audio_url")
                if not audio_url:
                    return "❌ No audio URL in response", None, gr.File(visible=False)

                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                temp_file.close()

                success = client.download_audio(audio_url, temp_file.name)
                if not success:
                    return (
                        "❌ Failed to download converted audio",
                        None,
                        gr.File(visible=False),
                    )

                # Format result info
                processing_time = result.get("processing_time", 0)

                info_text = f"""✅ **Conversion Successful**

**Statistics:**
- Processing Time: {processing_time:.1f}s
- Target Speaker: {target_speaker}
- Pitch Preservation: {"On" if preserve_pitch else "Off"}
"""

                return (
                    info_text,
                    temp_file.name,
                    gr.File(value=temp_file.name, visible=True),
                )

            except Exception as e:
                return f"❌ Conversion failed: {str(e)}", None, gr.File(visible=False)

        # Connect event handlers
        convert_btn.click(
            convert_voice,
            inputs=[audio_input, target_speaker_dropdown, preserve_pitch_checkbox],
            outputs=[result_info, audio_output, download_btn],
        )

        # Load speakers when interface is created
        target_speaker_dropdown.value = load_target_speakers().value
