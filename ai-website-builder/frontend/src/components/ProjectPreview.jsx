import React from "react";
import { getPreviewUrl, getDownloadUrl } from "../api";

const ProjectPreview = ({ projectId, loading = false }) => {
  if (!projectId) return null;

  const previewUrl = getPreviewUrl(projectId);
  const downloadUrl = getDownloadUrl(projectId);

  return (
    <div className="generated-preview">
      <div className="generated-toolbar">
        <span className="generated-label"><span className="status-dot" />PROJECT READY <span aria-hidden="true">/</span> {projectId}</span>
        <div className="generated-actions">
          <a href={previewUrl} target="_blank" rel="noopener noreferrer" className="generated-action">
            <span aria-hidden="true">↗</span> Open full preview
          </a>
          <a href={downloadUrl} className="generated-action primary" download>
            <span aria-hidden="true">↓</span> Download files
          </a>
        </div>
      </div>
      <div className="generated-frame-wrap">
        <iframe title="Generated website preview" src={previewUrl} className="preview-frame" />
        {loading && (
          <div className="loading-cover" role="status">
            <strong>Making your next version</strong>
            <span>Your current preview is staying right here.</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectPreview;
