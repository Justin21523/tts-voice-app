# VoiceAI Lab

A **personal, portable MVP** for voice synthesis and conversion tasks. Features both Web (React) and Desktop (PyQt) interfaces sharing a unified FastAPI backend.

## 🎯 Features

- **Text-to-Speech (TTS)**: XTTS and OpenVoice engines with multi-language support
- **Voice Conversion (VC)**: RVC and So-VITS-SVC for voice transformation
- **Speaker Management**: JSON-based speaker profiles with sample audio
- **Batch Processing**: Multi-text/audio processing with progress tracking
- **Dual Interface**: Web UI for accessibility + Desktop app for offline use
- **Model Switching**: Engine swapping via `.env` configuration
- **Audio Optimization**: LUFS normalization and silence trimming

## 🏗️ Architecture

```
voice-app/
├── backend/              # FastAPI backend service
│   ├── app.py           # Main FastAPI application entry point
│   ├── services/        # Core business logic
│   │   ├── tts_service.py    # TTS engine wrapper (XTTS/OpenVoice)
│   │   ├── vc_service.py     # VC engine wrapper (RVC/So-VITS-SVC)
│   │   └── audio_utils.py    # Audio processing (LUFS/trim/convert)
│   ├── core/            # Core utilities
│   │   ├── model_manager.py  # Model loading/unloading/caching
│   │   └── config.py         # Environment configuration management
│   └── requirements.txt      # Minimal dependency list
│
├── web/                 # React WebUI
│   ├── src/
│   │   ├── pages/
│   │   │   ├── TTSPage.tsx   # TTS operation interface
│   │   │   └── VCPage.tsx    # VC operation interface
│   │   ├── components/
│   │   │   ├── AudioPlayer.tsx
│   │   │   └── FileUpload.tsx
│   │   ├── services/api.ts   # Backend API calls
│   │   └── App.tsx           # Main application router
│   └── package.json
│
├── desktop/             # PyQt desktop application
│   ├── main.py          # PyQt main window
│   ├── widgets/         # UI components
│   │   ├── tts_widget.py     # TTS operation panel
│   │   └── vc_widget.py      # VC operation panel
│   └── requirements.txt      # PyQt dependencies
│
├── data/                # Data directory
│   ├── speakers/        # Speaker configuration files (JSON)
│   ├── outputs/         # Generated audio files
│   └── cache/           # Model cache for offline use
│
├── models/              # Model files (.gitignore)
│   ├── tts/             # TTS models
│   └── vc/              # VC models
│
└── scripts/             # Utility scripts
    ├── download_models.py    # Model download automation
    └── test_api.py          # API testing scripts
```

## 🚀 Quick Start

### Prerequisites

- NVIDIA GPU with 8-12GB VRAM
- CUDA 12.1+
- Conda/Miniconda

### Installation

```bash
# Create environment
conda create -n audio-speech-lab python=3.10
conda activate audio-speech-lab

# Clone repository
git clone <repository-url>
cd voice-app

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install web dependencies
cd ../web
npm install

# Install desktop dependencies
cd ../desktop
pip install -r requirements.txt

# Download models
cd ../scripts
python download_models.py
```

### Configuration

Copy `.env.example` to `.env` and configure:

```env
# Device & Performance
DEVICE=cuda
FP16=true
MAX_CONCURRENCY=2

# Engine Selection (restart to switch)
TTS_ENGINE=xtts     # xtts | openvoice | bark
VC_ENGINE=rvc       # rvc | sovits

# Paths
MODELS_DIR=./models
SPEAKER_DIR=./data/speakers
OUTPUT_DIR=./data/outputs
API_PREFIX=/api/v1
ALLOWED_ORIGINS=http://localhost:3000

# Audio Processing
TARGET_LUFS=-16
SAMPLE_RATE=22050
```

### Running the Application

```bash
# Start backend (Terminal 1)
cd backend && python app.py

# Start web UI (Terminal 2)
cd web && npm run dev

# Start desktop app (Terminal 3)
cd desktop && python main.py
```

## 📡 API Reference

### Text-to-Speech

**POST** `/api/v1/tts`

```json
{
  "text": "Text to synthesize",
  "speaker_id": "default",
  "language": "en",
  "speed": 1.0
}
```

**Response:**
```json
{
  "audio_url": "/outputs/tts_xxx.wav",
  "duration": 5.2,
  "processing_time": 3.1
}
```

### Voice Conversion

**POST** `/api/v1/vc`

```json
{
  "source_audio": "base64_encoded_wav",
  "target_speaker": "speaker_001",
  "preserve_pitch": true
}
```

**Response:**
```json
{
  "audio_url": "/outputs/vc_xxx.wav",
  "processing_time": 8.5
}
```

### Health Check

**GET** `/health`

Returns system status and available engines.

## 🧪 Testing

```bash
# Health check
curl http://localhost:8000/health

# Test TTS
curl -X POST http://localhost:8000/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello World","speaker_id":"default"}' \
  --output test.wav

# Test with script
python scripts/test_api.py
```

## 🎛️ Model Management

### Engine Switching

Modify `.env` and restart the backend:

```env
TTS_ENGINE=openvoice  # Switch from XTTS to OpenVoice
VC_ENGINE=sovits      # Switch from RVC to So-VITS-SVC
```

### Speaker Profiles

Speaker configurations are stored in `data/speakers/` as JSON files:

```json
{
  "id": "speaker_001",
  "name": "Alice",
  "language": "en",
  "gender": "female",
  "sample_audio": "alice_sample.wav",
  "description": "Clear female voice"
}
```

## ⚡ Performance Optimization

### Memory Requirements

- **TTS (XTTS)**: ~2.5GB VRAM
- **VC (RVC)**: ~1.5GB VRAM
- **Total**: ~4GB (fits comfortably in 8GB VRAM)

### Recommended Settings

```python
# Automatic optimizations enabled by default
torch.backends.cudnn.benchmark = True
torch.set_float32_matmul_precision('medium')

# Audio normalization to -16 LUFS
# FP16 precision for 2x memory savings
# Dynamic model loading/unloading
```

## 🐛 Troubleshooting

### Common Issues

**CUDA Out of Memory**
- Reduce `MAX_CONCURRENCY` in `.env`
- Enable FP16: `FP16=true`
- Close other GPU applications

**Audio Quality Issues**
- Check `TARGET_LUFS` setting (-16 recommended)
- Verify input audio format (WAV, 22050Hz preferred)
- Use `preserve_pitch=true` for voice conversion

