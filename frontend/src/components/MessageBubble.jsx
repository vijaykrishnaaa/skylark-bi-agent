import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot } from 'lucide-react';

const MessageBubble = ({ message, onQuestionClick }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`message-wrapper ${isUser ? 'user' : 'assistant'}`}>
      {!isUser && (
        <div className="bot-avatar-container">
          <div className="bot-avatar">
            <Bot size={20} />
          </div>
        </div>
      )}
      
      <div className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
        {isUser ? (
          message.content
        ) : (
          <div className="markdown-content">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}
        
        {message.sample_questions && message.sample_questions.length > 0 && (
          <div className="sample-questions-container">
            {message.sample_questions.map((question, idx) => (
              <button
                key={idx}
                className="sample-question-chip"
                onClick={() => onQuestionClick(question)}
              >
                {question}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
