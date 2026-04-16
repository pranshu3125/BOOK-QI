'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp, RefreshCw, Lightbulb, Tag, ThumbsUp, Sparkles } from 'lucide-react';

interface InsightCardProps {
  title: string;
  content: string;
  icon: 'summary' | 'genre' | 'recommendations' | 'sentiment';
  onRefresh?: () => Promise<void>;
  loading?: boolean;
}

const iconMap = {
  summary: Lightbulb,
  genre: Tag,
  recommendations: ThumbsUp,
  sentiment: Sparkles,
};

export default function InsightCard({ title, content, icon, onRefresh, loading }: InsightCardProps) {
  const [expanded, setExpanded] = useState(true);
  const Icon = iconMap[icon];

  return (
    <div className="bg-surface rounded-xl shadow-md overflow-hidden">
      <div
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Icon className="w-5 h-5 text-primary" />
          </div>
          <h3 className="font-semibold text-text-primary">{title}</h3>
        </div>
        <div className="flex items-center space-x-2">
          {onRefresh && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRefresh();
              }}
              disabled={loading}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 text-text-secondary ${loading ? 'animate-spin' : ''}`} />
            </button>
          )}
          {expanded ? (
            <ChevronUp className="w-5 h-5 text-text-secondary" />
          ) : (
            <ChevronDown className="w-5 h-5 text-text-secondary" />
          )}
        </div>
      </div>
      {expanded && (
        <div className="px-4 pb-4 animate-fadeIn">
          <p className="text-text-secondary whitespace-pre-wrap">{content}</p>
        </div>
      )}
    </div>
  );
}
