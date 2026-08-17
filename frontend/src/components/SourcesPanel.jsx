import { ExternalLink } from 'lucide-react';

export default function SourcesPanel({ sources, onClose }) {
  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between p-3 border-b border-border">
        <h3 className="text-sm font-semibold text-text">Sources</h3>
        <button onClick={onClose} className="lg:hidden p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800">
          <span className="text-xs text-gray-500">Close</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {!sources || sources.length === 0 ? (
          <p className="text-xs text-gray-400 text-center py-8">
            Ask a question to see sources here
          </p>
        ) : (
          sources.map((source, i) => (
            <div
              key={i}
              className="p-3 rounded-lg border border-border bg-gray-50/50 dark:bg-gray-800/30 space-y-2"
            >
              <div className="flex items-start justify-between gap-2">
                <span className="text-xs font-mono font-medium text-primary shrink-0">[{i + 1}]</span>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-text leading-snug">{source.title}</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-[11px] text-gray-500 dark:text-gray-400">
                <span className="font-mono bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">
                  {source.section}
                </span>
                {source.page && (
                  <span className="font-mono bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">
                    Page: {source.page}
                  </span>
                )}
                <span className="font-mono">
                  Score: {source.score.toFixed(4)}
                </span>
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed line-clamp-4">
                {source.snippet}
              </p>
              <button className="flex items-center gap-1 text-[11px] text-primary hover:underline">
                <ExternalLink size={10} />
                Open source
              </button>
            </div>
          ))
        )}
      </div>

      <div className="p-3 border-t border-border">
        <details className="text-xs">
          <summary className="cursor-pointer text-gray-500 hover:text-text transition-colors">
            Retrieval parameters
          </summary>
          <div className="mt-2 space-y-1 text-gray-500 dark:text-gray-400 font-mono text-[11px]">
            <p>Top-K: 5</p>
            <p>Similarity threshold: 0.35</p>
            <p>Embedding: all-MiniLM-L6-v2</p>
          </div>
        </details>
      </div>
    </div>
  );
}
