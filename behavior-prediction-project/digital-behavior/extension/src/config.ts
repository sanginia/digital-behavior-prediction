/**
 * Extension Configuration
 *
 * For production deployment:
 * 1. Update API_BASE_URL to your production backend URL
 * 2. Rebuild the extension: npm run build
 * 3. Load the updated dist/ folder in Chrome
 */

export const config = {
  // API Configuration
  // For production:
  API_BASE_URL: 'https://digital-behavior-backend.onrender.com/api/v1',

  // For local development:
  // API_BASE_URL: 'http://localhost:8000/api/v1',

  // Batch and sync settings
  BATCH_SIZE: 10,
  SYNC_INTERVAL_MS: 30000, // 30 seconds

  // User configuration (MVP: single user)
  USER_ID: 1
};
