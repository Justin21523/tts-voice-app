// ============ src/components/TTSForm.jsx ============
import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';

const TTSForm = ({ onResult, onError }) => {
  const [text, setText] = useState('');
  const [speakerId, setSpeakerId] = useState('default');
  const [language, setLanguage] = useState('zh');
  const [speed, setSpeed] = useState(1.0);
  const [loading, setLoading] = useState(false);
  const [profiles, setProfiles] = useState([]);

  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    try {
      const result = await apiClient.getProfiles();
      if (result.profiles) {
        setProfiles(result.profiles);
      }
    } catch (error) {
      console.error('Failed to load profiles:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!text.trim()) {
      onError('Please enter text to synthesize');
      return;
    }

    setLoading(true);
    try {
      const result = await apiClient.textToSpeech(text, {
        speakerId,
        language,
        speed
      });

      if (result.error) {
        onError(result.error);
      } else {
        onResult(result);
      }
    } catch (error) {
      onError('TTS request failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="tts-form">
      <div className="form-group">
        <label className="form-label">Text to Synthesize</label>
        <textarea
          className="form-textarea"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text here..."
          rows={6}
          maxLength={1000}
        />
        <div className="form-hint">
          {text.length}/1000 characters
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Speaker</label>
        <select
          className="form-select"
          value={speakerId}
          onChange={(e) => setSpeakerId(e.target.value)}
        >
          <option value="default">Default Speaker</option>
          {profiles.map((profile) => (
            <option key={profile.id} value={profile.id}>
              {profile.name}
            </option>
          ))}
        </select>
      </div>

      <div className="form-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
        <div className="form-group">
          <label className="form-label">Language</label>
          <select
            className="form-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            <option value="zh">Chinese</option>
            <option value="en">English</option>
            <option value="ja">Japanese</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Speed: {speed}x</label>
          <input
            type="range"
            min="0.5"
            max="2.0"
            step="0.1"
            value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            className="form-range"
          />
        </div>
      </div>

      <div className="form-actions">
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading || !text.trim()}
          style={{ width: '100%' }}
        >
          {loading ? (
            <div className="loading">
              <div className="spinner" />
              Synthesizing...
            </div>
          ) : (
            '🎤 Generate Speech'
          )}
        </button>
      </div>
    </form>
  );
};

export default TTSForm;
