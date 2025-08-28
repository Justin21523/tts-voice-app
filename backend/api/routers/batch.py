# backend/api/routers/batch.py

"""
批次處理路由
"""
import time
import uuid
from typing import List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from backend.api.dependencies import get_settings, get_model_manager
from backend.core.config import Settings
from backend.core.model_manager import ModelManager

router = APIRouter()


class BatchTTSItem(BaseModel):
    """批次 TTS 項目"""

    text: str = Field(..., min_length=1, max_length=10000)
    speaker_id: str = Field(default="default")
    language: str = Field(default="zh")
    speed: float = Field(default=1.0, ge=0.1, le=3.0)


class BatchTTSRequest(BaseModel):
    """批次 TTS 請求"""

    items: List[BatchTTSItem] = Field(..., min_items=1, max_items=50)
    output_format: str = Field(default="wav", description="輸出格式")


class BatchJobStatus(BaseModel):
    """批次任務狀態"""

    job_id: str
    status: str  # pending, processing, completed, failed
    total_items: int
    completed_items: int
    created_at: str
    results: List[Dict[str, Any]] = []


# 簡易內存任務儲存（實際專案應使用 Redis 或資料庫）
_batch_jobs: Dict[str, BatchJobStatus] = {}


@router.post("/batch/tts")
async def create_batch_tts_job(
    request: BatchTTSRequest,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings),
    model_manager: ModelManager = Depends(get_model_manager),
):
    """建立批次 TTS 任務"""
    job_id = str(uuid.uuid4())

    # 建立任務記錄
    job_status = BatchJobStatus(
        job_id=job_id,
        status="pending",
        total_items=len(request.items),
        completed_items=0,
        created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
    )
    _batch_jobs[job_id] = job_status

    # 添加背景任務
    background_tasks.add_task(
        _process_batch_tts, job_id, request.items, settings, model_manager
    )

    return {"job_id": job_id, "status": "created", "message": "批次任務已建立"}


@router.get("/batch/jobs/{job_id}")
async def get_batch_job_status(job_id: str):
    """查詢批次任務狀態"""
    if job_id not in _batch_jobs:
        raise HTTPException(status_code=404, detail="任務不存在")

    return _batch_jobs[job_id]


@router.get("/batch/jobs")
async def list_batch_jobs():
    """列出所有批次任務"""
    return {"jobs": list(_batch_jobs.values())}


async def _process_batch_tts(
    job_id: str,
    items: List[BatchTTSItem],
    settings: Settings,
    model_manager: ModelManager,
):
    """處理批次 TTS（背景任務）"""
    job_status = _batch_jobs[job_id]
    job_status.status = "processing"

    try:
        # 載入模型
        tts_model = await model_manager.load_tts_model()
        from backend.services.tts_service import TTSService

        tts_service = TTSService(tts_model, settings)

        results = []

        for i, item in enumerate(items):
            try:
                # 產生檔名
                file_id = f"batch_{job_id}_{i:03d}"
                output_filename = f"{file_id}.wav"
                output_path = Path(settings.OUTPUT_DIR) / output_filename

                # 執行 TTS
                result = await tts_service.synthesize(
                    text=item.text,
                    speaker_id=item.speaker_id,
                    language=item.language,
                    speed=item.speed,
                    output_path=str(output_path),
                )

                results.append(
                    {
                        "index": i,
                        "text": (
                            item.text[:50] + "..." if len(item.text) > 50 else item.text
                        ),
                        "audio_url": f"/outputs/{output_filename}",
                        "duration": result["duration"],
                        "status": "completed",
                    }
                )

            except Exception as e:
                results.append(
                    {
                        "index": i,
                        "text": (
                            item.text[:50] + "..." if len(item.text) > 50 else item.text
                        ),
                        "error": str(e),
                        "status": "failed",
                    }
                )

            # 更新進度
            job_status.completed_items = i + 1

        # 任務完成
        job_status.status = "completed"
        job_status.results = results

    except Exception as e:
        job_status.status = "failed"
        job_status.results = [{"error": str(e)}]
