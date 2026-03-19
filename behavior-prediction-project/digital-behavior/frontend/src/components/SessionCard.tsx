/**
 * SessionCard - Display session summary information
 */

'use client';

import { Session } from '@/types';
import { formatDuration, formatRelativeTime } from '@/lib/utils';
import { Clock, MousePointer, Globe } from 'lucide-react';

interface SessionCardProps {
  session: Session;
  onClick?: () => void;
}

export default function SessionCard({ session, onClick }: SessionCardProps) {
  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg border border-slate-200 p-4 card-shadow card-shadow-hover transition-all cursor-pointer hover:border-slate-300"
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="font-semibold text-slate-900">Session {session.id}</h3>
          <p className="text-sm text-slate-500">{formatRelativeTime(session.start_time)}</p>
        </div>
        <span className="text-xs font-medium px-2 py-1 rounded-full bg-slate-100 text-slate-700">
          {formatDuration(session.active_duration_seconds)}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3 text-sm">
        <div className="flex items-center gap-2 text-slate-600">
          <Clock className="w-4 h-4" />
          <div>
            <div className="font-medium">{Math.round(session.active_duration_seconds / 60)}m</div>
            <div className="text-xs text-slate-400">Duration</div>
          </div>
        </div>

        <div className="flex items-center gap-2 text-slate-600">
          <MousePointer className="w-4 h-4" />
          <div>
            <div className="font-medium">{session.switch_count}</div>
            <div className="text-xs text-slate-400">Switches</div>
          </div>
        </div>

        <div className="flex items-center gap-2 text-slate-600">
          <Globe className="w-4 h-4" />
          <div>
            <div className="font-medium">{(session.domain_diversity * 100).toFixed(0)}%</div>
            <div className="text-xs text-slate-400">Diversity</div>
          </div>
        </div>
      </div>
    </div>
  );
}
