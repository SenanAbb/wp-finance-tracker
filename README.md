<div align="center">

# WhatsApp Finance Tracker

**Asistente financiero personal impulsado por IA que convierte mensajes de WhatsApp en datos financieros estructurados, con búsqueda vectorial, máquina de estados y dashboard analítico.**

[![Node.js](https://img.shields.io/badge/Node.js-22-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![Fastify](https://img.shields.io/badge/Fastify-5-000000?logo=fastify&logoColor=white)](https://fastify.dev/)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?logo=next.js&logoColor=white)](https://nextjs.org/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3FCF8E?logo=supabase&logoColor=white)](https://supabase.com/)
[![pgvector](https://img.shields.io/badge/pgvector-HNSW-4169E1?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?logo=openai&logoColor=white)](https://openai.com/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-4-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)

```
"café 3 con tarjeta" → Gasto 3.00 EUR | Categoría: comida | Cuenta: Revolut
```

</div>

---

## Qué es este proyecto

Un sistema **end-to-end** que permite gestionar gastos, ingresos, cuentas e inversiones **directamente desde WhatsApp**, sin necesidad de abrir ninguna app. Cada mensaje se procesa mediante una pipeline inteligente que combina:

- **Búsqueda vectorial** (pgvector + HNSW) para detección de intenciones en milisegundos
- **RAG (Retrieval-Augmented Generation)** para enriquecer las respuestas de GPT con contexto financiero del usuario
- **Máquina de estados determinista** que orquesta todo el flujo conversacional
- **Dashboard web** (Next.js) para visualización de estadísticas y análisis

El resultado: un asistente financiero que entiende lenguaje natural, categoriza automáticamente y responde en menos de 2 segundos.

---

## Arquitectura del sistema

```
 Usuario (WhatsApp)
         │
         ▼
 Meta Cloud API (Kapso) ────────── Twilio (legacy)
         │
         │  Webhook POST
         ▼
 ┌──────────────────────────────────────────────────────┐
 │              Backend API (Node.js / Fastify 5)       │
 │                                                      │
 │  ┌─────────────┐   ┌──────────────────────────────┐  │
 │  │   Webhook   │──▶│     State Machine Engine      │  │
 │  │   Router    │   │                                │  │
 │  └─────────────┘   │  IDLE → SESSION → CONTEXT     │  │
 │                     │    → VECTOR_SEARCH            │  │
 │                     │    → AI_INTERPRETING           │  │
 │                     │    → BUSINESS_FLOW → DONE     │  │
 │                     └──────┬───────────┬────────────┘  │
 │                            │           │               │
 │              ┌─────────────┘           └──────┐        │
 │              ▼                                ▼        │
 │  ┌────────────────────┐         ┌──────────────────┐   │
 │  │  Vector Search     │         │  OpenAI GPT-4o   │   │
 │  │  (pgvector HNSW)   │         │  mini (RAG)      │   │
 │  │                    │         │                    │   │
 │  │  427 embeddings    │────────▶│  Interpreta con   │   │
 │  │  pre-entrenados    │  hints  │  contexto vectorial│   │
 │  │  1536 dimensiones  │         │  + datos usuario   │   │
 │  └────────────────────┘         └──────────────────┘   │
 │              │                          │               │
 │              └──────────┬───────────────┘               │
 │                         ▼                               │
 │  ┌──────────────────────────────────────────────────┐   │
 │  │              Domain Services (DDD)                │   │
 │  │  TransactionService · AccountService              │   │
 │  │  CategoryService · VectorSearchService            │   │
 │  │  AuthService · StatisticsService                  │   │
 │  └──────────────────────────────────────────────────┘   │
 └──────────────────────────┬──────────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │           Supabase (PostgreSQL + pgvector)            │
 │                                                       │
 │  users · sessions · accounts · transactions           │
 │  categories · investments · category_limits           │
 │  knowledge_embeddings (vector 1536)                   │
 │  match_embeddings() → RPC de búsqueda coseno          │
 └───────────────────────────┬───────────────────────────┘
                             │
                             ▼
 ┌──────────────────────────────────────────────────────┐
 │         Next.js 16 Dashboard (React 19)               │
 │                                                       │
 │  Autenticación OTP vía WhatsApp                       │
 │  Estadísticas · Gráficos (Recharts)                   │
 │  Gestión de cuentas y transacciones                   │
 │  TailwindCSS 4 · Lucide Icons                         │
 └───────────────────────────────────────────────────────┘
```

---

## Stack tecnológico

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| **Backend** | Node.js 22, Fastify 5 | API REST + webhooks, validación, routing |
| **Canal WhatsApp** | Meta Cloud API (Kapso), Twilio (legacy) | Recepción y envío de mensajes |
| **Inteligencia Artificial** | OpenAI GPT-4o-mini | Interpretación de lenguaje natural (RAG) |
| **Embeddings** | OpenAI text-embedding-3-small (1536 dims) | Vectorización semántica de mensajes |
| **Búsqueda vectorial** | pgvector + índice HNSW + RPC `match_embeddings` | Detección de intents, categorías, FAQ en <50ms |
| **Base de datos** | PostgreSQL 15 (Supabase) | Persistencia relacional + vectorial |
| **Frontend** | Next.js 16, React 19, TypeScript 5 | Dashboard analítico SPA |
| **Estilos** | TailwindCSS 4, Lucide Icons | UI moderna y responsive |
| **Gráficos** | Recharts 3 | Visualización de estadísticas financieras |
| **Autenticación** | JWT + OTP vía WhatsApp | Login sin contraseña |
| **Pre-entrenamiento** | Python 3.12 (scripts de embeddings) | Generación e inserción de 427 embeddings |
| **Monorepo** | Workspaces (apps/ + packages/) | Separación de concerns |

---

## Cómo funciona: RAG + Vector Search + State Machine

El corazón del sistema es una **pipeline híbrida** que combina búsqueda vectorial con GPT para lograr respuestas rápidas, precisas y económicas.

### Pipeline de procesamiento de cada mensaje

```
Mensaje del usuario
        │
        ▼
┌───────────────────────────────────────────┐
│  1. VECTOR SEARCH (pgvector + HNSW)       │
│                                           │
│  Mensaje → embedding (1536 dims)          │
│  → Búsqueda coseno contra 427 embeddings  │
│  → Top matches: intent, category, FAQ     │
└────────────┬──────────────────────────────┘
             │
     ┌───────┴───────┐
     ▼               ▼
 Alta confianza   Baja confianza
 (score ≥ 0.60)   (score < 0.60)
     │               │
     ▼               ▼
 ⚡ FAST PATH    🧠 RAG PATH
 Sin llamar      Hints vectoriales
 a GPT           + contexto → GPT
     │               │
     └───────┬───────┘
             ▼
     Business Flow
     (transaction, balance, etc.)
```

### El concepto de Fast Path

La clave de la eficiencia está en el **fast path**: cuando la búsqueda vectorial tiene alta confianza (score ≥ 0.60 para intents, ≥ 0.65 para FAQ), el sistema **no necesita llamar a GPT**. Esto significa:

- **Latencia ~200ms** en vez de ~1500ms
- **Coste $0** en tokens de OpenAI para ese mensaje
- **Cero alucinaciones** (respuesta determinista)

Para mensajes ambiguos, el sistema pasa al **RAG path**: los resultados vectoriales se inyectan como `hints` al prompt de GPT, reduciendo alucinaciones y mejorando la precisión de la interpretación.

### Tabla de decisión

| Mensaje | Embeddings | GPT | Resultado |
|---------|-----------|-----|-----------|
| "saldo" | ✅ intent=balance (0.98) | ❌ Fast path | → BALANCE_FLOW directo |
| "hola" | ✅ FAQ match (0.71) | ❌ Fast path | → Respuesta pre-definida |
| "mis cuentas" | ✅ intent=list_accounts (0.95) | ❌ Fast path | → LIST_ACCOUNTS_FLOW |
| "café 3" | ✅ intent=expense, cat=comida | ✅ Extrae amount=3 | → TRANSACTION_FLOW |
| "café 3, bus 2" | ✅ Sugiere expense | ✅ Parsea 2 transacciones | → TRANSACTION_FLOW |
| "café 3 con tarjeta" | ✅ expense + cuenta | ✅ Extrae amount + account | → TRANSACTION_FLOW |
| "asdfgh" | ❌ Baja confianza | ✅ GPT → unknown | → PERMISSION_DENIED |
| Error vectorial | ❌ Fallo técnico | ✅ Fallback total | → GPT decide solo |

---

## Embeddings: Base de conocimiento vectorial

El sistema mantiene **427 embeddings pre-entrenados** en la tabla `knowledge_embeddings`, generados con `text-embedding-3-small` (1536 dimensiones) e indexados con **HNSW** para búsqueda sub-lineal.

### Tipos de embeddings

| Tipo | Cantidad | Propósito | Ejemplo |
|------|----------|-----------|---------|
| `category` | ~150 | Sinónimos y variaciones de categorías | "mercadona", "supermercado" → comida |
| `intent` | ~120 | Frases que representan intenciones | "cuánto he gastado" → statistics |
| `faq` | ~100 | Preguntas frecuentes con respuesta directa | "hola", "ayuda", "gracias" |
| `account` | ~57 | Nombres y alias de cuentas bancarias | "tarjeta", "revolut" → cuenta |

### Función RPC: match_embeddings

```sql
SELECT * FROM match_embeddings(
  query_embedding := <vector 1536>,
  match_type     := 'intent',     -- o 'category', 'faq', 'account', NULL para todos
  match_threshold := 0.40,
  match_count     := 5
);
```

Devuelve los embeddings más similares usando **distancia coseno** con el índice HNSW, que ofrece búsqueda aproximada en **O(log n)** en lugar de O(n).

### Umbrales de confianza

| Tipo | Fast path | RAG hint | Ignorar |
|------|-----------|----------|---------|
| **FAQ** | ≥ 0.65 | — | < 0.40 |
| **Intent** | ≥ 0.60 | ≥ 0.40 | < 0.30 |
| **Category** | — | ≥ 0.40 | < 0.30 |
| **Account** | — | ≥ 0.40 | < 0.30 |

> **Nota**: `text-embedding-3-small` con distancia coseno produce similitudes típicas en el rango 0.3–0.7 para coincidencias reales.

---

## Máquina de estados (State Machine)

Cada mensaje de WhatsApp se procesa a través de una **máquina de estados determinista** que garantiza un flujo predecible y libre de race conditions.

### Grafo completo

```
                         ┌─────────┐
                         │  IDLE   │
                         └────┬────┘
                              │ Mensaje recibido
                              ▼
                     ┌─────────────────┐
                     │ SESSION_LOADER  │
                     └───┬───┬───┬────┘
                         │   │   │
          ┌──────────────┘   │   └──────────────┐
          ▼                  ▼                   ▼
   ┌────────────┐    ┌────────────┐     ┌──────────────────┐
   │ LOGIN_FLOW │    │ PERMISSION │     │ CONTEXT_LOADER   │
   │            │    │ _DENIED    │     └────────┬─────────┘
   └─────┬──────┘    └─────┬──────┘              │
         │                 │              Carga cuentas y categorías
         ▼                 ▼                     │
      ┌──────┐          ┌──────┐                 ▼
      │ DONE │          │ DONE │        ┌─────────────────┐
      └──────┘          └──────┘        │  VECTOR_SEARCH  │
                                        └──┬────┬────┬────┘
                                           │    │    │
                          ┌────────────────┘    │    └─────────────────┐
                          ▼                     ▼                      ▼
                   ┌────────────┐      ┌────────────────┐       ┌──────────┐
                   │  FAQ match │      │ Intent simple  │       │ RAG /    │
                   │  (≥ 0.65)  │      │ (≥ 0.60)       │       │ Fallback │
                   └─────┬──────┘      └───────┬────────┘       └────┬─────┘
                         │                     │                     │
                    Fast path             Fast path                  │
                         │                     │                     ▼
                         ▼                     │          ┌──────────────────┐
                      ┌──────┐                 │          │  AI_INTERPRETING │
                      │ DONE │                 │          └────┬────┬───────┘
                      └──────┘                 │               │    │
                                               │               │    └──► PERMISSION_DENIED
                                               │               │         (intent = unknown)
                                               │               │              │
                                               ▼               ▼              ▼
                                    ┌──────────────────────────────┐       ┌──────┐
                                    │      BUSINESS FLOWS          │       │ DONE │
                                    ├──────────────────────────────┤       └──────┘
                                    │  BALANCE_FLOW                │
                                    │  TRANSACTION_FLOW            │
                                    │  CREATE_ACCOUNT_FLOW         │
                                    │  LIST_ACCOUNTS_FLOW          │
                                    │  LIST_TRANSACTIONS_FLOW      │
                                    │  STATISTICS_FLOW             │
                                    └──────────────┬───────────────┘
                                                   │
                                                   ▼
                                                ┌──────┐
                                                │ DONE │
                                                └──────┘

              Cualquier estado con error → ERROR_RESPONSE → DONE
```

### Transiciones

| Origen | Destino | Condición |
|--------|---------|-----------|
| **IDLE** → SESSION_LOADER | Siempre | Mensaje recibido, inicia procesamiento |
| **SESSION_LOADER** → LOGIN_FLOW | Pide "login" | Usuario nuevo o renovación de sesión |
| **SESSION_LOADER** → PERMISSION_DENIED | Sin sesión | Usuario no existe o sesión expirada |
| **SESSION_LOADER** → CONTEXT_LOADER | Sesión válida | Usuario autenticado |
| **CONTEXT_LOADER** → VECTOR_SEARCH | Con cuentas | Cuentas y categorías cargadas desde BD |
| **CONTEXT_LOADER** → DONE | Sin cuentas | Solicita crear cuenta primero |
| **VECTOR_SEARCH** → DONE | FAQ ≥ 0.65 | ⚡ Fast path: respuesta directa |
| **VECTOR_SEARCH** → [FLOW] | Intent ≥ 0.60 | ⚡ Fast path: flujo directo |
| **VECTOR_SEARCH** → AI_INTERPRETING | Score bajo | 🧠 RAG path: GPT con hints vectoriales |
| **AI_INTERPRETING** → [FLOW] | Intent válido | GPT reconoce la intención |
| **AI_INTERPRETING** → PERMISSION_DENIED | Unknown | GPT no reconoce la intención |
| **[FLOW]** → DONE | Siempre | Flujo de negocio completado |

---

## Base de datos

### PostgreSQL + pgvector (Supabase)

| Tabla | Propósito |
|-------|-----------|
| `users` | Usuarios registrados (phone E.164) |
| `sessions` | Sesiones activas (JWT, dual origin: web/whatsapp) |
| `auth_challenges` | Desafíos OTP con rate limiting |
| `accounts` | Cuentas del usuario (banco, cash, inversión) |
| `categories` | Categorías globales (14 expense + income + investment) |
| `transactions` | Movimientos financieros con metadata JSONB |
| `category_limits` | Límites mensuales por categoría |
| `investments` | Portfolio de inversiones (crypto, stock, ETF) |
| `knowledge_embeddings` | 427 embeddings vectoriales (1536 dims, HNSW) |

### Extensiones habilitadas

- **pgvector** — Tipo `vector(1536)` + operador `<=>` (coseno) + índice HNSW
- **pgcrypto** — `gen_random_uuid()` para PKs
- **citext** — Case-insensitive para teléfonos

---

## Estructura del proyecto

```
whatsapp-finance-tracker/
│
├── apps/
│   ├── api/                              # Backend principal
│   │   ├── src/
│   │   │   ├── ai/
│   │   │   │   ├── embeddings.js         # Genera embedding del mensaje en runtime
│   │   │   │   ├── interpret.js          # System prompt + GPT con contexto RAG
│   │   │   │   └── openai.js             # Wrapper OpenAI API
│   │   │   ├── adapters/
│   │   │   │   ├── implementations/
│   │   │   │   │   ├── kapso/            # KapsoWhatsAppAdapter (canal principal)
│   │   │   │   │   └── supabase/         # Repositorios Supabase + client
│   │   │   │   └── repositories/         # Interfaces de repositorios
│   │   │   ├── domain/
│   │   │   │   ├── entities/             # Account, User, Session, Transaction
│   │   │   │   └── services/             # UserService, AccountService, VectorSearchService...
│   │   │   ├── routes/
│   │   │   │   ├── kapso.js              # Webhook Meta Cloud API
│   │   │   │   ├── twilio.js             # Webhook Twilio (legacy)
│   │   │   │   └── auth.js               # OTP + JWT authentication
│   │   │   ├── state/
│   │   │   │   ├── stateMachine.js       # Motor de máquina de estados
│   │   │   │   └── handlers/
│   │   │   │       ├── core/             # IDLE, SESSION_LOADER, CONTEXT_LOADER,
│   │   │   │       │                     # VECTOR_SEARCH, AI_INTERPRETING, DONE...
│   │   │   │       └── flows/            # BALANCE, TRANSACTION, STATISTICS...
│   │   │   └── utils/                    # Helpers: phone, errors, twiml
│   │   └── index.js                      # Entry point
│   │
│   └── web/                              # Dashboard Next.js 16
│       ├── app/                          # App Router (React 19)
│       ├── components/                   # UI components
│       └── lib/                          # Auth client, Supabase client
│
├── packages/
│   ├── database/
│   │   ├── schema.sql                    # Schema completo + pgvector + RPC
│   │   ├── seed.sql                      # Categorías y datos iniciales
│   │   └── revolut_seed/                 # Import histórico de transacciones
│   │       ├── csv_to_ai_json.py         # CSV Revolut → JSON para categorizar con IA
│   │       └── categorized_json_to_sql.py # JSON categorizado → SQL inserts
│   │
│   ├── embeddings/                       # Pre-entrenamiento de knowledge base
│   │   ├── seed.json                     # 427 entries: category, intent, faq, account
│   │   ├── generate_embeddings.py        # OpenAI API → embeddings SQL + JSON
│   │   ├── insert_embeddings.py          # Inserta en Supabase vía REST
│   │   └── requirements.txt              # openai, python-dotenv, httpx
│   
│
│
└── README.md
```

---

## Autenticación: OTP sin contraseña

El sistema implementa **autenticación passwordless** a través de WhatsApp:

1. El usuario introduce su número de teléfono en el dashboard web
2. El backend genera un OTP de 6 dígitos y lo envía por WhatsApp
3. El usuario introduce el código en la web
4. Se genera un JWT con refresh token
5. Sesión activa con dual origin (web + whatsapp)

---

## Comandos de WhatsApp

| Comando | Ejemplo | Intent detectado |
|---------|---------|-----------------|
| Registrar gasto | "café 3", "uber 8 con tarjeta" | `expense` |
| Registrar ingreso | "nómina 2500", "ingreso 500" | `income` |
| Múltiples gastos | "café 3, bus 2, parking 1.5" | `expense` (batch) |
| Consultar saldo | "saldo", "cuánto tengo" | `balance` |
| Ver cuentas | "mis cuentas" | `list_accounts` |
| Ver movimientos | "últimas transacciones" | `list_transactions` |
| Estadísticas | "estadísticas", "en qué gasto más" | `statistics` |
| Crear cuenta | "crear cuenta banco EUR" | `create_account` |
| Saludos / FAQ | "hola", "ayuda", "gracias" | FAQ (fast path) |

---

## Import histórico (Revolut CSV)

El sistema incluye scripts Python para importar transacciones históricas desde CSV bancarios (Revolut) para alimentar estadísticas **sin alterar los balances actuales** de las cuentas:

```bash
# 1. CSV → JSON intermedio (listo para categorizar con IA)
python csv_to_ai_json.py

# 2. Categorizar con IA (manual o automatizado)
# → revolut_transactions_categorized.json

# 3. JSON categorizado → SQL inserts
python categorized_json_to_sql.py --user-phone "+34..." --account-name "Revolut"

# 4. Ejecutar SQL en Supabase
```

Cada transacción importada incluye `metadata.historical_import = true` y `metadata.affects_account_balance = false` para trazabilidad completa.

---

## Roadmap

- [ ] Sincronización con Open Banking (cuentas bancarias reales)
- [ ] Detección automática de suscripciones recurrentes
- [ ] Resúmenes diarios/mensuales automáticos por WhatsApp
- [ ] Recomendaciones de ahorro personalizadas con IA
- [ ] Predicción de gasto mensual basada en histórico
- [ ] App móvil nativa (React Native)
- [ ] Multi-idioma (ES/EN)
- [ ] Exportación a CSV/PDF desde el dashboard

---

## Autor

**Sanan Abbasov** — Full-Stack Developer

---

<div align="center">

*Built with AI, vector search, and a lot of WhatsApp messages.*

</div>
