# backend/services/vc_service.py

"""
語音轉換 (VC) 服務
"""
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import torch
import numpy as np
import librosa
import soundfile as sf

from backend.core.config import Settings
from backend.core.audio.normalization import quick_normalize
from backend.core.audio.io import load_audio, trim_silence


class VCService:
    """VC 服務封裝"""

    def __init__(self, model: Dict[str, Any], settings: Settings):
        """
        初始化 VC 服務

        Args:
            model: 載入的 VC 模型
            settings: 應用設定
        """
        self.model = model
        self.settings = settings
        self.engine_type = model.get("type", "unknown")

        print(f"🎭 VC 服務初始化: {self.engine_type}")

    async def convert(
        self,
        source_audio_path: str,
        target_speaker: str,
        output_path: str,
        preserve_pitch: bool = True,
        denoise: bool = True,
        f0_method: str = "harvest",
    ) -> Dict[str, Any]:
        """
        執行語音轉換

        Args:
            source_audio_path: 源音檔路徑
            target_speaker: 目標說話者 ID
            output_path: 輸出檔案路徑
            preserve_pitch: 是否保持音調
            denoise: 是否降噪
            f0_method: 基頻提取方法

        Returns:
            轉換結果資訊
        """
        start_time = time.time()

        try:
            print(f"🎯 VC 轉換開始: {self.engine_type}")
            print(f"   源音檔: {source_audio_path}")
            print(f"   目標說話者: {target_speaker}")
            print(f"   設定: pitch={preserve_pitch}, denoise={denoise}, f0={f0_method}")

            # 載入源音檔
            source_audio, sample_rate = load_audio(
                source_audio_path, self.settings.SAMPLE_RATE
            )
            original_duration = len(source_audio) / sample_rate

            # 預處理
            if denoise:
                source_audio = await self._denoise_audio(source_audio, sample_rate)

            # 根據引擎類型執行轉換
            if self.engine_type == "rvc":
                converted_audio = await self._convert_rvc(
                    source_audio, target_speaker, preserve_pitch, f0_method
                )
            elif self.engine_type == "sovits":
                converted_audio = await self._convert_sovits(
                    source_audio, target_speaker, preserve_pitch, f0_method
                )
            else:
                raise ValueError(f"不支援的 VC 引擎: {self.engine_type}")

            # 後處理
            converted_audio = await self._post_process_audio(
                converted_audio, sample_rate
            )

            # 儲存音檔
            sf.write(output_path, converted_audio, sample_rate, format="WAV")

            processing_time = time.time() - start_time
            output_duration = len(converted_audio) / sample_rate

            print(
                f"✅ VC 轉換完成: {original_duration:.2f}s -> {output_duration:.2f}s，耗時 {processing_time:.2f}s"
            )
            print(f"💾 音檔已儲存: {output_path}")

            return {
                "sample_rate": sample_rate,
                "processing_time": processing_time,
                "engine": self.engine_type,
                "original_duration": original_duration,
                "output_duration": output_duration,
                "settings": {
                    "preserve_pitch": preserve_pitch,
                    "denoise": denoise,
                    "f0_method": f0_method,
                },
            }

        except Exception as e:
            processing_time = time.time() - start_time
            print(f"❌ VC 轉換失敗: {e} (耗時 {processing_time:.2f}s)")
            raise

    async def _convert_rvc(
        self,
        audio_data: np.ndarray,
        target_speaker: str,
        preserve_pitch: bool,
        f0_method: str,
    ) -> np.ndarray:
        """RVC 引擎轉換 (實作佔位符)"""
        await asyncio.sleep(0.5)  # 模擬處理時間

        print(f"🔄 RVC 轉換中: 目標說話者 {target_speaker}")

        # RVC 模擬實作
        # 實際應該載入 RVC 模型並進行語音轉換

        # 模擬音色轉換：調整頻譜特徵
        converted_audio = audio_data.copy()

        # 模擬音調保持/變化
        if preserve_pitch:
            # 保持原始音調，只改變音色
            pitch_shift = 0.0
        else:
            # 根據目標說話者調整音調
            speaker_pitch_map = {
                "default": 0.0,
                "speaker_001": 0.05,
                "speaker_002": -0.05,
                "speaker_003": 0.1,
            }
            pitch_shift = speaker_pitch_map.get(target_speaker, 0.0)

        # 應用音調偏移 (簡化實作)
        if pitch_shift != 0.0:
            converted_audio = librosa.effects.pitch_shift(
                converted_audio,
                sr=self.settings.SAMPLE_RATE,
                n_steps=pitch_shift * 12,  # 轉換為半音
            )

        # 模擬音色變化：調整諧波結構
        # 實際 RVC 會使用 VAE 和 flow-based 模型
        harmonic_shift = np.random.uniform(0.9, 1.1)

        # 簡單的頻域處理模擬
        stft = librosa.stft(converted_audio)
        magnitude = np.abs(stft)
        phase = np.angle(stft)

        # 調整頻譜包絡 (模擬聲道特徵變化)
        for i in range(magnitude.shape[0]):
            magnitude[i, :] *= 0.8 + 0.4 * np.random.random()

        # 重構音訊
        modified_stft = magnitude * np.exp(1j * phase)
        converted_audio = librosa.istft(modified_stft)

        # 確保長度一致
        if len(converted_audio) != len(audio_data):
            if len(converted_audio) > len(audio_data):
                converted_audio = converted_audio[: len(audio_data)]
            else:
                # 填補長度差異
                pad_length = len(audio_data) - len(converted_audio)
                converted_audio = np.pad(
                    converted_audio, (0, pad_length), mode="constant"
                )

        print(f"✨ RVC 轉換完成: 音調偏移 {pitch_shift:.2f}")

        return converted_audio

    async def _convert_sovits(
        self,
        audio_data: np.ndarray,
        target_speaker: str,
        preserve_pitch: bool,
        f0_method: str,
    ) -> np.ndarray:
        """So-VITS-SVC 引擎轉換 (實作佔位符)"""
        await asyncio.sleep(0.8)  # SoVITS 處理時間較長

        print(f"🔄 SoVITS 轉換中: 目標說話者 {target_speaker}, F0方法 {f0_method}")

        # So-VITS-SVC 模擬實作
        converted_audio = audio_data.copy()

        # F0 提取方法模擬
        f0_methods = {
            "harvest": 1.0,  # 較穩定
            "dio": 1.1,  # 較快但可能有雜訊
            "crepe": 0.95,  # 最準確但較慢
            "parselmouth": 1.05,  # 平衡選擇
        }

        f0_factor = f0_methods.get(f0_method, 1.0)

        # 模擬高品質語音轉換
        # 實際 SoVITS 使用 diffusion model 和 vector quantization

        # 音調處理
        if preserve_pitch:
            pitch_variation = np.random.uniform(0.98, 1.02)  # 微小變化
        else:
            # 目標說話者音調特徵
            speaker_f0_map = {
                "default": 1.0,
                "speaker_001": 1.15,  # 較高音
                "speaker_002": 0.85,  # 較低音
                "speaker_003": 1.25,  # 高音
            }
            pitch_variation = speaker_f0_map.get(target_speaker, 1.0)

        # 應用音調變化
        if pitch_variation != 1.0:
            converted_audio = librosa.effects.pitch_shift(
                converted_audio,
                sr=self.settings.SAMPLE_RATE,
                n_steps=12 * np.log2(pitch_variation * f0_factor),
            )

        # 模擬更精細的聲學特徵轉換
        # 添加細微的共振峰調整
        stft = librosa.stft(converted_audio, n_fft=2048, hop_length=512)
        magnitude = np.abs(stft)
        phase = np.angle(stft)

        # 模擬聲道長度變化 (改變共振峰)
        vocal_tract_scaling = np.random.uniform(0.9, 1.1)

        # 頻譜包絡調整 (模擬不同說話者的聲道特徵)
        freq_bins = magnitude.shape[0]
        for i in range(freq_bins):
            # 模擬共振峰偏移
            formant_factor = (
                1.0 + 0.1 * np.sin(i / freq_bins * 4 * np.pi) * vocal_tract_scaling
            )
            magnitude[i, :] *= formant_factor

        # 添加說話者特有的頻譜特徵
        speaker_coloring = {
            "default": 1.0,
            "speaker_001": [1.1, 0.9, 1.2],  # 強化高頻
            "speaker_002": [0.9, 1.1, 0.8],  # 強化中頻
            "speaker_003": [1.2, 1.0, 1.1],  # 均衡增強
        }

        if target_speaker in speaker_coloring and target_speaker != "default":
            coloring = speaker_coloring[target_speaker]
            # 分頻段調整
            low_end = freq_bins // 3
            mid_end = 2 * freq_bins // 3

            magnitude[:low_end, :] *= coloring[0]  # 低頻
            magnitude[low_end:mid_end, :] *= coloring[1]  # 中頻
            magnitude[mid_end:, :] *= coloring[2]  # 高頻

        # 重構音訊
        modified_stft = magnitude * np.exp(1j * phase)
        converted_audio = librosa.istft(modified_stft, hop_length=512)

        # 長度對齊
        if len(converted_audio) != len(audio_data):
            if len(converted_audio) > len(audio_data):
                converted_audio = converted_audio[: len(audio_data)]
            else:
                pad_length = len(audio_data) - len(converted_audio)
                converted_audio = np.pad(
                    converted_audio, (0, pad_length), mode="constant"
                )

        # 添加細微的動態範圍調整
        dynamic_factor = np.random.uniform(0.95, 1.05)
        converted_audio *= dynamic_factor

        print(
            f"✨ SoVITS 轉換完成: 音調變化 {pitch_variation:.2f}x, F0因子 {f0_factor:.2f}"
        )

        return converted_audio

    async def _denoise_audio(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> np.ndarray:
        """音訊降噪處理 (簡化實作)"""
        try:
            # 簡單的降噪：高通濾波 + 動態範圍壓縮

            # 1. 高通濾波去除低頻噪音
            from scipy.signal import butter, filtfilt

            nyquist = sample_rate / 2
            low_cutoff = 80 / nyquist  # 80Hz 高通

            b, a = butter(2, low_cutoff, btype="high")
            denoised_audio = filtfilt(b, a, audio_data)

            # 2. 動態範圍處理
            # 計算音訊包絡
            window_size = int(sample_rate * 0.02)  # 20ms 窗口
            envelope = np.convolve(
                np.abs(denoised_audio), np.ones(window_size) / window_size, mode="same"
            )

            # 噪音閾值
            noise_threshold = np.percentile(envelope, 20)  # 底部 20% 視為噪音

            # 軟性噪音門限
            gate_ratio = np.clip((envelope - noise_threshold) / noise_threshold, 0, 1)
            gate_ratio = gate_ratio**0.5  # 平滑過渡

            denoised_audio = denoised_audio * gate_ratio

            print(f"🔇 降噪完成: 噪音閾值 {noise_threshold:.4f}")

            return denoised_audio

        except Exception as e:
            print(f"⚠️ 降噪失敗: {e}")
            return audio_data

    async def _post_process_audio(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> np.ndarray:
        """音訊後處理"""
        try:
            # 去除前後靜音
            audio_data = trim_silence(audio_data, sample_rate, top_db=30)

            # LUFS 正規化
            audio_data = quick_normalize(
                audio_data, self.settings.TARGET_LUFS, sample_rate
            )

            # 軟限制器防止削波
            peak = np.max(np.abs(audio_data))
            if peak > 0.95:
                # 軟削波而非硬限制
                audio_data = np.tanh(audio_data / peak * 0.95) * 0.95

            # 添加微小的抖動減少量化噪音
            dither = np.random.normal(0, 1e-5, len(audio_data))
            audio_data += dither

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

            # 添加引擎特定的預設說話者
            engine_speakers = {
                "rvc": ["speaker_001", "speaker_002", "speaker_003"],
                "sovits": ["voice_a", "voice_b", "voice_c", "voice_d"],
            }

            if self.engine_type in engine_speakers:
                speakers.extend(engine_speakers[self.engine_type])

            return list(set(speakers))  # 去重

        except Exception as e:
            print(f"⚠️ 無法載入說話者列表: {e}")
            return ["default"]

    def get_supported_f0_methods(self) -> list:
        """取得支援的 F0 提取方法"""
        method_map = {
            "rvc": ["harvest", "dio", "crepe", "parselmouth"],
            "sovits": ["harvest", "dio", "crepe"],
        }

        return method_map.get(self.engine_type, ["harvest"])

    def estimate_processing_time(self, audio_duration: float) -> float:
        """估算處理時間"""
        # 根據引擎和音訊長度估算
        time_factors = {"rvc": 2.0, "sovits": 4.0}  # RVC 較快  # SoVITS 較慢但品質好

        base_factor = time_factors.get(self.engine_type, 3.0)

        # GPU 加速
        if torch.cuda.is_available():
            base_factor *= 0.3

        return audio_duration * base_factor
