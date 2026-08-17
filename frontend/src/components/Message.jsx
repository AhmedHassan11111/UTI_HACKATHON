import { useState } from 'react';
import { User, ChevronDown, ChevronUp, ExternalLink, Copy, Check } from 'lucide-react';
import DipstickStrip from './DipstickStrip';

function CiteChip({ index, onClick }) {
  return (
    <button
      onClick={onClick}
      className="inline-flex items-center justify-center w-5 h-5 text-[11px] font-mono font-medium bg-primary/10 text-primary hover:bg-primary/20 rounded transition-colors"
    >
      [{index}]
    </button>
  );
}

function SourceRow({ source, index, expanded, onToggle }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(source.snippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-3 py-2 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors text-left"
      >
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-xs font-mono font-medium text-primary shrink-0">[{index}]</span>
          <span className="text-sm font-medium text-text truncate">{source.title}</span>
        </div>
        {expanded ? <ChevronUp size={14} className="text-gray-400 shrink-0" /> : <ChevronDown size={14} className="text-gray-400 shrink-0" />}
      </button>

      {expanded && (
        <div className="px-3 pb-3 pt-1 border-t border-border bg-gray-50/50 dark:bg-gray-800/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-mono text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">
              Section: {source.section}
            </span>
            <div className="flex items-center gap-1">
              <button onClick={handleCopy} className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors" title="Copy snippet">
                {copied ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} className="text-gray-400" />}
              </button>
              <span className="text-[11px] font-mono text-gray-400">
                Score: {source.score.toFixed(4)}
              </span>
            </div>
          </div>
          <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
            {source.snippet}
          </p>
        </div>
      )}
    </div>
  );
}

export default function Message({ message, onSourceClick }) {
  const [showTrace, setShowTrace] = useState(false);
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex gap-3 justify-end">
        <div className="max-w-2xl">
          <div className="bg-primary text-white px-4 py-2.5 rounded-2xl rounded-tr-sm text-sm leading-relaxed">
            {message.content}
          </div>
        </div>
        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
          <User size={16} className="text-primary" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center shrink-0">
        <span className="text-accent font-bold text-xs">AI</span>
      </div>
      <div className="flex-1 min-w-0 space-y-3">
        <div className="prose prose-sm max-w-none text-text leading-relaxed">
          <div className="text-sm whitespace-pre-wrap">{message.content}</div>
        </div>

        {message.sources && message.sources.length > 0 && (
          <>
            <div className="space-y-1.5">
              <p className="text-[11px] font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Retrieved sources
              </p>
              <div className="flex flex-wrap gap-1.5">
                {message.sources.map((source, i) => (
                  <CiteChip key={i} index={i + 1} onClick={() => onSourceClick?.(i)} />
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <p className="text-[11px] font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Confidence
              </p>
              <DipstickStrip score={message.confidence || message.sources[0]?.score || 0} />
            </div>

            <button
              onClick={() => setShowTrace(!showTrace)}
              className="flex items-center gap-1.5 text-xs font-medium text-primary hover:underline"
            >
              {showTrace ? 'Hide' : 'View'} retrieval trace
              {showTrace ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>

            {showTrace && (
              <div className="space-y-2 pt-2">
                {message.sources.map((source, i) => (
                  <SourceRow
                    key={i}
                    source={source}
                    index={i + 1}
                    expanded={false}
                    onToggle={() => {}}
                  />
                ))}
              </div>
            )}

            <div className="flex flex-wrap gap-2 pt-2">
              {['What about pregnant women?', 'What are the side effects?'].map((q) => (
                <button
                  key={q}
                  className="text-xs px-3 py-1.5 rounded-full border border-border hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-300 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
