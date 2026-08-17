import { useState } from 'react';
import { Moon, Sun, Plus, BookOpen, ChevronLeft, ChevronRight } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';

export default function TopBar({ onToggleSidebar, sidebarOpen, onNewChat }) {
  const { isDark, toggle } = useTheme();
  const [model, setModel] = useState('Med Trace v1.0');

  return (
    <header className="h-14 border-b border-border flex items-center justify-between px-4 bg-surface shrink-0">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors lg:hidden"
          aria-label="Toggle sidebar"
        >
          {sidebarOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
        </button>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <span className="text-white font-bold text-sm">MT</span>
          </div>
          <div>
            <h1 className="text-sm font-semibold text-text leading-tight">Med Trace AI</h1>
            <p className="text-[10px] text-gray-500 dark:text-gray-400 leading-tight hidden sm:block">Every answer traced to its source</p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <div className="hidden md:flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 px-2.5 py-1 rounded-full border border-border">
          <BookOpen size={12} />
          <span>UTI Knowledge Base · 128 docs</span>
        </div>

        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="hidden sm:block text-xs bg-transparent border border-border rounded-lg px-2 py-1 text-text focus:outline-none focus:ring-2 focus:ring-primary/50"
        >
          <option>Med Trace v1.0</option>
          <option>Med Trace v0.9</option>
        </select>

        <button
          onClick={toggle}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          aria-label="Toggle theme"
        >
          {isDark ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <button
          onClick={onNewChat}
          className="hidden sm:flex items-center gap-1.5 text-xs font-medium bg-primary text-white px-3 py-1.5 rounded-lg hover:opacity-90 transition-opacity"
        >
          <Plus size={14} />
          New chat
        </button>
      </div>
    </header>
  );
}
