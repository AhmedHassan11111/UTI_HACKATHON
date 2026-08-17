import { useState, useEffect } from 'react';

const LEVELS = [
  { key: 'negative', label: 'Negative', color: 'bg-gray-200', text: 'text-gray-500', width: 0 },
  { key: 'trace', label: 'Trace', color: 'bg-blue-200', text: 'text-blue-600', width: 25 },
  { key: 'small', label: 'Small', color: 'bg-blue-400', text: 'text-blue-700', width: 50 },
  { key: 'moderate', label: 'Moderate', color: 'bg-emerald-400', text: 'text-emerald-700', width: 75 },
  { key: 'large', label: 'Large', color: 'bg-emerald-500', text: 'text-emerald-800', width: 100 },
];

function scoreToLevel(score) {
  if (score >= 0.90) return 'large';
  if (score >= 0.75) return 'moderate';
  if (score >= 0.55) return 'small';
  if (score >= 0.35) return 'trace';
  return 'negative';
}

export default function DipstickStrip({ score, animated = false }) {
  const level = scoreToLevel(score);
  const activeIndex = LEVELS.findIndex(l => l.key === level);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!animated) {
      setProgress(activeIndex);
      return;
    }
    let current = 0;
    const interval = setInterval(() => {
      current += 1;
      if (current > activeIndex) {
        clearInterval(interval);
        return;
      }
      setProgress(current);
    }, 300);
    return () => clearInterval(interval);
  }, [animated, activeIndex]);

  return (
    <div className="w-full">
      <div className="flex items-center gap-3 mb-2">
        <div className="flex-1 h-3 rounded-full bg-gray-100 dark:bg-gray-800 overflow-hidden flex">
          {LEVELS.map((lvl, i) => (
            <div
              key={lvl.key}
              className={`h-full transition-all duration-500 ${lvl.color} ${i <= progress ? 'opacity-100' : 'opacity-20'}`}
              style={{ width: `${100 / LEVELS.length}%` }}
            />
          ))}
        </div>
      </div>
      <div className="flex justify-between px-1">
        {LEVELS.map((lvl, i) => (
          <span
            key={lvl.key}
            className={`text-[10px] font-medium tracking-wide uppercase ${i <= progress ? lvl.text : 'text-gray-300 dark:text-gray-600'}`}
            style={{ width: `${100 / LEVELS.length}%`, textAlign: 'center' }}
          >
            {lvl.label}
          </span>
        ))}
      </div>
    </div>
  );
}
