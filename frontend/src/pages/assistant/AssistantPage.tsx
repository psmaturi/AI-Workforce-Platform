import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../../hooks/useChat';
import { ChatMessageItem, TypingIndicator } from '../../components/chat/ChatMessage';
import { Send, RotateCcw, MessageSquare } from 'lucide-react';

const SUGGESTED_QUESTIONS = [
  'What skills am I missing for my target role?',
  'What training should I complete next?',
  'How ready am I for the EAF Mechanical Specialist role?',
  'What are the key skills for my department?',
];

const AssistantPage: React.FC = () => {
  const { messages, isLoading, error, send, clear } = useChat();
  const [input, setInput] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    send(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-3.5rem-3rem)]">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 shrink-0">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">AI Workforce Assistant</h1>
          <p className="text-sm text-slate-500">Ask about your skills, career, training, and workforce insights</p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clear}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800 border border-slate-200 px-3 py-1.5 rounded"
          >
            <RotateCcw size={12} />
            New conversation
          </button>
        )}
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-4 min-h-0">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-6 py-8">
            <div className="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center">
              <MessageSquare size={22} className="text-blue-600" />
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-slate-700">AI Workforce Intelligence Assistant</p>
              <p className="text-xs text-slate-500 mt-1">Powered by Qwen2.5 · SteelCore Workforce Platform</p>
            </div>
            <div className="w-full max-w-md space-y-2">
              <p className="text-xs font-medium text-slate-500 text-center mb-1">Suggested questions</p>
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => send(q)}
                  className="w-full text-left px-4 py-2.5 text-sm text-slate-700 bg-white border border-slate-200 rounded-lg hover:border-blue-300 hover:text-blue-700 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <ChatMessageItem key={msg.id} message={msg} />
        ))}

        {isLoading && <TypingIndicator />}

        {error && (
          <div className="flex justify-center">
            <p className="text-xs text-red-600 bg-red-50 border border-red-200 px-3 py-2 rounded">{error}</p>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="mt-3 flex gap-2 shrink-0">
        <textarea
          ref={inputRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about skills, career goals, training, or workforce insights…"
          rows={2}
          disabled={isLoading}
          aria-label="Message input"
          className="flex-1 px-3 py-2.5 text-sm border border-slate-300 rounded-lg outline-none focus-visible:ring-2 focus-visible:ring-blue-500 resize-none disabled:bg-slate-50 disabled:text-slate-400"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          aria-label="Send message"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shrink-0 flex items-center"
        >
          <Send size={16} />
        </button>
      </div>
      <p className="text-xs text-slate-400 mt-1.5">Press Enter to send · Shift+Enter for new line</p>
    </div>
  );
};

export default AssistantPage;
