import redis
import snowflake.connector
import os
import time

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")

WAREHOUSE = "COMPUTE_WH"
DATABASE = "TRANSFORMING"
SCHEMA = "TRANSFORMING_CLIENTES"

QUERY = """
SELECT
  CLIENTE_ID,
  CLIENTE_ELEGIVEL_PROMOCAO
FROM DIM_CLIENTES_CLUBE
"""

def get_redis():
    while True:
        try:
            r = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True
            )
            r.ping()
            print("✅ Conectado ao Redis")
            return r
        except Exception as e:
            print("⏳ Redis indisponível, tentando novamente...", e)
            time.sleep(5)

def get_snowflake():
    while True:
        try:
            conn = snowflake.connector.connect(
                user=SNOWFLAKE_USER,
                password=SNOWFLAKE_PASSWORD,
                account=SNOWFLAKE_ACCOUNT,
                warehouse=WAREHOUSE,
                database=DATABASE,
                schema=SCHEMA
            )
            print("✅ Conectado ao Snowflake")
            return conn
        except Exception as e:
            print("⏳ Snowflake indisponível, tentando novamente...", e)
            time.sleep(10)

def load_cache(r, conn):
    cur = conn.cursor()
    cur.execute(QUERY)

    rows = cur.fetchall()
    print(f"🔄 Carregando {len(rows)} clientes no cache")

    for CLIENTE_ID, CLIENTE_ELEGIVEL_PROMOCAO in rows:
        status_str = str(CLIENTE_ELEGIVEL_PROMOCAO)

        r.hset(
            f"cliente:{CLIENTE_ID}",
            mapping={
                "status": status_str
            }
        )

    cur.close()
    print("✅ Cache atualizado com sucesso")

def main():
    r = get_redis()
    conn = get_snowflake()

    while True:
        try:
            load_cache(r, conn)
            time.sleep(300)  # 5 minutos
        except Exception as e:
            print("⚠️ Erro ao atualizar cache:", e)
            time.sleep(30)

if __name__ == "__main__":
    main()
