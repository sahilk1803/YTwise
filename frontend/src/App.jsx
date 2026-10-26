import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DailyOverview from './components/DailyOverview';
import IntentRealityCard from './components/IntentRealityCard';
import WeeklyTrend from './components/WeeklyTrend';
import TopTopicsList from './components/TopTopicsList';
import GoalSettingsModal from './components/GoalSettingsModal';
import { fetchDailyAnalytics, fetchWeeklyAnalytics, fetchProfile, seedDemoData } from './services/api';
import { Clock, Award, Target, Flame, ExternalLink, HelpCircle, Sparkles, RefreshCw } from 'lucide-react';

export default function App() {
  const [dailyData, setDailyData] = useState(null);
  const [weeklyData, setWeeklyData] = useState(null);
  const [profileData, setProfileData] = useState(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadAllData = async (isInitial = false) => {
    try {
      if (isInitial) setInitialLoading(true);
      else setIsRefreshing(true);
      setError(null);
      
      const [daily, weekly, profile] = await Promise.all([
        fetchDailyAnalytics('default_user'),
        fetchWeeklyAnalytics('default_user'),
        fetchProfile('default_user'),
      ]);
      setDailyData(daily);
      setWeeklyData(weekly);
      setProfileData(profile);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Unable to connect to YouTubeWise backend (http://localhost:8000). Please make sure the backend is running with "start_backend.bat".');
    } finally {
      setInitialLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadAllData(true);
    // Auto-refresh every 15 seconds to sync with extension watch events
    const interval = setInterval(() => loadAllData(false), 15000);
    return () => clearInterval(interval);
  }, []);

  const handleSeedDemo = async () => {
    try {
      setIsSeeding(true);
      await seedDemoData('default_user');
      await loadAllData(false);
    } catch (err) {
      console.error('Failed to seed demo data:', err);
    } finally {
      setIsSeeding(false);
    }
  };

  if (initialLoading && !dailyData) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#0B0F19] text-white p-6">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <h2 className="text-xl font-bold tracking-tight">Connecting to YouTubeWise...</h2>
          <p className="text-xs text-slate-400">Loading intelligence and session data from backend</p>
        </div>
      </div>
    );
  }

  // Top highlight stats
  const totalMins = (dailyData && dailyData.total_watch_minutes) || 0;
  const prodScore = (dailyData && dailyData.productivity_score) !== undefined ? dailyData.productivity_score : 100;
  const intentMatch = (dailyData && dailyData.intent_match_pct) !== undefined ? dailyData.intent_match_pct : 100;
  
  const entUsed = (dailyData && dailyData.category_breakdown && dailyData.category_breakdown.Entertainment) || 0;
  const entLimit = (dailyData && dailyData.category_limits && dailyData.category_limits.Entertainment) || 25;
  const entRemaining = Math.max(0, entLimit - entUsed);
  const isFreshData = totalMins === 0 && (!weeklyData || weeklyData.average_daily_minutes === 0);

  return (
    <div className="dashboard-container">
      {/* Navbar */}
      <Navbar
        onOpenSettings={() => setIsSettingsOpen(true)}
        onSeedDemo={handleSeedDemo}
        onRefresh={() => loadAllData(false)}
        isSeeding={isSeeding}
        isRefreshing={isRefreshing}
      />

      {/* Backend Error Alert if any */}
      {error && (
        <div className="bg-rose-950/60 border border-rose-700 text-rose-200 p-4 rounded-2xl text-xs flex justify-between items-center shadow-lg">
          <span className="font-medium">⚠️ {error}</span>
          <button className="btn btn-secondary text-xs py-1.5 px-3 bg-rose-900/60 hover:bg-rose-800" onClick={() => loadAllData(false)}>
            <RefreshCw size={13} className="mr-1 inline" /> Retry Connection
          </button>
        </div>
      )}

      {/* Welcome & Demo prompt if fresh database */}
      {isFreshData && !error && (
        <div className="bg-gradient-to-r from-indigo-900/40 via-purple-900/30 to-slate-900/50 border border-indigo-500/30 p-4 rounded-2xl flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center text-xl flex-shrink-0">
              ✨
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-100">Welcome to YouTubeWise Dashboard!</h4>
              <p className="text-xs text-slate-300">No watch history detected yet. You can start watching YouTube videos with the extension or load sample data.</p>
            </div>
          </div>
          <button 
            className="btn btn-primary text-xs py-2 px-4 whitespace-nowrap flex-shrink-0"
            onClick={handleSeedDemo}
            disabled={isSeeding}
          >
            <Sparkles size={14} className="text-amber-300" />
            <span>{isSeeding ? "Loading..." : "Load 7-Day Demo Data"}</span>
          </button>
        </div>
      )}

      {/* Top Hero Stat Highlight Cards */}
      <div className="metrics-row">
        {/* Stat 1: Total Watch Today */}
        <div className="glass-card stat-card">
          <div className="stat-header">
            <span className="stat-title">Watch Time Today</span>
            <div className="stat-icon-wrap text-indigo-400">
              <Clock size={18} />
            </div>
          </div>
          <div className="stat-number text-indigo-300">
            {totalMins.toFixed(0)} <span className="text-sm font-semibold text-slate-400">min</span>
          </div>
          <p className="stat-desc">Active viewing logged today</p>
        </div>

        {/* Stat 2: Productivity Score */}
        <div className="glass-card stat-card">
          <div className="stat-header">
            <span className="stat-title">Productivity Score</span>
            <div className="stat-icon-wrap text-emerald-400">
              <Award size={18} />
            </div>
          </div>
          <div className="stat-number text-emerald-400">
            {prodScore.toFixed(0)} <span className="text-sm font-semibold text-slate-400">/ 100</span>
          </div>
          <p className="stat-desc">Learning & career vs. leisure ratio</p>
        </div>

        {/* Stat 3: Intent Match */}
        <div className="glass-card stat-card">
          <div className="stat-header">
            <span className="stat-title">Intent Alignment</span>
            <div className="stat-icon-wrap text-cyan-400">
              <Target size={18} />
            </div>
          </div>
          <div className="stat-number text-cyan-300">
            {intentMatch.toFixed(0)}%
          </div>
          <p className="stat-desc">Stated focus vs actual viewed content</p>
        </div>

        {/* Stat 4: Entertainment Allowance */}
        <div className="glass-card stat-card">
          <div className="stat-header">
            <span className="stat-title">Leisure Budget Left</span>
            <div className="stat-icon-wrap text-amber-400">
              <Flame size={18} />
            </div>
          </div>
          <div className={`stat-number ${entRemaining === 0 ? 'text-rose-400' : 'text-amber-300'}`}>
            {entRemaining.toFixed(0)} <span className="text-sm font-semibold text-slate-400">min</span>
          </div>
          <p className="stat-desc">{entUsed.toFixed(0)}m of {entLimit}m cap used today</p>
        </div>
      </div>

      {/* Main Grid: Left Column (Visualizations) + Right Column (Intent & Quick Help) */}
      <div className="main-grid">
        <div className="flex flex-col gap-6">
          <DailyOverview dailyData={dailyData} />
          <WeeklyTrend weeklyData={weeklyData} />
          <TopTopicsList dailyData={dailyData} weeklyData={weeklyData} />
        </div>

        <div className="flex flex-col gap-6">
          <IntentRealityCard dailyData={dailyData} onIntentUpdated={() => loadAllData(false)} />

          {/* Extension Quick Instructions Card */}
          <div className="glass-card flex flex-col gap-4">
            <div className="flex items-center gap-2 border-b border-[rgba(255,255,255,0.08)] pb-3">
              <HelpCircle className="text-indigo-400" size={18} />
              <h3 className="text-sm font-bold text-slate-200">Chrome Extension Companion</h3>
            </div>
            
            <p className="text-xs text-slate-300 leading-relaxed">
              Install the unpacked extension in Chrome or Edge from the <code className="bg-slate-800 px-1.5 py-0.5 rounded text-indigo-300 font-mono text-[11px]">extension/</code> directory to get:
            </p>

            <ul className="text-xs text-slate-300 space-y-2 pl-4 list-disc">
              <li>In-page video value score pill on YouTube</li>
              <li>Dismissible limit warning interventions</li>
              <li>Real-time AI Chatbot advisor in the Side Panel</li>
              <li>Active watch duration tracking synced live to this dashboard</li>
            </ul>

            <div className="pt-2">
              <a 
                href="https://www.youtube.com" 
                target="_blank" 
                rel="noreferrer"
                className="btn btn-secondary w-full justify-center text-xs"
              >
                <span>Open YouTube</span>
                <ExternalLink size={13} />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Settings Modal */}
      <GoalSettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        profileData={profileData}
        onProfileSaved={() => loadAllData(false)}
      />
    </div>
  );
}
