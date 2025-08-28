# backend/services/tts_service.py

"""
文字轉語音 (TTS) 服務
"""
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

import numpy as np
import torch
import librosa
import soundfile as sf

from backend.core.config import Settings
from backend.core.audio.normalization import quick_normalize
from backend.core.audio.io import trim_silence


class TTSService:
    """TTS 服務封裝"""

    def __init__(self, model: Dict[str, Any], settings: Settings):
        """
        初始化 TTS 服務

        Args:
            model: 載入的 TTS 模型
            settings: 應用設定
        """
        self.model = model
        self.settings = settings
        self.engine_type = model.get("type", "unknown")

        print(f"🎤 TTS 服務初始化: {self.engine_type}")

    async def synthesize(
        self,
        text: str,
        speaker_id: str = "default",
        language: str = "zh",
        speed: float = 1.0,
        emotion: str = "neutral",
        output_path: str = None,
    ) -> Dict[str, Any]:
        """
        執行文字轉語音

        Args:
            text: 要合成的文字
            speaker_id: 說話者 ID
            language: 語言代碼
            speed: 語速倍率
            emotion: 情感風格
            output_path: 輸出檔案路徑

        Returns:
            合成結果資訊
        """
        start_time = time.time()

        try:
            print(f"🎯 TTS 合成開始: {self.engine_type}")
            print(f"   文字: {text[:50]}{'...' if len(text) > 50 else ''}")
            print(f"   說話者: {speaker_id}")
            print(f"   語言: {language}, 語速: {speed}x")

            # 根據引擎類型執行合成
            if self.engine_type == "xtts":
                audio_data, sample_rate = await self._synthesize_xtts(
                    text, speaker_id, language, speed, emotion
                )
            elif self.engine_type == "openvoice":
                audio_data, sample_rate = await self._synthesize_openvoice(
                    text, speaker_id, language, speed, emotion
                )
            elif self.engine_type == "bark":
                audio_data, sample_rate = await self._synthesize_bark(
                    text, speaker_id, language, speed, emotion
                )
            else:
                raise ValueError(f"不支援的 TTS 引擎: {self.engine_type}")

            # 後處理
            audio_data = await self._post_process_audio(audio_data, sample_rate)

            # 儲存音檔
            if output_path:
                sf.write(output_path, audio_data, sample_rate, format="WAV")
                print(f"💾 音檔已儲存: {output_path}")

            processing_time = time.time() - start_time
            duration = len(audio_data) / sample_rate

            print(f"✅ TTS 合成完成: {duration:.2f}s 音檔，耗時 {processing_time:.2f}s")

            return {
                "duration": duration,
                "sample_rate": sample_rate,
                "processing_time": processing_time,
                "engine": self.engine_type,
                "text_length": len(text),
            }

        except Exception as e:
            processing_time = time.time() - start_time
            print(f"❌ TTS 合成失敗: {e} (耗時 {processing_time:.2f}s)")
            raise

    async def _synthesize_xtts(
        self, text: str, speaker_id: str, language: str, speed: float, emotion: str
    ) -> tuple:
        """XTTS 引擎合成 (實作佔位符)"""
        # 這裡應該實作實際的 XTTS 呼叫
        # 暫時產生模擬音訊

        await asyncio.sleep(0.1)  # 模擬處理時間

        # 產生模擬音訊 (440Hz 正弦波，持續時間依文字長度)
        duration = max(1.0, len(text) * 0.05)  # 文字長度影響音檔長度
        sample_rate = self.settings.SAMPLE_RATE

        t = np.linspace(0, duration, int(sample_rate * duration), False)
        frequency = 440.0  # A4 音符

        # 根據語速調整
        frequency = frequency * (1.1 if speed > 1.0 else 0.9 if speed < 1.0 else 1.0)

        # 產生正弦波 + 少量噪音
        audio_data = 0.3 * np.sin(frequency * 2 * np.pi * t)
        audio_data += 0.05 * np.random.normal(0, 1, len(audio_data))  # 加入噪音

        # 添加包絡線使聲音更自然
        envelope = np.ones_like(audio_data)
        fade_samples = int(sample_rate * 0.05)  # 50ms fade
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        audio_data *= envelope

        print(f"🔊 XTTS 模擬合成: {duration:.2f}s, {sample_rate}Hz")

        return audio_data, sample_rate

    async def _synthesize_openvoice(
        self, text: str, speaker_id: str, language: str, speed: float, emotion: str
    ) -> tuple:
        """OpenVoice 引擎合成 (實作佔位符)"""
        await asyncio.sleep(0.1)

        # OpenVoice 模擬實作
        duration = max(1.0, len(text) * 0.06)
        sample_rate = self.settings.SAMPLE_RATE

        t = np.linspace(0, duration, int(sample_rate * duration), False)

        # 產生更複雜的合成音 (多個頻率組合)
        frequencies = [220, 440, 880]  # 基頻和諧波
        audio_data = np.zeros(len(t))

        for i, freq in enumerate(frequencies):
            amplitude = 0.2 / (i + 1)  # 諧波衰減
            audio_data += amplitude * np.sin(freq * speed * 2 * np.pi * t)

        # 添加包絡線和少量噪音
        envelope = 1 - 0.3 * np.random.random(len(audio_data))
        audio_data *= envelope
        audio_data += 0.02 * np.random.normal(0, 1, len(audio_data))

        print(f"🔊 OpenVoice 模擬合成: {duration:.2f}s")

        return audio_data, sample_rate

    async def _synthesize_bark(
        self, text: str, speaker_id: str, language: str, speed: float, emotion: str
    ) -> tuple:
        """Bark 引擎合成 (實作佔位符)"""
        await asyncio.sleep(0.2)

        # Bark 模擬實作 (更有創意的合成)
        duration = max(1.5, len(text) * 0.08)
        sample_rate = self.settings.SAMPLE_RATE

        t = np.linspace(0, duration, int(sample_rate * duration), False)

        # 產生類似語音的頻譜
        formants = [800, 1200, 2400]  # 語音共振峰
        audio_data = np.zeros(len(t))

        for formant in formants:
            # 隨機調製頻率
            modulation = 1 + 0.1 * np.sin(5 * 2 * np.pi * t)
            freq = formant * speed * modulation

            amplitude = 0.15 * np.random.random()
            audio_data += amplitude * np.sin(freq * 2 * np.pi * t)

        # 添加語音特有的時變包絡
        segments = int(duration * 3)  # 每秒 3 個音段
        for i in range(segments):
            start_idx = int(i * len(audio_data) / segments)
            end_idx = int((i + 1) * len(audio_data) / segments)

            segment_envelope = np.random.random() * 0.8 + 0.2
            audio_data[start_idx:end_idx] *= segment_envelope

        print(f"🔊 Bark 模擬合成: {duration:.2f}s (創意模式)")

        return audio_data, sample_rate

    async def _post_process_audio(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> np.ndarray:
        """音訊後處理"""
        try:
            # 去除前後靜音
            audio_data = trim_silence(audio_data, sample_rate, top_db=25)

            # LUFS 正規化
            audio_data = quick_normalize(
                audio_data, self.settings.TARGET_LUFS, sample_rate
            )

            # 限制峰值避免削波
            peak = np.max(np.abs(audio_data))
            if peak > 0.95:
                audio_data = audio_data / peak * 0.95

            print(
                f"🎚️ 後處理完成: 峰值 {peak:.3f}, 長度 {len(audio_data)/sample_rate:.2f}s"
            )

            return audio_data

        except Exception as e:
            print(f"⚠️ 音訊後處理失敗: {e}")
            return audio_data

    def get_available_speakers(self) -> list:
        """取得可用說話者列表"""
        try:
            speakers_dir = Path(self.settings.SPEAKER_DIR)
            speakers = ["default"]

            if speakers_dir.exists():
                for speaker_file in speakers_dir.glob("*.json"):
                    speakers.append(speaker_file.stem)

            return speakers

        except Exception as e:
            print(f"⚠️ 無法載入說話者列表: {e}")
            return ["default"]

    def get_supported_languages(self) -> list:
        """取得支援的語言列表"""
        # 根據引擎返回支援的語言
        language_map = {
            "xtts": ["zh", "en", "ja", "ko", "es", "fr", "de", "it"],
            "openvoice": ["zh", "en", "ja", "ko"],
            "bark": ["zh", "en", "multilingual"],
        }

        return language_map.get(self.engine_type, ["zh", "en"])
