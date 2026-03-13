import React from 'react';

export default function Header() {
  return (
    <header className="header">
      <a className="header-logo" href="/">
        <div className="header-icon">🎬</div>
        <span className="header-wordmark">Studio<em>Avatar</em>AI</span>
      </a>
      <span className="header-badge">v2.0 Beta</span>
    </header>
  );
}