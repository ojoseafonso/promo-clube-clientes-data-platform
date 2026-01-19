import time
import uuid
import random
import hashlib
import psycopg2
from faker import Faker
from datetime import datetime, timedelta
import os
import unicodedata


fake = Faker("pt_BR")

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "source_db"),
    "user": os.getenv("POSTGRES_USER", "source_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "source_pass"),
}

INITIAL_LOAD_SIZE = int(os.getenv("INITIAL_LOAD_SIZE", 10000))
INSERT_BATCH_SIZE = int(os.getenv("INSERT_BATCH_SIZE", 100))
UPDATE_BATCH_SIZE = int(os.getenv("UPDATE_BATCH_SIZE", 50))
SLEEP_SECONDS = int(os.getenv("SLEEP_SECONDS", 30))


def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ASCII", "ignore").decode("ASCII")
    return text.lower().replace(" ", ".")

def hash_cpf(cpf: str) -> str:
    return hashlib.sha256(cpf.encode()).hexdigest()

def generate_person(sexo):
    if sexo == "M":
        nome = fake.first_name_male()
    else:
        nome = fake.first_name_female()

    sobrenome = fake.last_name()
    nome_completo = f"{nome} {sobrenome}"

    email = f"{nome}.{sobrenome}".lower().replace(" ", "") + f"{random.randint(1,999)}@email.com"

    return nome_completo, email

def create_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clientes_clube (
                    cliente_id UUID PRIMARY KEY,
                    cpf_hash TEXT UNIQUE,
                    nome_completo TEXT,
                    email TEXT UNIQUE,
                    telefone TEXT,
                    data_nascimento DATE,
                    sexo TEXT,
                    cidade TEXT,
                    estado TEXT,
                    cep TEXT,
                    canal_cadastro TEXT,
                    data_cadastro TIMESTAMP,
                    ultima_atualizacao TIMESTAMP,
                    status_clube TEXT,
                    opt_in_marketing BOOLEAN,
                    ticket_medio_estimado NUMERIC,
                    origem_campanha TEXT
                );
            """)
            conn.commit()


def generate_cliente():
    cpf = fake.cpf()
    now = datetime.utcnow()

    sexo = random.choice(["M", "F"])
    nome_completo, email = generate_person(sexo)

    return (
        str(uuid.uuid4()),
        hash_cpf(cpf),
        nome_completo,
        email,
        fake.phone_number(),
        fake.date_of_birth(minimum_age=18, maximum_age=80),
        sexo,
        fake.city(),
        fake.state_abbr(),
        fake.postcode(),
        random.choice(["loja", "app", "site"]),
        now,
        now,
        "ATIVO",
        random.choice([True, False]),
        round(random.uniform(20, 300), 2),
        random.choice(["verao", "inverno", "black_friday", "dia_das_maes"])
    )


def initial_load():
    print(f"🔄 Iniciando carga inicial: {INITIAL_LOAD_SIZE} registros")
    with get_connection() as conn:
        with conn.cursor() as cur:
            for _ in range(INITIAL_LOAD_SIZE):
                cur.execute("""
                    INSERT INTO clientes_clube (
                        cliente_id,
                        cpf_hash,
                        nome_completo,
                        email,
                        telefone,
                        data_nascimento,
                        sexo,
                        cidade,
                        estado,
                        cep,
                        canal_cadastro,
                        data_cadastro,
                        ultima_atualizacao,
                        status_clube,
                        opt_in_marketing,
                        ticket_medio_estimado,
                        origem_campanha
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """, 
                    generate_cliente()
                )
            conn.commit()
    print("✅ Carga inicial concluída")


def insert_new_clients():
    with get_connection() as conn:
        with conn.cursor() as cur:
            for _ in range(INSERT_BATCH_SIZE):
                cur.execute("""
                    INSERT INTO clientes_clube (
                        cliente_id,
                        cpf_hash,
                        nome_completo,
                        email,
                        telefone,
                        data_nascimento,
                        sexo,
                        cidade,
                        estado,
                        cep,
                        canal_cadastro,
                        data_cadastro,
                        ultima_atualizacao,
                        status_clube,
                        opt_in_marketing,
                        ticket_medio_estimado,
                        origem_campanha
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT DO NOTHING
                """, generate_cliente())
            conn.commit()
    print("➕ Novos clientes inseridos")


def update_existing_clients():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT cliente_id FROM clientes_clube
                ORDER BY random()
                LIMIT %s
            """, (UPDATE_BATCH_SIZE,))
            ids = [row[0] for row in cur.fetchall()]

            for cid in ids:
                cur.execute("""
                    UPDATE clientes_clube
                    SET
                        status_clube = %s,
                        ultima_atualizacao = %s
                    WHERE cliente_id = %s
                """, (
                    random.choice(["ATIVO", "INATIVO"]),
                    datetime.utcnow(),
                    cid
                ))
            conn.commit()
    print("🔁 Clientes atualizados")


def main():
    print("🚀 Iniciando Faker Service")
    create_table()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM clientes_clube")
            count = cur.fetchone()[0]

    if count == 0:
        initial_load()

    while True:
        insert_new_clients()
        update_existing_clients()
        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
