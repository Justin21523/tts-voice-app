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
