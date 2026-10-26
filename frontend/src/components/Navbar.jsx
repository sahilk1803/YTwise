import React from 'react';
import { Sparkles, Sliders, RefreshCw, CheckCircle2 } from 'lucide-react';

export default function Navbar({ onOpenSettings, onSeedDemo, onRefresh, isSeeding, isRefreshing }) {
  return (
    <header className="navbar">
      <div className="brand-wrapper">
        <div className="brand-logo-glow">
          <span>🧠</span>
        </div>
        <div>
          <h1 className="brand-title">YouTubeWise</h1>
          <p className="brand-subtitle">AI-Powered Content Intelligence & Digital Wellbeing</p>
        </div>
      </div>

      <div className="nav-actions">
        <div className="badge badge-emerald">
          <CheckCircle2 size={13} />
          <span>System Active</span>
        </div>

        <button 
          className="btn btn-secondary"
          onClick={onRefresh}
          disabled={isRefreshing}
          title="Refresh Dashboard Data"
        >
          <RefreshCw size={15} className={isRefreshing ? "animate-spin" : ""} />
          <span>Refresh</span>
        </button>

        <button 
          className="btn btn-secondary"
          onClick={onSeedDemo}
          disabled={isSeeding}
          title="Load 7-day realistic viewing sample data"
        >
          <Sparkles size={15} className="text-amber-400" />
          <span>{isSeeding ? "Seeding..." : "Load Demo Data"}</span>
        </button>

        <button 
          className="btn btn-primary"
          onClick={onOpenSettings}
        >
          <Sliders size={15} />
          <span>Goals & Limits</span>
        </button>
      </div>
    </header>
  );
}
