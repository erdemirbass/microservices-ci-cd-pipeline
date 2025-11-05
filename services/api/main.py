import hashlib
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_TTL = int(os.getenv("REDIS_TTL", "86400"))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


class ShortenRequest(BaseModel):
    url: str


@app.get("/healthz")
def healthz():
    try:
        redis_client.ping()
    except redis.RedisError as exc:
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc
    return {"ok": True}


@app.post("/shorten")
def shorten_link(payload: ShortenRequest):
    code = hashlib.sha1(payload.url.encode("utf-8")).hexdigest()[:7]
    key = f"url:{code}"
    redis_client.setex(key, REDIS_TTL, payload.url)
    return {"code": code}


@app.get("/r/{code}")
def retrieve_url(code: str):
    key = f"url:{code}"
    url = redis_client.get(key)
    if url is None:
        raise HTTPException(status_code=404, detail="Not found")
    return {"url": url}
