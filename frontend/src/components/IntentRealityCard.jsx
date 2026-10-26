import React, { useState } from 'react';
import { Target, Compass, Lightbulb, CheckCircle, ArrowRight } from 'lucide-react';
import { logIntent } from '../services/api';

export default function IntentRealityCard({ dailyData, onIntentUpdated }) {
  const [intentInput, setIntentInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!dailyData) return null;

  const {
    current_intent,
    intent_match_pct = 100,
    intent_vs_reality_summary = '',
    ai_wellness_tip = ''
  } = dailyData;

  const handleSetIntent = async (e) => {
    e.preventDefault();
    if (!intentInput.trim()) return;

    try {
      setIsSubmitting(true);
      await logIntent('default_user', intentInput.trim());
      setIntentInput('');
      if (onIntentUpdated) onIntentUpdated();
    } catch (err) {
      console.error('Failed to log intent:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  let matchBadge = 'badge-emerald';
  if (intent_match_pct < 50) matchBadge = 'badge-rose';
  else if (intent_match_pct < 75) matchBadge = 'badge-amber';

  return (
    <div className="glass-card flex flex-col gap-5">
      <div className="flex justify-between items-center border-b border-[rgba(255,255,255,0.08)] pb-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Target className="text-indigo-400" size={20} />
            Intent vs. Reality Analysis
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Tracking your stated intentions against actual viewing behavior</p>
        </div>
        <span className={`badge ${matchBadge}`}>
          {intent_match_pct.toFixed(0)}% Intent Match
        </span>
      </div>

      {/* Goal Display & Gap Summary */}
      <div className="bg-[rgba(99,102,241,0.08)] border border-[rgba(99,102,241,0.2)] rounded-2xl p-4 flex flex-col gap-3">
        <div className="flex items-center gap-2 text-xs font-bold text-indigo-300 uppercase tracking-wider">
          <Compass size={16} />
          Active Stated Focus Target
        </div>
        <div className="text-base font-bold text-slate-100">
          "{current_intent || 'No active focus goal set for this session'}"
        </div>
        <div className="text-xs text-slate-300 leading-relaxed bg-[rgba(15,23,42,0.6)] p-3 rounded-xl border border-[rgba(255,255,255,0.06)]">
          {intent_vs_reality_summary}
        </div>
      </div>

      {/* AI Wellness Tip */}
      {ai_wellness_tip && (
        <div className="bg-[rgba(16,185,129,0.06)] border border-[rgba(16,185,129,0.2)] rounded-xl p-3.5 flex items-start gap-3">
          <Lightbulb className="text-emerald-400 flex-shrink-0 mt-0.5" size={18} />
          <div>
            <span className="text-xs font-bold text-emerald-300 uppercase tracking-wider block">AI Productivity Insight</span>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">{ai_wellness_tip}</p>
          </div>
        </div>
      )}

      {/* Quick Set Goal Form */}
      <form onSubmit={handleSetIntent} className="flex flex-col gap-2 pt-2 border-t border-[rgba(255,255,255,0.08)]">
        <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Update Session Focus Goal</label>
        <div className="flex gap-2">
          <input
            type="text"
            className="form-input flex-1 text-xs"
            placeholder="e.g. Master Graph BFS/DFS for 1 hour"
            value={intentInput}
            onChange={(e) => setIntentInput(e.target.value)}
          />
          <button 
            type="submit" 
            className="btn btn-primary text-xs py-2 px-4 whitespace-nowrap"
            disabled={isSubmitting || !intentInput.trim()}
          >
            {isSubmitting ? 'Setting...' : 'Set Goal'}
            <ArrowRight size={14} />
          </button>
        </div>
      </form>
    </div>
  );
}
