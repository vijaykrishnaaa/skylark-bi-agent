import React, { useState, useEffect } from 'react';
import { Bot } from 'lucide-react';

const LoadingIndicator = () => {
  const [loadingText, setLoadingText] = useState("Connecting to Monday.com...");
  
  useEffect(() => {
    const states = [
      "Connecting to Monday.com...",
      "Reading Deals board...",
      "Reading Work Orders board...",
      "Cleaning & normalizing data...",
      "Calculating pipeline metrics...",
      "Analyzing sector performance...",
      "Cross-referencing boards...",
      "Generating insights...",
      "Formatting response...",
      "Almost there, finalizing..."
    ];
    let currentIndex = 0;
    
    const intervalId = setInterval(() => {
      currentIndex = currentIndex + 1;
      if (currentIndex < states.length) {
        setLoadingText(states[currentIndex]);
      }
      // Stop cycling once we reach the last state — no more repeats
    }, 5000);
    
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="message-wrapper assistant">
      <div className="bot-avatar-container">
        <div className="bot-avatar pulsing">
          <Bot size={20} />
        </div>
      </div>
      <div className="message-bubble assistant loading-bubble">
        <div className="loading-text-container">
          <span className="loading-text">{loadingText}</span>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;
