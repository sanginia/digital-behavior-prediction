/**
 * TypeScript type definitions for Digital Behavior Twin
 */

export interface BrowserEvent {
  id: number;
  session_id: number;
  event_type: string;
  url?: string;
  domain?: string;
  title?: string;
  tab_id?: number;
  window_id?: number;
  is_active: boolean;
  timestamp: string;
}

export interface Session {
  id: number;
  user_id: number;
  start_time: string;
  end_time?: string;
  active_duration_seconds: number;
  switch_count: number;
  domain_diversity: number;
  inactivity_gap_seconds: number;
}

export interface FeatureSnapshot {
  id: number;
  session_id: number;
  timestamp: string;
  session_length_minutes: number;
  avg_time_per_tab_seconds: number;
  tab_switch_frequency: number;
  repeated_revisits: number;
  unique_domains_count: number;
  inactivity_gap_detected: boolean;
  late_night_behavior: boolean;
  volatility_score: number;
  task_continuity_estimate: number;
}

export interface Prediction {
  id: number;
  session_id: number;
  timestamp: string;
  abandonment_risk_score: number;
  context_switch_likelihood: number;
  explanation: string;
  contributing_factors: string;
}

export interface Intervention {
  id: number;
  prediction_id: number;
  suggested_intervention: string;
  rule_triggered: string;
  is_displayed: boolean;
  displayed_at?: string;
}

export interface SessionAnalysis {
  session: Session;
  events_count: number;
  events: Array<{
    id: number;
    event_type: string;
    domain: string;
    timestamp: string;
    tab_id: number;
  }>;
  features: {
    session_length_minutes: number;
    tab_switch_frequency: number;
    avg_time_per_tab_seconds: number;
    volatility_score: number;
    task_continuity_estimate: number;
    unique_domains_count: number;
    late_night_behavior: boolean;
  } | null;
  predictions: Array<{
    id: number;
    abandonment_risk_score: number;
    context_switch_likelihood: number;
    explanation: string;
    timestamp: string;
  }>;
}

export type RiskLevel = 'low' | 'medium' | 'high';

export interface DashboardStats {
  totalSessions: number;
  totalEvents: number;
  averageRiskScore: number;
  recentPredictions: Prediction[];
}
