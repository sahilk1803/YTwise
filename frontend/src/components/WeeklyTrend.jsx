import React from 'react';
import 'chart.js/auto';
import { Bar } from 'react-chartjs-2';
import { TrendingUp, Zap } from 'lucide-react';

const CATEGORIES = ["Education", "Technology", "Career", "Productivity", "Entertainment", "Gaming", "Vlog", "Music", "Other"];
const CATEGORY_COLORS = {
  Education: '#10B981',
  Technology: '#3B82F6',
  Career: '#6366F1',
  Productivity: '#8B5CF6',
  Entertainment: '#F59E0B',
  Gaming: '#EF4444',
  Vlog: '#EC4899',
  Music: '#06B6D4',
  Other: '#64748B'
};

export default function WeeklyTrend({ weeklyData }) {
  if (!weeklyData || !weeklyData.days) return null;

  const labels = weeklyData.days.map(d => `${d.day_name} (${d.date.slice(5)})`);

  // Build datasets for each category
  const datasets = CATEGORIES.map(cat => ({
    label: cat,
    data: weeklyData.days.map(d => (d.category_breakdown && d.category_breakdown[cat]) || 0),
    backgroundColor: CATEGORY_COLORS[cat],
    borderRadius: 4,
    stack: 'Stack 0',
  }));

  const chartData = {
    labels,
    datasets,
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#94A3B8',
          font: { family: 'Plus Jakarta Sans', size: 11 },
          boxWidth: 10,
          padding: 8,
        },
      },
      tooltip: {
        callbacks: {
          afterTitle: (items) => {
            const dayIdx = items[0].dataIndex;
            const day = weeklyData.days[dayIdx];
            return `Total: ${day.total_minutes.toFixed(0)}m | Prod: ${day.productivity_score.toFixed(0)}%`;
          }
        }
      }
    },
    scales: {
      x: {
        stacked: true,
        grid: { color: 'rgba(255, 255, 255, 0.04)' },
        ticks: { color: '#94A3B8', font: { size: 11 } },
      },
      y: {
        stacked: true,
        grid: { color: 'rgba(255, 255, 255, 0.04)' },
        ticks: {
          color: '#94A3B8',
          font: { size: 11 },
          callback: (value) => `${value}m`,
        },
        title: {
          display: true,
          text: 'Minutes Watched',
          color: '#64748B',
          font: { size: 11 }
        }
      },
    },
  };

  return (
    <div className="glass-card flex flex-col gap-5">
      <div className="flex justify-between items-center border-b border-[rgba(255,255,255,0.08)] pb-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <TrendingUp className="text-indigo-400" size={20} />
            7-Day Category Habits & Trends
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Stacked daily breakdown of learning vs. entertainment over time</p>
        </div>

        <div className="flex gap-4 text-right">
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Avg Daily Time</span>
            <span className="text-base font-bold text-slate-200">{weeklyData.average_daily_minutes.toFixed(0)}m</span>
          </div>
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Weekly Avg Prod</span>
            <span className="text-base font-bold text-emerald-400">{weeklyData.average_productivity_score.toFixed(0)}%</span>
          </div>
        </div>
      </div>

      {/* Stacked Bar Chart */}
      <div className="h-72 w-full">
        <Bar data={chartData} options={chartOptions} />
      </div>

      {/* Weekly Assessment Banner */}
      <div className="bg-[rgba(99,102,241,0.06)] border border-[rgba(99,102,241,0.18)] rounded-xl p-3.5 flex items-center gap-3">
        <Zap className="text-indigo-400 flex-shrink-0" size={18} />
        <span className="text-xs text-slate-300 font-medium leading-relaxed">
          {weeklyData.weekly_ai_assessment}
        </span>
      </div>
    </div>
  );
}
