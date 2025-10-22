# apps/backend/src/core/rate_limit.py
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, list] = defaultdict(list)
        self.user_requests: Dict[str, list] = defaultdict(list)
    
    def _clean_old_requests(self, requests_list: list, window: timedelta):
        """Remove requests older than window"""
        cutoff = datetime.utcnow() - window
        return [req_time for req_time in requests_list if req_time > cutoff]
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health/metrics
        if request.url.path in ["/health", "/metrics", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # IP-based rate limiting
        client_ip = request.client.host
        now = datetime.utcnow()
        
        # Clean old requests
        self.requests[client_ip] = self._clean_old_requests(
            self.requests[client_ip], 
            timedelta(minutes=1)
        )
        
        # Check per-minute limit
        if len(self.requests[client_ip]) >= 60:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded: 60 requests per minute"
            )
        
        self.requests[client_ip].append(now)
        
        # User-based rate limiting (if authenticated)
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                # Extract user from token (simplified)
                user_key = f"user_{auth_header[:20]}"
                self.user_requests[user_key] = self._clean_old_requests(
                    self.user_requests[user_key],
                    timedelta(hours=1)
                )
                
                if len(self.user_requests[user_key]) >= 1000:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded: 1000 requests per hour"
                    )
                
                self.user_requests[user_key].append(now)
            except:
                pass
        
        response = await call_next(request)
        return response
