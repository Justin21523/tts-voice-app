# backend/api/dependencies.py
"""
依賴注入模組：載入 .env、初始化共享快取、CORS 設定
"""

import os
from pathlib import Path
from functools import lru_cache
from typing import Optional

from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import Settings
from backend.core.shared_cache import setup_shared_cache
from backend.core.model_manager import ModelManager


# 單例設定
@lru_cache()
def get_settings() -> Settings:
    """載入設定檔（單例模式）"""
    return Settings()


# 全域模型管理器（延遲初始化）
_model_manager: Optional[ModelManager] = None


def get_model_manager(settings: Settings = Depends(get_settings)) -> ModelManager:
    """取得模型管理器（單例）"""
    global _model_manager
    if _model_manager is None:
        # 初始化共享快取
        setup_shared_cache(settings.AI_CACHE_ROOT)
        _model_manager = ModelManager(settings)
    return _model_manager


def add_cors_middleware(app):
    """添加 CORS 中介層"""
    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
