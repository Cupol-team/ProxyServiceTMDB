from fastapi import FastAPI, Request, Response, HTTPException, Depends, APIRouter
from fastapi.responses import StreamingResponse
import httpx
import os
from dotenv import load_dotenv
import logging
from typing import Dict, Any, Optional
import hashlib
import json
from cache import cache

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="TMDB Proxy Service",
    description="Прокси-сервис для API TMDB",
    version="0.1.0",
)

router = APIRouter(prefix="/TMDBProxy")

TARGET_API_BASE_URL = os.getenv("TARGET_API_BASE_URL", "https://api.themoviedb.org/3")
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
CACHE_CLEANUP_INTERVAL = int(os.getenv("CACHE_CLEANUP_INTERVAL", "60"))

http_client = httpx.AsyncClient(timeout=30.0)

def generate_cache_key(request: Request, path: str) -> str:
    """
    генерирование ключа для кэша
    
    Args:
        request: Объект запроса
        path: Путь запроса
        
    Returns:
        Строка ключа кэша
    """
    key_data = {
        "method": request.method,
        "path": path,
        "params": dict(request.query_params),
    }
    
    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_str.encode()).hexdigest()

@router.get("/")
async def root():
    return {"status": "ok", "message": "TMDB Proxy Service works"}

@router.get("/cache/stats")
async def cache_stats():
    """
    получение статистики кэша
    """
    if not ENABLE_CACHE:
        return {"status": "disabled"}
    return cache.get_stats()

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_endpoint(request: Request, path: str):
    """
    Прокси-эндпоинт, который перенаправляет все запросы на API нашего любимого не русского TMDB
    """
    try:
        if ENABLE_CACHE and request.method == "GET":
            cache_key = generate_cache_key(request, path)
            cached_response = cache.get(cache_key)
            
            if cached_response:
                content, status_code, headers = cached_response
                return Response(
                    content=content,
                    status_code=status_code,
                    headers=headers,
                )
        
        target_url = f"{TARGET_API_BASE_URL}/{path}"
        
        params = dict(request.query_params)
        
        headers = dict(request.headers)
        headers.pop("host", None)
        
        headers["Accept-Encoding"] = "gzip, deflate"
        
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        
        response = await http_client.request(
            method=request.method,
            url=target_url,
            params=params,
            headers=headers,
            content=body,
        )
        
        response_headers = dict(response.headers)
        
        response_headers.pop("content-encoding", None)
        
        if ENABLE_CACHE and request.method == "GET" and response.status_code == 200:
            cache_key = generate_cache_key(request, path)
            cache.set(cache_key, (response.content, response.status_code, response_headers))
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers,
        )
        
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, 
            detail=f"error request: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"error: {str(e)}"
        )

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """
    при запуска запускаем мусорщика кэша
    """
    if ENABLE_CACHE:
        await cache.start_cleanup_task()

@app.on_event("shutdown")
async def shutdown_event():
    """
    закрываем http клиент и мусорщик кэша при завершении работы прокси
    """
    await http_client.aclose()
    if ENABLE_CACHE and cache.cleanup_task:
        cache.cleanup_task.cancel()