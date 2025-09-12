from fastapi import APIRouter, Request, Depends
from app.db.redis_client import RedisClient
from app.utils.cache import Cache

router = APIRouter()

@router.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "message": "Server is healthy"}

@router.get("/health/redis", tags=["health"])
async def redis_health_check(request: Request):
    redis_client = request.app.state.redis_client
    redis_status = "ok" if redis_client.check_health() else "error"
    return {"status": redis_status, "message": f"Redis is {redis_status}"}

@router.get("/health/cache/metrics", tags=["health"])
async def cache_metrics(request: Request):
    cache = request.app.state.cache
    total_requests = cache.hits + cache.misses
    hit_rate = (cache.hits / total_requests) * 100 if total_requests > 0 else 0
    
    return {
        "total_requests": total_requests,
        "hits": cache.hits,
        "misses": cache.misses,
        "hit_rate": f"{hit_rate:.2f}%",
        "cache_enabled": cache.is_connected
    }
