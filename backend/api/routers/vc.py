# backend/api/routers/vc.py

"""
語音轉換 (VC) 路由
"""
import time
import uuid
import base64
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from backend.api.dependencies import get_settings, get_model_manager
from backend.core.config import Settings
from backend.core.model_manager import ModelManager
from backend.services.vc_service import VCService
from backend.core.audio.io import save_base64_audio, save_uploaded_audio

router = APIRouter()


class VCRequest(BaseModel):
    """VC 請求模型（base64 版本）"""

    source_audio: str = Field(..., description="源音檔 (base64 編碼)")
    target_speaker: str = Field(..., description="目標說話者 ID")
    preserve_pitch: bool = Field(default=True, description="保持音調")
    denoise: bool = Field(default=True, description="降噪處理")
    f0_method: str = Field(default="harvest", description="基頻提取方法")


class VCResponse(BaseModel):
    """VC 回應模型"""

    audio_url: str = Field(..., description="轉換後音檔 URL")
    processing_time: float = Field(..., description="處理耗時（秒）")
    file_size: int = Field(..., description="檔案大小（位元組）")
    sample_rate: int = Field(..., description="取樣率")


@router.post("/vc", response_model=VCResponse)
async def voice_conversion(
    request: VCRequest,
    settings: Settings = Depends(get_settings),
    model_manager: ModelManager = Depends(get_model_manager),
):
    """語音轉換 (base64 版本)"""
    start_time = time.time()

    try:
        # 載入 VC 模型
        vc_model = await model_manager.load_vc_model()

        # 初始化 VC 服務
        vc_service = VCService(vc_model, settings)

        # 產生唯一檔名
        file_id = str(uuid.uuid4())
        temp_input = f"temp_input_{file_id}.wav"
        output_filename = f"vc_{file_id}.wav"

        temp_input_path = Path(settings.OUTPUT_DIR) / temp_input
        output_path = Path(settings.OUTPUT_DIR) / output_filename

        # 儲存 base64 音檔到暫存檔
        await save_base64_audio(request.source_audio, str(temp_input_path))

        # 執行語音轉換
        result = await vc_service.convert(
            source_audio_path=str(temp_input_path),
            target_speaker=request.target_speaker,
            output_path=str(output_path),
            preserve_pitch=request.preserve_pitch,
            denoise=request.denoise,
            f0_method=request.f0_method,
        )

        processing_time = time.time() - start_time

        # 清理暫存檔
        if temp_input_path.exists():
            temp_input_path.unlink()

        # 取得檔案資訊
        file_size = output_path.stat().st_size

        return VCResponse(
            audio_url=f"/outputs/{output_filename}",
            processing_time=processing_time,
            file_size=file_size,
            sample_rate=result["sample_rate"],
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"參數錯誤: {str(e)}")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"檔案未找到: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VC 處理失敗: {str(e)}")


@router.post("/vc/upload", response_model=VCResponse)
async def voice_conversion_upload(
    audio_file: UploadFile = File(...),
    target_speaker: str = "default",
    preserve_pitch: bool = True,
    denoise: bool = True,
    f0_method: str = "harvest",
    settings: Settings = Depends(get_settings),
    model_manager: ModelManager = Depends(get_model_manager),
):
    """語音轉換 (檔案上傳版本)"""
    start_time = time.time()

    try:
        # 驗證檔案類型
        if not audio_file.content_type.startswith("audio/"):
            raise ValueError("只接受音訊檔案")

        # 載入 VC 模型
        vc_model = await model_manager.load_vc_model()
        vc_service = VCService(vc_model, settings)

        # 產生唯一檔名
        file_id = str(uuid.uuid4())
        temp_input = f"temp_input_{file_id}.wav"
        output_filename = f"vc_{file_id}.wav"

        temp_input_path = Path(settings.OUTPUT_DIR) / temp_input
        output_path = Path(settings.OUTPUT_DIR) / output_filename

        # 儲存上傳檔案
        await save_uploaded_audio(audio_file, str(temp_input_path))

        # 執行語音轉換
        result = await vc_service.convert(
            source_audio_path=str(temp_input_path),
            target_speaker=target_speaker,
            output_path=str(output_path),
            preserve_pitch=preserve_pitch,
            denoise=denoise,
            f0_method=f0_method,
        )

        processing_time = time.time() - start_time

        # 清理暫存檔
        if temp_input_path.exists():
            temp_input_path.unlink()

        file_size = output_path.stat().st_size

        return VCResponse(
            audio_url=f"/outputs/{output_filename}",
            processing_time=processing_time,
            file_size=file_size,
            sample_rate=result["sample_rate"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"檔案上傳 VC 失敗: {str(e)}")