**Model Loading Errors**
- Run `python scripts/download_models.py`
- Check `MODELS_DIR` path in `.env`
- Ensure sufficient disk space (models ~2-5GB each)

## 🔧 Development

### Project Structure Philosophy

- **Minimal Dependencies**: Only essential packages
- **Single Repository**: Mono-repo approach for simplicity
- **Offline-First**: Desktop app works without internet
- **API-Driven**: Shared backend for multiple frontends
- **Configuration-Based**: Engine switching via environment

### Adding New Engines

1. Implement service in `backend/services/`
2. Update `model_manager.py` loading logic
3. Add engine option to `.env.example`
4. Update API documentation

### Git Workflow

```bash
# Feature branches
git checkout -b feature/new-tts-engine

# Conventional commits
git commit -m "feat(tts): add bark engine support"
git commit -m "fix(vc): resolve audio format compatibility"
git commit -m "docs(api): update endpoint documentation"
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# CentOS/RHEL
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# macOS
brew install node

# Windows
winget install OpenJS.NodeJS
```

#### 安裝 FFmpeg
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# macOS
brew install ffmpeg

# Windows (使用 Chocolatey)
choco install ffmpeg
```

### 2. 專案下載與設定

```bash
# 克隆專案
git clone https://github.com/your-username/voice-app.git
cd voice-app

# 建立 Python 環境
conda create -n audio-speech-lab python=3.10
conda activate audio-speech-lab

# 設定快取路徑 (重要!)
export AI_CACHE_ROOT="/path/to/your/ai/cache"
# Windows: set AI_CACHE_ROOT=C:\your\ai\cache
```

### 3. 自動化安裝

```bash
# 一鍵安裝所有依賴
python scripts/setup_dev.py

# 檢查安裝狀態
python scripts/setup_dev.py --status
```

### 4. 手動安裝 (如需要)

#### 後端依賴
```bash
cd backend
pip install -r requirements.txt
```

#### React 前端
```bash
cd frontend/react_app
npm install
```

#### Gradio 前端
```bash
cd frontend/gradio_app
pip install -r requirements.txt
```

#### PyQt 桌面版
```bash
cd frontend/pyqt_app
pip install -r requirements.txt
```

### 5. 模型設定

```bash
# 創建模型目錄與範例設定
python scripts/download_models.py --setup

# 檢查模型狀態
python scripts/download_models.py --check
```

### 6. 配置檔案

複製並編輯環境變數：
```bash
cd backend
cp .env.example .env
nano .env  # 編輯配置
```

關鍵配置項：
```env
# GPU 設定
DEVICE=cuda              # cuda | cpu
FP16=true               # 使用半精度浮點數

# 引擎選擇
TTS_ENGINE=xtts         # xtts | openvoice | bark
VC_ENGINE=rvc           # rvc | sovits

# 路徑配置 (修改為你的路徑)
AI_CACHE_ROOT=/home/user/ai_cache
OUTPUT_DIR=${AI_CACHE_ROOT}/outputs/voice-app
SPEAKER_DIR=${AI_CACHE_ROOT}/voice/speakers

# 網路設定
API_PREFIX=/api/v1
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:7860
MAX_CONCURRENCY=2       # 並發請求數量
```

### 7. 首次啟動測試

```bash
# 啟動後端
cd backend
python -m api.main

# 新終端：測試 API
python scripts/test_api.py --quick

# 成功訊息範例:
# ✅ Backend is healthy
# 📡 Backend URL: http://localhost:8000
```

## 🔧 平台特定設定

### Windows 設定

#### PowerShell 執行原則
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 環境變數設定
```batch
# 系統環境變數
setx AI_CACHE_ROOT "C:\Users\%USERNAME%\AppData\Local\VoiceApp\cache"

# 或在 .env 檔案中設定
AI_CACHE_ROOT=C:/Users/%USERNAME%/AppData/Local/VoiceApp/cache
```

#### CUDA 安裝
```batch
# 安裝 CUDA Toolkit
# 下載: https://developer.nvidia.com/cuda-downloads

# 驗證安裝
nvcc --version
python -c "import torch; print(torch.cuda.is_available())"
```

### macOS 設定

#### Homebrew 依賴
```bash
# 安裝開發工具
brew install git python@3.10 node ffmpeg

# M1/M2 Mac 特殊設定
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

#### 路徑設定
```bash
# 加入 .zshrc 或 .bashrc
export AI_CACHE_ROOT="$HOME/.cache/voice-app"
export PATH="/opt/homebrew/bin:$PATH"  # M1/M2
```

### Linux 設定

#### GPU 驅動安裝
```bash
# NVIDIA 驅動 (Ubuntu)
sudo apt update
sudo apt install nvidia-driver-525
sudo reboot

# 驗證
nvidia-smi
```

#### 權限設定
```bash
# 音訊設備權限
sudo usermod -a -G audio $USER

# 快取目錄權限
mkdir -p $AI_CACHE_ROOT
chmod 755 $AI_CACHE_ROOT
```

## 🐳 Docker 部署 (選用)

### Dockerfile
```dockerfile
FROM python:3.10-slim

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製並安裝 Python 依賴
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式
COPY . .

# 暴露端口
EXPOSE 8000

# 啟動指令
CMD ["python", "-m", "api.main"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  voice-app-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AI_CACHE_ROOT=/app/cache
      - DEVICE=cpu
    volumes:
      - ./cache:/app/cache
      - ./data:/app/data

  voice-app-frontend:
    image: node:18-alpine
    working_dir: /app
    command: npm start
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/react_app:/app
    depends_on:
      - voice-app-backend
```

### 容器啟動
```bash
# 構建與啟動
docker-compose up --build

# 後台運行
docker-compose up -d

# 查看日誌
docker-compose logs -f
```

## ⚡ 效能調校

### GPU 最佳化

#### CUDA 設定
```bash
# 檢查 CUDA 版本兼容性
python -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'CUDA Available: {torch.cuda.is_available()}')
print(f'CUDA Version: {torch.version.cuda}')
print(f'GPU Count: {torch.cuda.device_count()}')
"
```

