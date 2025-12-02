/**
 * Upload Page Component
 * Main page for file and URL uploads
 */

import React from 'react';
import { UploadZone } from './UploadZone';
import { URLIngestion } from './URLIngestion';
import { UploadQueue } from './UploadQueue';
import { useUploadQueue } from '../../../lib/hooks/useUploadQueue';
import './UploadPage.css';

export const UploadPage: React.FC = () => {
  const {
    queue,
    addFiles,
    addURL,
    retryUpload,
    cancelUpload,
    clearCompleted,
  } = useUploadQueue({
    maxConcurrent: 3,
    pollInterval: 5000,
    pollTimeout: 300000,
  });

  return (
    <div className="upload-page">
      <div className="upload-page__container">
        {/* Header */}
        <header className="upload-page__header">
          <h1 className="upload-page__title">Upload Resources</h1>
          <p className="upload-page__description">
            Add new resources to your library by uploading files or providing URLs
          </p>
        </header>

        {/* Upload Zone */}
        <section className="upload-page__section">
          <h2 className="upload-page__section-title">Upload Files</h2>
          <UploadZone
            onFilesAdded={addFiles}
            accept=".pdf,.epub,.txt,.doc,.docx"
            maxSize={50 * 1024 * 1024} // 50MB
            maxFiles={10}
          />
        </section>

        {/* URL Ingestion */}
        <section className="upload-page__section">
          <h2 className="upload-page__section-title">Add from URL</h2>
          <URLIngestion
            onURLSubmit={addURL}
            disabled={queue.some(item => item.status === 'uploading' || item.status === 'processing')}
          />
        </section>

        {/* Upload Queue */}
        {queue.length > 0 && (
          <section className="upload-page__section">
            <UploadQueue
              queue={queue}
              onRetry={retryUpload}
              onCancel={cancelUpload}
              onClearCompleted={clearCompleted}
            />
          </section>
        )}

        {/* Help Text */}
        <section className="upload-page__help">
          <h3 className="upload-page__help-title">Supported Formats</h3>
          <ul className="upload-page__help-list">
            <li>PDF documents (.pdf)</li>
            <li>EPUB books (.epub)</li>
            <li>Text files (.txt)</li>
            <li>Word documents (.doc, .docx)</li>
          </ul>
          <p className="upload-page__help-note">
            Maximum file size: 50MB per file. You can upload up to 10 files at once.
          </p>
        </section>
      </div>
    </div>
  );
};

export default UploadPage;
