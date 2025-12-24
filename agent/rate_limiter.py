"""
Rate Limiting Middleware for Flask
Protects API endpoints from abuse
"""
from functools import wraps
from flask import request, jsonify
import time
from collections import defaultdict
import threading

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = threading.Lock()
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """
        Check if request is allowed
        
        Args:
            key: Unique identifier (IP, user_id, etc.)
            limit: Max requests allowed
            window: Time window in seconds
        
        Returns:
            True if allowed, False if rate limit exceeded
        """
        now = time.time()
        
        with self.lock:
            # Clean old requests
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < window
            ]
            
            # Check if limit exceeded
            if len(self.requests[key]) >= limit:
                return False
            
            # Add current request
            self.requests[key].append(now)
            return True
    
    def get_reset_time(self, key: str, window: int) -> int:
        """Get seconds until rate limit resets"""
        if not self.requests[key]:
            return 0
        
        oldest = min(self.requests[key])
        reset_time = oldest + window - time.time()
        return max(0, int(reset_time))


# Global rate limiter instance
limiter = RateLimiter()


def rate_limit(limit: int = 60, window: int = 60, key_func=None):
    """
    Rate limiting decorator
    
    Args:
        limit: Max requests allowed
        window: Time window in seconds
        key_func: Function to generate rate limit key (default: IP address)
    
    Usage:
        @rate_limit(limit=10, window=60)  # 10 requests per minute
        def my_endpoint():
            return jsonify({"data": "..."})
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate key
            if key_func:
                key = key_func()
            else:
                # Use IP address as default key
                key = request.remote_addr or 'unknown'
            
            # Check rate limit
            if not limiter.is_allowed(key, limit, window):
                reset_time = limiter.get_reset_time(key, window)
                return jsonify({
                    "status": "error",
                    "code": 429,
                    "message": "Rate limit exceeded",
                    "reason": f"Too many requests. Try again in {reset_time} seconds.",
                    "retry_after": reset_time
                }), 429
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Redis-based rate limiter (for production)
class RedisRateLimiter:
    """Redis-based rate limiter for distributed systems"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed using Redis"""
        if not self.redis:
            return True  # Fallback if Redis unavailable
        
        try:
            # Use Redis sorted set for sliding window
            now = time.time()
            key_name = f"rate_limit:{key}"
            
            # Remove old entries
            self.redis.zremrangebyscore(key_name, 0, now - window)
            
            # Count requests in window
            count = self.redis.zcard(key_name)
            
            if count >= limit:
                return False
            
            # Add current request
            self.redis.zadd(key_name, {str(now): now})
            self.redis.expire(key_name, window)
            
            return True
        
        except Exception as e:
            # Log error and allow request (fail open)
            print(f"Rate limiter error: {e}")
            return True


def rate_limit_redis(redis_client, limit: int = 60, window: int = 60, key_func=None):
    """
    Redis-based rate limiting decorator
    
    Usage:
        from agent.cache import cache
        
        @rate_limit_redis(cache.redis_client, limit=100, window=60)
        def my_endpoint():
            return jsonify({"data": "..."})
    """
    redis_limiter = RedisRateLimiter(redis_client)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if key_func:
                key = key_func()
            else:
                key = request.remote_addr or 'unknown'
            
            if not redis_limiter.is_allowed(key, limit, window):
                return jsonify({
                    "status": "error",
                    "code": 429,
                    "message": "Rate limit exceeded",
                    "reason": "Too many requests. Please try again later."
                }), 429
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
