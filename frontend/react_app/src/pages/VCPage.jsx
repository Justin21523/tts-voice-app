// ============ src/pages/VCPage.js ============
import React, { useState } from 'react';
import VCForm from '../components/VCForm';
import AudioPlayer from '../components/AudioPlayer';
import apiClient from '../services/api';

const VCPage = () => {
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleResult = (vcResult) => {
    setResult(vcResult);
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
        <h1 className="page-title">Voice Conversion</h1>
        <p className="page-subtitle">Convert your voice to match different speakers</p>
      </div>

      <div className="vc-page">
        <div className="vc-upload-section">
          <div className="card">
            <div className="card-header">
              <h2>Input</h2>
            </div>
            <div className="card-body">
              <VCForm onResult={handleResult} onError={handleError} />
            </div>
          </div>
        </div>

        <div className="vc-result-section">
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
                <div className="vc-result">
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
                        <strong>Processing:</strong><br />
                        {result.processing_time ? `${result.processing_time.toFixed(1)}s` : 'N/A'}
                      </div>
                      <div>
                        <strong>Status:</strong><br />
                        ✅ Completed
                      </div>
                    </div>
                  </div>

                  <AudioPlayer
                    src={apiClient.getAudioUrl(result.audio_url)}
                    filename={`vc_${Date.now()}.wav`}
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
                    🎭
                  </div>
                  <p>Upload audio and select target speaker to convert voice</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VCPage;