#### 記憶體管理
```env
# .env 效能設定
FP16=true                    # 半精度浮點數
MAX_CONCURRENCY=2            # 限制並發數
TORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

### CPU 模式設定
```env
# CPU 模式 (無 GPU 時)
DEVICE=cpu
FP16=false
MAX_CONCURRENCY=1
```

### 網路優化
```env
# 網路快取設定
HF_HUB_CACHE=${AI_CACHE_ROOT}/hf/hub
HF_DATASETS_OFFLINE=1        # 離線模式
TRANSFORMERS_OFFLINE=1
```

## 🔍 驗證安裝

### 完整測試腳本
```bash
#!/bin/bash
# test_installation.sh

echo "🧪 Voice App Installation Test"
echo "=============================="

# 測試 Python 環境
python --version
pip list | grep -E "(torch|transformers|fastapi)"

# 測試 Node.js
node --version
npm --version

# 測試 FFmpeg
ffmpeg -version | head -1

# 測試 API
python scripts/test_api.py --quick

# 測試前端
cd frontend/react_app && npm run build
cd ../gradio_app && python -c "import gradio; print('Gradio OK')"
cd ../pyqt_app && python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"

echo "✅ Installation test completed!"
```

### 效能基準測試
```bash
# 執行基準測試
python scripts/benchmark.py

# 預期結果:
# TTS Processing: ~3-8s per sentence
# VC Processing: ~5-15s per audio file
# GPU Memory Usage: <4GB for standard models
```

---

# docs/API.md - API 完整文檔

## 🔌 Voice App API v1 Reference

Base URL: `http://localhost:8000/api/v1`

## 認證與授權

目前版本為本地開發使用，無需認證。未來版本將支援 API Key 認證。

## 錯誤處理

所有 API 端點遵循統一錯誤格式：

```json
{
  "error": "Error message description",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

HTTP 狀態碼：
- `200`: 成功
- `400`: 請求參數錯誤
- `422`: 驗證失敗
- `500`: 伺服器內部錯誤
- `503`: 服務暫時不可用

## 端點列表

### 健康檢查

#### GET /healthz

檢查後端服務狀態。

**回應:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600.5,
  "gpu_available": true,
  "models_loaded": {
    "tts": "xtts",
    "vc": "rvc"
  }
}
```

### 文字轉語音 (TTS)

#### POST /api/v1/tts

將文字轉換為語音。

**請求體:**
```json
{
  "text": "要合成的文字內容",
  "speaker_id": "default",
  "language": "zh",
  "speed": 1.0,
  "emotion": "neutral"
}
```

**參數說明:**
- `text` (必需): 要合成的文字，最大 1000 字元
- `speaker_id` (可選): 說話者 ID，預設 "default"
- `language` (可選): 語言代碼 ("zh", "en", "ja")，預設 "zh"
- `speed` (可選): 語速倍率 (0.5-2.0)，預設 1.0
- `emotion` (可選): 情感 ("neutral", "happy", "sad")，預設 "neutral"

**回應:**
```json
{
  "audio_url": "/outputs/tts_20241201_123456.wav",
  "duration": 5.2,
  "processing_time": 3.1,
  "sample_rate": 22050,
  "file_size": 230400
}
```

**範例:**
```bash
curl -X POST http://localhost:8000/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "歡迎使用語音合成系統",
    "speaker_id": "female_zh",
    "language": "zh",
    "speed": 1.2
  }'
```

### 語音轉換 (VC)

#### POST /api/v1/vc

將語音轉換為目標說話者聲線。

**請求體:**
```json
{
  "source_audio": "base64_encoded_audio_data",
  "target_speaker": "speaker_001",
  "preserve_pitch": true,
  "noise_reduction": true
}
```

**參數說明:**
- `source_audio` (必需): Base64 編碼的音訊資料
- `target_speaker` (必需): 目標說話者 ID
- `preserve_pitch` (可選): 是否保持音調，預設 true
- `noise_reduction` (可選): 是否降噪，預設 false

**回應:**
```json
{
  "audio_url": "/outputs/vc_20241201_123456.wav",
  "processing_time": 8.5,
  "sample_rate": 22050,
  "file_size": 451200
}
```

**範例:**
```bash
# 上傳音檔並轉換
curl -X POST http://localhost:8000/api/v1/vc \
  -H "Content-Type: application/json" \
  -d '{
    "source_audio": "'$(base64 -w 0 input.wav)'",
    "target_speaker": "male_en",
    "preserve_pitch": true
  }'
```

### 說話者資料

#### GET /api/v1/profiles

取得所有可用的說話者資料。

**回應:**
```json
{
  "profiles": [
    {
      "id": "default",
      "name": "預設說話者",
      "language": "zh",
      "gender": "neutral",
      "description": "系統預設說話者",
      "sample_audio": "/samples/default.wav",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

#### POST /api/v1/profiles

建立新的說話者資料。

**請求體:**
```json
{
  "name": "新說話者",
  "language": "zh",
  "gender": "female",
  "description": "自訂女性說話者",
  "sample_audio": "base64_encoded_sample"
}
```

#### GET /api/v1/profiles/{profile_id}

取得特定說話者資料。

#### PUT /api/v1/profiles/{profile_id}

更新說話者資料。

#### DELETE /api/v1/profiles/{profile_id}

刪除說話者資料。

### 批次處理

#### POST /api/v1/batch/tts

批次文字轉語音。

**請求體:**
```json
{
  "texts": [
    "第一段文字",
    "第二段文字",
    "第三段文字"
  ],
  "speaker_id": "default",
  "language": "zh",
  "speed": 1.0
}
```

**回應:**
```json
{
  "job_id": "batch_20241201_123456",
  "status": "processing",
  "results": [
    {
      "index": 0,
      "audio_url": "/outputs/batch_0_20241201_123456.wav",
      "duration": 3.2
    }
  ],
  "progress": {
    "completed": 1,
    "total": 3,
    "percentage": 33.3
  }
}
```

#### GET /api/v1/batch/{job_id}

查詢批次工作狀態。

### 音訊處理

#### POST /api/v1/audio/normalize

音訊正規化處理。

**請求體:**
```json
{
  "audio": "base64_encoded_audio",
  "target_lufs": -16.0,
  "remove_silence": true
}
```

#### POST /api/v1/audio/convert

音訊格式轉換。

**請求體:**
```json
{
  "audio": "base64_encoded_audio",
  "output_format": "wav",
  "sample_rate": 22050,
  "bit_depth": 16
}
```

## 🔧 SDK 與客戶端

### Python SDK

```python
from voice_app_client import VoiceAPIClient

