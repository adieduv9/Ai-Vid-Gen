import React from 'react';

export default function VideoResult({ url, jobId, onReset }) {
  return (
    <div className="result-wrapper">
      <h2 className="result-title">✨ Avatar Ready!</h2>
      <p className="result-sub">Your AI talking avatar has been generated. Preview and download below.</p>

      <div className="video-frame">
        <video controls autoPlay loop src={url} />
      </div>

      <div className="result-actions">
        <a href={url} download={`avatar_${jobId?.slice(0,8)}.mp4`} className="btn-download">
          ⬇ Download MP4
        </a>
        <button className="btn-new" onClick={onReset}>
          + Create Another
        </button>
      </div>
    </div>
  );
}