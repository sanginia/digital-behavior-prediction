# Testing Before Deployment

This guide helps you test your production configuration locally before deploying.

## Quick Test

Run the basic deployment test:

```bash
# From the project root
bash test-deployment.sh
```

This tests:
- ✅ All services running
- ✅ Backend health check
- ✅ Environment variables loaded
- ✅ API endpoints responding
- ✅ Database connection
- ✅ Frontend accessible
- ✅ Extension built
- ✅ CORS configuration

---

## Manual Testing Steps

### 1. Test Environment Variables

**Check loaded environment variables:**

```bash
# Backend env vars
docker exec digital-behavior-backend printenv | grep -E "DATABASE_URL|ALLOWED_ORIGINS"

# Frontend env vars
docker exec digital-behavior-frontend printenv | grep NEXT_PUBLIC
```

**Expected output:**
```
DATABASE_URL=postgresql://dbuser:dbpassword@postgres:5432/digital_behavior_prediction
ALLOWED_ORIGINS=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_USER_ID=1
```

---

### 2. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# API docs (should be accessible)
open http://localhost:8000/api/docs

# Sessions endpoint
curl -H "X-User-ID: 1" http://localhost:8000/api/v1/sessions
```

---

### 3. Test Frontend

```bash
# Check frontend status
curl -I http://localhost:3000

# Open in browser
open http://localhost:3000
```

**Verify:**
- Dashboard loads without errors
- Can see sessions (if you have demo data)
- No console errors in browser DevTools

---

### 4. Test Chrome Extension

**Update config for local testing:**

Edit `extension/src/config.ts`:
```typescript
export const config = {
  API_BASE_URL: 'http://localhost:8000/api/v1',  // Should match backend
  BATCH_SIZE: 10,
  SYNC_INTERVAL_MS: 30000,
  USER_ID: 1
};
```

**Rebuild and test:**
```bash
cd extension
npm run build

# Load in Chrome:
# 1. Go to chrome://extensions/
# 2. Enable Developer mode
# 3. Click "Load unpacked"
# 4. Select extension/dist folder
```

**Test extension:**
1. Click extension icon - should show tracking status
2. Browse some websites
3. Check dashboard - events should appear
4. Check Chrome DevTools console for errors

---

### 5. Simulate Production Environment

**Test with production-like configuration:**

```bash
# Copy test production config
cp .env.test-production .env

# Restart services with new config
docker-compose down
docker-compose up -d

# Verify new ALLOWED_ORIGINS loaded
docker exec digital-behavior-backend printenv ALLOWED_ORIGINS
```

**Expected:** Shows production domains instead of localhost

**Important:** Reset to local config after testing:
```bash
# Restore local development config
git checkout .env
# OR manually edit .env back to localhost settings

docker-compose down && docker-compose up -d
```

---

### 6. Test Database Migrations

**Verify migrations ran:**

```bash
# Check database tables exist
docker exec digital-behavior-db psql -U dbuser -d digital_behavior_prediction -c "\dt"
```

**Expected tables:**
- users
- sessions
- browser_events
- feature_snapshots
- predictions
- interventions
- alembic_version (migration tracker)

**Test migration on fresh database:**

```bash
# Remove volume (WARNING: deletes all data)
docker-compose down -v

# Restart (migrations run automatically)
docker-compose up -d

# Watch backend logs
docker logs -f digital-behavior-backend
```

Look for: `INFO  [alembic.runtime.migration] Running upgrade -> xxxxxx`

---

### 7. Test CORS with Different Origins

**Test allowed origin:**
```bash
curl -v http://localhost:8000/health \
  -H "Origin: http://localhost:3000" \
  2>&1 | grep -i access-control
```

**Test blocked origin:**
```bash
curl -v http://localhost:8000/health \
  -H "Origin: https://malicious-site.com" \
  2>&1 | grep -i access-control
```

---

## Production Build Test

Test production builds (optimized, minified):

### Frontend Production Build

```bash
cd frontend

# Build for production
npm run build

# Test production server
npm start

# Visit http://localhost:3000
```

### Extension Production Build

```bash
cd extension

# Build for production (default)
npm run build

# Check build output
ls -lh dist/
```

---

## Load Testing (Optional)

Test with realistic load:

```bash
# Install Apache Bench
brew install ab  # macOS
# sudo apt-get install apache2-utils  # Linux

# Test backend (100 requests, 10 concurrent)
ab -n 100 -c 10 http://localhost:8000/health

# Test with authentication
ab -n 100 -c 10 -H "X-User-ID: 1" http://localhost:8000/api/v1/sessions
```

---

## Troubleshooting

### Environment Variables Not Loading

**Problem:** Changed .env but variables haven't updated

**Solution:**
```bash
# Containers must be recreated, not just restarted
docker-compose down
docker-compose up -d
```

### Database Connection Failed

**Problem:** `password authentication failed`

**Solution:**
```bash
# Check .env password matches database
docker exec digital-behavior-db psql -U dbuser -d digital_behavior_prediction -c "SELECT 1"

# If needed, recreate database with new password
docker-compose down -v
docker-compose up -d
```

### Frontend Can't Connect to Backend

**Problem:** API requests fail with CORS or network errors

**Check:**
1. Is `NEXT_PUBLIC_API_URL` correct in frontend?
2. Is backend running? `curl http://localhost:8000/health`
3. Check browser DevTools Network tab for errors

**Solution:**
```bash
# Verify frontend env
docker exec digital-behavior-frontend printenv | grep NEXT_PUBLIC

# Should match backend URL (http://localhost:8000 for local)
```

### Extension Not Sending Events

**Problem:** Extension icon shows 0 events

**Check:**
1. DevTools console for errors (right-click extension → Inspect popup)
2. Is API_BASE_URL correct in `extension/src/config.ts`?
3. Did you rebuild after changing config?

**Solution:**
```bash
cd extension
npm run build

# Reload extension in Chrome:
# chrome://extensions/ → Click reload icon
```

---

## Pre-Deployment Checklist

Before deploying to production, ensure:

- [ ] All tests pass (`bash test-deployment.sh`)
- [ ] Environment variables configured for production
- [ ] Database migrations tested
- [ ] Frontend builds successfully (`npm run build`)
- [ ] Extension built with production API URL
- [ ] CORS configured with production domains
- [ ] No hardcoded secrets in code
- [ ] `.env` files not committed to git (in `.gitignore`)
- [ ] Production database password changed from default
- [ ] Extension tested in Chrome with production backend
- [ ] API docs accessible (for testing after deployment)

---

## Next Steps

Once all tests pass:

1. **Read deployment guide**: See `DEPLOYMENT.md`
2. **Choose hosting**: Render.com (free) or Railway.app
3. **Update production config**:
   - Backend `ALLOWED_ORIGINS`
   - Frontend `NEXT_PUBLIC_API_URL`
   - Extension `API_BASE_URL`
4. **Deploy services**: Follow platform-specific steps
5. **Test production**: Run same tests against production URLs
6. **Load extension**: Rebuild with production URL and test

Good luck with your deployment! 🚀
