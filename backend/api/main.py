# backend/api/main.py
"""
FastAPI 應用入口點
"""

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.api.dependencies import get_settings, add_cors_middleware
from backend.api.middleware import LoggingMiddleware, ErrorHandlingMiddleware
from backend.api.routers import health, tts, vc, batch, profiles

# 初始化 FastAPI 應用
app = FastAPI(
    title="Voice App API",
    description="個人語音合成/轉換工具 - TTS & VC MVP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 添加中介層（順序很重要）
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)
add_cors_middleware(app)

# 掛載路由
app.include_router(health.router, tags=["Health"])
app.include_router(tts.router, prefix="/api/v1", tags=["TTS"])
app.include_router(vc.router, prefix="/api/v1", tags=["VC"])
app.include_router(batch.router, prefix="/api/v1", tags=["Batch"])
app.include_router(profiles.router, prefix="/api/v1", tags=["Profiles"])


# 靜態檔案服務（輸出音檔）
@app.on_event("startup")
async def setup_static_files():
    """啟動時設定靜態檔案目錄"""
    settings = get_settings()
    output_dir = Path(settings.OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    app.mount("/outputs", StaticFiles(directory=str(output_dir)), name="outputs")
    print(f"📁 靜態檔案服務：/outputs -> {output_dir}")


if __name__ == "__main__":
    settings = get_settings()

    print(f"🚀 啟動 Voice App Backend")
    print(f"📡 API Docs: http://localhost:8000/docs")
    print(f"🔧 引擎設定: TTS={settings.TTS_ENGINE}, VC={settings.VC_ENGINE}")
    print(f"💾 快取路徑: {settings.AI_CACHE_ROOT}")

    uvicorn.run(
        "backend.api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