# 初始化客戶端
client = VoiceAPIClient("http://localhost:8000")

# TTS 合成
result = client.text_to_speech(
    text="Hello World",
    speaker_id="default",
    language="en"
)

# VC 轉換
with open("input.wav", "rb") as f:
    result = client.voice_conversion(
        audio_file=f.read(),
        target_speaker="speaker_001"
    )
```

### JavaScript SDK

```javascript
import { VoiceAPIClient } from './voice-app-client.js';

const client = new VoiceAPIClient('http://localhost:8000');

// TTS 合成
const ttsResult = await client.textToSpeech('Hello World', {
  speakerId: 'default',
  language: 'en'
});

// VC 轉換
const vcResult = await client.voiceConversion(audioFile, 'speaker_001');
```

## 📊 限制與配額

| 項目 | 限制 |
|------|------|
| 文字長度 | 1000 字元 |
| 音訊檔案大小 | 50MB |
| 並發請求數 | 可設定 (預設 2) |
| 批次處理數量 | 100 項目 |
| API 呼叫頻率 | 無限制 (本地部署) |

## 🔒 安全性

### 輸入驗證
- 所有輸入參數都經過驗證和清理
- 檔案類型檢查與大小限制
- SQL 注入防護

### 資料隱私
- 所有音訊處理在本地進行
- 不會上傳資料到外部服務
- 可設定自動清理暫存檔案

---

# docs/DEVELOPMENT.md - 開發指南

## 👨‍💻 Voice App 開發指南

本文檔說明 Voice App 的開發工作流程、程式碼規範和最佳實踐。

## 🏗️ 專案結構詳解

### 後端架構 (backend/)

```
backend/
├── api/                        # FastAPI 應用層
│   ├── dependencies.py        # 依賴注入與中間件
│   ├── middleware.py          # CORS、日誌、錯誤處理
│   ├── main.py                # FastAPI 應用入口
│   └── routers/               # API 路由模組
│       ├── health.py          # 健康檢查端點
│       ├── tts.py             # TTS API 路由
│       ├── vc.py              # VC API 路由
│       ├── batch.py           # 批次處理路由
│       └── profiles.py        # 說話者管理路由
├── core/                      # 核心功能模組
│   ├── config.py              # Pydantic 設定管理
│   ├── shared_cache.py        # AI 快取系統
│   ├── model_manager.py       # 模型載入與管理
│   ├── performance.py         # 效能優化設定
│   └── audio/                 # 音訊處理工具
│       ├── io.py              # 音訊 I/O 與轉換
│       └── normalization.py   # 音量正規化
├── services/                  # 業務邏輯服務
│   ├── tts_service.py         # TTS 引擎封裝
│   └── vc_service.py          # VC 引擎封裝
└── tests/                     # 測試套件
    ├── test_health.py         # 健康檢查測試
    ├── test_tts.py            # TTS API 測試
    └── test_vc.py             # VC API 測試
```

### 前端架構 (frontend/)

```
frontend/
├── shared/                    # 跨平台共用模組
│   ├── api_client.py          # Python API 客戶端
│   └── api_client.js          # JavaScript API 客戶端
├── react_app/                 # React Web 應用
│   ├── src/
│   │   ├── components/        # 可複用組件
│   │   ├── pages/             # 頁面組件
│   │   ├── services/          # API 服務層
│   │   ├── styles/            # CSS 樣式檔案
│   │   └── utils/             # 工具函數
│   ├── package.json           # NPM 依賴管理
│   └── webpack.config.js      # Webpack 配置
├── gradio_app/                # Gradio 研究界面
│   ├── components/            # Gradio 界面組件
│   ├── styles/                # 自訂樣式與主題
│   └── app.py                 # Gradio 應用入口
└── pyqt_app/                  # PyQt 桌面應用
    ├── widgets/               # PyQt 界面元件
    ├── styles/                # QSS 樣式檔案
    ├── utils/                 # 桌面應用工具
    └── main.py                # PyQt 應用入口
```

## 🔄 開發工作流程

### 1. 開發環境設定

```bash
# 克隆專案並切換到開發分支
git clone https://github.com/your-username/voice-app.git
cd voice-app
git checkout develop

# 建立開發環境
conda create -n voice-app-dev python=3.10
conda activate voice-app-dev

# 安裝開發依賴
python scripts/setup_dev.py

# 安裝開發工具
pip install black isort flake8 pytest pre-commit
```

### 2. Git 分支策略

我們使用 Git Flow 分支模型：

- `main`: 穩定發布版本
- `develop`: 開發整合分支
- `feature/*`: 功能開發分支
- `hotfix/*`: 緊急修復分支
- `release/*`: 發布準備分支

```bash
# 建立功能分支
git checkout develop
git pull origin develop
git checkout -b feature/add-bark-tts-engine

# 開發完成後提交
git add .
git commit -m "feat(tts): add Bark engine support with emotional control"

# 推送並建立 PR
git push origin feature/add-bark-tts-engine
```

### 3. 程式碼規範

#### Python 程式碼風格 (PEP 8)

```python
# 檔案頂部註釋
"""
TTS Service Module

Provides text-to-speech functionality with support for multiple engines
including XTTS, OpenVoice, and Bark.
"""

import os
from typing import Dict, List, Optional, Union
from pathlib import Path

# 類別定義
class TTSService:
    """Text-to-Speech service with multi-engine support."""

    def __init__(self, engine: str = "xtts", device: str = "cuda"):
        """
        Initialize TTS service.

        Args:
            engine: TTS engine name ("xtts", "openvoice", "bark")
            device: Computation device ("cuda", "cpu")
        """
        self.engine = engine
        self.device = device
        self._model = None

    async def synthesize(
        self,
        text: str,
        speaker_id: str = "default",
        **kwargs
    ) -> Dict[str, Union[str, float]]:
        """
        Synthesize speech from text.

        Args:
            text: Input text to synthesize
            speaker_id: Speaker identifier
            **kwargs: Additional engine-specific parameters

        Returns:
            Dictionary containing audio_url and metadata

        Raises:
            ValueError: If text is empty or too long
            RuntimeError: If synthesis fails
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")

        # Implementation here...
        return {
            "audio_url": "/outputs/tts_example.wav",
            "duration": 5.2,
            "processing_time": 3.1
        }
```

#### JavaScript 程式碼風格 (ESLint + Prettier)

```javascript
/**
 * Audio Player Component
 *
 * Provides audio playback controls with progress tracking
 */
