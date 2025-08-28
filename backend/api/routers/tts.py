# backend/api/routers/tts.py
"""
文字轉語音 (TTS) 路由
"""

import time
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import get_settings, get_model_manager
from backend.core.config import Settings
from backend.core.model_manager import ModelManager
from backend.services.tts_service import TTSService

router = APIRouter()


class TTSRequest(BaseModel):
    """TTS 請求模型"""

    text: str = Field(..., min_length=1, max_length=10000, description="要合成的文字")
    speaker_id: str = Field(default="default", description="說話者 ID")
    language: str = Field(default="zh", description="語言代碼 (zh/en)")
    speed: float = Field(default=1.0, ge=0.1, le=3.0, description="語速倍率")
    emotion: str = Field(default="neutral", description="情感風格")


class TTSResponse(BaseModel):
    """TTS 回應模型"""

    audio_url: str = Field(..., description="音檔下載 URL")
    duration: float = Field(..., description="音檔長度（秒）")
    processing_time: float = Field(..., description="處理耗時（秒）")
    file_size: int = Field(..., description="檔案大小（位元組）")
    sample_rate: int = Field(..., description="取樣率")


@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(
    request: TTSRequest,
    settings: Settings = Depends(get_settings),
    model_manager: ModelManager = Depends(get_model_manager),
):
    """文字轉語音"""
    start_time = time.time()

    try:
        # 載入 TTS 模型
        tts_model = await model_manager.load_tts_model()

        # 初始化 TTS 服務
        tts_service = TTSService(tts_model, settings)

        # 產生唯一檔名
        file_id = str(uuid.uuid4())
        output_filename = f"tts_{file_id}.wav"
        output_path = Path(settings.OUTPUT_DIR) / output_filename

        # 執行 TTS
        result = await tts_service.synthesize(
            text=request.text,
            speaker_id=request.speaker_id,
            language=request.language,
            speed=request.speed,
            emotion=request.emotion,
            output_path=str(output_path),
        )

        processing_time = time.time() - start_time

        # 取得檔案資訊
        file_size = output_path.stat().st_size

        return TTSResponse(
            audio_url=f"/outputs/{output_filename}",
            duration=result["duration"],
            processing_time=processing_time,
            file_size=file_size,
            sample_rate=result["sample_rate"],
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"參數錯誤: {str(e)}")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"模型檔案未找到: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS 處理失敗: {str(e)}")


@router.get("/tts/speakers")
async def get_available_speakers(settings: Settings = Depends(get_settings)):
    """取得可用說話者列表"""
    try:
        speakers_dir = Path(settings.SPEAKER_DIR)
        speakers = []

        if speakers_dir.exists():
            for speaker_file in speakers_dir.glob("*.json"):
                speaker_id = speaker_file.stem
                speakers.append(
                    {
                        "id": speaker_id,
                        "name": speaker_id.replace("_", " ").title(),
                        "config_file": str(speaker_file),
                    }
                )

        # 總是包含預設說話者
        if not any(s["id"] == "default" for s in speakers):
            speakers.insert(
                0, {"id": "default", "name": "Default", "config_file": None}
            )

        return {"speakers": speakers}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"無法載入說話者列表: {str(e)}")
