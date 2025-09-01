// ============ src/pages/TTSPage.jsx ============
import React, { useState } from 'react';
import TTSForm from '../components/TTSForm';
import AudioPlayer from '../components/AudioPlayer';
import apiClient from '../services/api';

const TTSPage = () => {
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleResult = (ttsResult) => {
    setResult(ttsResult);
    setError('');
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
    setResult(null);
  };

  const handleDownload = async (audioUrl, filename) => {
    const success = await apiClient.downloadAudio(audioUrl, filename);
    if (!success) {
      setError('Download failed');
    }
  };

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Text-to-Speech</h1>
        <p className="page-subtitle">Convert text to natural-sounding speech</p>
      </div>

      <div className="tts-page">
        <div className="tts-form-section">
          <div className="card">
            <div className="card-header">
              <h2>Input</h2>
            </div>
            <div className="card-body">
              <TTSForm onResult={handleResult} onError={handleError} />
            </div>
          </div>
        </div>

        <div className="tts-result-section">
          <div className="card">
            <div className="card-header">
              <h2>Result</h2>
            </div>
            <div className="card-body">
              {error && (
                <div className="alert alert-error" style={{
                  padding: 'var(--spacing-sm)',
                  backgroundColor: '#fee2e2',
                  color: '#dc2626',
                  border: '1px solid #fecaca',
                  borderRadius: 'var(--border-radius)',
                  marginBottom: 'var(--spacing-md)'
                }}>
                  ❌ {error}
                </div>
              )}

              {result ? (
                <div className="tts-result">
                  <div className="result-info" style={{ marginBottom: 'var(--spacing-md)' }}>
                    <div className="result-stats" style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                      gap: 'var(--spacing-sm)',
                      padding: 'var(--spacing-sm)',
                      backgroundColor: 'var(--bg-secondary)',
                      borderRadius: 'var(--border-radius)',
                      fontSize: 'var(--font-size-sm)'
                    }}>
                      <div>
                        <strong>Duration:</strong><br />
                        {result.duration ? `${result.duration.toFixed(1)}s` : 'N/A'}
                      </div>
                      <div>
                        <strong>Processing:</strong><br />
                        {result.processing_time ? `${result.processing_time.toFixed(1)}s` : 'N/A'}
                      </div>
                    </div>
                  </div>

                  <AudioPlayer
                    src={apiClient.getAudioUrl(result.audio_url)}
                    filename={`tts_${Date.now()}.wav`}
                    onDownload={handleDownload}
                  />
                </div>
              ) : (
                <div className="no-result" style={{
                  textAlign: 'center',
                  padding: 'var(--spacing-xl)',
                  color: 'var(--text-muted)'
                }}>
                  <div style={{ fontSize: 'var(--font-size-2xl)', marginBottom: 'var(--spacing-sm)' }}>
                    🎤
                  </div>
                  <p>Enter text and click "Generate Speech" to create audio</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TTSPage;