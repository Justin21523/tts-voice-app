# 🟦 1. 文字輸出／LLM 對話、知識問答（RAG/Agent 整合）

| 模型/工具       | 主要應用/特色                                 | Hugging Face/GitHub  | 使用方式 & 前端       | 格式/插件支援         |
|-----------------|----------------------------------------------|----------------------|----------------------|----------------------|
| Deepseek LLM    | 長上下文、推理強、支援 Function Calling、RAG  | [deepseek-ai](https://huggingface.co/deepseek-ai) | transformers、llama.cpp、FastChat、text-gen-webui | fp16/gguf、API       |
| Qwen            | 中文極強、Qwen-VL多模態、版本齊全            | [Qwen](https://huggingface.co/Qwen) | transformers、OpenCompass、FastChat | fp16/gguf、API       |
| Yi              | 開源、可商用，6B/34B中文/英文雙優            | [01-ai](https://huggingface.co/01-ai) | transformers、text-gen-webui、Ollama | fp16/gguf            |
| ChatGLM3        | 中文本地對話、指令精細、商用                  | [THUDM/ChatGLM3](https://huggingface.co/THUDM/chatglm3-6b) | transformers、web demo | API、fp16/gguf        |
| Baichuan        | 中文知識庫/FAQ、百川系列多大小                | [baichuan-inc](https://huggingface.co/baichuan-inc) | transformers、text-gen-webui | fp16/gguf            |
| MiniCPM         | 輕量LLM、嵌入式應用、本地端部署快              | [OpenBMB/MiniCPM](https://huggingface.co/openbmb/MiniCPM) | transformers、llama.cpp、Ollama | fp16/gguf            |
| OpenHermes/MythoMax | 無審查話題/角色扮演、英文NSFW應用          | [teknium](https://huggingface.co/teknium) | text-gen-webui、KoboldAI | LoRA、fp16/gguf      |

### RAG/Agent框架
| 工具/框架          | 功能/應用                                  | 官方資源                     | 常用方式              |
|-------------------|-------------------------------------------|-----------------------------|-----------------------|
| LangChain         | 知識庫、WebSearch、流程自動化、Agent       | [langchain-ai/langchain](https://github.com/langchain-ai/langchain) | Python CLI/Notebook   |
| LlamaIndex        | 文件RAG、資料夾問答、向量庫查詢            | [jerryjliu/llama_index](https://github.com/jerryjliu/llama_index) | Python CLI/Notebook   |
| Haystack          | 企業級RAG、多模態、API/向量庫              | [deepset-ai/haystack](https://github.com/deepset-ai/haystack) | Python CLI/Web UI     |
| text-gen-webui    | 多模型WebUI，RAG/網頁搜尋插件多             | [oobabooga/text-generation-webui](https://github.com/oobabooga/text-generation-webui) | 本地Web介面           |

---

# 🟩 2. 圖像輸出（文字生圖、動畫、影片、修復潤飾等）

### a. 文字→圖像（生圖）

| 模型/工具             | 主要應用/特色                             | Hugging Face/GitHub   | 使用方式 & 前端     | 格式/支援             |
|-----------------------|-------------------------------------------|-----------------------|--------------------|----------------------|
| Stable Diffusion      | 泛用高效生圖，多LoRA/插件                  | [stabilityai](https://huggingface.co/stabilityai/stable-diffusion-2-1) | AUTOMATIC1111、ComfyUI、InvokeAI | .ckpt/.safetensors、diffusers |
| SDXL                  | 超高畫質、多風格                          | [stabilityai/SDXL](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) | 上述同上             | .safetensors、diffusers      |
| DeepFloyd IF          | 細節強、插畫/寫實                          | [DeepFloyd/IF](https://huggingface.co/DeepFloyd/IF-I-XL-v1.0) | diffusers、ComfyUI   | .safetensors                |
| PixArt-α/Sigma        | 多題材插畫、接近MJ                        | [PixArt-Alpha](https://huggingface.co/PixArt-alpha) | ComfyUI、diffusers   | .safetensors                |
| Stable Cascade        | 速度極快、Runway新一代                    | [stabilityai/stable-cascade](https://huggingface.co/stabilityai/stable-cascade) | diffusers、WebUI     | .safetensors                |

### b. 文字→影片（動畫/動圖/短片）

| 模型/工具            | 主要應用/特色                               | Hugging Face/GitHub                   | 使用方式 & 前端      | 格式/支援           |
|----------------------|---------------------------------------------|---------------------------------------|---------------------|---------------------|
| AnimateDiff          | SD動畫/動圖LoRA，二創/插畫動態              | [guoyww/AnimateDiff](https://github.com/guoyww/AnimateDiff) | ComfyUI、A1111 WebUI | .ckpt/.safetensors |
| Stable Video Diffusion| 文生短片，寫實/動漫                         | [stabilityai/stable-video-diffusion-img2vid](https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt) | ComfyUI、diffusers  | .safetensors       |
| ModelScope T2V       | 中文/多語T2V，短片創作                      | [damo-vilab/text-to-video-ms-1.7b](https://huggingface.co/damo-vilab/text-to-video-ms-1.7b) | Colab、CLI          | .bin/.pth          |
| VideoCrafter2        | 高品質T2V多語                              | [videocrafter2](https://github.com/VideoCrafter/VideoCrafter2) | CLI、Colab          | .pth               |

### c. 圖像修復/潤飾

| 模型/工具          | 主要應用/特色                                 | Hugging Face/GitHub                | 使用方式 & 前端        | 格式/支援         |
|--------------------|-----------------------------------------------|------------------------------------|-----------------------|-------------------|
| Real-ESRGAN        | 圖片/影片超分辨率，多風格，動畫也支援           | [xinntao/Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) | CLI、ComfyUI、A1111   | .pth/.onnx/.ncnn  |
| GFPGAN/CodeFormer  | 人臉修復，自然還原                            | [TencentARC/GFPGAN](https://github.com/TencentARC/GFPGAN) / [sczhou/CodeFormer](https://github.com/sczhou/CodeFormer) | WebUI/CLI             | .pth/.onnx        |
| Anime4K/Waifu2x    | 動漫放大、去鋸齒、補色                         | [Waifu2x](https://github.com/nagadomi/waifu2x) | GUI/CLI、Video2X      | 多格式            |
| Video2X/Flowframes | 多幀影片批次增強/補幀                          | [Video2X](https://github.com/k4yt3x/video2x) / [Flowframes](https://nmkd.itch.io/flowframes) | GUI/CLI               | 多格式            |
| EDVR/BasicVSR      | 專業影片修復、時序穩定、動畫/舊片重製           | [xinntao/EDVR](https://github.com/xinntao/EDVR) / [BasicVSR](https://github.com/ckkelvinchan/BasicVSR_PyTorch) | CLI                   | .pth              |

---

# 🟨 3. 聲音輸出（語音合成、聲音複製）

| 模型/工具          | 主要應用/特色                             | Hugging Face/GitHub            | 使用方式 & 前端        | 格式/支援         |
|--------------------|-------------------------------------------|-------------------------------|-----------------------|-------------------|
| OpenVoice          | 少樣本快速仿聲，多語TTS                   | [myshell-ai/OpenVoice](https://github.com/myshell-ai/OpenVoice) | WebUI/CLI           | .pth              |
| Coqui XTTS         | 多語高品質仿聲TTS，情感強                 | [coqui-ai/TTS](https://github.com/coqui-ai/TTS) | WebUI/CLI           | .pth              |
| Bark               | 多情感語音生成、支援背景音樂               | [suno-ai/Bark](https://github.com/suno-ai/bark) | CLI、WebUI           | .pth              |
| So-VITS-SVC        | 歌聲AI、任意語音/歌手仿聲                 | [so-vits-svc](https://github.com/svc-develop-team/so-vits-svc) | WebUI/CLI           | .pth              |
| RVC                | 任意聲線轉換/克隆，動漫/主播/角色           | [RVC-Project](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) | WebUI、CLI           | .pth              |

---

# 🟧 4. 圖像分析/理解（圖片→文字/特徵）

| 模型/工具              | 主要應用/特色                             | Hugging Face/GitHub         | 使用方式 & 前端         | 格式/支援         |
|------------------------|-------------------------------------------|-----------------------------|------------------------|-------------------|
| BLIP-2/3               | 圖像描述/Caption，自動物件/情緒分析        | [Salesforce/LAVIS](https://github.com/salesforce/LAVIS) | CLI、Notebook、Gradio | .pth/.bin         |
| MiniGPT-4/LLaVA        | 多模態圖文問答，支援本地/多語             | [MiniGPT-4](https://github.com/Vision-CAIR/MiniGPT-4) / [LLaVA](https://github.com/haotian-liu/LLaVA) | CLI、WebUI、Notebook | .pth              |
| Qwen-VL/VisualGLM      | 中文圖像描述/分析，支援動漫/插畫           | [Qwen-VL](https://github.com/Qwen-VL) / [VisualGLM](https://github.com/THUDM/VisualGLM-6B) | CLI、Gradio          | .bin/.pth         |
| AniCaption/AniGPT      | 動漫角色/插畫特化描述/特徵標註            | [AniCaption](https://github.com/nlpxucan/AniCaption) / [AniGPT](https://github.com/cpbox/AniGPT) | CLI、WebUI           | .pth              |
| WD14-tagger/DeepDanbooru| 動漫/插畫標註，屬性批次標籤               | [WD14-tagger](https://github.com/toriato/stable-diffusion-webui-wd14-tagger) / [DeepDanbooru](https://github.com/KichangKim/DeepDanbooru) | WebUI、CLI           | .pth              |

---

# 🟫 5. 影片/多幀圖像處理

| 模型/工具          | 主要應用/特色                             | Hugging Face/GitHub        | 使用方式 & 前端          | 格式/支援         |
|--------------------|-------------------------------------------|----------------------------|-------------------------|-------------------|
| Real-ESRGAN/Anime4K/Video2X | 多幀修復/增強/動畫放大，影片補幀        | 上述各專案                | CLI、WebUI、GUI          | 多格式            |
| RIFE/DAIN/FLAVR    | AI補幀、畫面流暢提升                      | [RIFE](https://github.com/megvii-research/ECCV2022-RIFE) / [DAIN](https://github.com/baowenbo/DAIN) / [FLAVR](https://github.com/tarun005/FLAVR) | Flowframes、CLI          | .pth              |
| EDVR/BasicVSR      | 老片/動畫專業修復，時序穩定               | [EDVR](https://github.com/xinntao/EDVR) / [BasicVSR](https://github.com/ckkelvinchan/BasicVSR_PyTorch) | CLI                    | .pth              |
| Flowframes         | 補幀/超分整合GUI，支援多AI模型             | [Flowframes](https://nmkd.itch.io/flowframes) | GUI                     | 多格式            |
