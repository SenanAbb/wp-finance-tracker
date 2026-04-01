#!/usr/bin/env python3
"""
============================================================================
Generate Embeddings - Pre-entrenamiento para búsqueda vectorial
============================================================================
Lee seed.json, genera embeddings con OpenAI text-embedding-3-small,
y produce un fichero SQL con INSERTs para copiar/pegar en Supabase.

Uso:
  1. pip install -r requirements.txt
  2. Asegurar que OPENAI_API_KEY está en apps/api/.env o como variable de entorno
  3. python generate_embeddings.py
  4. Copiar el contenido de output/embeddings_seed.sql en el SQL editor de Supabase

El script:
  - Lee seed.json con las entradas (categorías, intents, FAQ)
  - Genera embeddings en batches (max 2048 textos por batch)
  - Genera output/embeddings_seed.sql con los INSERTs
  - Muestra estadísticas de tokens usados y coste estimado
============================================================================
"""

import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# ============================================================================
# Configuración
# ============================================================================

SCRIPT_DIR = Path(__file__).parent
SEED_FILE = SCRIPT_DIR / "seed.json"
OUTPUT_DIR = SCRIPT_DIR / "output"
OUTPUT_SQL = OUTPUT_DIR / "embeddings_seed.sql"

# Cargar .env local (packages/embeddings/.env)
LOCAL_ENV = SCRIPT_DIR / ".env"
if LOCAL_ENV.exists():
    load_dotenv(LOCAL_ENV)
    print(f"✓ Loaded env from {LOCAL_ENV}")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("✗ ERROR: OPENAI_API_KEY no encontrada.")
    print("  Asegúrate de que existe en apps/api/.env o como variable de entorno.")
    sys.exit(1)

BATCH_SIZE = 2048  # Máximo de OpenAI embeddings API
MODEL = "text-embedding-3-small"
DIMENSIONS = 1536

# ============================================================================
# Funciones
# ============================================================================

def load_seed() -> dict:
    """Carga seed.json y valida estructura."""
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    entries = data.get("entries", [])
    if not entries:
        print("✗ ERROR: seed.json no tiene entries.")
        sys.exit(1)
    
    # Validar cada entrada
    for i, entry in enumerate(entries):
        if "type" not in entry or "content" not in entry or "metadata" not in entry:
            print(f"✗ ERROR: Entry {i} incompleta: {entry}")
            sys.exit(1)
    
    return data


def generate_embeddings_batch(client: OpenAI, texts: list[str]) -> list[list[float]]:
    """Genera embeddings para un batch de textos."""
    response = client.embeddings.create(
        model=MODEL,
        input=texts,
        dimensions=DIMENSIONS,
    )
    return [item.embedding for item in response.data]


def escape_sql(text: str) -> str:
    """Escapa comillas simples para SQL."""
    return text.replace("'", "''")


def vector_to_sql(embedding: list[float]) -> str:
    """Convierte un vector a formato SQL pgvector."""
    values = ",".join(f"{v:.8f}" for v in embedding)
    return f"'[{values}]'"


