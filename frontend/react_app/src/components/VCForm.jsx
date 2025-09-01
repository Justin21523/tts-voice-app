// ============ src/components/VCForm.jsx ============
import React, { useState, useEffect } from 'react';
import FileUpload from './FileUpload';
import apiClient from '../services/api';

const VCForm = ({ onResult, onError }) => {
  const [sourceFile, setSourceFile] = useState(null);
  const [targetSpeaker, setTargetSpeaker] = useState('');
  const [preservePitch, setPreservePitch] = useState(true);
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
        if (result.profiles.length > 0) {
          setTargetSpeaker(result.profiles[0].id);
        }
      }
    } catch (error) {
      console.error('Failed to load profiles:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!sourceFile) {
      onError('Please select an audio file');
      return;
    }

    if (!targetSpeaker) {
      onError('Please select a target speaker');
      return;
    }

    setLoading(true);
    try {
      const result = await apiClient.voiceConversion(
        sourceFile,
        targetSpeaker,
        { preservePitch }
      );

      if (result.error) {
        onError(result.error);
      } else {
        onResult(result);
      }
    } catch (error) {
      onError('Voice conversion failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="vc-form">
      <div className="form-group">
        <label className="form-label">Source Audio</label>
        <FileUpload
          onFileSelect={setSourceFile}
          accept="audio/*"
        />
      </div>

      <div className="form-group">
        <label className="form-label">Target Speaker</label>
        <select
          className="form-select"
          value={targetSpeaker}
          onChange={(e) => setTargetSpeaker(e.target.value)}
        >
          <option value="">Select target speaker...</option>
          {profiles.map((profile) => (
            <option key={profile.id} value={profile.id}>
              {profile.name}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label className="form-label">
          <input
            type="checkbox"
            checked={preservePitch}
            onChange={(e) => setPreservePitch(e.target.checked)}
            style={{ marginRight: 'var(--spacing-xs)' }}
          />
          Preserve Pitch
        </label>
        <div className="form-hint">
          Keep original pitch characteristics during conversion
        </div>
      </div>

      <div className="form-actions">
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading || !sourceFile || !targetSpeaker}
          style={{ width: '100%' }}
        >
          {loading ? (
            <div className="loading">
              <div className="spinner" />
              Converting...
            </div>
          ) : (
            '🎭 Convert Voice'
          )}
        </button>
      </div>
    </form>
  );
};

export default VCForm;