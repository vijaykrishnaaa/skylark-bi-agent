import React from 'react';
import { Bot } from 'lucide-react';

const Header = () => {
  return (
    <header className="app-header">
      <div className="header-icon">
        <Bot size={32} />
      </div>
      <div className="header-title-container">
        <h1>Skylark BI Agent</h1>
        <div className="header-subtitle">Monday.com Business Intelligence Assistant</div>
      </div>
    </header>
  );
};

export default Header;
