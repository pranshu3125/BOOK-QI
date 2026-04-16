'use client';

import { useState, useRef } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface QuestionInputProps {
  onSubmit: (question: string) => Promise<void>;
  disabled?: boolean;
}

export default function QuestionInput({ onSubmit, disabled }: QuestionInputProps) {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = async () => {
    if (!question.trim() || loading || disabled) return;
    
    setLoading(true);
    try {
      await onSubmit(question);
      setQuestion('');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="bg-surface rounded-xl shadow-md p-4">
      <textarea
        ref={textareaRef}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about the book..."
        className="w-full p-3 border border-gray-200 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
        rows={3}
        disabled={disabled || loading}
      />
      <div className="flex items-center justify-between mt-3">
        <span className="text-xs text-text-secondary">
          {question.length} characters
        </span>
        <button
          onClick={handleSubmit}
          disabled={!question.trim() || loading || disabled}
          className="flex items-center space-x-2 bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
          <span>{loading ? 'Thinking...' : 'Ask'}</span>
        </button>
      </div>
    </div>
  );
}
