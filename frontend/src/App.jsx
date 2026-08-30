import { useState } from 'react';
import Header from './components/Header';
import ChatWindow from './components/ChatWindow';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Welcome to the Skylark Business Intelligence Agent! I can help you analyze your Monday.com data. Here are some things you can ask me:',
      sample_questions: [
        'What is the status of the latest projects?',
        'Show me the team\'s performance metrics.',
        'Which tasks are overdue?'
      ]
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (customMessage = null) => {
    const textToSend = typeof customMessage === 'string' ? customMessage : inputValue;
    if (!textToSend.trim()) return;

    const userMessage = { role: 'user', content: textToSend };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const chatHistory = messages.map(msg => ({ role: msg.role, content: msg.content }));
      
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: textToSend,
          chat_history: chatHistory
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to connect to the server');
      }

      const data = await response.json();
      
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Error: Could not process your request. Please ensure the backend is running at ${API_URL}. Details: ${error.message}` 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header />
      <ChatWindow
        messages={messages}
        inputValue={inputValue}
        setInputValue={setInputValue}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
      />
    </div>
  );
}

export default App;
