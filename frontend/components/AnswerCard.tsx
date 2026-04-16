'use client';

import { Copy, Quote } from 'lucide-react';
import type { QAHistory } from '@/lib/api';

interface AnswerCardProps {
  question: string;
  answer: string;
  sources?: { index: number; text: string }[];
}

export default function AnswerCard({ question, answer, sources = [] }: AnswerCardProps) {
  const copyToClipboard = () => {
    navigator.clipboard.writeText(answer);
  };

  return (
    <div className="bg-surface rounded-xl shadow-md overflow-hidden animate-fadeIn">
      <div className="p-4 border-b border-gray-100">
        <p className="text-sm font-medium text-text-secondary">Question</p>
        <p className="mt-1 text-text-primary font-medium">{question}</p>
      </div>
      <div className="p-4">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm font-medium text-text-secondary">Answer</p>
          <button
            onClick={copyToClipboard}
            className="flex items-center space-x-1 text-xs text-text-secondary hover:text-primary transition-colors"
          >
            <Copy className="w-3 h-3" />
            <span>Copy</span>
          </button>
        </div>
        <div className="prose prose-sm max-w-none">
          <p className="text-text-primary whitespace-pre-wrap">{answer}</p>
        </div>
        {sources.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <p className="text-xs font-medium text-text-secondary mb-2">Sources</p>
            <div className="space-y-2">
              {sources.map((source, idx) => (
                <div key={idx} className="bg-gray-50 rounded-lg p-3 text-sm">
                  <div className="flex items-start space-x-2">
                    <Quote className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" />
                    <span className="text-text-secondary line-clamp-2">
                      {source.text}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
