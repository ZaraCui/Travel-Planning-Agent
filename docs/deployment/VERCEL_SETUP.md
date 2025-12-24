# 🚀 Vercel Quick Setup Guide

## Fix Map Not Displaying Issue Now

### Step 1: Set Environment Variables in Vercel

1. Visit your Vercel project: https://vercel.com/dashboard
2. Select your project
3. Click **Settings** → **Environment Variables**
4. Add the following two variables:

```
Name: GOOGLE_MAPS_API_KEY
Value: [your Google Maps API key]
Environment: ✅ Production ✅ Preview ✅ Development
```

```
Name: API_BASE
Value: https://travel-planning-agent.onrender.com
Environment: ✅ Production ✅ Preview ✅ Development
```

### Step 2: Get Google Maps API Key (if you don't have one)

1. Visit: https://console.cloud.google.com/google/maps-apis
2. Create or select a project
3. Enable **Maps JavaScript API**
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. Copy the generated key

### Step 3: Restrict API Key (Recommended)

1. Click on your API key in Google Cloud Console
2. Select **Application restrictions** → **HTTP referrer**
3. Add website restrictions:
   ```
   https://*.vercel.app/*
   http://localhost:*
   ```
4. Click **Save**

### Step 4: Trigger Redeployment

In your Vercel project:
1. Go to **Deployments** tab
2. Click the **⋯** menu on the latest deployment
3. Select **Redeploy**
4. Wait for deployment to complete

## ✅ Verification

After deployment, visit your website:
1. Fill out the form and submit
2. You should see:
   - ✅ Itinerary planning results
   - ✅ Map display (with markers and routes)
   - ✅ No console errors

## 🐛 Troubleshooting

### Issue: Map still not displaying

Open browser developer tools (F12) and check console:

**Error**: `Google Maps API error: InvalidKeyMapError`
- Cause: API key is incorrect
- Solution: Check if `GOOGLE_MAPS_API_KEY` in Vercel environment variables is correct

**Error**: `Google Maps JavaScript API has not been authorized`
- Cause: API not enabled
- Solution: Enable Maps JavaScript API in Google Cloud Console

**Error**: `RefererNotAllowedMapError`
- Cause: Domain restrictions don't match
- Solution: Add your Vercel domain to API key's allowed list in Google Cloud

**Error**: `GOOGLE_MAPS_API_KEY is undefined`
- Cause: Environment variable not set or not applied
- Solution: Confirm environment variable is set in Vercel and redeploy

### Issue: Button click has no response

Open browser developer tools and check network requests:

**Error**: `Failed to fetch` or CORS error
- Cause: Backend API unreachable or CORS configuration issue
- Solution: Confirm `API_BASE` environment variable is correct and backend service is running normally

## 📝 Technical Details

What happens during the build process:

1. Vercel runs `npm run build`
2. Executes `node build-config.js`
3. Reads environment variables `API_BASE` and `GOOGLE_MAPS_API_KEY`
4. Generates `static/config.js`:
   ```javascript
   const API_BASE = 'https://...';
   window.GOOGLE_MAPS_API_KEY = 'AIza...';
   ```
5. Deploys static files to Vercel

## 📚 More Information

- [Complete Deployment Guide](DEPLOY_VERCEL.md)
- [Deployment Checklist](VERCEL_CHECKLIST.md)
