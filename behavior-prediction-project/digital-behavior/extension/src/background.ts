/**
 * Background Service Worker for Digital Behavior Prediction Extension
 *
 * Responsibilities:
 * - Track tab activations, creations, updates, and removals
 * - Monitor window focus changes
 * - Batch and send events to the backend API
 * - Manage tracking state (enabled/disabled)
 */

import { config } from './config';

interface BrowserEvent {
  event_type: string;
  url?: string;
  domain?: string;
  title?: string;
  tab_id?: number;
  window_id?: number;
  is_active?: boolean;
  timestamp?: string;
}

interface ExtensionState {
  isTracking: boolean;
  eventsToday: number;
  lastSyncTime: number;
}

// Configuration from config file
const { API_BASE_URL, BATCH_SIZE, SYNC_INTERVAL_MS, USER_ID } = config;

// State management
let eventQueue: BrowserEvent[] = [];
let state: ExtensionState = {
  isTracking: true,
  eventsToday: 0,
  lastSyncTime: Date.now()
};

/**
 * Initialize extension state from storage
 */
async function initializeState() {
  try {
    const stored = await chrome.storage.local.get(['isTracking', 'eventsToday', 'lastSyncTime']);
    if (stored.isTracking !== undefined) state.isTracking = stored.isTracking;
    if (stored.eventsToday !== undefined) state.eventsToday = stored.eventsToday;
    if (stored.lastSyncTime !== undefined) state.lastSyncTime = stored.lastSyncTime;

    // Reset daily counter if it's a new day
    const lastDate = new Date(state.lastSyncTime).toDateString();
    const today = new Date().toDateString();
    if (lastDate !== today) {
      state.eventsToday = 0;
      await saveState();
    }
  } catch (error) {
    console.error('Error initializing state:', error);
  }
}

/**
 * Save current state to storage
 */
async function saveState() {
  try {
    await chrome.storage.local.set({
      isTracking: state.isTracking,
      eventsToday: state.eventsToday,
      lastSyncTime: state.lastSyncTime
    });
  } catch (error) {
    console.error('Error saving state:', error);
  }
}

/**
 * Extract domain from URL
 */
function extractDomain(url: string): string {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname;
  } catch {
    return '';
  }
}

/**
 * Create a browser event object
 */
function createEvent(
  eventType: string,
  tabId?: number,
  url?: string,
  title?: string,
  windowId?: number,
  isActive: boolean = false
): BrowserEvent {
  const event: BrowserEvent = {
    event_type: eventType,
    timestamp: new Date().toISOString(),
    tab_id: tabId,
    window_id: windowId,
    is_active: isActive
  };

  if (url && !url.startsWith('chrome://') && !url.startsWith('chrome-extension://')) {
    event.url = url;
    event.domain = extractDomain(url);
  }

  if (title) {
    event.title = title;
  }

  return event;
}

/**
 * Add event to queue
 */
function queueEvent(event: BrowserEvent) {
  if (!state.isTracking) return;

  eventQueue.push(event);
  state.eventsToday++;

  console.log(`Event queued: ${event.event_type}`, event);

  // Auto-sync if queue is full
  if (eventQueue.length >= BATCH_SIZE) {
    syncEvents();
  }

  saveState();
}

/**
 * Send events to backend API
 */
async function syncEvents() {
  if (eventQueue.length === 0) return;

  const eventsToSend = [...eventQueue];
  eventQueue = [];

  try {
    const response = await fetch(`${API_BASE_URL}/events/batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': USER_ID.toString()
      },
      body: JSON.stringify(eventsToSend)
    });

    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }

    const result = await response.json();
    console.log(`Synced ${eventsToSend.length} events successfully`, result);

    state.lastSyncTime = Date.now();
    await saveState();
  } catch (error) {
    console.error('Error syncing events:', error);
    // Re-add events to queue on failure
    eventQueue = [...eventsToSend, ...eventQueue];
  }
}

/**
 * Event Listeners
 */

// Tab activated (user switches to a different tab)
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  try {
    const tab = await chrome.tabs.get(activeInfo.tabId);
    queueEvent(createEvent(
      'tab_activated',
      tab.id,
      tab.url,
      tab.title,
      activeInfo.windowId,
      true
    ));
  } catch (error) {
    console.error('Error handling tab activation:', error);
  }
});

// Tab created
chrome.tabs.onCreated.addListener((tab) => {
  queueEvent(createEvent(
    'tab_created',
    tab.id,
    tab.url,
    tab.title,
    tab.windowId,
    tab.active
  ));
});

// Tab updated (URL change, title change, etc.)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  // Only track when URL or title changes and page is loaded
  if (changeInfo.status === 'complete' && (changeInfo.url || changeInfo.title)) {
    queueEvent(createEvent(
      'tab_updated',
      tabId,
      tab.url,
      tab.title,
      tab.windowId,
      tab.active
    ));
  }
});

// Tab removed (closed)
chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
  queueEvent(createEvent(
    'tab_closed',
    tabId,
    undefined,
    undefined,
    removeInfo.windowId,
    false
  ));
});

// Window focus changed
chrome.windows.onFocusChanged.addListener(async (windowId) => {
  if (windowId === chrome.windows.WINDOW_ID_NONE) {
    // Browser lost focus
    queueEvent(createEvent('window_unfocused', undefined, undefined, undefined, undefined, false));
  } else {
    // Browser gained focus
    try {
      const [activeTab] = await chrome.tabs.query({ active: true, windowId });
      if (activeTab) {
        queueEvent(createEvent(
          'window_focused',
          activeTab.id,
          activeTab.url,
          activeTab.title,
          windowId,
          true
        ));
      }
    } catch (error) {
      console.error('Error handling window focus:', error);
    }
  }
});

/**
 * Periodic sync timer
 */
setInterval(() => {
  if (state.isTracking && eventQueue.length > 0) {
    syncEvents();
  }
}, SYNC_INTERVAL_MS);

/**
 * Message handler for popup communication
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'getState') {
    sendResponse(state);
  } else if (message.action === 'toggleTracking') {
    state.isTracking = !state.isTracking;
    saveState();
    sendResponse({ isTracking: state.isTracking });
  } else if (message.action === 'syncNow') {
    syncEvents().then(() => {
      sendResponse({ success: true });
    }).catch((error) => {
      sendResponse({ success: false, error: error.message });
    });
    return true; // Keep message channel open for async response
  }
});

/**
 * Initialize on installation/update
 */
chrome.runtime.onInstalled.addListener(async (details) => {
  if (details.reason === 'install') {
    console.log('Digital Behavior Prediction extension installed');
    await initializeState();
  } else if (details.reason === 'update') {
    console.log('Digital Behavior Prediction extension updated');
    await initializeState();
  }
});

// Initialize state on startup
initializeState();

console.log('Digital Behavior Prediction background service worker started');
