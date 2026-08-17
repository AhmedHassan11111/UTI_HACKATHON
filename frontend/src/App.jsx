import { useState } from 'react';
import TopBar from './components/TopBar';
import Sidebar from './components/Sidebar';
import Message from './components/Message';
import SourcesPanel from './components/SourcesPanel';
import Composer from './components/Composer';
import EmptyState from './components/EmptyState';
import { useTheme } from './hooks/useTheme';
import { useChat } from './hooks/useChat';

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sourcesOpen, setSourcesOpen] = useState(true);
  const [selectedSourceIndex, setSelectedSourceIndex] = useState(null);
  const { messages, isLoading, loadingStage, sendMessage, clearChat } = useChat();
  const { isDark } = useTheme();

  const handleSelectSuggestion = (text) => {
    sendMessage(text);
  };

  const handleSourceClick = (index) => {
    setSelectedSourceIndex(index);
    setSourcesOpen(true);
  };

  const currentSources = messages.length > 0
    ? messages[messages.length - 1]?.sources || []
    : [];

  return (
    <div className="h-screen flex flex-col bg-bg text-text overflow-hidden">
      <TopBar
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        sidebarOpen={sidebarOpen}
        onNewChat={clearChat}
      />

      <div className="flex-1 flex overflow-hidden">
        <main className="flex-1 flex flex-col min-w-0">
          {messages.length === 0 ? (
            <EmptyState onSelect={handleSelectSuggestion} />
          ) : (
            <div className="flex-1 overflow-y-auto">
              <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
                {messages.map((msg, i) => (
                  <Message
                    key={i}
                    message={msg}
                    onSourceClick={handleSourceClick}
                  />
                ))}
                {isLoading && (
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center shrink-0">
                      <span className="text-accent font-bold text-xs">AI</span>
                    </div>
                    <div className="flex-1">
                      <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
                      <div className="h-3 w-48 bg-gray-100 dark:bg-gray-800 rounded animate-pulse" />
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="max-w-3xl mx-auto w-full px-4">
            <Composer onSend={sendMessage} isLoading={isLoading} loadingStage={loadingStage} />
          </div>
        </main>

        <aside
          className={`
            hidden lg:flex w-80 border-l border-border bg-surface flex-col shrink-0
            transition-all duration-200
            ${sourcesOpen ? 'w-80' : 'w-0 overflow-hidden'}
          `}
        >
          {sourcesOpen && (
            <SourcesPanel
              sources={currentSources}
              onClose={() => setSourcesOpen(false)}
            />
          )}
        </aside>
      </div>

      {sourcesOpen && (
        <div className="lg:hidden fixed inset-x-0 bottom-0 z-10 bg-surface border-t border-border rounded-t-2xl max-h-[50vh] flex flex-col shadow-[0_-4px_20px_rgba(0,0,0,0.1)]">
          <div className="p-3 border-b border-border flex items-center justify-between">
            <h3 className="text-sm font-semibold text-text">Sources</h3>
            <button onClick={() => setSourcesOpen(false)} className="text-xs text-gray-500">Close</button>
          </div>
          <div className="flex-1 overflow-y-auto">
            <SourcesPanel sources={currentSources} />
          </div>
        </div>
      )}
    </div>
  );
}