def generate_sql(entries: list[dict], embeddings: list[list[float]]) -> str:
    """Genera el fichero SQL con INSERTs."""
    lines = []
    lines.append("-- ============================================================================")
    lines.append("-- Knowledge Embeddings Seed")
    lines.append(f"-- Generado automáticamente el {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"-- Modelo: {MODEL} ({DIMENSIONS} dimensiones)")
    lines.append(f"-- Total: {len(entries)} embeddings")
    lines.append("-- ============================================================================")
    lines.append("-- INSTRUCCIONES:")
    lines.append("-- 1. Abre el SQL Editor de Supabase")
    lines.append("-- 2. Asegúrate de que la tabla knowledge_embeddings existe (ejecuta schema.sql)")
    lines.append("-- 3. Pega y ejecuta este SQL")
    lines.append("-- ============================================================================")
    lines.append("")
    lines.append("-- Limpiar embeddings anteriores (opcional, descomenta si quieres)")
    lines.append("-- truncate table public.knowledge_embeddings;")
    lines.append("")

    for i, (entry, embedding) in enumerate(zip(entries, embeddings)):
        entry_type = escape_sql(entry["type"])
        content = escape_sql(entry["content"])
        metadata = escape_sql(json.dumps(entry["metadata"], ensure_ascii=False))
        vector = vector_to_sql(embedding)

        lines.append(
            f"insert into public.knowledge_embeddings (type, content, metadata, embedding) "
            f"values ('{entry_type}', '{content}', '{metadata}', {vector}) "
            f"on conflict (content, type) do update set metadata = excluded.metadata, embedding = excluded.embedding;"
        )

    lines.append("")
    lines.append(f"-- ✓ {len(entries)} embeddings insertados")
    lines.append("")

    return "\n".join(lines)


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 60)
    print("  Generate Embeddings - Pre-entrenamiento")
    print("=" * 60)
    print()

    # 1. Cargar seed
    print(f"📂 Cargando seed desde {SEED_FILE}...")
    data = load_seed()
    entries = data["entries"]
    
    # Estadísticas por tipo
    type_counts = {}
    for e in entries:
        t = e["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print(f"   Total: {len(entries)} entries")
    for t, count in sorted(type_counts.items()):
        print(f"   - {t}: {count}")
    print()

    # 2. Generar embeddings
    print(f"🤖 Generando embeddings con {MODEL}...")
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    texts = [entry["content"] for entry in entries]
    all_embeddings = []
    total_tokens = 0

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"   Batch {batch_num}/{total_batches} ({len(batch)} textos)...", end=" ", flush=True)
        
        response = client.embeddings.create(
            model=MODEL,
            input=batch,
            dimensions=DIMENSIONS,
        )
        
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)
        batch_tokens = response.usage.total_tokens
        total_tokens += batch_tokens
        
        print(f"✓ ({batch_tokens} tokens)")

    # Coste estimado: text-embedding-3-small = $0.02 / 1M tokens
    cost_estimate = (total_tokens / 1_000_000) * 0.02
    print(f"\n   Total tokens: {total_tokens}")
    print(f"   Coste estimado: ${cost_estimate:.6f}")
    print()

    # 3. Generar SQL
    print(f"📝 Generando SQL...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sql_content = generate_sql(entries, all_embeddings)
    
    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        f.write(sql_content)
    
    file_size_mb = os.path.getsize(OUTPUT_SQL) / (1024 * 1024)
    print(f"   ✓ SQL escrito en {OUTPUT_SQL}")
    print(f"   Tamaño: {file_size_mb:.2f} MB")

    # 3b. Generar JSON para inserción vía REST API
    OUTPUT_JSON = OUTPUT_DIR / "embeddings_seed.json"
    json_rows = []
    for entry, embedding in zip(entries, all_embeddings):
        json_rows.append({
            "type": entry["type"],
            "content": entry["content"],
            "metadata": entry["metadata"],
            "embedding": embedding,
        })
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(json_rows, f, ensure_ascii=False)
    
    json_size_mb = os.path.getsize(OUTPUT_JSON) / (1024 * 1024)
    print(f"   ✓ JSON escrito en {OUTPUT_JSON}")
    print(f"   Tamaño: {json_size_mb:.2f} MB")
    print()

    # 4. Resumen
    print("=" * 60)
    print("  ✅ Pre-entrenamiento completado")
    print("=" * 60)
    print()
    print("  Siguiente paso:")
    print(f"  1. Abre Supabase SQL Editor")
    print(f"  2. Ejecuta schema.sql (si no lo has hecho)")
    print(f"  3. Pega y ejecuta: {OUTPUT_SQL}")
    print()


if __name__ == "__main__":
    main()
