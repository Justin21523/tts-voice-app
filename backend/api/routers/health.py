# backend/api/routers/health.py
"""
健康檢查路由
"""

import torch
import psutil
from datetime import datetime
from fastapi import APIRouter, Depends

from backend.api.dependencies import get_settings, get_model_manager
from backend.core.config import Settings
from backend.core.model_manager import ModelManager

router = APIRouter()


@router.get("/healthz")
async def health_check(
    settings: Settings = Depends(get_settings),
    model_manager: ModelManager = Depends(get_model_manager),
):
    """系統健康檢查"""

    # GPU 資訊
    gpu_info = {
        "available": torch.cuda.is_available(),
        "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "current_device": (
            torch.cuda.current_device() if torch.cuda.is_available() else None
        ),
        "memory_allocated": (
            f"{torch.cuda.memory_allocated() / 1024**3:.2f} GB"
            if torch.cuda.is_available()
            else "N/A"
        ),
        "memory_reserved": (
            f"{torch.cuda.memory_reserved() / 1024**3:.2f} GB"
            if torch.cuda.is_available()
            else "N/A"
        ),
    }

    # 系統資源
    memory = psutil.virtual_memory()
    system_info = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_total": f"{memory.total / 1024**3:.2f} GB",
        "memory_available": f"{memory.available / 1024**3:.2f} GB",
        "memory_percent": memory.percent,
    }

    # 模型載入狀態
    model_status = {
        "tts_engine": settings.TTS_ENGINE,
        "vc_engine": settings.VC_ENGINE,
        "tts_loaded": model_manager.is_tts_loaded(),
        "vc_loaded": model_manager.is_vc_loaded(),
        "loaded_models": list(model_manager.get_loaded_models()),
    }

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "config": {
            "device": settings.DEVICE,
            "fp16": settings.FP16,
            "max_concurrency": settings.MAX_CONCURRENCY,
            "cache_root": settings.AI_CACHE_ROOT,
        },
        "gpu": gpu_info,
        "system": system_info,
        "models": model_status,
    }
