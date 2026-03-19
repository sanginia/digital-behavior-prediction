/**
 * PredictionCard - Display prediction information with explanation
 */

'use client';

import { Prediction } from '@/types';
import { formatRelativeTime } from '@/lib/utils';
import RiskBadge from './RiskBadge';
import { AlertTriangle, Zap } from 'lucide-react';

interface PredictionCardProps {
  prediction: Prediction;
}

export default function PredictionCard({ prediction }: PredictionCardProps) {
  const factors = prediction.contributing_factors
    ? prediction.contributing_factors.split(',').map(f => f.trim().replace(/_/g, ' '))
    : [];

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-5 card-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-amber-500" />
          <h3 className="font-semibold text-slate-900">Prediction Analysis</h3>
        </div>
        <span className="text-xs text-slate-500">{formatRelativeTime(prediction.timestamp)}</span>
      </div>

      <div className="space-y-4">
        {/* Risk Scores */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <p className="text-xs text-slate-600 mb-1.5">Abandonment Risk</p>
            <RiskBadge score={prediction.abandonment_risk_score} />
          </div>
          <div>
            <p className="text-xs text-slate-600 mb-1.5">Context Switch Likelihood</p>
            <RiskBadge score={prediction.context_switch_likelihood} showLabel={false} />
          </div>
        </div>

        {/* Explanation */}
        <div className="bg-slate-50 rounded-lg p-3">
          <p className="text-sm text-slate-700 leading-relaxed">{prediction.explanation}</p>
        </div>

        {/* Contributing Factors */}
        {factors.length > 0 && (
          <div>
            <p className="text-xs font-medium text-slate-600 mb-2 flex items-center gap-1">
              <Zap className="w-3 h-3" />
              Contributing Factors
            </p>
            <div className="flex flex-wrap gap-2">
              {factors.map((factor, idx) => (
                <span
                  key={idx}
                  className="text-xs px-2 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200"
                >
                  {factor}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
