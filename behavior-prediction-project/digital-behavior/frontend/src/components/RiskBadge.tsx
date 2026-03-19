/**
 * RiskBadge - Display risk level with color coding
 */

import { getRiskColor, getRiskLabel, formatPercent } from '@/lib/utils';

interface RiskBadgeProps {
  score: number;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export default function RiskBadge({ score, showLabel = true, size = 'md' }: RiskBadgeProps) {
  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2',
  };

  return (
    <span className={`inline-flex items-center gap-1 font-semibold rounded-full ${getRiskColor(score)} ${sizeClasses[size]}`}>
      {showLabel && <span>{getRiskLabel(score)}</span>}
      <span className="opacity-75">{formatPercent(score)}</span>
    </span>
  );
}