import React, { useState, useRef, useEffect } from 'react';

const AudioPlayer = ({ src, filename = 'audio.wav', onDownload }) => {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration || 0);

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
    };
  }, [src]);

  // Component implementation...
};

export default AudioPlayer;
```

### 4. 測試策略

#### 單元測試 (pytest)

```python
# tests/test_tts_service.py
import pytest
from unittest.mock import Mock, patch
from backend.services.tts_service import TTSService

class TestTTSService:
    """Test suite for TTS service."""

    @pytest.fixture
    def tts_service(self):
        """Create TTS service instance for testing."""
        return TTSService(engine="xtts", device="cpu")

    @pytest.mark.asyncio
    async def test_synthesize_success(self, tts_service):
        """Test successful text synthesis."""
        result = await tts_service.synthesize("Hello World")

        assert "audio_url" in result
        assert result["duration"] > 0
        assert result["processing_time"] > 0

    @pytest.mark.asyncio
    async def test_synthesize_empty_text(self, tts_service):
        """Test synthesis with empty text raises ValueError."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await tts_service.synthesize("")

    @patch('backend.services.tts_service.torch')
    def test_model_loading(self, mock_torch, tts_service):
        """Test model loading with mocked torch."""
        mock_torch.cuda.is_available.return_value = True
        # Test implementation...
```

#### 整合測試

```python
# tests/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_tts_endpoint():
    """Test TTS endpoint with valid input."""
    payload = {
        "text": "Test synthesis",
        "speaker_id": "default",
        "language": "en"
    }
    response = client.post("/api/v1/tts", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "audio_url" in data
```

#### 前端測試 (Jest + React Testing Library)

```javascript
// frontend/react_app/src/components/__tests__/AudioPlayer.test.js
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import AudioPlayer from '../AudioPlayer';

describe('AudioPlayer', () => {
  const mockProps = {
    src: '/test/audio.wav',
    filename: 'test-audio.wav',
    onDownload: jest.fn()
  };

  test('renders audio player with controls', () => {
    render(<AudioPlayer {...mockProps} />);

    expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /stop/i })).toBeInTheDocument();
  });

  test('calls onDownload when download button clicked', () => {
    render(<AudioPlayer {...mockProps} />);

    const downloadBtn = screen.getByRole('button', { name: /download/i });
    fireEvent.click(downloadBtn);

    expect(mockProps.onDownload).toHaveBeenCalledWith(
      mockProps.src,
      mockProps.filename
    );
  });
});
```

### 5. 程式碼品質工具

#### 自動格式化與檢查

```bash
# Python 程式碼格式化
black backend/ scripts/
isort backend/ scripts/

# 程式碼風格檢查
flake8 backend/ scripts/
mypy backend/ scripts/

# JavaScript 格式化
cd frontend/react_app
npm run lint
npm run format
```

#### Pre-commit 掛鉤

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.44.0
    hooks:
      - id: eslint
        files: \.(js|jsx)$
        additional_dependencies:
          - eslint@8.44.0
          - eslint-plugin-react@7.32.2
```

## 🏛️ 架構設計原則

### 1. 模組化設計

每個功能模組都應該：
- **單一職責**: 每個模組只處理一種功能
- **鬆散耦合**: 模組間依賴最小化
- **高內聚**: 相關功能聚集在同一模組

```python
# 良好的模組化設計範例
class ModelManager:
    """統一的模型管理介面"""

    def load_model(self, model_type: str, engine: str) -> None:
        """載入指定類型和引擎的模型"""
        pass

    def unload_model(self, model_type: str) -> None:
        """卸載指定類型的模型"""
        pass

    def switch_engine(self, model_type: str, new_engine: str) -> None:
        """切換模型引擎"""
        pass
```

### 2. 依賴注入

使用依賴注入模式降低耦合度：

```python
# backend/api/dependencies.py
from fastapi import Depends
from backend.core.config import Settings
from backend.services.tts_service import TTSService

def get_settings() -> Settings:
    return Settings()

def get_tts_service(settings: Settings = Depends(get_settings)) -> TTSService:
    return TTSService(
        engine=settings.TTS_ENGINE,
        device=settings.DEVICE
    )

# 在路由中使用
@router.post("/tts")
async def synthesize_speech(
    request: TTSRequest,
    tts_service: TTSService = Depends(get_tts_service)
):
    return await tts_service.synthesize(request.text)
```

### 3. 錯誤處理策略

統一的錯誤處理和日誌記錄：

```python
# backend/core/exceptions.py
class VoiceAppException(Exception):
    """基礎例外類"""
    def __init__(self, message: str, code: str = "VOICE_APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

class TTSError(VoiceAppException):
    """TTS 相關錯誤"""
    pass

class VCError(VoiceAppException):
    """VC 相關錯誤"""
    pass

# 全域錯誤處理器
@app.exception_handler(VoiceAppException)
async def voice_app_exception_handler(request: Request, exc: VoiceAppException):
    logger.error(f"Voice App Error: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.message,
            "code": exc.code
        }
    )
```

## 🔧 開發最佳實踐

### 1. 異步程式設計

使用 async/await 提升效能：

```python
import asyncio
from typing import List

class BatchProcessor:
    """批次處理器"""

    async def process_batch_tts(
        self,
        texts: List[str],
        concurrency: int = 3
    ) -> List[Dict]:
        """並行處理多個 TTS 請求"""
        semaphore = asyncio.Semaphore(concurrency)

        async def process_single(text: str) -> Dict:
            async with semaphore:
                return await self.tts_service.synthesize(text)

        tasks = [process_single(text) for text in texts]
        return await asyncio.gather(*tasks)
```

### 2. 快取策略

實現多層快取提升效能：

```python
# backend/core/cache.py
import asyncio
from typing import Optional, Any
from functools import wraps

class CacheManager:
    """統一快取管理"""

    def __init__(self):
        self._memory_cache = {}
        self._disk_cache_path = Path("cache/")

    async def get(self, key: str) -> Optional[Any]:
        """從快取獲取資料"""
        # 先檢查記憶體快取
        if key in self._memory_cache:
            return self._memory_cache[key]

        # 再檢查磁碟快取
        disk_path = self._disk_cache_path / f"{key}.pkl"
        if disk_path.exists():
            import pickle
            with open(disk_path, 'rb') as f:
                data = pickle.load(f)
                self._memory_cache[key] = data  # 載入到記憶體
                return data

        return None

    async def set(self, key: str, value: Any, disk: bool = True):
        """設定快取資料"""
        self._memory_cache[key] = value

        if disk:
            import pickle
            self._disk_cache_path.mkdir(exist_ok=True)
            with open(self._disk_cache_path / f"{key}.pkl", 'wb') as f:
                pickle.dump(value, f)

def cache_result(cache_key_func):
    """快取裝飾器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = cache_key_func(*args, **kwargs)

            # 嘗試從快取獲取
            cached = await cache_manager.get(cache_key)
            if cached is not None:
                return cached

            # 執行函數並快取結果
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result)
            return result
        return wrapper
    return decorator
