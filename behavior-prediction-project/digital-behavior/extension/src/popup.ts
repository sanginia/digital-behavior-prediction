/**
 * Popup UI controller for Digital Behavior Prediction Extension
 *
 * Handles user interactions and displays tracking status
 */

interface ExtensionState {
  isTracking: boolean;
  eventsToday: number;
  lastSyncTime: number;
}

// DOM elements
const statusDot = document.getElementById('statusDot') as HTMLDivElement;
const statusText = document.getElementById('statusText') as HTMLSpanElement;
const toggleButton = document.getElementById('toggleButton') as HTMLButtonElement;
const toggleText = document.getElementById('toggleText') as HTMLSpanElement;
const eventsTodayEl = document.getElementById('eventsToday') as HTMLDivElement;
const lastSyncEl = document.getElementById('lastSync') as HTMLDivElement;
const syncButton = document.getElementById('syncButton') as HTMLButtonElement;
const dashboardButton = document.getElementById('dashboardButton') as HTMLButtonElement;

/**
 * Format timestamp for display
 */
function formatLastSync(timestamp: number): string {
  if (!timestamp) return 'Never';

  const now = Date.now();
  const diff = now - timestamp;

  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (seconds < 60) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return new Date(timestamp).toLocaleDateString();
}

/**
 * Update UI with current state
 */
function updateUI(state: ExtensionState) {
  // Update status indicator
  if (state.isTracking) {
    statusDot.className = 'status-dot active';
    statusText.textContent = 'Tracking Active';
    toggleText.textContent = 'Pause Tracking';
    toggleButton.className = 'toggle-btn';
  } else {
    statusDot.className = 'status-dot inactive';
    statusText.textContent = 'Tracking Paused';
    toggleText.textContent = 'Resume Tracking';
    toggleButton.className = 'toggle-btn inactive';
  }

  // Update stats
  eventsTodayEl.textContent = state.eventsToday.toString();
  lastSyncEl.textContent = formatLastSync(state.lastSyncTime);
}

/**
 * Get current state from background worker
 */
async function getState(): Promise<ExtensionState> {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ action: 'getState' }, (response) => {
      resolve(response as ExtensionState);
    });
  });
}

/**
 * Toggle tracking on/off
 */
async function toggleTracking() {
  toggleButton.disabled = true;

  try {
    const response = await new Promise<{ isTracking: boolean }>((resolve) => {
      chrome.runtime.sendMessage({ action: 'toggleTracking' }, resolve);
    });

    const state = await getState();
    updateUI(state);
  } catch (error) {
    console.error('Error toggling tracking:', error);
  } finally {
    toggleButton.disabled = false;
  }
}

/**
 * Manually trigger sync
 */
async function syncNow() {
  syncButton.disabled = true;
  syncButton.textContent = 'Syncing...';

  try {
    await new Promise<{ success: boolean }>((resolve) => {
      chrome.runtime.sendMessage({ action: 'syncNow' }, resolve);
    });

    // Update state after sync
    const state = await getState();
    updateUI(state);

    // Show success feedback
    syncButton.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="20 6 9 17 4 12"></polyline>
      </svg>
      Synced!
    `;

    setTimeout(() => {
      syncButton.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="23 4 23 10 17 10"></polyline>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
        </svg>
        Sync Now
      `;
    }, 2000);
  } catch (error) {
    console.error('Error syncing:', error);
    syncButton.textContent = 'Sync Failed';
    setTimeout(() => {
      syncButton.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="23 4 23 10 17 10"></polyline>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
        </svg>
        Sync Now
      `;
    }, 2000);
  } finally {
    syncButton.disabled = false;
  }
}

/**
 * Open dashboard in new tab
 */
function openDashboard() {
  chrome.tabs.create({ url: 'http://localhost:3000' });
}

/**
 * Initialize popup
 */
async function initialize() {
  const state = await getState();
  updateUI(state);

  // Set up periodic UI updates
  setInterval(async () => {
    const currentState = await getState();
    updateUI(currentState);
  }, 5000); // Update every 5 seconds
}

// Event listeners
toggleButton.addEventListener('click', toggleTracking);
syncButton.addEventListener('click', syncNow);
dashboardButton.addEventListener('click', openDashboard);

// Initialize on load
initialize();
