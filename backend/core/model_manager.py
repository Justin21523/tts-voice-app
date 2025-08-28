# backend/core/model_manager.py
"""
模型載入與管理
"""

import torch
from typing import Dict, Any, Optional
from pathlib import Path

from backend.core.config import Settings
from backend.core.performance import setup_performance_defaults


class ModelManager:
    """模型管理器"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.loaded_models: Dict[str, Any] = {}

        # 設定效能預設值
        setup_performance_defaults(settings)

        print(f"🎛️ 模型管理器初始化")
        print(f"   TTS 引擎: {settings.TTS_ENGINE}")
        print(f"   VC 引擎: {settings.VC_ENGINE}")
        print(f"   裝置: {settings.DEVICE}")
        print(f"   FP16: {settings.FP16}")

    async def load_tts_model(self) -> Any:
        """載入 TTS 模型"""
        model_key = f"tts_{self.settings.TTS_ENGINE}"

        if model_key in self.loaded_models:
            print(f"♻️ 重用已載入的 TTS 模型: {self.settings.TTS_ENGINE}")
            return self.loaded_models[model_key]

        print(f"📥 載入 TTS 模型: {self.settings.TTS_ENGINE}")

        try:
            if self.settings.TTS_ENGINE == "xtts":
                model = await self._load_xtts_model()
            elif self.settings.TTS_ENGINE == "openvoice":
                model = await self._load_openvoice_model()
            elif self.settings.TTS_ENGINE == "bark":
                model = await self._load_bark_model()
            else:
                raise ValueError(f"不支援的 TTS 引擎: {self.settings.TTS_ENGINE}")

            self.loaded_models[model_key] = model
            print(f"✅ TTS 模型載入成功: {self.settings.TTS_ENGINE}")
            return model

        except Exception as e:
            print(f"❌ TTS 模型載入失敗: {e}")
            raise

    async def load_vc_model(self) -> Any:
        """載入 VC 模型"""
        model_key = f"vc_{self.settings.VC_ENGINE}"

        if model_key in self.loaded_models:
            print(f"♻️ 重用已載入的 VC 模型: {self.settings.VC_ENGINE}")
            return self.loaded_models[model_key]

        print(f"📥 載入 VC 模型: {self.settings.VC_ENGINE}")

        try:
            if self.settings.VC_ENGINE == "rvc":
                model = await self._load_rvc_model()
            elif self.settings.VC_ENGINE == "sovits":
                model = await self._load_sovits_model()
            else:
                raise ValueError(f"不支援的 VC 引擎: {self.settings.VC_ENGINE}")

            self.loaded_models[model_key] = model
            print(f"✅ VC 模型載入成功: {self.settings.VC_ENGINE}")
            return model

        except Exception as e:
            print(f"❌ VC 模型載入失敗: {e}")
            raise

    async def _load_xtts_model(self):
        """載入 XTTS 模型 (實作佔位符)"""
        # 這裡應該實作實際的 XTTS 模型載入
        # 暫時回傳模擬物件
        return {
            "type": "xtts",
            "device": self.settings.DEVICE,
            "fp16": self.settings.FP16,
            "model_path": f"{self.settings.MODELS_TTS_DIR}/xtts",
            "loaded": True,
        }

    async def _load_openvoice_model(self):
        """載入 OpenVoice 模型 (實作佔位符)"""
        return {
            "type": "openvoice",
            "device": self.settings.DEVICE,
            "fp16": self.settings.FP16,
            "model_path": f"{self.settings.MODELS_TTS_DIR}/openvoice",
            "loaded": True,
        }

    async def _load_bark_model(self):
        """載入 Bark 模型 (實作佔位符)"""
        return {
            "type": "bark",
            "device": self.settings.DEVICE,
            "fp16": self.settings.FP16,
            "model_path": f"{self.settings.MODELS_TTS_DIR}/bark",
            "loaded": True,
        }

    async def _load_rvc_model(self):
        """載入 RVC 模型 (實作佔位符)"""
        return {
            "type": "rvc",
            "device": self.settings.DEVICE,
            "fp16": self.settings.FP16,
            "model_path": f"{self.settings.MODELS_VC_DIR}/rvc",
            "loaded": True,
        }

    async def _load_sovits_model(self):
        """載入 So-VITS-SVC 模型 (實作佔位符)"""
        return {
            "type": "sovits",
            "device": self.settings.DEVICE,
            "fp16": self.settings.FP16,
            "model_path": f"{self.settings.MODELS_VC_DIR}/sovits",
            "loaded": True,
        }

    def unload_model(self, model_key: str):
        """卸載模型"""
        if model_key in self.loaded_models:
            del self.loaded_models[model_key]
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print(f"🗑️ 已卸載模型: {model_key}")

    def unload_all_models(self):
        """卸載所有模型"""
        self.loaded_models.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print(f"🗑️ 已卸載所有模型")

    def is_tts_loaded(self) -> bool:
        """檢查 TTS 模型是否已載入"""
        return f"tts_{self.settings.TTS_ENGINE}" in self.loaded_models

    def is_vc_loaded(self) -> bool:
        """檢查 VC 模型是否已載入"""
        return f"vc_{self.settings.VC_ENGINE}" in self.loaded_models

    def get_loaded_models(self) -> Dict[str, str]:
        """取得已載入模型清單"""
        return {k: v.get("type", "unknown") for k, v in self.loaded_models.items()}

    def get_memory_usage(self) -> Dict[str, Any]:
        """取得記憶體使用狀況"""
        if torch.cuda.is_available():
            return {
                "gpu_allocated": f"{torch.cuda.memory_allocated() / 1024**3:.2f} GB",
                "gpu_reserved": f"{torch.cuda.memory_reserved() / 1024**3:.2f} GB",
                "gpu_free": f"{torch.cuda.memory_reserved() - torch.cuda.memory_allocated() / 1024**3:.2f} GB",
            }
        else:
            return {"gpu_available": False}
