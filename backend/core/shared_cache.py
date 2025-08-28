# backend/core/shared_cache.py
"""
共享快取初始化
"""

import os
import torch
from pathlib import Path
from typing import Dict


def setup_shared_cache(cache_root: str = None) -> Dict[str, str]:  # type: ignore
    """
    設定共享 AI 模型快取

    Args:
        cache_root: 快取根目錄，預設從環境變數或 ../ai_warehouse/cache

    Returns:
        設定的環境變數字典
    """
    if cache_root is None:
        cache_root = os.getenv("AI_CACHE_ROOT", "../ai_warehouse/cache")

    # 確保快取根目錄存在
    Path(cache_root).mkdir(parents=True, exist_ok=True)

    # HuggingFace 快取設定
    hf_cache_vars = {
        "HF_HOME": f"{cache_root}/hf",
        "TRANSFORMERS_CACHE": f"{cache_root}/hf/transformers",
        "HF_DATASETS_CACHE": f"{cache_root}/hf/datasets",
        "HUGGINGFACE_HUB_CACHE": f"{cache_root}/hf/hub",
    }

    # PyTorch 快取設定
    torch_cache_vars = {
        "TORCH_HOME": f"{cache_root}/torch",
        "TORCH_EXTENSIONS_DIR": f"{cache_root}/torch/extensions",
    }

    # 應用特定目錄
    app_dirs = {
        "MODELS_TTS_DIR": f"{cache_root}/models/tts",
        "MODELS_VC_DIR": f"{cache_root}/models/vc",
        "MODELS_ASR_DIR": f"{cache_root}/models/asr",
        "VOICE_SPEAKERS_DIR": f"{cache_root}/voice/speakers",
        "VOICE_OUTPUTS_DIR": f"{cache_root}/outputs/voice-app",
    }

    # 合併所有設定
    all_cache_vars = {**hf_cache_vars, **torch_cache_vars, **app_dirs}

    # 設定環境變數並建立目錄
    for key, path in all_cache_vars.items():
        os.environ[key] = path
        Path(path).mkdir(parents=True, exist_ok=True)

    # 顯示設定資訊
    gpu_available = torch.cuda.is_available()
    gpu_count = torch.cuda.device_count() if gpu_available else 0

    print(f"🏠 共享快取根目錄: {cache_root}")
    print(f"🔥 GPU 可用: {gpu_available} ({gpu_count} 裝置)")

    if gpu_available:
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"💾 GPU 記憶體: {gpu_memory:.1f} GB")

    return all_cache_vars


def get_cache_info() -> Dict[str, str]:
    """取得當前快取設定資訊"""
    cache_vars = [
        "AI_CACHE_ROOT",
        "HF_HOME",
        "TRANSFORMERS_CACHE",
        "TORCH_HOME",
        "MODELS_TTS_DIR",
        "MODELS_VC_DIR",
    ]

    return {var: os.getenv(var, "未設定") for var in cache_vars}


def cleanup_cache(cache_root: str = None, keep_models: bool = True):  # type: ignore
    """
    清理快取目錄

    Args:
        cache_root: 快取根目錄
        keep_models: 是否保留模型檔案
    """
    if cache_root is None:
        cache_root = os.getenv("AI_CACHE_ROOT", "/tmp/ai_cache")

    import shutil

    cleanup_dirs = [
        f"{cache_root}/outputs",
        f"{cache_root}/temp",
    ]

    if not keep_models:
        cleanup_dirs.extend(
            [
                f"{cache_root}/hf/transformers",
                f"{cache_root}/torch",
            ]
        )

    for dir_path in cleanup_dirs:
        path = Path(dir_path)
        if path.exists():
            shutil.rmtree(path)
            print(f"🗑️ 已清理: {dir_path}")

    print(f"✅ 快取清理完成")
