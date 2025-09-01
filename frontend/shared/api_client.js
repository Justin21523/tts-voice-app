/**
 * JavaScript API client for Voice App backend
 */
class VoiceAPIClient {
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.defaultHeaders = {
      "Content-Type": "application/json",
      "User-Agent": "VoiceApp-WebClient/1.0",
    };
  }

  /**
   * Make HTTP request with error handling
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      headers: { ...this.defaultHeaders, ...options.headers },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Request failed: ${error.message}`);
      return { error: error.message };
    }
  }

  /**
   * Check backend health status
   */
  async healthCheck() {
    return await this.request("/healthz");
  }

  /**
   * Convert text to speech
   */
  async textToSpeech(text, options = {}) {
    const payload = {
      text,
      speaker_id: options.speakerId || "default",
      language: options.language || "zh",
      speed: options.speed || 1.0,
    };

    return await this.request("/api/v1/tts", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  /**
   * Convert voice to target speaker
   */
  async voiceConversion(audioFile, targetSpeaker, options = {}) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = async () => {
        const arrayBuffer = reader.result;
        const uint8Array = new Uint8Array(arrayBuffer);
        const audioB64 = this.arrayBufferToBase64(uint8Array);

        const payload = {
          source_audio: audioB64,
          target_speaker: targetSpeaker,
          preserve_pitch: options.preservePitch !== false,
        };

        const result = await this.request("/api/v1/vc", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        resolve(result);
      };

      reader.onerror = () => reject(new Error("File read failed"));
      reader.readAsArrayBuffer(audioFile);
    });
  }

  /**
   * Get available speaker profiles
   */
  async getProfiles() {
    return await this.request("/api/v1/profiles");
  }

  /**
   * Batch text-to-speech conversion
   */
  async batchTTS(texts, options = {}) {
    const payload = {
      texts,
      ...options,
    };

    return await this.request("/api/v1/batch/tts", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  /**
   * Get audio file URL for playback
   */
  getAudioUrl(audioPath) {
    if (audioPath.startsWith("/")) {
      return `${this.baseUrl}${audioPath}`;
    }
    return audioPath;
  }

  /**
   * Download audio file
   */
  async downloadAudio(audioUrl, filename) {
    try {
      const fullUrl = this.getAudioUrl(audioUrl);
      const response = await fetch(fullUrl);

      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }

      const blob = await response.blob();

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename || "audio.wav";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      return true;
    } catch (error) {
      console.error("Download failed:", error);
      return false;
    }
  }

  /**
   * Convert ArrayBuffer to Base64
   */
  arrayBufferToBase64(buffer) {
    let binary = "";
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  }

  /**
   * Validate audio file type
   */
  isValidAudioFile(file) {
    const validTypes = ["audio/wav", "audio/mp3", "audio/ogg", "audio/m4a"];
    return validTypes.includes(file.type);
  }

  /**
   * Format file size for display
   */
  formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  }
}

// Export for different module systems
if (typeof module !== "undefined" && module.exports) {
  module.exports = VoiceAPIClient;
}

if (typeof window !== "undefined") {
  window.VoiceAPIClient = VoiceAPIClient;
}