```

### 3. 監控與日誌

完善的監控和日誌系統：

```python
# backend/core/monitoring.py
import logging
import time
from functools import wraps
from typing import Dict, Any

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/voice_app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def monitor_performance(func):
    """效能監控裝飾器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time

            logger.info(f"{func.__name__} completed in {duration:.2f}s")
            return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {e}")
            raise

    return wrapper

class MetricsCollector:
    """效能指標收集器"""

    def __init__(self):
        self.metrics = {
            "tts_requests": 0,
            "vc_requests": 0,
            "total_processing_time": 0.0,
            "error_count": 0
        }

    def record_tts_request(self, processing_time: float):
        """記錄 TTS 請求"""
        self.metrics["tts_requests"] += 1
        self.metrics["total_processing_time"] += processing_time

    def record_error(self):
        """記錄錯誤"""
        self.metrics["error_count"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計資料"""
        total_requests = self.metrics["tts_requests"] + self.metrics["vc_requests"]
        avg_processing_time = (
            self.metrics["total_processing_time"] / total_requests
            if total_requests > 0 else 0
        )

        return {
            **self.metrics,
            "total_requests": total_requests,
            "average_processing_time": avg_processing_time,
            "error_rate": self.metrics["error_count"] / total_requests if total_requests > 0 else 0
        }
```

## 📊 效能優化指南

### 1. GPU 記憶體管理

```python
import torch
from contextlib import contextmanager

@contextmanager
def gpu_memory_guard():
    """GPU 記憶體保護上下文管理器"""
    try:
        yield
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

class ModelLoader:
    """智能模型載入器"""

    def __init__(self, max_models: int = 2):
        self.loaded_models = {}
        self.max_models = max_models
        self.access_count = {}

    def load_model(self, model_key: str, loader_func):
        """載入模型，支援 LRU 快取"""
        if model_key in self.loaded_models:
            self.access_count[model_key] += 1
            return self.loaded_models[model_key]

        # 如果超過最大模型數，卸載最少使用的模型
        if len(self.loaded_models) >= self.max_models:
            lru_key = min(self.access_count, key=self.access_count.get)
            self.unload_model(lru_key)

        with gpu_memory_guard():
            model = loader_func()
            self.loaded_models[model_key] = model
            self.access_count[model_key] = 1

        return model

    def unload_model(self, model_key: str):
        """卸載模型釋放記憶體"""
        if model_key in self.loaded_models:
            del self.loaded_models[model_key]
            del self.access_count[model_key]

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
```

### 2. 音訊處理優化

```python
import librosa
import numpy as np
from concurrent.futures import ThreadPoolExecutor

