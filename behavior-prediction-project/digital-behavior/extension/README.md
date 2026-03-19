# Digital Behavior Twin - Chrome Extension

Browser extension that tracks user behavior patterns for task abandonment prediction.

## Features

- Tracks tab activations, creations, updates, and closures
- Monitors window focus changes
- Batches events and syncs to backend API
- Privacy-focused: only collects metadata (URLs, domains, timestamps)
- Toggle tracking on/off
- View daily event count and sync status

## Development

### Setup

```bash
npm install
```

### Build

```bash
# Development build with watch mode
npm run dev

# Production build
npm run build
```

### Load Extension in Chrome

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `dist` folder from this directory

## Configuration

The extension is configured to connect to:
- Backend API: `http://localhost:8000`
- Frontend Dashboard: `http://localhost:3000`

Update these URLs in `src/background.ts` if your setup differs.

## Privacy

This extension only collects:
- Event types (tab opened, closed, activated, etc.)
- Timestamps
- Domain names (no full URLs are stored)
- Tab/window IDs
- Page titles (metadata only)

No page content, form data, or sensitive information is captured.
