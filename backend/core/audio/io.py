# backend/core/audio/io.py

"""
音訊 I/O 處理工具
"""
import base64
import tempfile
from pathlib import Path
from typing import Union, Tuple
import librosa
import soundfile as sf
import numpy as np
from fastapi import UploadFile


async def save_base64_audio(
    base64_data: str, output_path: str
) -> Tuple[np.ndarray, int]:
    """
    儲存 base64 編碼音訊到檔案

    Args:
        base64_data: base64 編碼的音訊資料
        output_path: 輸出檔案路徑

    Returns:
        (audio_data, sample_rate) 元組
    """
    try:
        # 移除可能的 data URL 前綴
        if base64_data.startswith("data:audio"):
            base64_data = base64_data.split(",")[1]

        # 解碼 base64
        audio_bytes = base64.b64decode(base64_data)

        # 寫入暫存檔案
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        # 使用 librosa 載入並重新取樣
        audio_data, sample_rate = librosa.load(temp_path, sr=22050)

        # 儲存為標準 WAV
        sf.write(output_path, audio_data, sample_rate, format="WAV")

        # 清理暫存檔案
        Path(temp_path).unlink(missing_ok=True)

        return audio_data, sample_rate

    except Exception as e:
        raise ValueError(f"base64 音訊解碼失敗: {e}")


async def save_uploaded_audio(
    upload_file: UploadFile, output_path: str
) -> Tuple[np.ndarray, int]:
    """
    儲存上傳的音訊檔案

    Args:
        upload_file: FastAPI 上傳檔案
        output_path: 輸出檔案路徑

    Returns:
        (audio_data, sample_rate) 元組
    """
    try:
        # 讀取檔案內容
        content = await upload_file.read()

        # 寫入暫存檔案
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        # 載入音訊
        audio_data, sample_rate = librosa.load(temp_path, sr=22050)

        # 儲存為標準 WAV
        sf.write(output_path, audio_data, sample_rate, format="WAV")

        # 清理暫存檔案
        Path(temp_path).unlink(missing_ok=True)

        return audio_data, sample_rate

    except Exception as e:
        raise ValueError(f"音訊檔案處理失敗: {e}")


def load_audio(
    file_path: Union[str, Path], target_sr: int = 22050
) -> Tuple[np.ndarray, int]:
    """
    載入音訊檔案

    Args:
        file_path: 音訊檔案路徑
        target_sr: 目標取樣率

    Returns:
        (audio_data, sample_rate) 元組
    """
    try:
        audio_data, sample_rate = librosa.load(str(file_path), sr=target_sr)
        return audio_data, sample_rate
    except Exception as e:
        raise FileNotFoundError(f"無法載入音訊檔案 {file_path}: {e}")


def save_audio(
    audio_data: np.ndarray, output_path: Union[str, Path], sample_rate: int = 22050
):
    """
    儲存音訊資料到檔案

    Args:
        audio_data: 音訊資料
        output_path: 輸出檔案路徑
        sample_rate: 取樣率
    """
    try:
        sf.write(str(output_path), audio_data, sample_rate, format="WAV")
    except Exception as e:
        raise IOError(f"無法儲存音訊檔案 {output_path}: {e}")


def convert_to_base64(file_path: Union[str, Path]) -> str:
    """
    將音訊檔案轉換為 base64

    Args:
        file_path: 音訊檔案路徑

    Returns:
        base64 編碼字串
    """
    try:
        with open(str(file_path), "rb") as f:
            audio_bytes = f.read()

        base64_data = base64.b64encode(audio_bytes).decode("utf-8")
        return f"data:audio/wav;base64,{base64_data}"

    except Exception as e:
        raise IOError(f"無法轉換音訊檔案為 base64: {e}")


def get_audio_info(file_path: Union[str, Path]) -> dict:
    """
    取得音訊檔案資訊

    Args:
        file_path: 音訊檔案路徑

    Returns:
        包含音訊資訊的字典
    """
    try:
        # 使用 librosa 取得基本資訊
        audio_data, sample_rate = librosa.load(str(file_path), sr=None)
        duration = len(audio_data) / sample_rate

        # 取得檔案大小
        file_size = Path(file_path).stat().st_size

        return {
            "duration": duration,
            "sample_rate": sample_rate,
            "channels": 1 if audio_data.ndim == 1 else audio_data.shape[0],
            "file_size": file_size,
            "format": Path(file_path).suffix.lower(),
        }

    except Exception as e:
        raise ValueError(f"無法取得音訊檔案資訊: {e}")


def trim_silence(
    audio_data: np.ndarray,
    sample_rate: int,
    top_db: int = 20,
    frame_length: int = 2048,
    hop_length: int = 512,
) -> np.ndarray:
    """
    去除音訊前後的靜音

    Args:
        audio_data: 音訊資料
        sample_rate: 取樣率
        top_db: 靜音閾值 (dB)
        frame_length: 幀長度
        hop_length: 跳躍長度

    Returns:
        去除靜音後的音訊資料
    """
    try:
        # 使用 librosa 去除靜音
        trimmed_audio, _ = librosa.effects.trim(
            audio_data, top_db=top_db, frame_length=frame_length, hop_length=hop_length
        )

        return trimmed_audio

    except Exception as e:
        raise ValueError(f"去除靜音失敗: {e}")


def resample_audio(audio_data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """
    重新取樣音訊

    Args:
        audio_data: 原始音訊資料
        orig_sr: 原始取樣率
        target_sr: 目標取樣率

    Returns:
        重新取樣後的音訊資料
    """
    try:
        if orig_sr == target_sr:
            return audio_data

        resampled_audio = librosa.resample(
            audio_data, orig_sr=orig_sr, target_sr=target_sr
        )
        return resampled_audio

    except Exception as e:
        raise ValueError(f"重新取樣失敗: {e}")


def normalize_audio(audio_data: np.ndarray, method: str = "peak") -> np.ndarray:
    """
    正規化音訊

    Args:
        audio_data: 音訊資料
        method: 正規化方法 ("peak" 或 "rms")

    Returns:
        正規化後的音訊資料
    """
    try:
        if method == "peak":
            # 峰值正規化
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                return audio_data / max_val
        elif method == "rms":
            # RMS 正規化
            rms = np.sqrt(np.mean(audio_data**2))
            if rms > 0:
                return audio_data / rms * 0.1  # 調整到合適的 RMS 等級

        return audio_data

    except Exception as e:
        raise ValueError(f"音訊正規化失敗: {e}")
