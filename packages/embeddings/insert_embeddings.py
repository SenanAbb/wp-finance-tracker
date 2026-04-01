#!/usr/bin/env python3
"""
Inserta embeddings pre-generados en Supabase vía REST API (PostgREST).

Uso:
  1. python generate_embeddings.py   (genera output/embeddings_seed.json)
  2. python insert_embeddings.py     (inserta vía Supabase REST API)

Requiere SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY en apps/api/.env.
"""

import json
import os
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

# ── Config ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_ENV = SCRIPT_DIR / ".env"
JSON_FILE = SCRIPT_DIR / "output" / "embeddings_seed.json"
BATCH_SIZE = 50  # rows per HTTP request


def load_env() -> tuple[str, str]:
    if LOCAL_ENV.exists():
        load_dotenv(LOCAL_ENV)
        print(f"✓ Loaded env from {LOCAL_ENV}")

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print("✗ SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY no encontrados.")
        print(f"  Asegúrate de que existen en {LOCAL_ENV}")
        sys.exit(1)

    return url, key


def load_data() -> list[dict]:
    print(f"\n📂 Leyendo datos desde {JSON_FILE}...")
    if not JSON_FILE.exists():
        print(f"✗ No se encontró {JSON_FILE}")
        print("  Ejecuta primero: python generate_embeddings.py")
        sys.exit(1)

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        rows = json.load(f)

    print(f"   Total: {len(rows)} registros")
    return rows


def format_row(row: dict) -> dict:
    """Formatea una fila para la REST API de Supabase/PostgREST."""
    embedding = row["embedding"]
    # pgvector espera string formato '[0.1,0.2,...]'
    if isinstance(embedding, list):
        embedding = "[" + ",".join(str(v) for v in embedding) + "]"
    return {
        "type": row["type"],
        "content": row["content"],
        "metadata": row["metadata"],
        "embedding": embedding,
    }


def insert(supabase_url: str, service_key: str, rows: list[dict]):
    """Inserta los registros vía Supabase REST API en batches."""
    endpoint = f"{supabase_url}/rest/v1/knowledge_embeddings"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }

    total = len(rows)
    inserted = 0
    errors = 0
    start = time.time()
    total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"\n� Insertando {total} registros en {total_batches} batches vía REST API...\n")

    with httpx.Client(timeout=60.0) as client:
        for i in range(0, total, BATCH_SIZE):
            batch = rows[i : i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            payload = [format_row(r) for r in batch]

            try:
                resp = client.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    params={"on_conflict": "content,type"},
                )
                if resp.status_code in (200, 201):
                    inserted += len(batch)
                    pct = (inserted / total) * 100
                    print(f"   Batch {batch_num}/{total_batches} ✓ ({inserted}/{total} - {pct:.0f}%)")
                else:
                    errors += len(batch)
                    print(f"   Batch {batch_num}/{total_batches} ✗ HTTP {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                errors += len(batch)
                print(f"   Batch {batch_num}/{total_batches} ✗ Error: {e}")

    elapsed = time.time() - start

    print(f"\n{'=' * 60}")
    print(f"  ✅ Inserción completada en {elapsed:.1f}s")
    print(f"{'=' * 60}")
    print(f"  Insertados: {inserted}")
    if errors:
        print(f"  Errores:    {errors}")
    print()

    verify(supabase_url, service_key)


def verify(supabase_url: str, service_key: str):
    """Verifica los registros insertados vía REST API."""
    print("🔍 Verificando...")

    # Usamos RPC para ejecutar una query de conteo agrupado
    endpoint = f"{supabase_url}/rest/v1/knowledge_embeddings"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(
                endpoint,
                headers={**headers, "Prefer": "count=exact"},
                params={"select": "type"},
            )
            if resp.status_code == 200:
                total = int(resp.headers.get("content-range", "0/0").split("/")[-1])
                rows = resp.json()
                # Count by type
                counts = {}
                for r in rows:
                    t = r["type"]
                    counts[t] = counts.get(t, 0) + 1
                for t, c in sorted(counts.items()):
                    print(f"   {t}: {c}")
                print(f"   ──────────")
                print(f"   TOTAL: {total}")
            else:
                print(f"   ⚠ Error verificando: HTTP {resp.status_code}")
    except Exception as e:
        print(f"   ⚠ Error verificando: {e}")


if __name__ == "__main__":
    supabase_url, service_key = load_env()
    rows = load_data()
    insert(supabase_url, service_key, rows)
