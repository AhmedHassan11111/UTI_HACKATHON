import { AlertTriangle } from 'lucide-react';

export default function Sidebar({ open, onClose }) {

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 bg-black/20 z-20 lg:hidden"
          onClick={onClose}
        />
      )}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-30 w-72 bg-surface border-r border-border flex flex-col
          transform transition-transform duration-200 ease-in-out
          ${open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <div className="p-3 border-b border-border hidden lg:flex items-center justify-between">
          <span className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Menu</span>
        </div>

        <div className="flex-1 overflow-y-auto p-3">
          <div className="px-3 py-8 text-center text-xs text-gray-400">
            Start a conversation to see sources here
          </div>
        </div>

        <div className="p-4 border-t border-border">
          <div className="flex items-start gap-2 p-3 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/30">
            <AlertTriangle size={16} className="text-amber-600 dark:text-amber-500 shrink-0 mt-0.5" />
            <p className="text-[11px] text-amber-800 dark:text-amber-200 leading-relaxed">
              For educational purposes only — not a substitute for professional medical advice.
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
