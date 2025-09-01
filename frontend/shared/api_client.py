# frontend/shared/api_client.py

import requests
import base64
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class VoiceAPIClient:
    """Python API client for Voice App backend"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "VoiceApp-PythonClient/1.0",
            }
        )

    def health_check(self) -> Dict[str, Any]:
        """Check backend health status"""
        try:
            response = self.session.get(f"{self.base_url}/healthz")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "message": str(e)}

    def text_to_speech(
        self,
        text: str,
        speaker_id: str = "default",
        language: str = "zh",
        speed: float = 1.0,
    ) -> Dict[str, Any]:
        """Convert text to speech"""
        payload = {
            "text": text,
            "speaker_id": speaker_id,
            "language": language,
            "speed": speed,
        }

        try:
            response = self.session.post(f"{self.base_url}/api/v1/tts", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TTS request failed: {e}")
            return {"error": str(e)}

    def voice_conversion(
        self,
        audio_file: Union[str, Path, bytes],
        target_speaker: str,
        preserve_pitch: bool = True,
    ) -> Dict[str, Any]:
        """Convert voice to target speaker"""

        # Handle different input types
        if isinstance(audio_file, (str, Path)):
            with open(audio_file, "rb") as f:
                audio_data = f.read()
        else:
            audio_data = audio_file

        # Encode to base64
        audio_b64 = base64.b64encode(audio_data).decode("utf-8")

        payload = {
            "source_audio": audio_b64,
            "target_speaker": target_speaker,
            "preserve_pitch": preserve_pitch,
        }

        try:
            response = self.session.post(f"{self.base_url}/api/v1/vc", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"VC request failed: {e}")
            return {"error": str(e)}

    def get_profiles(self) -> Dict[str, Any]:
        """Get available speaker profiles"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/profiles")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Get profiles failed: {e}")
            return {"profiles": [], "error": str(e)}

    def batch_tts(self, texts: list, **kwargs) -> Dict[str, Any]:
        """Batch text-to-speech conversion"""
        payload = {"texts": texts, **kwargs}

        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/batch/tts", json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Batch TTS failed: {e}")
            return {"error": str(e)}

    def download_audio(self, audio_url: str, save_path: Union[str, Path]) -> bool:
        """Download audio file from backend"""
        try:
            full_url = (
                f"{self.base_url}{audio_url}"
                if audio_url.startswith("/")
                else audio_url
            )
            response = self.session.get(full_url)
            response.raise_for_status()

            with open(save_path, "wb") as f:
                f.write(response.content)
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Download failed: {e}")
            return False
