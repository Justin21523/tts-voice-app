// ============ src/components/FileUpload.jsx ============
import React, { useState, useRef } from 'react';

const FileUpload = ({ onFileSelect, accept = 'audio/*', multiple = false, className = '' }) => {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      const file = files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
        onFileSelect(file);
      }
    }
  };

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      const file = files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
        onFileSelect(file);
      }
    }
  };

  const validateFile = (file) => {
    const validTypes = ['audio/wav', 'audio/mp3', 'audio/ogg', 'audio/m4a', 'audio/flac'];
    if (!validTypes.includes(file.type)) {
      alert('Please select a valid audio file (WAV, MP3, OGG, M4A, FLAC)');
      return false;
    }

    // 50MB limit
    if (file.size > 50 * 1024 * 1024) {
      alert('File size must be less than 50MB');
      return false;
    }

    return true;
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const clearFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    onFileSelect(null);
  };

  return (
    <div className={`file-upload-container ${className}`}>
      {!selectedFile ? (
        <div
          className={`file-upload ${dragOver ? 'drag-over' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleClick}
        >
          <div className="file-upload-icon">📁</div>
          <div className="file-upload-text">
            Drop audio file here or click to browse
          </div>
          <div className="file-upload-hint">
            Supports WAV, MP3, OGG, M4A, FLAC (max 50MB)
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept={accept}
            multiple={multiple}
            onChange={handleFileInput}
            style={{ display: 'none' }}
          />
        </div>
      ) : (
        <div className="file-selected">
          <div className="file-info">
            <div className="file-name">📎 {selectedFile.name}</div>
            <div className="file-size">
              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
            </div>
          </div>
          <button className="btn btn-secondary" onClick={clearFile}>
            ✕ Remove
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
