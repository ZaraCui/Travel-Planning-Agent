# Vercel + Redis Deployment Guide

## Overview

This guide explains how to deploy Travel Planning Agent on Vercel and enable Redis caching functionality.

## Why Does Vercel Need External Redis?

Vercel is a serverless platform with these characteristics:
- ❌ Cannot run Docker containers
- ❌ No persistent local storage
- ✅ Requires cloud Redis service
- ✅ Supports environment variable configuration

## Option 1: Using Upstash (Recommended)

### Why Choose Upstash?
- ✅ **Designed for serverless**: No connection limit
- ✅ **Pay per request**: Only pay for actual usage
- ✅ **Generous free tier**: 10,000 requests/day
- ✅ **Global CDN**: Low latency
- ✅ **Perfect Vercel integration**

### Step 1: Create Upstash Account and Database

1. Visit [Upstash](https://upstash.com/) and register
2. Create new Redis database:
   - Click "Create Database"
   - Select region (recommended: closest to your users)
   - Select "Global" type (free)
   - Click create

3. Get connection info:
   ```
   Endpoint: us1-merry-fox-12345.upstash.io
   Port: 6379
   Password: AaBbCcDdEeFfGgHhIiJj
   ```

### Step 2: Configure Environment Variables in Vercel

Add the following environment variables in your Vercel project settings:

```env
# Enable Redis cache
REDIS_ENABLED=True

# Upstash connection info
REDIS_HOST=us1-merry-fox-12345.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=your-upstash-password
REDIS_DB=0
REDIS_SOCKET_TIMEOUT=5
```

### Step 3: Deploy

```bash
git add .
git commit -m "Enable Redis cache with Upstash"
git push origin main
```

Vercel will automatically redeploy and apply the new environment variables.

### Step 4: Verify

After deployment, visit:
```
https://your-app.vercel.app/api/cache/stats
```

You should see:
```json
{
  "status": "success",
  "data": {
    "enabled": true,
    "connected": true,
    "keys_count": 0,
    ...
  }
}
```

## Option 2: Using Redis Cloud

### Step 1: Create Redis Cloud Account

1. Visit [Redis Cloud](https://redis.com/try-free/)
2. Register and create free database (30MB)
3. Get connection info:
   ```
   Host: redis-12345.c123.us-east-1-1.ec2.cloud.redislabs.com
   Port: 12345
   Password: your-password
   ```

### Step 2: Configure in Vercel

```env
REDIS_ENABLED=True
REDIS_HOST=redis-12345.c123.us-east-1-1.ec2.cloud.redislabs.com
REDIS_PORT=12345
REDIS_PASSWORD=your-password
REDIS_DB=0
```

## Option 3: Using Railway Redis

If your backend is deployed on Railway:

1. Add Redis service in Railway project
2. Railway will automatically provide environment variables
3. Configure Vercel frontend to point to Railway Redis

## Vercel-Specific Optimizations

### 1. Adjust Cache TTL

Due to serverless nature, recommend longer TTLs:

In `agent/cache.py`:
```python
# City list - 48 hours (rarely changes)
cache.set(cache_key, cities, ttl=172800)

# Spot data - 24 hours
cache.set(cache_key, result, ttl=86400)
```

### 2. Use Redis Connection Pool

Already implemented in `agent/cache.py`:
```python
self.redis_client = redis.Redis(
    ...
    health_check_interval=30,  # Keep connection healthy
    retry_on_timeout=True      # Automatic retry
)
```

### 3. Monitor Cache Performance

Use Vercel Analytics and Upstash Dashboard:
- Vercel: View function execution time
- Upstash: View request count and latency

## Cost Estimation

### Upstash Free Plan
- 10,000 requests/day
- Sufficient for small to medium applications
- Example: 1000 users/day, 10 requests each = sufficient

### Redis Cloud Free Plan
- 30MB storage
- 30 concurrent connections
- Suitable for small applications

### Expected Usage
For 1000 API calls per day:
- City list: ~10 times (cached 48 hours)
- Spot data: ~100 times (cached 24 hours)
- Redis operations: ~110 times/day
- **Well below free tier**

## Deployment Checklist

### Before Deployment
- [ ] Create Upstash/Redis Cloud account
- [ ] Get Redis connection info
- [ ] Set environment variables in Vercel
- [ ] Test local connection (optional)

### After Deployment
- [ ] Visit `/api/cache/stats` to confirm connection
- [ ] Test API response speed
- [ ] Check Upstash Dashboard for requests
- [ ] Monitor Vercel function execution time

## Common Questions

### Q: Will Vercel deployment fail without Redis configured?

A: **No!** Redis is an optional feature. If `REDIS_ENABLED=False` or not set, the application will run normally but without caching.

### Q: How to clear cache on Vercel?

A: Visit API endpoint:
```bash
curl -X POST https://your-app.vercel.app/api/cache/invalidate/all
```

Or operate directly in Upstash Dashboard.

### Q: Will Redis connection failure affect the application?

A: **No!** The code has proper error handling, and will automatically fallback when Redis fails:
```python
except redis.ConnectionError as e:
    logger.warning("Redis cache disabled due to connection failure")
    self.enabled = False
```

### Q: How to switch Redis providers?

A: Just update Vercel environment variables, no code changes needed:
```env
# Switch from Redis Cloud to Upstash
REDIS_HOST=new-host.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=new-password
```

### Q: Can local development and Vercel deployment use different Redis?

A: **Yes!** Use different `.env` files:
- Local: `.env` (use localhost or Docker)
- Vercel: Environment variables (use Upstash)

## Performance Comparison

### Without Cache (Vercel Serverless)
```
/api/cities: ~150-300ms (cold start)
/api/spots: ~200-500ms (file read)
```

### With Cache (Upstash Redis)
```
/api/cities: ~50-100ms (cache hit)
/api/spots: ~80-150ms (cache hit)
Performance improvement: 60-70%
```

## Monitoring and Maintenance

### 1. Upstash Dashboard
- View request count
- Monitor latency
- Check storage usage

### 2. Vercel Analytics
- Function execution time
- Cold start frequency
- Error rate

### 3. Custom Monitoring
Add logs in code:
```python
import logging
logger.info(f"Cache hit rate: {hits}/{total}")
```

## Advanced Configuration

### Using Redis TLS (Recommended for Production)

Upstash supports TLS by default, no additional configuration needed.

For Redis Cloud, if TLS is required:
```python
# Add in agent/cache.py
self.redis_client = redis.Redis(
    ...
    ssl=True,
    ssl_cert_reqs=None  # or use certificate verification
)
```

### Multi-Region Deployment

If using Vercel Edge Functions:
1. Select "Global" database in Upstash
2. Automatically routes to nearest node
3. Lower latency

## Troubleshooting

### Redis Connection Timeout

Check:
1. Are Vercel environment variables correct?
2. Is Redis service online?
3. Firewall settings (usually auto-configured for cloud services)

View Vercel logs:
```bash
vercel logs
```

### Cache Not Working

1. Confirm `REDIS_ENABLED=True`
2. Check `/api/cache/stats`
3. View Upstash Dashboard

## Cost Optimization Tips

### 1. Set Reasonable TTL
```python
# Static data uses longer TTL
cities_ttl = 172800  # 48 hours

# User-specific data uses short TTL
plan_ttl = 3600  # 1 hour
```

### 2. Use Cache Key Namespaces
```python
# Easy batch cleanup
cache_key = f"v1:spots:{city}"  # Version control
```

### 3. Monitor Free Tier
- Set Upstash alerts
- Check usage weekly
- Optimize cache strategy

## Summary

✅ **Recommended Setup**: Vercel + Upstash
- Zero configuration complexity
- Best performance
- Generous free tier

🚀 **Quick Start**:
1. Register Upstash (5 minutes)
2. Add environment variables in Vercel (2 minutes)
3. Redeploy (1 minute)
4. Verify `/api/cache/stats` (1 minute)

**Total: Enable Redis cache in production in 10 minutes!**

## Related Resources

- 📖 [Upstash Documentation](https://docs.upstash.com/)
- 🚀 [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- 🔧 [Local Redis Configuration](REDIS_CACHE_GUIDE.md)
