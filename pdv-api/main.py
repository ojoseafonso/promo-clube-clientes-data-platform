from fastapi import FastAPI, HTTPException
import redis
import time
import os

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/cliente/{cliente_id}/status")
def get_cliente_status(cliente_id: str):
    start = time.time()

    key = f"cliente:{cliente_id}"
    data = redis_client.hgetall(key)

    if not data:
        return {
            "cliente_id": cliente_id,
            "status": "CADASTRO INEXISTENTE",
            "fonte": "REDIS",
            "latencia_ms": int((time.time() - start) * 1000)
        }

    return {
        "cliente_id": cliente_id,
        "status_clube": data.get("status"),
        "origem_campanha": data.get("origem_campanha"),
        "fonte": "REDIS",
        "latencia_ms": int((time.time() - start) * 1000)
    }
