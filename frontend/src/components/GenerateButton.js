import React from 'react';

export default function GenerateButton({ disabled, onClick }) {
  return (
    <button className="btn-generate" disabled={disabled} onClick={onClick} type="button">
      <span className="spark">✨</span>
      Generate Avatar Video
    </button>
  );
}