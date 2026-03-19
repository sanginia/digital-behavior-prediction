/**
 * RiskTrendChart - Line chart showing abandonment risk over time
 */

'use client';

import { Prediction } from '@/types';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { formatDateTime } from '@/lib/utils';

interface RiskTrendChartProps {
  predictions: Prediction[];
}

export default function RiskTrendChart({ predictions }: RiskTrendChartProps) {
  const data = predictions
    .slice()
    .reverse()
    .map(p => ({
      timestamp: formatDateTime(p.timestamp),
      risk: Math.round(p.abandonment_risk_score * 100),
      contextSwitch: Math.round(p.context_switch_likelihood * 100),
    }));

  if (data.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-slate-200 p-6 card-shadow">
        <h3 className="font-semibold text-slate-900 mb-4">Risk Trend</h3>
        <div className="h-64 flex items-center justify-center text-slate-400">
          No prediction data available
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6 card-shadow">
      <h3 className="font-semibold text-slate-900 mb-4">Risk Trend Over Time</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="timestamp"
            tick={{ fill: '#64748b', fontSize: 12 }}
            tickLine={{ stroke: '#cbd5e1' }}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fill: '#64748b', fontSize: 12 }}
            tickLine={{ stroke: '#cbd5e1' }}
            label={{ value: 'Risk Score (%)', angle: -90, position: 'insideLeft', fill: '#64748b' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="risk"
            name="Abandonment Risk"
            stroke="#ef4444"
            strokeWidth={2}
            dot={{ fill: '#ef4444', r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line
            type="monotone"
            dataKey="contextSwitch"
            name="Context Switch"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={{ fill: '#f59e0b', r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
