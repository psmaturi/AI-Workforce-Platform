import React from 'react';
import type { ChatMessage } from '../../types';
import { Bot, User } from 'lucide-react';

interface ChatMessageProps {
  message: ChatMessage;
}

const formatContent = (text: string): React.ReactNode => {
  // Simple line-based markdown rendering — bold, bullets
  const lines = text.split('\n');
  return lines.map((line, i) => {
    if (line.startsWith('- ') || line.startsWith('• ')) {
      return <li key={i} className="ml-3">{line.replace(/^[-•]\s+/, '')}</li>;
    }
    if (line.startsWith('**') && line.endsWith('**')) {
      return <p key={i} className="font-semibold">{line.replace(/\*\*/g, '')}</p>;
    }
    if (line === '') return <br key={i} />;
    return <p key={i}>{line}</p>;
  });
};

export const ChatMessageItem: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center shrink-0 mt-0.5">
          <Bot size={14} className="text-white" />
        </div>
      )}
      <div className={`max-w-xl px-4 py-3 rounded-lg text-sm leading-relaxed prose-chat ${
        isUser
          ? 'bg-blue-600 text-white rounded-tr-sm'
          : 'bg-white border border-slate-200 text-slate-800 rounded-tl-sm'
      }`}>
        {isUser ? message.content : <div className="space-y-1">{formatContent(message.content)}</div>}
        <p className={`text-xs mt-1.5 ${isUser ? 'text-blue-200' : 'text-slate-400'}`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
      {isUser && (
        <div className="w-7 h-7 rounded-full bg-slate-200 flex items-center justify-center shrink-0 mt-0.5">
          <User size={14} className="text-slate-600" />
        </div>
      )}
    </div>
  );
};

// Typing indicator
export const TypingIndicator: React.FC = () => (
  <div className="flex gap-3 justify-start">
    <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center shrink-0">
      <Bot size={14} className="text-white" />
    </div>
    <div className="px-4 py-3 rounded-lg bg-white border border-slate-200">
      <div className="flex gap-1">
        {[0, 1, 2].map(i => (
          <div
            key={i}
            className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
            style={{ animationDelay: `${i * 150}ms` }}
          />
        ))}
      </div>
    </div>
  </div>
);
