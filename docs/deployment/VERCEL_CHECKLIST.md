# ✅ Vercel Deployment Checklist

## 🔧 Required Configuration

### 1. Set Environment Variables in Vercel

**Important**: Vercel will automatically generate `static/config.js` during build, no manual editing needed.

Add environment variables in your Vercel project settings:

1. Visit your Vercel project dashboard
2. Go to **Settings** > **Environment Variables**
3. Add the following variables:

| Variable Name | Value | Description |
|--------|-----|------|
| `API_BASE` | `https://travel-planning-agent.onrender.com` | Backend API address |
| `GOOGLE_MAPS_API_KEY` | `AIza...` | Your Google Maps API key |

**Get Google Maps API Key**:
1. Visit: https://console.cloud.google.com/google/maps-apis
2. Create/select project
3. Enable "Maps JavaScript API"
4. Go to Credentials > Create Credentials > API Key

### 2. Restrict API Key (Recommended)

In Google Cloud Console:
- Application restrictions > HTTP referrer
- Add website restrictions:
  - `https://your-project.vercel.app/*`
  - `https://*.vercel.app/*` (for preview deployments)
  - `http://localhost:*` (local testing)

### 3. Check Files

Confirm these files exist and are configured correctly:

- ✅ `static/index.html` - Includes Google Maps code
- ✅ `build-config.js` - Generates config.js during build
- ✅ `vercel.json` - Deployment configuration

## 🚀 Deployment Steps

```bash
# 1. Commit code to GitHub
git add .
git commit -m "Add Google Maps integration"
git push origin main

# 2. Set environment variables in Vercel project (see above)

# 3. Vercel will automatically redeploy
# Or manually trigger: Deployments > Redeploy
```

**No need** to manually create or edit `static/config.js`, the build script will generate it automatically!

## ⚠️ Important Notes

1. **Do not commit real API keys to GitHub**
   - `static/config.js` is already in `.gitignore`
   - Only commit `config.example.js` as a template

2. **Use Vercel Environment Variables**
   - Don't hardcode API keys in code
   - Use Vercel's environment variables feature
   - Build script will automatically read and generate configuration file

3. **Configure on Vercel**
   - Settings > Environment Variables
   - Add `GOOGLE_MAPS_API_KEY` and `API_BASE`
   - Save and redeploy

4. **Verify Deployment**
   - Check browser console for no errors
   - Verify markers and routes display correctly

## 📱 Troubleshooting

| Issue | Check |
|------|--------|
| Map not displaying | 1. Check browser console errors<br>2. Confirm API key is correct<br>3. Check if API is enabled |
| "InvalidKeyMapError" | API key is incorrect |
| "RefererNotAllowedMapError" | Need to add domain to API key restrictions list |
| "ApiNotActivatedMapError" | Need to enable Maps JavaScript API in Google Cloud |

## 📚 Reference Documentation

- [Complete Deployment Guide](DEPLOY_VERCEL.md)
- [Google Maps API Documentation](https://developers.google.com/maps/documentation/javascript)
- [Vercel Deployment Documentation](https://vercel.com/docs)
