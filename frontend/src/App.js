import React, { useState, useCallback } from 'react';
import './App.css';
import Header from './components/Header';
import StepIndicator from './components/StepIndicator';
import AvatarUpload from './components/AvatarUpload';
import BackgroundUpload from './components/BackgroundUpload';
import ScriptPanel from './components/ScriptPanel';
import GenerateButton from './components/GenerateButton';
import ProgressPanel from './components/ProgressPanel';
import VideoResult from './components/VideoResult';

const STEPS = ['Avatar', 'Background', 'Script & Voice'];

export default function App() {
  const [step, setStep]         = useState(0);
  const [avatar, setAvatar]     = useState(null);
  const [background, setBg]     = useState(null);
  const [script, setScript]     = useState('');
  const [voice, setVoice]       = useState('en-US-AriaNeural');
  const [rate, setRate]         = useState(1.0);
  const [jobId, setJobId]       = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [error, setError]       = useState(null);

  const canProceed = useCallback(() => {
    if (step === 0) return !!avatar;
    if (step === 1) return !!background;
    if (step === 2) return script.trim().length > 5;
    return false;
  }, [step, avatar, background, script]);

  const handleGenerate = async () => {
    setError(null);
    setStep(3);
    const form = new FormData();
    form.append('avatar', avatar.file);
    form.append('background', background.file);
    form.append('script', script);
    form.append('voice', voice);
    form.append('removal_mode', avatar.mode);
    form.append('speaking_rate', rate.toString());
    try {
      const res  = await fetch('/generate', { method: 'POST', body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Server error');
      setJobId(data.job_id);
    } catch (e) {
      setError(e.message);
      setStep(2);
    }
  };

  const handleReset = () => {
    setStep(0); setAvatar(null); setBg(null);
    setScript(''); setVoice('en-US-AriaNeural'); setRate(1.0);
    setJobId(null); setVideoUrl(null); setError(null);
  };

  return (
    <div className="app">
      <div className="bg-orbs" aria-hidden>
        <div className="orb orb-1"/><div className="orb orb-2"/><div className="orb orb-3"/>
      </div>

      <Header />

      <main className="main">
        {step < 3 && (
          <div className="hero">
            <span className="hero-tag">AI-Powered Studio</span>
            <h1 className="hero-title">Create a <em>Talking Avatar</em><br/>in under a minute</h1>
            <p className="hero-sub">
              Upload a photo, pick a background, write your script.<br/>
              Our AI composes, voices, and animates — fully production-ready.
            </p>
          </div>
        )}

        {step < 3 && <StepIndicator steps={STEPS} current={step} />}

        <div className="step-content">
          {step === 0 && <AvatarUpload value={avatar} onChange={setAvatar} />}
          {step === 1 && <BackgroundUpload value={background} onChange={setBg} />}
          {step === 2 && (
            <ScriptPanel
              script={script} setScript={setScript}
              voice={voice}   setVoice={setVoice}
              rate={rate}     setRate={setRate}
            />
          )}
          {step === 3 && jobId && (
            <ProgressPanel
              jobId={jobId}
              onDone={(url) => { setVideoUrl(url); setStep(4); }}
              onError={(e)  => { setError(e); setStep(2); }}
            />
          )}
          {step === 4 && <VideoResult url={videoUrl} jobId={jobId} onReset={handleReset} />}
        </div>

        {error && (
          <div className="error-banner">
            <span className="error-icon">⚠</span>
            <span>{error}</span>
            <button className="error-close" onClick={() => setError(null)}>✕</button>
          </div>
        )}

        {step < 3 && (
          <div className="nav-row">
            {step > 0 && (
              <button className="btn-ghost" onClick={() => setStep(s => s - 1)}>← Back</button>
            )}
            <div style={{ flex: 1 }} />
            {step < 2 && (
              <button
                className={`btn-primary ${!canProceed() ? 'disabled' : ''}`}
                disabled={!canProceed()}
                onClick={() => setStep(s => s + 1)}
              >
                Continue →
              </button>
            )}
            {step === 2 && <GenerateButton disabled={!canProceed()} onClick={handleGenerate} />}
          </div>
        )}
      </main>
    </div>
  );
}