class AudioProcessor:
    """高效音訊處理器"""

    def __init__(self, target_sr: int = 22050):
        self.target_sr = target_sr
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def process_audio_async(self, audio_path: str) -> np.ndarray:
        """異步音訊處理"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._process_audio_sync,
            audio_path
        )

    def _process_audio_sync(self, audio_path: str) -> np.ndarray:
        """同步音訊處理核心邏輯"""
        # 載入音訊
        audio, sr = librosa.load(audio_path, sr=None)

        # 重新取樣
        if sr != self.target_sr:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=self.target_sr)

        # 正規化
        audio = self._normalize_audio(audio)

        return audio

    def _normalize_audio(self, audio: np.ndarray, target_lufs: float = -16.0) -> np.ndarray:
        """音量正規化到目標 LUFS"""
        try:
            import pyloudnorm as pyln
            meter = pyln.Meter(self.target_sr)
            loudness = meter.integrated_loudness(audio)
            normalized_audio = pyln.normalize.loudness(audio, loudness, target_lufs)
            return normalized_audio
        except ImportError:
            # 回退到簡單正規化
            return audio / np.max(np.abs(audio)) * 0.95
```

## 🚀 部署與發布

### 1. 環境分離

使用不同的配置檔案管理各環境：

```python
# backend/core/config.py
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """應用設定"""

    # 環境標識
    ENV: str = "development"
    DEBUG: bool = True

    # 伺服器設定
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # AI 設定
    DEVICE: str = "cuda"
    FP16: bool = True
    TTS_ENGINE: str = "xtts"
    VC_ENGINE: str = "rvc"

    # 路徑設定
    AI_CACHE_ROOT: str = "/tmp/voice-app-cache"
    OUTPUT_DIR: Optional[str] = None
    SPEAKER_DIR: Optional[str] = None

    # 效能設定
    MAX_CONCURRENCY: int = 2
    MODEL_CACHE_SIZE: int = 3

    class Config:
        env_file = ".env"

    def __post_init__(self):
        """設定後處理"""
        if self.OUTPUT_DIR is None:
            self.OUTPUT_DIR = f"{self.AI_CACHE_ROOT}/outputs"
        if self.SPEAKER_DIR is None:
            self.SPEAKER_DIR = f"{self.AI_CACHE_ROOT}/speakers"

# 環境特定設定
class DevelopmentSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

class ProductionSettings(Settings):
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    MAX_CONCURRENCY: int = 4

def get_settings() -> Settings:
    """根據環境變數返回對應設定"""
    env = os.getenv("ENV", "development")

    if env == "production":
        return ProductionSettings()
    else:
        return DevelopmentSettings()
```

### 2. CI/CD 工作流程

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ develop, main ]
  pull_request:
    branches: [ develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r backend/requirements.txt
        pip install -r backend/requirements-dev.txt

    - name: Run tests
      run: |
        cd backend
        python -m pytest tests/ -v --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml

  lint:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.10

    - name: Install linting tools
      run: |
        pip install black isort flake8 mypy

    - name: Run linting
      run: |
        black --check backend/ scripts/
        isort --check-only backend/ scripts/
        flake8 backend/ scripts/
        mypy backend/

  frontend-test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install frontend dependencies
      run: |
        cd frontend/react_app
        npm ci

    - name: Run frontend tests
      run: |
        cd frontend/react_app
        npm run test -- --coverage --watchAll=false

    - name: Build frontend
      run: |
        cd frontend/react_app
        npm run build
```

### 3. Docker 化部署

```dockerfile
# Dockerfile.backend
FROM python:3.10-slim

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# 建立應用目錄
WORKDIR /app

# 複製並安裝 Python 依賴
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY backend/ ./backend/
COPY frontend/shared/ ./frontend/shared/

# 建立快取目錄
RUN mkdir -p /app/cache/models /app/cache/outputs

# 設定環境變數
ENV AI_CACHE_ROOT=/app/cache
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/healthz || exit 1

# 啟動指令
CMD ["python", "-m", "backend.api.main"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  voice-app-backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - ENV=production
      - DEVICE=cpu
      - AI_CACHE_ROOT=/app/cache
    volumes:
      - ./cache:/app/cache
      - ./logs:/app/logs
    restart: unless-stopped

  voice-app-frontend:
    build:
      context: frontend/react_app
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - voice-app-backend
    environment:
      - REACT_APP_API_URL=http://voice-app-backend:8000
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - voice-app-frontend
      - voice-app-backend
    restart: unless-stopped
```

## 📝 文檔維護

### 1. API 文檔自動生成

FastAPI 自動生成 OpenAPI 文檔，可以通過以下方式自訂：

```python
# backend/api/main.py
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI(
    title="Voice App API",
    description="Personal Voice Synthesis & Conversion Tool",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.15.5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.15.5/swagger-ui.css",
    )
```

### 2. 程式碼文檔

使用 Sphinx 生成程式碼文檔：

```bash
# 安裝 Sphinx
pip install sphinx sphinx-rtd-theme

# 初始化文檔專案
cd docs/
sphinx-quickstart

# 配置 conf.py
# 生成文檔
make html
```

## 🔍 除錯與問題排解

### 1. 常見問題診斷

```python
# scripts/diagnose.py
"""系統診斷腳本"""

import torch
import platform
import subprocess
from pathlib import Path

def check_system():
    """檢查系統環境"""
    print("=== 系統資訊 ===")
    print(f"作業系統: {platform.system()} {platform.release()}")
    print(f"Python 版本: {platform.python_version()}")
    print(f"CPU 核心數: {os.cpu_count()}")

    # 檢查 GPU
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name()}")
        print(f"CUDA 版本: {torch.version.cuda}")
        print(f"可用記憶體: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print("GPU: 不可用")

def check_dependencies():
    """檢查依賴套件"""
    required_packages = [
        "torch", "torchaudio", "transformers",
        "fastapi", "gradio", "PyQt6"
    ]

    print("\n=== 套件版本 ===")
    for package in required_packages:
        try:
            module = __import__(package)
            version = getattr(module, "__version__", "未知")
            print(f"{package}: {version}")
        except ImportError:
            print(f"{package}: 未安裝")

def check_models():
    """檢查模型狀態"""
    from backend.core.config import get_settings

    settings = get_settings()
    cache_root = Path(settings.AI_CACHE_ROOT)

    print(f"\n=== 模型快取 ({cache_root}) ===")

    if cache_root.exists():
        model_files = list(cache_root.glob("**/*.bin")) + list(cache_root.glob("**/*.pth"))
        print(f"找到 {len(model_files)} 個模型檔案")

        total_size = sum(f.stat().st_size for f in model_files) / 1e9
        print(f"總大小: {total_size:.1f} GB")
    else:
        print("快取目錄不存在")

if __name__ == "__main__":
    check_system()
    check_dependencies()
    check_models()
```

### 2. 效能分析

```python
# scripts/profile.py
"""效能分析腳本"""

import time
import cProfile
import pstats
from memory_profiler import profile
from backend.services.tts_service import TTSService

@profile
def profile_tts():
    """分析 TTS 效能"""
    service = TTSService(engine="xtts", device="cuda")

    start_time = time.time()
    result = service.synthesize("這是效能測試文字")
    end_time = time.time()

    print(f"TTS 處理時間: {end_time - start_time:.2f} 秒")
    return result

def run_profiling():
    """執行效能分析"""
    profiler = cProfile.Profile()
    profiler.enable()

    # 執行要分析的函數
    profile_tts()

    profiler.disable()

    # 儲存結果
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # 顯示前 20 個最耗時的函數

    # 儲存到檔案
    stats.dump_stats('performance_profile.prof')

if __name__ == "__main__":
    run_profiling()
```

---

通過遵循以上開發指南，你可以建立高品質、可維護的 Voice App 專案。記住始終遵循最佳實踐，編寫清晰的程式碼，並保持良好的測試覆蓋率。# 🎙️ Voice App MVP - Personal Voice Synthesis & Conversion Tool

個人用語音合成與轉換工具，支援文字轉語音(TTS)和語音轉換(VC)功能。提供三種前端界面：React Web應用、Gradio研究界面和PyQt桌面應用。

## ✨ 核心功能

- **🎤 文字轉語音 (TTS)**: 支援多語言、多說話者、語速控制
- **🎭 語音轉換 (VC)**: 將錄音轉換為不同說話者聲線
- **👤 說話者管理**: 可自定義說話者資料與聲音樣本
- **📱 多平台支援**: Web、桌面、研究界面三合一
- **💾 離線快取**: 模型本地緩存，支援離線使用
- **🔄 引擎切換**: 透過設定檔輕鬆切換TTS/VC引擎

## 🏗️ 系統架構

```
voice-app/
├── backend/                    # FastAPI 後端服務
│   ├── api/                   # API 路由與中間件
│   ├── core/                  # 核心配置與模型管理
│   ├── services/              # TTS/VC 服務實作
│   └── tests/                 # API 測試
├── frontend/                   # 前端應用
│   ├── shared/                # 共用 API 客戶端
│   ├── react_app/             # React Web 應用
│   ├── gradio_app/            # Gradio 研究界面
│   └── pyqt_app/              # PyQt 桌面應用
├── scripts/                   # 工具腳本
└── docs/                      # 專案文件
```

## 🚀 快速開始

### 1. 環境安裝

```bash
# 建立 Conda 環境
conda create -n audio-speech-lab python=3.10
conda activate audio-speech-lab

# 設定快取路徑 (重要!)
export AI_CACHE_ROOT=/your/preferred/cache/path

# 自動安裝依賴與設定
python scripts/setup_dev.py
```

### 2. 啟動服務

```bash
# 方法一: 一鍵啟動所有前端
python scripts/start_all.py

# 方法二: 分別啟動
# 後端
cd backend && python -m api.main

# React (新終端)
cd frontend/react_app && npm start

# Gradio (新終端)
cd frontend/gradio_app && python app.py

# PyQt (新終端)
cd frontend/pyqt_app && python main.py
```

### 3. 訪問應用

- **React Web**: http://localhost:3000
- **Gradio Interface**: http://localhost:7860
- **PyQt Desktop**: 桌面應用視窗

### 4. 測試API

```bash
# 健康檢查
python scripts/test_api.py --quick

# 完整測試
python scripts/test_api.py
```

## 🎛️ 配置說明

### 環境變數 (.env)

```env
# 設備與效能
DEVICE=cuda
FP16=true
MAX_CONCURRENCY=2

# 引擎選擇 (修改後重啟即切換)
TTS_ENGINE=xtts      # xtts | openvoice
VC_ENGINE=rvc        # rvc | sovits

# 快取與路徑 (關鍵設定)
AI_CACHE_ROOT=/your/ai/warehouse/path
OUTPUT_DIR=${AI_CACHE_ROOT}/outputs/voice-app
SPEAKER_DIR=${AI_CACHE_ROOT}/voice/speakers
```

### 引擎切換

只需修改 `.env` 中的引擎參數：

```bash
# 切換到 OpenVoice TTS
TTS_ENGINE=openvoice

# 切換到 So-VITS-SVC 語音轉換
VC_ENGINE=sovits

# 重啟後端即可生效
```

## 📡 API 介面

### TTS 語音合成

```bash
curl -X POST http://localhost:8000/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，這是語音合成測試",
    "speaker_id": "default",
    "language": "zh",
    "speed": 1.0
  }'
```

### VC 語音轉換

```bash
curl -X POST http://localhost:8000/api/v1/vc \
  -H "Content-Type: application/json" \
  -d '{
    "source_audio": "base64_encoded_audio_data",
    "target_speaker": "speaker_001",
    "preserve_pitch": true
  }'
```

完整 API 文檔請參閱 [docs/API.md](docs/API.md)

## 🖥️ 前端特色

### React Web 應用
- 現代化響應式界面
- 拖放上傳文件
- 即時音頻預覽
- 原生 CSS 樣式系統

### Gradio 研究界面
- AI 研究人員友好
- 快速原型測試
- 自動生成界面
- 支援批量處理

### PyQt 桌面應用
- 原生桌面體驗
- 離線模型快取
- 拖放批量處理
- 深色/淺色主題

## 🔧 開發指南

### 專案結構說明

- `backend/api/`: FastAPI 路由與中間件
- `backend/core/`: 核心配置、模型管理、性能優化
- `backend/services/`: TTS/VC 引擎封裝
- `frontend/shared/`: 跨平台 API 客戶端
- `scripts/`: 開發工具與測試腳本

### Git 工作流程

```bash
# 創建功能分支
git checkout -b feature/new-tts-engine

# 提交變更 (使用 Conventional Commits)
git commit -m "feat(tts): add OpenVoice engine support"
git commit -m "fix(vc): resolve pitch preservation issue"
git commit -m "docs(readme): update setup instructions"

# 合併到主分支
git checkout develop
git merge --no-ff feature/new-tts-engine
```

### 測試策略

```bash
# 單元測試
cd backend && python -m pytest tests/

# API 整合測試
python scripts/test_api.py

# 前端測試
cd frontend/react_app && npm test
```

## 📚 文檔與資源

- [📖 設定指南](docs/SETUP.md) - 詳細安裝與配置說明
- [🔌 API 文檔](docs/API.md) - 完整 API 參考
- [👨‍💻 開發指南](docs/DEVELOPMENT.md) - 開發工作流程與最佳實踐

## 🔍 故障排除

### 常見問題

**問題: 後端啟動失敗**
```bash
# 檢查依賴是否安裝完整
pip install -r backend/requirements.txt

# 檢查 CUDA 是否可用
python -c "import torch; print(torch.cuda.is_available())"
```

**問題: 模型下載失敗**
```bash
# 檢查快取目錄權限
ls -la $AI_CACHE_ROOT

# 手動創建目錄
python scripts/download_models.py --setup
```

**問題: 前端連線失敗**
```bash
# 檢查後端健康狀態
curl http://localhost:8000/healthz

# 檢查防火牆設定
netstat -an | grep :8000
```

### 效能優化

- **VRAM 不足**: 調整 `MAX_CONCURRENCY=1` 或使用 CPU 模式
- **處理速度慢**: 確保 GPU 驅動與 CUDA 版本匹配
- **音質問題**: 檢查 `LUFS` 正規化設定


## 📄 授權條款

MIT License - 詳見 [LICENSE](LICENSE) 文件

## 🙏 致謝

- [XTTS](https://github.com/coqui-ai/TTS) - 高品質文字轉語音
- [RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) - 語音轉換技術
- [FastAPI](https://fastapi.tiangolo.com/) - 現代 Python Web 框架
- [React](https://reactjs.org/) - 前端開發框架
- [Gradio](https://gradio.app/) - AI 模型界面生成
- [PyQt](https://www.riverbankcomputing.com/software/pyqt/) - 跨平台桌面應用框架

---

**Voice App MVP** - 讓語音合成變得簡單易用！ 🎤✨

---

# docs/SETUP.md - 詳細安裝指南

## 🛠️ 系統需求

### 最低需求
- **作業系統**: Windows 10+, macOS 10.14+, Linux Ubuntu 18.04+
- **Python**: 3.8+ (建議 3.10)
- **記憶體**: 8GB RAM (建議 16GB+)
- **儲存空間**: 10GB (模型快取需額外空間)

### 推薦需求
- **GPU**: NVIDIA RTX 3060+ (8GB+ VRAM)
- **CPU**: 8核心以上
- **記憶體**: 32GB RAM
- **儲存**: SSD 硬碟

### 軟體依賴
- **Node.js**: 14+ (React 前端)
- **FFmpeg**: 音訊處理
- **Git**: 版本控制
- **CUDA**: 11.8+ (GPU 加速)

