import React from 'react';
import { ListOrdered, Tv, Video } from 'lucide-react';

export default function TopTopicsList({ dailyData, weeklyData }) {
  const topVideos = (dailyData && dailyData.top_videos) || [];
  const topChannels = (weeklyData && weeklyData.top_channels) || [];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Top Videos Today */}
      <div className="glass-card flex flex-col gap-4">
        <div className="flex items-center gap-2 border-b border-[rgba(255,255,255,0.08)] pb-3">
          <Video className="text-indigo-400" size={18} />
          <h3 className="text-sm font-bold text-slate-200">Top Videos Watched Today</h3>
        </div>

        <div className="flex flex-col gap-2.5">
          {topVideos.length === 0 ? (
            <p className="text-xs text-slate-400 italic py-2">No videos logged today yet.</p>
          ) : (
            topVideos.map((v, idx) => (
              <div key={idx} className="flex justify-between items-center bg-[rgba(255,255,255,0.03)] p-2.5 rounded-xl border border-[rgba(255,255,255,0.05)]">
                <div className="flex items-center gap-2.5 min-w-0 pr-2">
                  <span className="text-xs font-bold text-slate-500 w-4 text-center">{idx + 1}</span>
                  <div className="truncate">
                    <div className="text-xs font-semibold text-slate-200 truncate">{v.title}</div>
                    <span className="text-[10px] text-indigo-400 font-medium">{v.category}</span>
                  </div>
                </div>
                <span className="text-xs font-bold text-slate-300 bg-[rgba(255,255,255,0.06)] px-2 py-1 rounded-md flex-shrink-0">
                  {v.minutes}
                </span>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Top Channels & Creators This Week */}
      <div className="glass-card flex flex-col gap-4">
        <div className="flex items-center gap-2 border-b border-[rgba(255,255,255,0.08)] pb-3">
          <Tv className="text-indigo-400" size={18} />
          <h3 className="text-sm font-bold text-slate-200">Top Channels This Week</h3>
        </div>

        <div className="flex flex-col gap-2.5">
          {topChannels.length === 0 ? (
            <p className="text-xs text-slate-400 italic py-2">No channel data available yet.</p>
          ) : (
            topChannels.map((c, idx) => (
              <div key={idx} className="flex justify-between items-center bg-[rgba(255,255,255,0.03)] p-2.5 rounded-xl border border-[rgba(255,255,255,0.05)]">
                <div className="flex items-center gap-2.5">
                  <span className="text-xs font-bold text-slate-500 w-4 text-center">{idx + 1}</span>
                  <span className="text-xs font-semibold text-slate-200">{c.channel}</span>
                </div>
                <span className="text-xs font-bold text-slate-300 bg-[rgba(255,255,255,0.06)] px-2 py-1 rounded-md">
                  {c.minutes.toFixed(0)} min
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
