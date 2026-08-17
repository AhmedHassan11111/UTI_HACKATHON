import { useState, useRef, useEffect } from 'react';
import { Send, Paperclip } from 'lucide-react';

export default function Composer({ onSend, isLoading, loadingStage }) {
  const [value, setValue] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [value]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!value.trim() || isLoading) return;
    onSend(value);
    setValue('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="border-t border-border bg-surface p-4">
      {isLoading && (
        <div className="mb-3 flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
          <div className="flex gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <span>{loadingStage}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="relative">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about UTI symptoms, treatment, prevention..."
          rows={1}
          className="w-full resize-none rounded-xl border border-border bg-bg px-4 py-3 pr-24 text-sm text-text placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
          disabled={isLoading}
        />
        <div className="absolute right-2 bottom-2 flex items-center gap-1">
          <button
            type="button"
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-400 hover:text-text transition-colors"
            title="Attach file"
          >
            <Paperclip size={16} />
          </button>
          <button
            type="submit"
            disabled={!value.trim() || isLoading}
            className="p-2 rounded-lg bg-primary text-white hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed transition-opacity"
          >
            <Send size={16} />
          </button>
        </div>
      </form>

      <p className="text-[10px] text-gray-400 text-center mt-2">
        Med Trace AI may produce inaccurate information. Always verify with a healthcare professional.
      </p>
    </div>
  );
}
