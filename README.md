# WhatsApp Finance Tracker

Sistema personal para **gestionar gastos, ingresos e inversiones directamente desde WhatsApp**, con almacenamiento en base de datos, **búsqueda vectorial (RAG)** para detección rápida de intenciones, y una **web app para análisis y estadísticas**.

```
"café 3 con tarjeta" → Gasto 3€ | Categoría: comida | Cuenta: Revolut
```

---

## Arquitectura del sistema

```
Usuario (WhatsApp)
        │
        ▼
Kapso / Meta Cloud API (principal) ──o── Twilio (legacy)
        │
        │ Webhook POST
        ▼
Backend API (Node.js / Fastify)
        │
        ├─ Máquina de estados (state machine)
        ├─ Embeddings + Búsqueda vectorial (pgvector)
        ├─ OpenAI GPT (interpretación RAG)
        ├─ Lógica financiera (services)
        │
        ▼
Supabase (PostgreSQL + pgvector)
        │
        ├─ users, sessions, accounts, transactions, categories
        ├─ knowledge_embeddings (427 embeddings pre-entrenados)
        └─ match_embeddings() función RPC
        │
        ▼
Next.js Dashboard (web app)
```

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| **Backend** | Node.js, Fastify 5 |
| **Canal WhatsApp** | Kapso (@kapso/whatsapp-cloud-api), Twilio (legacy) |
| **IA** | OpenAI GPT-4o-mini (interpretación), text-embedding-3-small (embeddings) |
| **Base de datos** | PostgreSQL (Supabase) con pgvector |
| **Búsqueda vectorial** | pgvector + HNSW index + match_embeddings RPC |
| **Pre-entrenamiento** | Python (generate_embeddings.py → insert_embeddings.py) |
| **Frontend** | Next.js |

---

## Procesamiento de mensajes: RAG + State Machine

El sistema usa un enfoque híbrido **Embeddings + GPT** para minimizar latencia, coste y alucinaciones:

1. **Embeddings** detectan rápidamente QUÉ quiere el usuario (intent, categoría, cuenta, FAQ)
2. **GPT** extrae datos estructurados cuando es necesario (importes, múltiples transacciones)
3. **Fast path** evita llamar a GPT cuando la confianza vectorial es alta

### ¿Cuándo se usa cada componente?

| Mensaje | Embeddings | GPT | Resultado |
|---------|-----------|-----|-----------|
| "saldo" | ✅ intent=balance (1.0) | ❌ Fast path | → BALANCE_FLOW directo |
| "hola" | ✅ FAQ (0.71) | ❌ Fast path | → Respuesta pre-definida |
| "mis cuentas" | ✅ intent=list_accounts (1.0) | ❌ Fast path | → LIST_ACCOUNTS_FLOW |
| "café 3" | ✅ intent=expense, cat=comida | ✅ Extrae amount=3 | → TRANSACTION_FLOW |
| "café 3, bus 2" | ✅ Sugiere expense, comida | ✅ Parsea 2 transacciones | → TRANSACTION_FLOW |
| "café 3 con tarjeta" | ✅ expense, comida, banco | ✅ Extrae amount + account | → TRANSACTION_FLOW |
| "asdfgh" | ❌ Baja confianza | ✅ GPT solo → unknown | → PERMISSION_DENIED |
| Error vector search | ❌ Fallo técnico | ✅ Fallback total | → GPT decide solo |

---

