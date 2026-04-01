# Embeddings - Pre-entrenamiento para búsqueda vectorial

Script para generar embeddings de categorías, intents y FAQ usando OpenAI `text-embedding-3-small`.

## Requisitos

- Python 3.10+
- `OPENAI_API_KEY` configurada en `apps/api/.env`

## Uso

```bash
cd packages/embeddings
pip install -r requirements.txt
python generate_embeddings.py
```

## Ficheros

| Fichero | Descripción |
|---------|-------------|
| `seed.json` | Datos de pre-entrenamiento (categorías, intents, FAQ) |
| `generate_embeddings.py` | Script que genera embeddings y produce SQL |
| `output/embeddings_seed.sql` | SQL generado para insertar en Supabase |

## Flujo

1. Editar `seed.json` con nuevas categorías/intents/FAQ
2. Ejecutar `python generate_embeddings.py`
3. Copiar `output/embeddings_seed.sql` en el SQL Editor de Supabase
4. Ejecutar el SQL

## Coste estimado

~300 entries × ~5 tokens/entry = ~1500 tokens → **~$0.00003** (prácticamente gratis)
