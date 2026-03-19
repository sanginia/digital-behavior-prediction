/**
 * API client for Digital Behavior Twin backend
 */

import {
  Session,
  Prediction,
  BrowserEvent,
  SessionAnalysis,
  Intervention
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const USER_ID = process.env.NEXT_PUBLIC_USER_ID || '1';

const headers = {
  'Content-Type': 'application/json',
  'X-User-ID': USER_ID,
};

/**
 * Sessions API
 */
export const sessionsAPI = {
  /**
   * Get recent sessions for the user
   */
  async getAll(limit: number = 20): Promise<Session[]> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/sessions?limit=${limit}`,
      { headers }
    );
    if (!response.ok) throw new Error('Failed to fetch sessions');
    return response.json();
  },

  /**
   * Get a specific session by ID
   */
  async getById(sessionId: number): Promise<Session> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/sessions/${sessionId}`,
      { headers }
    );
    if (!response.ok) throw new Error('Failed to fetch session');
    return response.json();
  },

  /**
   * Get comprehensive analysis for a session
   */
  async getAnalysis(sessionId: number): Promise<SessionAnalysis> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/sessions/${sessionId}/analysis`,
      { headers }
    );
    if (!response.ok) throw new Error('Failed to fetch session analysis');
    return response.json();
  },

  /**
   * Trigger feature computation for a session
   */
  async computeFeatures(sessionId: number): Promise<any> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/sessions/${sessionId}/compute-features`,
      { method: 'POST', headers }
    );
    if (!response.ok) throw new Error('Failed to compute features');
    return response.json();
  },
};

/**
 * Predictions API
 */
export const predictionsAPI = {
  /**
   * Create a new prediction for a session
   */
  async create(sessionId: number): Promise<Prediction> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/predictions/session/${sessionId}`,
      { method: 'POST', headers }
    );
    if (!response.ok) throw new Error('Failed to create prediction');
    return response.json();
  },

  /**
   * Get all predictions for a session
   */
  async getForSession(sessionId: number): Promise<Prediction[]> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/predictions/session/${sessionId}`,
      { headers }
    );
    if (!response.ok) throw new Error('Failed to fetch predictions');
    return response.json();
  },

  /**
   * Get recent predictions for the user
   */
  async getRecent(limit: number = 20): Promise<Prediction[]> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/predictions/recent?limit=${limit}`,
      { headers }
    );
    if (!response.ok) throw new Error('Failed to fetch recent predictions');
    return response.json();
  },

  /**
   * Get interventions for a prediction
   */
  async getInterventions(predictionId: number): Promise<Intervention[]> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/predictions/${predictionId}/interventions`,
      { headers }
    );
    if (!response.ok) throw new Error('Failed to fetch interventions');
    return response.json();
  },

  /**
   * Mark an intervention as displayed
   */
  async markInterventionDisplayed(interventionId: number): Promise<any> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/predictions/interventions/${interventionId}/mark-displayed`,
      { method: 'PUT', headers }
    );
    if (!response.ok) throw new Error('Failed to mark intervention as displayed');
    return response.json();
  },
};

/**
 * Events API
 */
export const eventsAPI = {
  /**
   * Get events for a specific session
   */
  async getForSession(sessionId: number): Promise<BrowserEvent[]> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/events/session/${sessionId}`,
      { headers }
    );
    if (!response.ok) throw new Error('Failed to fetch events');
    return response.json();
  },

  /**
   * Get recent events for the user
   */
  async getRecent(limit: number = 50): Promise<BrowserEvent[]> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/events/recent?limit=${limit}`,
      { headers }
    );
    if (!response.ok) throw new Error('Failed to fetch recent events');
    return response.json();
  },
};

/**
 * Health check
 */
export async function healthCheck(): Promise<{ status: string; service: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) throw new Error('Health check failed');
  return response.json();
}
