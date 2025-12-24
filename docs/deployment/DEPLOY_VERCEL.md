# Vercel Deployment Configuration Guide

## Problem Description

Local development uses `templates/index.html` (includes Google Maps), while Vercel deployment uses `static/index.html`. Google Maps integration code has been added to the static version.

## Configuration Steps

### 1. Obtain Google Maps API Key

1. 访问 [Google Cloud Console](https://console.cloud.google.com/google/maps-apis)
2. 创建新项目或选择现有项目
3. 启用 **Maps JavaScript API**
4. 创建 API 密钥（建议：限制密钥使用范围到你的域名）

### 2. Configure Environment Variables in Vercel

⚠️ **Important**: Do not hardcode API keys in your code, use Vercel's environment variables feature.

1. Log in to Vercel and navigate to your project
2. Go to **Settings** > **Environment Variables**
3. Add the following environment variables:

```
Variable Name: API_BASE
Value: https://travel-planning-agent.onrender.com
Environment: Production, Preview, Development

Variable Name: GOOGLE_MAPS_API_KEY  
Value: AIza...your-actual-key
Environment: Production, Preview, Development
```

### 3. Deploy to Vercel

```bash
# Commit code
git add .
git commit -m "Add Google Maps integration"
git push origin main

# Vercel will automatically deploy (if connected to GitHub)
# Build process will read environment variables and generate static/config.js
```

The build script (`build-config.js`) will automatically:
- Read environment variables `API_BASE` and `GOOGLE_MAPS_API_KEY`
- Generate `static/config.js` file
- Inject into the static website

### 4. Verify Deployment

Visit your Vercel website and check:
- Form can be submitted
- Itinerary planning results are displayed
- **Google Maps displays correctly** (below the itinerary)

## Common Issues

### Q: Map not displaying?

Check browser console for errors:

1. **API Key Error**
   - Error: "Google Maps API error: InvalidKeyMapError"
   - Solution: Check if API key in `static/config.js` is correct

2. **API Not Enabled**
   - Error: "Google Maps JavaScript API has not been authorized"
   - Solution: Enable Maps JavaScript API in Google Cloud Console

3. **Domain Restrictions**
   - Error: "RefererNotAllowedMapError"
   - Solution: Add your Vercel domain to API key's allowed list in Google Cloud Console

### Q: Why does it work locally but not on Vercel?

- **Local**: Flask uses `templates/index.html`
- **Vercel**: Uses `static/index.html` (now includes map code)
- **Solution**: Configure `GOOGLE_MAPS_API_KEY` environment variable in Vercel project settings

### Q: How does the build script work?

`build-config.js` during build:
1. Reads environment variables `API_BASE` and `GOOGLE_MAPS_API_KEY`
2. Generates `static/config.js`:
   ```javascript
   const API_BASE = 'https://...';
   window.GOOGLE_MAPS_API_KEY = 'AIza...';
   ```
3. Static website loads this configuration file

### Q: How to protect my API Key?

Google Maps API key cannot be completely hidden when used on the frontend, recommendations:

1. **Use Vercel Environment Variables**
   - Don't hardcode API key in code
   - Use Vercel's environment variables feature
   - Won't be exposed in GitHub repository

2. **限制密钥使用**
   - 在 Google Cloud Console 中限制密钥只能从你的域名使用
   - 添加 HTTP referrer 限制（例如：`*.vercel.app/*`）

3. **设置使用配额**
   - 设置每日使用配额防止滥用
   - 启用计费提醒

4. **监控使用情况**
   - 定期检查 API 使用情况
   - 如发现异常立即重新生成密钥

## 文件说明

- `static/index.html` - 静态前端页面（Vercel 部署）
- `build-config.js` - 构建脚本，生成 config.js
- `static/config.example.js` - 配置模板（仅供参考）
- `templates/index.html` - Flask 模板（本地开发）
- `vercel.json` - Vercel 部署配置
- `package.json` - 定义构建命令

## 安全建议

⚠️ **使用 Vercel 环境变量，不要在代码中硬编码 API key！**

`static/config.js` 会在构建时自动生成，不需要提交到仓库。`.gitignore` 已配置忽略此文件。
