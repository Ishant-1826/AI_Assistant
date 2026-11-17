import React from 'react';
import { Globe, ExternalLink, ShieldCheck } from 'lucide-react';
import { WebSource } from '../types';

interface SourceCardsProps {
  sources: WebSource[];
  queries?: string[];
}

export const SourceCards: React.FC<SourceCardsProps> = ({ sources, queries }) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-gray-100 text-xs">
      <div className="flex items-center justify-between text-gray-500 mb-2">
        <div className="flex items-center gap-1.5 font-semibold text-[11px] text-gray-700">
          <Globe className="w-3.5 h-3.5 text-blue-600" />
          <span>Sources & Verified Educational Grounding ({sources.length})</span>
        </div>
        {queries && queries.length > 0 && (
          <span className="text-[10px] text-gray-400 font-mono truncate max-w-[200px]">
            query: &ldquo;{queries[0]}&rdquo;
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {sources.map((source, idx) => (
          <a
            key={idx}
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="group p-2.5 bg-gray-50 hover:bg-blue-50/60 border border-gray-200 hover:border-blue-300 rounded-xl transition flex flex-col justify-between shadow-2xs gap-1 text-left select-none"
          >
            <div className="flex items-start justify-between gap-1">
              <span className="font-semibold text-gray-900 group-hover:text-blue-700 line-clamp-1 transition text-xs">
                {source.title}
              </span>
              <ExternalLink className="w-3 h-3 text-gray-400 group-hover:text-blue-600 shrink-0 mt-0.5" />
            </div>

            {source.snippet && (
              <p className="text-[10px] text-gray-500 line-clamp-2 leading-relaxed">
                {source.snippet}
              </p>
            )}

            <div className="flex items-center gap-1 text-[10px] text-gray-400 pt-0.5">
              <ShieldCheck className="w-3 h-3 text-emerald-600 shrink-0" />
              <span className="truncate">{source.source_name || 'web'}</span>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
};
