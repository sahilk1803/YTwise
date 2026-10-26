import React, { useState, useEffect } from 'react';
import { X, Save, Check } from 'lucide-react';
import { updateProfile } from '../services/api';

const ALL_CATEGORIES = [
  "Education", "Career", "Technology", "Productivity", 
  "Entertainment", "Gaming", "Vlog", "Music", "News", "Shorts", "Other"
];

export default function GoalSettingsModal({ isOpen, onClose, profileData, onProfileSaved }) {
  if (!isOpen) return null;

  const [primaryGoal, setPrimaryGoal] = useState('');
  const [learningTopics, setLearningTopics] = useState('');
  const [dailyBudget, setDailyBudget] = useState(120);
  const [categoryLimits, setCategoryLimits] = useState({});
  const [customUseful, setCustomUseful] = useState([]);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (profileData) {
      setPrimaryGoal(profileData.primary_goal || '');
      setLearningTopics((profileData.learning_topics || []).join(', '));
      setDailyBudget(profileData.daily_budget_min || 120);
      setCategoryLimits(profileData.category_limits || {});
      setCustomUseful(profileData.custom_useful_categories || ["Education", "Career", "Technology", "Productivity"]);
    }
  }, [profileData]);

  const toggleUsefulCategory = (cat) => {
    if (customUseful.includes(cat)) {
      setCustomUseful(customUseful.filter(c => c !== cat));
    } else {
      setCustomUseful([...customUseful, cat]);
    }
  };

  const handleLimitChange = (cat, val) => {
    setCategoryLimits({
      ...categoryLimits,
      [cat]: parseInt(val) || 0
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setIsSaving(true);
      const payload = {
        primary_goal: primaryGoal.trim(),
        learning_topics: learningTopics.split(',').map(t => t.trim()).filter(Boolean),
        daily_budget_min: parseInt(dailyBudget) || 120,
        category_limits: categoryLimits,
        custom_useful_categories: customUseful
      };

      await updateProfile('default_user', payload);
      setSaveSuccess(true);
      setTimeout(() => {
        setSaveSuccess(false);
        if (onProfileSaved) onProfileSaved();
        onClose();
      }, 1000);
    } catch (err) {
      console.error('Failed to update profile settings:', err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header border-b border-[rgba(255,255,255,0.08)] pb-4">
          <div>
            <h2 className="modal-title text-slate-100">Personal Goals & Limits Setup</h2>
            <p className="text-xs text-slate-400 mt-0.5">Customize what counts as productive and configure time budgets</p>
          </div>
          <button className="text-slate-400 hover:text-white p-1 rounded-lg" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          {/* Primary Goal */}
          <div className="form-group">
            <label className="form-label">Primary Learning / Career Goal</label>
            <input
              type="text"
              className="form-input"
              value={primaryGoal}
              onChange={(e) => setPrimaryGoal(e.target.value)}
              placeholder="e.g. Placement Preparation (DSA, AI/ML, System Design)"
              required
            />
          </div>

          {/* Topics */}
          <div className="form-group">
            <label className="form-label">Target Learning Topics (comma-separated)</label>
            <input
              type="text"
              className="form-input"
              value={learningTopics}
              onChange={(e) => setLearningTopics(e.target.value)}
              placeholder="DSA, Machine Learning, System Design, Python, React"
            />
          </div>

          {/* Total Budget */}
          <div className="form-group">
            <label className="form-label">Daily Total YouTube Budget (minutes)</label>
            <input
              type="number"
              className="form-input"
              value={dailyBudget}
              onChange={(e) => setDailyBudget(e.target.value)}
              min="10"
              max="600"
            />
          </div>

          {/* Custom Useful Categories */}
          <div className="form-group">
            <label className="form-label">Define Your Personally "Useful" Categories</label>
            <p className="text-[11px] text-slate-400 mb-2">Selected categories will be scored as productive rather than leisure.</p>
            <div className="flex flex-wrap gap-2">
              {ALL_CATEGORIES.map(cat => {
                const isChecked = customUseful.includes(cat);
                return (
                  <button
                    type="button"
                    key={cat}
                    onClick={() => toggleUsefulCategory(cat)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                      isChecked 
                        ? 'bg-indigo-600/30 border-indigo-500 text-indigo-200' 
                        : 'bg-[rgba(255,255,255,0.04)] border-[rgba(255,255,255,0.08)] text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {isChecked ? '✓ ' : '+ '}{cat}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Individual Category Caps */}
          <div className="form-group">
            <label className="form-label">Category Time Limits (minutes per day)</label>
            <div className="grid grid-cols-2 gap-3 mt-1">
              {["Entertainment", "Gaming", "Vlog", "Music", "Education", "Career"].map(cat => (
                <div key={cat} className="flex justify-between items-center bg-[rgba(255,255,255,0.03)] p-2 rounded-lg border border-[rgba(255,255,255,0.06)]">
                  <span className="text-xs text-slate-300">{cat}</span>
                  <input
                    type="number"
                    className="w-16 bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-right text-slate-100"
                    value={categoryLimits[cat] || 20}
                    onChange={(e) => handleLimitChange(cat, e.target.value)}
                    min="5"
                    max="300"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-3 border-t border-[rgba(255,255,255,0.08)]">
            <button type="button" className="btn btn-secondary text-xs" onClick={onClose}>
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn btn-primary text-xs"
              disabled={isSaving}
            >
              {saveSuccess ? (
                <>
                  <Check size={14} />
                  <span>Saved!</span>
                </>
              ) : (
                <>
                  <Save size={14} />
                  <span>{isSaving ? "Saving..." : "Save Settings"}</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
