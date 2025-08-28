# backend/core/audio/normalization.py

"""
LUFS 響度正規化工具
"""
import numpy as np
import librosa
from typing import Tuple, Union, Optional
import scipy.signal
from pathlib import Path


class LUFSNormalizer:
    """LUFS 響度正規化器"""

    def __init__(self, target_lufs: float = -16.0, sample_rate: int = 22050):
        """
        初始化 LUFS 正規化器

        Args:
            target_lufs: 目標響度 (LUFS)
            sample_rate: 取樣率
        """
        self.target_lufs = target_lufs
        self.sample_rate = sample_rate

        # 預計算濾波器係數 (簡化版 K-weighting)
        self._setup_filters()

    def _setup_filters(self):
        """設定 K-weighting 濾波器 (簡化版)"""
        try:
            # High-pass filter (去除低頻)
            self.hp_b, self.hp_a = scipy.signal.butter(
                2, 20.0, btype="high", fs=self.sample_rate
            )

            # Pre-emphasis filter (高頻增強)
            self.pre_b, self.pre_a = scipy.signal.butter(
                1, 1000.0, btype="high", fs=self.sample_rate
            )

        except Exception as e:
            print(f"⚠️ 濾波器設定失敗，使用簡化版: {e}")
            self.hp_b = self.hp_a = None
            self.pre_b = self.pre_a = None

    def measure_lufs(self, audio_data: np.ndarray) -> float:
        """
        測量音訊的 LUFS 響度

        Args:
            audio_data: 音訊資料

        Returns:
            LUFS 值
        """
        try:
            if len(audio_data) == 0:
                return -float("inf")

            # 應用 K-weighting 濾波器 (簡化版)
            filtered_audio = self._apply_k_weighting(audio_data)

            # 計算均方根功率
            mean_square = np.mean(filtered_audio**2)

            if mean_square <= 0:
                return -float("inf")

            # 轉換為 LUFS (近似)
            lufs = -0.691 + 10 * np.log10(mean_square)

            return lufs

        except Exception as e:
            print(f"⚠️ LUFS 測量失敗: {e}")
            # 簡化版：使用 RMS
            rms = np.sqrt(np.mean(audio_data**2))
            return 20 * np.log10(rms + 1e-8) if rms > 0 else -60.0

    def _apply_k_weighting(self, audio_data: np.ndarray) -> np.ndarray:
        """應用 K-weighting 濾波器 (簡化版)"""
        try:
            if self.hp_a is not None and self.pre_a is not None:
                # 應用高通濾波器
                filtered = scipy.signal.filtfilt(self.hp_b, self.hp_a, audio_data)
                # 應用預增強濾波器
                filtered = scipy.signal.filtfilt(self.pre_b, self.pre_a, filtered)
                return filtered
            else:
                # 簡化版：只應用簡單的高通
                return audio_data

        except Exception as e:
            print(f"⚠️ K-weighting 濾波失敗: {e}")
            return audio_data

    def normalize_to_lufs(
        self, audio_data: np.ndarray, target_lufs: Optional[float] = None
    ) -> Tuple[np.ndarray, dict]:
        """
        將音訊正規化到目標 LUFS

        Args:
            audio_data: 輸入音訊資料
            target_lufs: 目標 LUFS (None 使用預設)

        Returns:
            (正規化後的音訊, 處理資訊)
        """
        if target_lufs is None:
            target_lufs = self.target_lufs

        try:
            # 測量原始響度
            current_lufs = self.measure_lufs(audio_data)

            if current_lufs == -float("inf"):
                # 靜音處理
                return audio_data, {
                    "original_lufs": current_lufs,
                    "target_lufs": target_lufs,
                    "gain_db": 0.0,
                    "normalized": False,
                    "peak": 0.0,
                }

            # 計算所需增益
            gain_db = target_lufs - current_lufs
            gain_linear = 10 ** (gain_db / 20)

            # 應用增益
            normalized_audio = audio_data * gain_linear

            # 檢查峰值限制
            peak = np.max(np.abs(normalized_audio))

            if peak > 0.95:  # 避免削波
                # 降低增益以防止削波
                safety_gain = 0.95 / peak
                normalized_audio *= safety_gain
                actual_gain_db = gain_db + 20 * np.log10(safety_gain)
            else:
                actual_gain_db = gain_db

            # 驗證結果
            final_lufs = self.measure_lufs(normalized_audio)

            return normalized_audio, {
                "original_lufs": current_lufs,
                "target_lufs": target_lufs,
                "final_lufs": final_lufs,
                "gain_db": actual_gain_db,
                "normalized": True,
                "peak": np.max(np.abs(normalized_audio)),
            }

        except Exception as e:
            print(f"⚠️ LUFS 正規化失敗: {e}")
            # 簡化版：使用峰值正規化
            peak = np.max(np.abs(audio_data))
            if peak > 0:
                normalized_audio = audio_data / peak * 0.9
            else:
                normalized_audio = audio_data

            return normalized_audio, {
                "original_lufs": -60.0,
                "target_lufs": target_lufs,
                "gain_db": 0.0,
                "normalized": False,
                "peak": np.max(np.abs(normalized_audio)),
                "fallback": "peak_normalization",
            }

    def normalize_file(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        target_lufs: Optional[float] = None,
    ) -> dict:
        """
        正規化音訊檔案

        Args:
            input_path: 輸入檔案路徑
            output_path: 輸出檔案路徑
            target_lufs: 目標 LUFS

        Returns:
            處理資訊
        """
        try:
            # 載入音訊
            audio_data, sample_rate = librosa.load(str(input_path), sr=self.sample_rate)

            # 正規化
            normalized_audio, info = self.normalize_to_lufs(audio_data, target_lufs)

            # 儲存檔案
            import soundfile as sf

            sf.write(str(output_path), normalized_audio, sample_rate, format="WAV")

            info.update(
                {
                    "input_file": str(input_path),
                    "output_file": str(output_path),
                    "sample_rate": sample_rate,
                }
            )

            return info

        except Exception as e:
            raise IOError(f"檔案正規化失敗: {e}")


def quick_normalize(
    audio_data: np.ndarray, target_lufs: float = -16.0, sample_rate: int = 22050
) -> np.ndarray:
    """
    快速 LUFS 正規化 (簡化版)

    Args:
        audio_data: 音訊資料
        target_lufs: 目標 LUFS
        sample_rate: 取樣率

    Returns:
        正規化後的音訊
    """
    normalizer = LUFSNormalizer(target_lufs, sample_rate)
    normalized_audio, _ = normalizer.normalize_to_lufs(audio_data)
    return normalized_audio


def normalize_batch(
    file_list: list,
    output_dir: Union[str, Path],
    target_lufs: float = -16.0,
    sample_rate: int = 22050,
) -> list:
    """
    批次正規化音訊檔案

    Args:
        file_list: 輸入檔案路徑列表
        output_dir: 輸出目錄
        target_lufs: 目標 LUFS
        sample_rate: 取樣率

    Returns:
        處理結果列表
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    normalizer = LUFSNormalizer(target_lufs, sample_rate)
    results = []

    for input_file in file_list:
        try:
            input_path = Path(input_file)
            output_path = output_dir / f"normalized_{input_path.name}"

            info = normalizer.normalize_file(input_path, output_path, target_lufs)
            results.append({"status": "success", "info": info})

        except Exception as e:
            results.append(
                {"status": "failed", "file": str(input_file), "error": str(e)}
            )

    return results
