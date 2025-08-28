# backend/core/config.py

"""
應用程式設定管理
"""
import os
from typing import List, Union
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """應用程式設定"""

    # 基本設定
    DEVICE: str = Field(default="cuda", description="運算裝置")
    FP16: bool = Field(default=True, description="是否使用 FP16")
    MAX_CONCURRENCY: int = Field(default=2, description="最大並發數")

    # 引擎設定
    TTS_ENGINE: str = Field(default="xtts", description="TTS 引擎")
    VC_ENGINE: str = Field(default="rvc", description="VC 引擎")

    # 路徑設定 (基於 AI_CACHE_ROOT)
    AI_CACHE_ROOT: str = Field(default="/tmp/ai_cache", description="AI 模型快取根目錄")
    OUTPUT_DIR: str = Field(default="", description="輸出目錄")
    SPEAKER_DIR: str = Field(default="", description="說話者目錄")
    MODELS_TTS_DIR: str = Field(default="", description="TTS 模型目錄")
    MODELS_VC_DIR: str = Field(default="", description="VC 模型目錄")

    # API 設定
    API_PREFIX: str = Field(default="/api/v1", description="API 前綴")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="允許的 CORS 來源",
    )

    # 音訊設定
    TARGET_LUFS: float = Field(default=-16.0, description="目標響度")
    SAMPLE_RATE: int = Field(default=22050, description="預設取樣率")

    @field_validator("TTS_ENGINE", mode="after")
    def validate_tts_engine(cls, v):
        valid_engines = ["xtts", "openvoice", "bark"]
        if v not in valid_engines:
            raise ValueError(f"TTS_ENGINE 必須是: {valid_engines}")
        return v

    @field_validator("VC_ENGINE", mode="after")
    def validate_vc_engine(cls, v):
        valid_engines = ["rvc", "sovits"]
        if v not in valid_engines:
            raise ValueError(f"VC_ENGINE 必須是: {valid_engines}")
        return v

    @field_validator("OUTPUT_DIR", mode="after")
    def set_output_dir(cls, v, values):
        if not v:
            return f"{values.get('AI_CACHE_ROOT', '/tmp/ai_cache')}/outputs/voice-app"
        return v

    @field_validator("SPEAKER_DIR", mode="after")
    def set_speaker_dir(cls, v, values):
        if not v:
            return f"{values.get('AI_CACHE_ROOT', '/tmp/ai_cache')}/voice/speakers"
        return v

    @field_validator("MODELS_TTS_DIR", mode="after")
    def set_models_tts_dir(cls, v, values):
        if not v:
            return f"{values.get('AI_CACHE_ROOT', '/tmp/ai_cache')}/models/tts"
        return v

    @field_validator("MODELS_VC_DIR", mode="after")
    def set_models_vc_dir(cls, v, values):
        if not v:
            return f"{values.get('AI_CACHE_ROOT', '/tmp/ai_cache')}/models/vc"
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 全域設定實例（可選）
settings = Settings()
