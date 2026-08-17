import { MessageSquare, HelpCircle, Stethoscope, ShieldCheck } from 'lucide-react';

const SUGGESTIONS = [
  { icon: MessageSquare, text: 'Common symptoms of UTI' },
  { icon: HelpCircle, text: 'Do I need antibiotics?' },
  { icon: Stethoscope, text: 'When should I see a doctor?' },
  { icon: ShieldCheck, text: 'Preventing recurrence' },
];

export default function EmptyState({ onSelect }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
      <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-4">
        <span className="text-2xl font-bold text-primary">MT</span>
      </div>
      <h2 className="text-xl font-semibold text-text mb-2">What would you like to know about UTIs?</h2>
      <p className="text-sm text-gray-500 dark:text-gray-400 max-w-md mb-6">
        Ask any question about urinary tract infections. I'll retrieve evidence from clinical guidelines and provide fully traced answers.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
        {SUGGESTIONS.map((s, i) => (
          <button
            key={i}
            onClick={() => onSelect(s.text)}
            className="flex items-center gap-3 px-4 py-3 rounded-xl border border-border hover:border-primary hover:bg-primary/5 transition-colors text-left group"
          >
            <div className="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center group-hover:bg-primary/10 transition-colors">
              <s.icon size={16} className="text-gray-500 group-hover:text-primary" />
            </div>
            <span className="text-sm text-text">{s.text}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
