# Production Deployment Guide

This guide explains how to deploy Digital Behavior Prediction to production for **free** or low cost.

## Table of Contents

1. [Free Deployment Options](#free-deployment-options)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Option 1: Render.com (Recommended)](#option-1-rendercom-recommended)
4. [Option 2: Railway.app](#option-2-railwayapp)
5. [Chrome Extension Setup](#chrome-extension-setup)
6. [Post-Deployment](#post-deployment)

---

## Free Deployment Options

| Platform | Database | Backend | Frontend | Cost |
|----------|----------|---------|----------|------|
| **Render** | PostgreSQL (Free) | Web Service (Free) | Web Service (Free) | $0 (with sleep) |
| **Railway** | PostgreSQL (Free) | Web Service | Web Service | $5/month credit |
| **Local** | Docker | Docker | Docker | $0 |

**Note**: Free tiers have limitations (sleep after inactivity, limited hours, etc.)

---

## Pre-Deployment Checklist

### 1. Update Environment Variables

Create `.env.production` in the root directory:

```bash
# Database (you'll get this from your hosting provider)
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=digital_behavior_prediction

# Backend API URL (replace with your actual domain)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_USER_ID=1
```

### 2. Update Extension Config

Edit `extension/src/config.ts`:

```typescript
export const config = {
  // Change this to your production API URL
  API_BASE_URL: 'https://api.yourdomain.com/api/v1',

  BATCH_SIZE: 10,
  SYNC_INTERVAL_MS: 30000,
  USER_ID: 1
};
```

Then rebuild:
```bash
cd extension
npm run build
```

---

## Option 1: Render.com (Recommended)

### Step 1: Create PostgreSQL Database

1. Go to https://render.com and sign up
2. Click "New +" → "PostgreSQL"
3. Configure:
   - **Name**: `digital-behavior-db`
   - **Database**: `digital_behavior_prediction`
   - **User**: (auto-generated)
   - **Region**: Choose closest to you
   - **Plan**: Free
4. Click "Create Database"
5. **Save the Internal Database URL** (starts with `postgres://`)

### Step 2: Deploy Backend

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `digital-behavior-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

4. Add Environment Variables:
   - `DATABASE_URL`: Paste the Internal Database URL from Step 1
   - `ALLOWED_ORIGINS`: `https://your-frontend-url.onrender.com`
   - `API_HOST`: `0.0.0.0`
   - `API_PORT`: `$PORT`

5. Click "Create Web Service"
6. **Save your backend URL** (e.g., `https://digital-behavior-backend.onrender.com`)

### Step 3: Deploy Frontend

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `digital-behavior-frontend`
   - **Region**: Same as backend
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Runtime**: Node
   - **Build Command**:
     ```bash
     npm install && npm run build
     ```
   - **Start Command**:
     ```bash
     npm start
     ```

4. Add Environment Variables:
   - `NEXT_PUBLIC_API_URL`: Your backend URL from Step 2
   - `NEXT_PUBLIC_USER_ID`: `1`

5. Click "Create Web Service"
6. **Save your frontend URL** (e.g., `https://digital-behavior-frontend.onrender.com`)

### Step 4: Update Backend CORS

Go back to your backend service and update the `ALLOWED_ORIGINS` environment variable with your actual frontend URL:

```
ALLOWED_ORIGINS=https://your-frontend-url.onrender.com
```

Then redeploy the backend.

---

## Option 2: Railway.app

### Step 1: Install Railway CLI (Optional)

```bash
npm install -g @railway/cli
railway login
```

Or use the web dashboard at https://railway.app

### Step 2: Create New Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your repository

### Step 3: Add PostgreSQL

1. Click "New" → "Database" → "Add PostgreSQL"
2. Copy the connection string

### Step 4: Deploy Services

Railway will auto-detect your Docker Compose file. Configure environment variables:

**Backend**:
- `DATABASE_URL`: Connection string from PostgreSQL
- `ALLOWED_ORIGINS`: Your frontend URL
- `PORT`: `8000`

**Frontend**:
- `NEXT_PUBLIC_API_URL`: Your backend URL
- `NEXT_PUBLIC_USER_ID`: `1`

### Step 5: Generate Domains

Click on each service → Settings → Generate Domain

---

## Chrome Extension Setup

### For Users (After Deployment)

1. **Update Extension Config**:
   - Edit `extension/src/config.ts`
   - Change `API_BASE_URL` to your production backend URL
   - Run `npm run build`

2. **Load in Chrome**:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `extension/dist` folder

3. **Test**:
   - Click the extension icon
   - Verify it's tracking (should show event count)
   - Open your frontend dashboard to see data

### For Distribution (Optional)

To distribute your extension:

1. Create a ZIP of the `extension/dist` folder
2. Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
3. Pay one-time $5 developer fee
4. Upload your extension
5. Wait for review (1-3 days)

---

## Post-Deployment

### 1. Test Everything

- [ ] Visit your frontend URL
- [ ] Check that the dashboard loads
- [ ] Visit backend URL + `/api/docs` for API docs
- [ ] Load the extension and browse the web
- [ ] Verify events appear in the dashboard

### 2. Monitor Services

**Render.com**:
- Free services sleep after 15min of inactivity
- First request after sleep takes ~30s to wake up
- Dashboard: https://dashboard.render.com

**Railway.app**:
- $5/month free credit
- Monitor usage at https://railway.app/account/usage

### 3. Security Checklist

- [ ] Change default database password
- [ ] Enable HTTPS (automatic on Render/Railway)
- [ ] Review CORS settings (only allow your domains)
- [ ] Set up database backups (paid feature)
- [ ] Monitor API rate limits

### 4. Seed Demo Data (Optional)

SSH into your backend container and run:

```bash
python scripts/seed_data.py --sessions 20
```

Or create an API endpoint to trigger seeding remotely.

---

## Troubleshooting

### Extension Can't Connect to Backend

**Check**:
1. Is `API_BASE_URL` in `extension/src/config.ts` correct?
2. Did you rebuild the extension after changing config?
3. Is CORS configured correctly in backend?
4. Open Chrome DevTools → Console → Check for errors

### Frontend Can't Fetch Data

**Check**:
1. Is `NEXT_PUBLIC_API_URL` environment variable set?
2. Can you access `<API_URL>/health` directly?
3. Check Network tab in DevTools for CORS errors

### Database Connection Failed

**Check**:
1. Is `DATABASE_URL` format correct?
2. Is the database running?
3. Check backend logs for connection errors

### Backend Returns 500 Errors

**Check**:
1. View backend logs in your hosting dashboard
2. Are all environment variables set?
3. Did migrations run (`alembic upgrade head`)?

---

## Cost Breakdown

### Free Option (Render.com)

- **Database**: Free (512MB RAM, 1GB storage)
- **Backend**: Free (sleeps after 15min inactivity)
- **Frontend**: Free (sleeps after 15min inactivity)
- **Total**: $0/month

**Limitations**:
- Services sleep when inactive
- 750 hours/month free compute
- Limited resources

### Paid Option (Render.com)

- **Database**: $7/month (1GB RAM, 10GB storage)
- **Backend**: $7/month (always on)
- **Frontend**: $7/month (always on)
- **Total**: $21/month

### DIY Option (VPS)

- **DigitalOcean Droplet**: $6/month (1GB RAM)
- **Linode**: $5/month (1GB RAM)
- **Total**: $5-6/month

---

## Need Help?

- Check the [README.md](README.md) for local development
- Open an issue on GitHub
- Review API docs at `<your-backend-url>/api/docs`

Happy deploying! 🚀
