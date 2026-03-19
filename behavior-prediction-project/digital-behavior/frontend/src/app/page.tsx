/**
 * Main Dashboard Page
 *
 * Displays overview of browsing sessions, behavioral analytics,
 * risk predictions, and interventions.
 */

'use client';

import { useState, useEffect } from 'react';
import { Session, Prediction } from '@/types';
import { sessionsAPI, predictionsAPI } from '@/lib/api';
import { average, formatDuration } from '@/lib/utils';
import StatCard from '@/components/StatCard';
import SessionCard from '@/components/SessionCard';
import PredictionCard from '@/components/PredictionCard';
import RiskTrendChart from '@/components/RiskTrendChart';
import { Activity, Clock, AlertTriangle, TrendingUp } from 'lucide-react';

export default function Dashboard() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  async function loadDashboardData() {
    setLoading(true);
    setError(null);

    try {
      const [sessionsData, predictionsData] = await Promise.all([
        sessionsAPI.getAll(20),
        predictionsAPI.getRecent(20),
      ]);

      setSessions(sessionsData);
      setPredictions(predictionsData);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  }

  // Calculate statistics
  const totalSessions = sessions.length;
  const totalDuration = sessions.reduce((sum, s) => sum + s.active_duration_seconds, 0);
  const avgRiskScore = predictions.length > 0
    ? average(predictions.map(p => p.abandonment_risk_score))
    : 0;
  const highRiskSessions = predictions.filter(p => p.abandonment_risk_score >= 0.6).length;

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-pulse space-y-4">
            <div className="w-16 h-16 bg-blue-200 rounded-full mx-auto"></div>
            <p className="text-slate-600">Loading dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg border border-red-200 p-6 max-w-md">
          <div className="flex items-center gap-3 mb-3">
            <AlertTriangle className="w-6 h-6 text-red-500" />
            <h2 className="text-lg font-semibold text-slate-900">Connection Error</h2>
          </div>
          <p className="text-slate-600 mb-4">{error}</p>
          <button
            onClick={loadDashboardData}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Digital Behavior Twin</h1>
              <p className="text-slate-600 mt-1">Behavioral modeling and task abandonment prediction</p>
            </div>
            <button
              onClick={loadDashboardData}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <TrendingUp className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Sessions"
            value={totalSessions}
            icon={<Activity className="w-5 h-5" />}
          />
          <StatCard
            title="Total Active Time"
            value={formatDuration(totalDuration)}
            icon={<Clock className="w-5 h-5" />}
          />
          <StatCard
            title="Avg. Risk Score"
            value={`${Math.round(avgRiskScore * 100)}%`}
            icon={<AlertTriangle className="w-5 h-5" />}
          />
          <StatCard
            title="High Risk Sessions"
            value={highRiskSessions}
            icon={<AlertTriangle className="w-5 h-5" />}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Sessions List */}
          <div className="lg:col-span-2 space-y-6">
            {/* Risk Trend Chart */}
            <RiskTrendChart predictions={predictions.slice(0, 10)} />

            {/* Recent Sessions */}
            <div className="bg-white rounded-lg border border-slate-200 p-6 card-shadow">
              <h2 className="text-xl font-semibold text-slate-900 mb-4">Recent Sessions</h2>
              {sessions.length === 0 ? (
                <div className="text-center py-12 text-slate-400">
                  <Activity className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>No sessions yet. Start browsing with the extension installed.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {sessions.slice(0, 10).map(session => (
                    <SessionCard key={session.id} session={session} />
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Predictions & Insights */}
          <div className="space-y-6">
            {/* Latest Prediction */}
            {predictions.length > 0 && (
              <div>
                <h2 className="text-lg font-semibold text-slate-900 mb-4">Latest Prediction</h2>
                <PredictionCard prediction={predictions[0]} />
              </div>
            )}

            {/* Insights Panel */}
            <div className="bg-white rounded-lg border border-slate-200 p-6 card-shadow">
              <h3 className="font-semibold text-slate-900 mb-4">Behavioral Insights</h3>
              <div className="space-y-4 text-sm">
                {totalSessions > 0 && (
                  <>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-600">Avg. Session Duration</span>
                      <span className="font-medium text-slate-900">
                        {formatDuration(totalDuration / totalSessions)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-600">Avg. Tab Switches</span>
                      <span className="font-medium text-slate-900">
                        {Math.round(average(sessions.map(s => s.switch_count)))}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-600">Domain Diversity</span>
                      <span className="font-medium text-slate-900">
                        {Math.round(average(sessions.map(s => s.domain_diversity)) * 100)}%
                      </span>
                    </div>
                  </>
                )}
                {predictions.length > 0 && (
                  <div className="pt-4 border-t border-slate-100">
                    <p className="text-xs text-slate-500 mb-2">RECOMMENDATION</p>
                    <p className="text-slate-700">
                      {avgRiskScore > 0.6
                        ? 'Your attention patterns suggest frequent task switching. Consider taking breaks between tasks.'
                        : avgRiskScore > 0.3
                        ? 'Moderate distraction detected. Try to minimize context switching for better focus.'
                        : 'Your focus patterns are stable. Keep up the good work!'}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Extension Status */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-6">
              <h3 className="font-semibold text-slate-900 mb-2">Extension Active</h3>
              <p className="text-sm text-slate-600 mb-3">
                The Digital Behavior Twin extension is tracking your browsing patterns.
              </p>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span className="text-xs font-medium text-slate-700">
                  {sessions.length} sessions recorded
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
