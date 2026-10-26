import React from 'react';
import 'chart.js/auto';
import { Doughnut } from 'react-chartjs-2';
import { Clock, Award, ShieldAlert } from 'lucide-react';

const CATEGORY_COLORS = {
  Education: '#10B981', // Emerald
  Technology: '#3B82F6', // Blue
  Career: '#6366F1', // Indigo
  Productivity: '#8B5CF6', // Purple
  Entertainment: '#F59E0B', // Amber
  Gaming: '#EF4444', // Red
  Vlog: '#EC4899', // Pink
  Music: '#06B6D4', // Cyan
  News: '#14B8A6', // Teal
  Shorts: '#F97316', // Orange
  Other: '#64748B' // Slate
};

export default function DailyOverview({ dailyData }) {
  if (!dailyData) return null;

  const {
    total_watch_minutes = 0,
    productivity_score = 100,
    category_breakdown = {},
    category_limits = {}
  } = dailyData;

  const categories = Object.keys(category_breakdown);
  const minutes = Object.values(category_breakdown);

  const chartData = {
    labels: categories.length > 0 ? categories : ['No watch activity'],
    datasets: [
      {
        data: minutes.length > 0 ? minutes : [1],
        backgroundColor: categories.length > 0 
          ? categories.map(c => CATEGORY_COLORS[c] || '#64748B')
          : ['#334155'],
        borderColor: '#131B2E',
        borderWidth: 3,
        hoverOffset: 6,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#94A3B8',
          font: { family: 'Plus Jakarta Sans', size: 11 },
          boxWidth: 12,
          padding: 10,
        },
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label || '';
            const value = context.parsed || 0;
            const pct = total_watch_minutes > 0 ? Math.round((value / total_watch_minutes) * 100) : 0;
            return ` ${label}: ${value}m (${pct}%)`;
          },
        },
      },
    },
    cutout: '72%',
  };

  // Status color for productivity score
  let scoreBadgeClass = 'badge-emerald';
  let scoreComment = 'High Focus & Learning';
  if (productivity_score < 45) {
    scoreBadgeClass = 'badge-rose';
    scoreComment = 'Leisure Drift Detected';
  } else if (productivity_score < 75) {
    scoreBadgeClass = 'badge-amber';
    scoreComment = 'Balanced Viewing';
  }

  return (
    <div className="glass-card flex flex-col gap-6">
      <div className="flex justify-between items-center border-b border-[rgba(255,255,255,0.08)] pb-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Clock className="text-indigo-400" size={20} />
            Today's Wellbeing & Time Allocation
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Real-time category breakdown and budget consumption</p>
        </div>
        <div className="text-right">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Total Active Watch</span>
          <span className="text-2xl font-black text-indigo-300">{total_watch_minutes.toFixed(0)} <span className="text-sm font-medium text-slate-400">min</span></span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
        {/* Doughnut Chart */}
        <div className="relative h-60 flex items-center justify-center">
          <Doughnut data={chartData} options={chartOptions} />
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none pb-8">
            <span className="text-3xl font-extrabold text-slate-100">{productivity_score.toFixed(0)}</span>
            <span className="text-[10px] font-bold text-slate-400 tracking-widest uppercase">PROD SCORE</span>
          </div>
        </div>

        {/* Category Budget Meters */}
        <div className="flex flex-col gap-4">
          <div className="flex justify-between items-center bg-[rgba(255,255,255,0.03)] p-3 rounded-xl border border-[rgba(255,255,255,0.06)]">
            <div className="flex items-center gap-2.5">
              <Award className="text-amber-400" size={18} />
              <div>
                <div className="text-xs text-slate-400">Productivity Score</div>
                <div className="text-sm font-bold text-slate-200">{scoreComment}</div>
              </div>
            </div>
            <span className={`badge ${scoreBadgeClass}`}>{productivity_score.toFixed(0)} / 100</span>
          </div>

          <div className="flex flex-col gap-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Category Limits Progress</span>
            {categories.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No watch sessions recorded yet today. Open YouTube to begin tracking.</p>
            ) : (
              categories.map(cat => {
                const used = category_breakdown[cat] || 0;
                const limit = category_limits[cat] || 60;
                const pct = Math.min(100, Math.round((used / limit) * 100));
                const isExceeded = used >= limit && ['Entertainment', 'Gaming', 'Vlog', 'Music', 'Shorts'].includes(cat);

                return (
                  <div key={cat} className="progress-container">
                    <div className="progress-header">
                      <span className="flex items-center gap-1.5 text-xs text-slate-300">
                        <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: CATEGORY_COLORS[cat] || '#64748B' }}></span>
                        {cat}
                        {isExceeded && <ShieldAlert size={13} className="text-rose-400 inline" />}
                      </span>
                      <span className="text-xs text-slate-400">
                        <strong className={isExceeded ? "text-rose-400" : "text-slate-200"}>{used.toFixed(0)}m</strong> / {limit}m ({pct}%)
                      </span>
                    </div>
                    <div className="progress-track-lg">
                      <div 
                        className="progress-fill" 
                        style={{ 
                          width: `${pct}%`, 
                          backgroundColor: isExceeded ? '#EF4444' : CATEGORY_COLORS[cat] || '#6366F1' 
                        }}
                      />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