## Grafo completo de la máquina de estados

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
                   │  FAQ match │      │ Intent simple  │       │ RAG/     │
                   │  (≥0.90)   │      │ (≥0.88)        │       │ Fallback │
                   └─────┬──────┘      └───────┬────────┘       └────┬─────┘
                         │                     │                     │
                    Fast path             Fast path                  │
                         │                     │                     ▼
                         ▼                     │          ┌──────────────────┐
                      ┌──────┐                 │          │  AI_INTERPRETING │
                      │ DONE │                 │          └────┬────┬───────┘
                      └──────┘                 │               │    │
                                               │               │    └──► PERMISSION_DENIED
                                               │               │         (intent=unknown)
                                               │               │              │
                                               ▼               ▼              ▼
                                    ┌──────────────────────────────┐       ┌──────┐
                                    │     FLUJOS DE NEGOCIO        │       │ DONE │
                                    ├──────────────────────────────┤       └──────┘
                                    │ BALANCE_FLOW                 │
                                    │ TRANSACTION_FLOW             │
                                    │ CREATE_ACCOUNT_FLOW          │
                                    │ LIST_ACCOUNTS_FLOW           │
                                    │ LIST_TRANSACTIONS_FLOW       │
                                    │ STATISTICS_FLOW              │
                                    └──────────────┬───────────────┘
                                                   │
                                                   ▼
                                                ┌──────┐
                                                │ DONE │
                                                └──────┘

              Cualquier estado con error → ERROR_RESPONSE → DONE
