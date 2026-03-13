import React from 'react';

export default function StepIndicator({ steps, current }) {
  return (
    <nav className="step-indicator" aria-label="Progress">
      {steps.map((label, i) => {
        const state = i < current ? 'done' : i === current ? 'active' : '';
        return (
          <React.Fragment key={i}>
            <div className={`step-node ${state}`}>
              <div className={`step-circle ${state}`}>{i < current ? '✓' : i + 1}</div>
              <span className="step-label">{label}</span>
            </div>
            {i < steps.length - 1 && (
              <div className={`step-line ${i < current ? 'done' : ''}`} />
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
}