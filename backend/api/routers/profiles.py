# backend/api/routers/profile.py

"""
說話者檔案管理路由
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from backend.api.dependencies import get_settings
from backend.core.config import Settings

router = APIRouter()


class SpeakerProfile(BaseModel):
    """說話者檔案模型"""

    id: str = Field(..., description="說話者唯一 ID")
    name: str = Field(..., description="顯示名稱")
    description: str = Field(default="", description="說明")
    language: str = Field(default="zh", description="主要語言")
    gender: str = Field(default="unknown", description="性別")
    sample_rate: int = Field(default=22050, description="取樣率")
    model_path: str = Field(default="", description="模型檔案路徑")
    config: Dict[str, Any] = Field(default_factory=dict, description="引擎特定設定")


class CreateSpeakerRequest(BaseModel):
    """建立說話者請求"""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    language: str = Field(default="zh")
    gender: str = Field(default="unknown")


@router.get("/profiles", response_model=List[SpeakerProfile])
async def get_speaker_profiles(settings: Settings = Depends(get_settings)):
    """取得所有說話者檔案"""
    try:
        speakers_dir = Path(settings.SPEAKER_DIR)
        profiles = []

        if speakers_dir.exists():
            for profile_file in speakers_dir.glob("*.json"):
                try:
                    with open(profile_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        profiles.append(SpeakerProfile(**data))
                except Exception as e:
                    print(f"⚠️ 無法載入說話者檔案 {profile_file}: {e}")

        # 添加預設說話者
        default_profile = SpeakerProfile(
            id="default",
            name="預設說話者",
            description="系統預設語音",
            language="zh",
            gender="unknown",
        )
        profiles.insert(0, default_profile)

        return profiles

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"無法載入說話者檔案: {str(e)}")


@router.get("/profiles/{speaker_id}", response_model=SpeakerProfile)
async def get_speaker_profile(
    speaker_id: str, settings: Settings = Depends(get_settings)
):
    """取得特定說話者檔案"""
    if speaker_id == "default":
        return SpeakerProfile(
            id="default",
            name="預設說話者",
            description="系統預設語音",
            language="zh",
            gender="unknown",
        )

    try:
        profile_file = Path(settings.SPEAKER_DIR) / f"{speaker_id}.json"

        if not profile_file.exists():
            raise HTTPException(status_code=404, detail="說話者不存在")

        with open(profile_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return SpeakerProfile(**data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"無法載入說話者檔案: {str(e)}")


@router.post("/profiles", response_model=SpeakerProfile)
async def create_speaker_profile(
    request: CreateSpeakerRequest, settings: Settings = Depends(get_settings)
):
    """建立新說話者檔案"""
    try:
        # 產生說話者 ID
        speaker_id = request.name.lower().replace(" ", "_").replace("-", "_")

        # 確保 ID 唯一
        speakers_dir = Path(settings.SPEAKER_DIR)
        speakers_dir.mkdir(parents=True, exist_ok=True)

        counter = 1
        original_id = speaker_id
        while (speakers_dir / f"{speaker_id}.json").exists():
            speaker_id = f"{original_id}_{counter}"
            counter += 1

        # 建立說話者檔案
        profile = SpeakerProfile(
            id=speaker_id,
            name=request.name,
            description=request.description,
            language=request.language,
            gender=request.gender,
        )

        # 儲存檔案
        profile_file = speakers_dir / f"{speaker_id}.json"
        with open(profile_file, "w", encoding="utf-8") as f:
            json.dump(profile.dict(), f, ensure_ascii=False, indent=2)

        return profile

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"建立說話者檔案失敗: {str(e)}")


@router.put("/profiles/{speaker_id}", response_model=SpeakerProfile)
async def update_speaker_profile(
    speaker_id: str, profile: SpeakerProfile, settings: Settings = Depends(get_settings)
):
    """更新說話者檔案"""
    if speaker_id == "default":
        raise HTTPException(status_code=400, detail="無法修改預設說話者")

    try:
        profile_file = Path(settings.SPEAKER_DIR) / f"{speaker_id}.json"

        if not profile_file.exists():
            raise HTTPException(status_code=404, detail="說話者不存在")

        # 確保 ID 一致
        profile.id = speaker_id

        # 儲存檔案
        with open(profile_file, "w", encoding="utf-8") as f:
            json.dump(profile.dict(), f, ensure_ascii=False, indent=2)

        return profile

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新說話者檔案失敗: {str(e)}")


@router.delete("/profiles/{speaker_id}")
async def delete_speaker_profile(
    speaker_id: str, settings: Settings = Depends(get_settings)
):
    """刪除說話者檔案"""
    if speaker_id == "default":
        raise HTTPException(status_code=400, detail="無法刪除預設說話者")

    try:
        profile_file = Path(settings.SPEAKER_DIR) / f"{speaker_id}.json"

        if not profile_file.exists():
            raise HTTPException(status_code=404, detail="說話者不存在")

        profile_file.unlink()

        return {"message": f"說話者 {speaker_id} 已刪除"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刪除說話者檔案失敗: {str(e)}")
