import React, { useEffect, useState } from 'react';

const STAGES = [
  { label: 'Uploading files',        threshold: 10 },
  { label: 'Removing background',    threshold: 30 },
  { label: 'Synthesising voice',     threshold: 42 },
  { label: 'Animating lips & mouth', threshold: 90 },
  { label: 'Encoding final video',   threshold: 99 },
];

export default function ProgressPanel({ jobId, onDone, onError }) {
  const [progress,  setProgress]  = useState(0);
  const [stepLabel, setStepLabel] = useState('Initialising…');

  useEffect(() => {
    if (!jobId) return;
    const es = new EventSource(`/progress/${jobId}`);
    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        setProgress(data.progress || 0);
        setStepLabel(data.step || '');
        if (data.status === 'done')  { es.close(); onDone(`/download/${jobId}`); }
        if (data.status === 'error') { es.close(); onError(data.error || 'Processing failed'); }
      } catch {}
    };
    es.onerror = () => { es.close(); onError('Connection lost. Please retry.'); };
    return () => es.close();
  }, [jobId, onDone, onError]);

  return (
    <div className="progress-wrapper">
      <h2 className="progress-title">🎬 Generating Your Avatar</h2>
      <p className="progress-step-label">{stepLabel}</p>

      <div className="progress-bar-track">
        <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
      </div>
      <p className="progress-pct">{progress}%</p>

      <ul className="progress-steps-list">
        {STAGES.map((s, i) => {
          const isDone   = progress > s.threshold;
          const isActive = !isDone && progress >= (s.threshold - 20);
          return (
            <li key={i} className={`progress-step-item ${isDone ? 'done' : isActive ? 'active' : ''}`}>
              <span className="step-dot" />
              {s.label}
              {isDone && <span style={{ marginLeft:'auto', fontSize:12 }}>✓</span>}
            </li>
          );
        })}
      </ul>
    </div>
  );
}