# backend/api/middleware.py
"""
中介層：CORS、日誌、錯誤處理
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# 設定日誌
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """請求日誌中介層"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # 記錄請求
        logger.info(f"📥 {request.method} {request.url.path}")

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # 記錄回應
            logger.info(
                f"📤 {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)"
            )

            # 添加處理時間標頭
            response.headers["X-Process-Time"] = str(process_time)
            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"❌ {request.method} {request.url.path} - ERROR: {str(e)} ({process_time:.3f}s)"
            )

            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": str(e),
                    "path": request.url.path,
                },
            )


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """全域錯誤處理中介層"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except ValueError as e:
            logger.warning(f"⚠️ ValueError: {str(e)}")
            return JSONResponse(
                status_code=400, content={"error": "Bad Request", "message": str(e)}
            )
        except FileNotFoundError as e:
            logger.warning(f"⚠️ FileNotFoundError: {str(e)}")
            return JSONResponse(
                status_code=404, content={"error": "File Not Found", "message": str(e)}
            )
        except Exception as e:
            logger.error(f"❌ Unhandled Exception: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                },
            )
