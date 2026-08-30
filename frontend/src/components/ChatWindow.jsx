import React, { useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import MessageBubble from './MessageBubble';
import LoadingIndicator from './LoadingIndicator';

const ChatWindow = ({ messages, inputValue, setInputValue, onSendMessage, isLoading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSendMessage();
    }
  };

  return (
    <div className="chat-window">
      <div className="messages-container">
        {messages.map((msg, index) => (
          <MessageBubble 
            key={index} 
            message={msg} 
            onQuestionClick={onSendMessage}
          />
        ))}
        {isLoading && <LoadingIndicator />}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="input-container">
        <div className="input-wrapper">
          <input
            type="text"
            className="chat-input"
            placeholder="Ask a question about your Monday.com data..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <button 
            className="send-button" 
            onClick={() => onSendMessage()}
            disabled={!inputValue.trim() || isLoading}
            aria-label="Send message"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;