```

### Descripción de cada transición

| Origen | Destino | Condición |
|--------|---------|-----------|
| **IDLE** → SESSION_LOADER | Siempre | Mensaje recibido, inicia procesamiento |
| **SESSION_LOADER** → LOGIN_FLOW | Usuario nuevo pide "login" | O usuario existente pide "login" (renovar sesión) |
| **SESSION_LOADER** → PERMISSION_DENIED | Sin sesión activa | Usuario no existe o sesión expirada |
| **SESSION_LOADER** → CONTEXT_LOADER | Sesión válida | Usuario autenticado con sesión activa |
| **CONTEXT_LOADER** → VECTOR_SEARCH | Siempre (si tiene cuentas) | Cuentas y categorías cargadas desde BD |
| **CONTEXT_LOADER** → DONE | Sin cuentas | Pide al usuario crear una cuenta primero |
| **VECTOR_SEARCH** → DONE | FAQ con score ≥ 0.65 | ⚡ Fast path: respuesta directa pre-definida |
| **VECTOR_SEARCH** → [FLOW] | Intent simple ≥ 0.60 | ⚡ Fast path: balance, list_accounts, list_transactions, statistics |
| **VECTOR_SEARCH** → AI_INTERPRETING | Score < 0.60 o intent con transacciones | 🧠 RAG path: pasa sugerencias vectoriales como hints a GPT |
| **VECTOR_SEARCH** → AI_INTERPRETING | Error en búsqueda vectorial | 🔄 Fallback: GPT sin sugerencias |
| **AI_INTERPRETING** → [FLOW] | Intent válido reconocido por GPT | expense, income, balance, create_account, etc. |
| **AI_INTERPRETING** → PERMISSION_DENIED | Intent unknown | GPT no reconoce la intención |
| **AI_INTERPRETING** → ERROR_RESPONSE | Error en llamada GPT | Fallo técnico en OpenAI |
| **[FLOW]** → DONE | Siempre | Flujo de negocio completado |
| **ERROR_RESPONSE** → DONE | Siempre | Mensaje de error enviado al usuario |
| **PERMISSION_DENIED** → DONE | Siempre | Mensaje de denegación enviado |

### Umbrales de confianza vectorial

| Tipo | Fast path | RAG (hint a GPT) | Ignorar |
|------|-----------|-------------------|---------|
| **FAQ** | ≥ 0.65 | — | < 0.40 |
| **Intent** | ≥ 0.60 (solo sin transacciones) | ≥ 0.40 | < 0.30 |
| **Category** | — | ≥ 0.40 | < 0.30 |
| **Account** | — | ≥ 0.40 | < 0.30 |

> **Nota**: `text-embedding-3-small` con distancia coseno produce similitudes en el rango 0.3–0.7 para coincidencias reales. No esperar >0.9.

---

## Estructura del proyecto

```
whatsapp-finance-tracker/
├── apps/
│   ├── api/                          # Backend principal (Node.js / Fastify)
│   │   ├── src/
│   │   │   ├── ai/
│   │   │   │   ├── embeddings.js     # Genera embeddings del mensaje del usuario (runtime)
│   │   │   │   ├── interpret.js      # System prompt + llamada GPT con RAG context
│   │   │   │   └── openai.js         # Wrapper OpenAI API
│   │   │   ├── adapters/
│   │   │   │   ├── implementations/
│   │   │   │   │   ├── kapso/        # KapsoWhatsAppAdapter (canal principal)
│   │   │   │   │   └── supabase/     # Repositories Supabase (+ supabase client)
│   │   │   │   └── repositories/     # Interfaces de repositorios
│   │   │   ├── domain/
│   │   │   │   ├── entities/         # Account, User, Session, Transaction
│   │   │   │   └── services/         # UserService, AccountService, VectorSearchService, etc.
│   │   │   ├── routes/
│   │   │   │   ├── kapso.js          # Webhook Kapso (principal)
│   │   │   │   ├── twilio.js         # Webhook Twilio (legacy)
│   │   │   │   └── auth.js           # Rutas de autenticación
│   │   │   ├── state/
│   │   │   │   ├── stateMachine.js   # Clase StateMachine
│   │   │   │   └── handlers/
│   │   │   │       ├── core/         # IDLE, SESSION_LOADER, CONTEXT_LOADER,
│   │   │   │       │                 # VECTOR_SEARCH, AI_INTERPRETING, DONE, etc.
│   │   │   │       └── flows/        # BALANCE_FLOW, TRANSACTION_FLOW, etc.
│   │   │   └── utils/                # phone, twiml, errors, twilioClient
│   │   ├── .env                      # Variables de entorno API
│   │   └── index.js                  # Entry point
│   │
│   └── web/                          # Frontend Next.js
│
├── packages/
│   ├── database/
│   │   ├── schema.sql                # Schema completo (pgvector, knowledge_embeddings, match_embeddings)
│   │   └── seed.sql                  # Datos iniciales
│   │
│   ├── embeddings/                   # Pre-entrenamiento de embeddings
│   │   ├── seed.json                 # 427 entries: categories, intents, FAQ, accounts
│   │   ├── generate_embeddings.py    # Genera embeddings con OpenAI → SQL + JSON
│   │   ├── insert_embeddings.py      # Inserta en Supabase vía REST API
│   │   ├── requirements.txt          # openai, python-dotenv, psycopg2-binary, httpx
│   │   └── .env                      # OPENAI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
│   │
│   └── shared/                       # Tipos y constantes compartidas
│
├── infra/
│   ├── docker/
│   └── env/
│
└── README.md
```

---

## Base de datos (Supabase / PostgreSQL + pgvector)

### Tablas principales

- **users** — Usuarios registrados
- **sessions** — Sesiones activas (JWT)
- **accounts** — Cuentas del usuario (tipo: banco, cash, inversion)
- **categories** — Categorías de gastos/ingresos
- **transactions** — Movimientos financieros
- **investments** — Inversiones
- **knowledge_embeddings** — 427 embeddings pre-entrenados (vector 1536 dims)

### Función RPC: match_embeddings

```sql
match_embeddings(query_embedding, match_type, match_threshold, match_count)
```

Busca los embeddings más similares usando distancia coseno con índice HNSW.

---

## Canales de mensajería

| Canal | Estado | Formato webhook |
|-------|--------|----------------|
| **Kapso** (Meta Cloud API) | Principal | `{ message: { from, text, type } }` |
| **Twilio** | Legacy (dev/testing) | Form-data con `Body`, `From` |

---

## Comandos de WhatsApp

| Comando | Ejemplo | Intent |
|---------|---------|--------|
| Registrar gasto | "café 3", "uber 8 con tarjeta" | expense |
| Registrar ingreso | "nómina 2500", "ingreso 500" | income |
| Consultar saldo | "saldo", "cuánto tengo" | balance |
| Ver cuentas | "mis cuentas" | list_accounts |
| Ver movimientos | "últimas transacciones" | list_transactions |
| Estadísticas | "estadísticas", "en qué gasto más" | statistics |
| Crear cuenta | "crear cuenta banco EUR" | create_account |
| Saludos/FAQ | "hola", "ayuda", "gracias" | FAQ (fast path) |

---

## Posibles mejoras futuras

- Sincronización con cuentas bancarias reales
- Detección automática de suscripciones
- Resúmenes diarios/mensuales automáticos
- Recomendaciones de ahorro con IA
- Predicción de gasto mensual
- App móvil nativa
