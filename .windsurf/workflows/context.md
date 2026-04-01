# Contexto Global del Proyecto — WhatsApp Finance Tracker

Este documento proporciona **el contexto completo del proyecto** para que una IA pueda comprender el sistema antes de ayudar en su desarrollo.

---

## Descripción del proyecto

WhatsApp Finance Tracker es un sistema para **gestionar finanzas personales directamente desde WhatsApp**, usando **búsqueda vectorial (RAG)** para detección rápida de intenciones y **GPT** para extracción de datos estructurados.

```
"café 3 con tarjeta" → Gasto 3€ | Categoría: comida | Cuenta: Revolut
```

---

## Arquitectura general

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
        │     IDLE → SESSION_LOADER → CONTEXT_LOADER → VECTOR_SEARCH
        │         ↳ fast path → [FLOW] → DONE
        │         ↳ RAG path → AI_INTERPRETING → [FLOW] → DONE
        │
        ├─ Embeddings (text-embedding-3-small, 1536 dims)
        ├─ Búsqueda vectorial (pgvector + match_embeddings RPC)
        ├─ OpenAI GPT-4o-mini (interpretación con contexto RAG)
        ├─ Servicios de dominio (accounts, transactions, categories, etc.)
        │
        ▼
Supabase (PostgreSQL + pgvector)
        │
        ├─ users, sessions, accounts, transactions, categories
        ├─ knowledge_embeddings (427 embeddings pre-entrenados)
        └─ match_embeddings() función RPC (búsqueda por coseno + HNSW)
        │
        ▼
Next.js Dashboard (web app)
```

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| **Backend** | Node.js, Fastify 5 |
| **Canal WhatsApp** | Kapso (@kapso/whatsapp-cloud-api) principal, Twilio legacy |
| **IA - Embeddings** | OpenAI text-embedding-3-small (1536 dims) |
| **IA - Interpretación** | OpenAI GPT-4o-mini con JSON schema |
| **Base de datos** | PostgreSQL (Supabase) con pgvector + HNSW index |
| **Pre-entrenamiento** | Python scripts (generate_embeddings.py, insert_embeddings.py) |
| **Frontend** | Next.js |

---

## Procesamiento de mensajes: RAG + State Machine

El sistema combina **embeddings vectoriales** con **GPT** de forma híbrida:

1. **Embeddings** — Detectan QUÉ quiere el usuario (intent, categoría, cuenta, FAQ) comparando su mensaje con 427 embeddings pre-entrenados
2. **GPT** — Extrae datos estructurados cuando es necesario (importes, descripciones, múltiples transacciones)
3. **Fast path** — Evita llamar a GPT cuando la confianza vectorial es alta (ahorra latencia y coste)

### ¿Cuándo se usa GPT (AI_INTERPRETING)?

| Situación | Embeddings | GPT | Por qué |
|-----------|-----------|-----|---------|
| "saldo" | ✅ intent=balance (1.0) | ❌ Fast path | No necesita parsear datos |
| "hola" | ✅ FAQ (0.71) | ❌ Fast path | Respuesta pre-definida |
| "mis cuentas" | ✅ intent=list_accounts (1.0) | ❌ Fast path | No necesita parsear datos |
| "café 3" | ✅ Sugiere intent + categoría | ✅ Necesario | Debe extraer amount=3, desc="café" |
| "café 3, bus 2, pan 1" | ✅ Sugiere expense + comida | ✅ Necesario | Debe parsear 3 transacciones |
| "nómina 2500 revolut" | ✅ income + banco | ✅ Necesario | Debe extraer amount=2500, account |
| "crear cuenta banco EUR" | ✅ create_account | ✅ Necesario | Debe extraer type, name, currency |
| "asdfgh" | ❌ Baja confianza | ✅ GPT decide | intent=unknown → PERMISSION_DENIED |
| Error vector search | ❌ Fallo técnico | ✅ Fallback total | GPT trabaja sin sugerencias |

**Resumen**: Embeddings = detección rápida. GPT = extracción de datos + resolución de ambiguedad + fallback.

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

### Descripción de cada vértice (estado)

| Estado | Archivo | Responsabilidad |
|--------|---------|----------------|
| **IDLE** | `handlers/core/idle.js` | Estado inicial. Recibe el mensaje y transiciona a SESSION_LOADER. |
| **SESSION_LOADER** | `handlers/core/sessionLoader.js` | Busca usuario por teléfono, verifica sesión activa. Si no hay sesión → PERMISSION_DENIED. Si pide login → LOGIN_FLOW. Si sesión válida → CONTEXT_LOADER. |
| **LOGIN_FLOW** | `handlers/core/loginFlow.js` | Crea usuario (si nuevo) y sesión. Envía mensaje de bienvenida → DONE. |
| **PERMISSION_DENIED** | `handlers/core/permissionDenied.js` | Envía mensaje de denegación con lista de acciones posibles → DONE. |
| **CONTEXT_LOADER** | `handlers/core/contextLoader.js` | Carga cuentas y categorías del usuario desde BD. Si no tiene cuentas → DONE (pide crear una). Si todo OK → VECTOR_SEARCH. |
| **VECTOR_SEARCH** | `handlers/core/vectorSearch.js` | Embebe el mensaje del usuario y busca en knowledge_embeddings (4 búsquedas paralelas: intent, category, account, faq). Decide: fast path o RAG path. |
| **AI_INTERPRETING** | `handlers/core/aiInterpreting.js` | Envía mensaje a GPT con system prompt financiero + sugerencias RAG. Recibe intent + transacciones. Decide flujo → [FLOW] o PERMISSION_DENIED. |
| **BALANCE_FLOW** | `handlers/flows/balanceFlow.js` | Consulta saldo de todas las cuentas → DONE. |
| **TRANSACTION_FLOW** | `handlers/flows/transactionFlow.js` | Registra gasto o ingreso, actualiza balance → DONE. |
| **CREATE_ACCOUNT_FLOW** | `handlers/flows/createAccountFlow.js` | Crea nueva cuenta (banco/cash/inversion) → DONE. |
| **LIST_ACCOUNTS_FLOW** | `handlers/flows/listAccountsFlow.js` | Lista cuentas del usuario → DONE. |
| **LIST_TRANSACTIONS_FLOW** | `handlers/flows/listTransactionsFlow.js` | Lista últimas transacciones → DONE. |
| **STATISTICS_FLOW** | `handlers/flows/statisticsFlow.js` | Genera estadísticas de gastos → DONE. |
| **ERROR_RESPONSE** | `handlers/core/errorResponse.js` | Construye mensaje de error apropiado → DONE. |
| **DONE** | `handlers/core/done.js` | Envía respuesta final al usuario por Kapso o Twilio. Loguea historial de estados. |

### Descripción de cada arista (transición)

| Origen → Destino | Condición | Ejemplo |
|-------------------|-----------|---------|
| IDLE → SESSION_LOADER | Siempre | Cualquier mensaje entrante |
| SESSION_LOADER → LOGIN_FLOW | Usuario dice "login" | "login", "iniciar sesión" |
| SESSION_LOADER → PERMISSION_DENIED | Sin usuario o sin sesión | Primer mensaje sin login |
| SESSION_LOADER → CONTEXT_LOADER | Sesión activa válida | Usuario autenticado |
| CONTEXT_LOADER → VECTOR_SEARCH | Usuario tiene ≥1 cuenta | Tras cargar cuentas y categorías |
| CONTEXT_LOADER → DONE | Sin cuentas | "Debes crear al menos una cuenta" |
| VECTOR_SEARCH → DONE | FAQ score ≥ 0.65 | "hola", "ayuda", "gracias" → respuesta directa |
| VECTOR_SEARCH → [FLOW] | Intent simple ≥ 0.60 | "saldo" → BALANCE_FLOW sin GPT |
| VECTOR_SEARCH → AI_INTERPRETING | Score < 0.60 o intent transaccional | "café 3" → GPT extrae datos |
| VECTOR_SEARCH → AI_INTERPRETING | Error en embedding/RPC | Fallback sin sugerencias |
| AI_INTERPRETING → [FLOW] | Intent válido por GPT | expense → TRANSACTION_FLOW |
| AI_INTERPRETING → PERMISSION_DENIED | intent=unknown por GPT | "asdfgh" |
| AI_INTERPRETING → ERROR_RESPONSE | Error en llamada GPT | Fallo de OpenAI |
| [FLOW] → DONE | Siempre | Tras ejecutar lógica de negocio |
| PERMISSION_DENIED → DONE | Siempre | Tras enviar mensaje de denegación |
| ERROR_RESPONSE → DONE | Siempre | Tras construir mensaje de error |

### Umbrales de confianza vectorial (VECTOR_SEARCH)

| Tipo | Fast path (sin GPT) | RAG (hint a GPT) | Ignorar |
|------|---------------------|-------------------|---------|
| **FAQ** | ≥ 0.65 | — | < 0.40 |
| **Intent** | ≥ 0.60 (solo balance, list_accounts, list_transactions, statistics) | ≥ 0.40 | < 0.30 |
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
│   │   │   │   ├── embeddings.js     # Genera embedding del mensaje del usuario (runtime)
│   │   │   │   ├── interpret.js      # System prompt financiero + GPT con RAG context
│   │   │   │   └── openai.js         # Wrapper OpenAI API (chat completions)
│   │   │   ├── adapters/
│   │   │   │   ├── implementations/
│   │   │   │   │   ├── kapso/        # KapsoWhatsAppAdapter (canal principal)
│   │   │   │   │   └── supabase/     # Repositories + supabase client (expuesto para RPC)
│   │   │   │   └── repositories/     # Interfaces abstractas
│   │   │   ├── domain/
│   │   │   │   ├── entities/         # Account (con type), User, Session, Transaction
│   │   │   │   └── services/         # UserService, AccountService, VectorSearchService, etc.
│   │   │   ├── routes/
│   │   │   │   ├── kapso.js          # Webhook Kapso (principal) — parsea payload.message directo
│   │   │   │   ├── twilio.js         # Webhook Twilio (legacy)
│   │   │   │   └── auth.js           # Rutas de autenticación JWT
│   │   │   ├── state/
│   │   │   │   ├── stateMachine.js   # Clase StateMachine (estado + contexto + historial)
│   │   │   │   └── handlers/
│   │   │   │       ├── core/         # IDLE, SESSION_LOADER, CONTEXT_LOADER,
│   │   │   │       │                 # VECTOR_SEARCH, AI_INTERPRETING,
│   │   │   │       │                 # PERMISSION_DENIED, ERROR_RESPONSE, DONE
│   │   │   │       └── flows/        # BALANCE, TRANSACTION, CREATE_ACCOUNT,
│   │   │   │                         # LIST_ACCOUNTS, LIST_TRANSACTIONS, STATISTICS
│   │   │   ├── middleware/           # JWT auth middleware
│   │   │   └── utils/                # phone, twiml, errors, twilioClient, logger
│   │   ├── .env
│   │   └── index.js                  # Entry point — inicializa repos, services, routes
│   │
│   └── web/                          # Frontend Next.js (dashboard)
│
├── packages/
│   ├── database/
│   │   ├── schema.sql                # pgvector + knowledge_embeddings + match_embeddings RPC
│   │   └── seed.sql                  # Categorías + datos de prueba
│   │
│   ├── embeddings/                   # Pre-entrenamiento offline
│   │   ├── seed.json                 # 427 entries: categories, intents, FAQ, accounts
│   │   ├── generate_embeddings.py    # Lee seed.json → OpenAI → SQL + JSON
│   │   ├── insert_embeddings.py      # JSON → Supabase REST API (batches)
│   │   └── .env                      # OPENAI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
│   │
│   └── shared/                       # Tipos y constantes compartidas
│
├── infra/
│   ├── docker/
│   └── env/
│       └── .env.example
│
└── README.md
```

---

## Base de datos (Supabase / PostgreSQL + pgvector)

### Tablas

| Tabla | Descripción |
|-------|------------|
| users | Usuarios registrados (phone E.164) |
| sessions | Sesiones activas con TTL |
| accounts | Cuentas: banco, cash, inversion (con type, currency, balance) |
| categories | expense, income, investment |
| transactions | Movimientos financieros |
| investments | Inversiones |
| knowledge_embeddings | 427 vectores pre-entrenados (1536 dims, tipo: intent/category/faq/account) |

### Función RPC: match_embeddings

```sql
match_embeddings(query_embedding vector(1536), match_type text, match_threshold float, match_count int)
→ RETURNS TABLE(id, content, type, metadata, similarity)
```

Busca los K embeddings más similares usando distancia coseno con índice HNSW. Filtra por tipo y umbral.

---

## Canales de mensajería

| Canal | Estado | Notas |
|-------|--------|-------|
| **Kapso** (Meta Cloud API) | Principal | Formato: `{ message: { from, text, type } }`. NO usar normalizeWebhook. |
| **Twilio** | Legacy | Form-data con `Body`, `From`. TwiML responses. |

---

## Variables de entorno

### apps/api/.env
- SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
- OPENAI_API_KEY, OPENAI_MODEL
- KAPSO_API_KEY, KAPSO_PHONE_NUMBER_ID, KAPSO_WEBHOOK_VERIFY_TOKEN
- TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM (legacy)
- JWT_SECRET, JWT_EXPIRATION

### packages/embeddings/.env
- OPENAI_API_KEY
- SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

---

## Logs del flujo (desarrollo)

Cada estado emite logs con emoji para seguir la ejecución:

```
🟢 IDLE → Mensaje recibido, iniciando procesamiento
🔐 SESSION_LOADER → Verificando sesión
🔐 SESSION_LOADER → Sesión válida → CONTEXT_LOADER
📦 CONTEXT_LOADER → Cargando cuentas y categorías
📦 CONTEXT_LOADER → Contexto cargado → VECTOR_SEARCH
🔍 VECTOR_SEARCH → Embebiendo mensaje y buscando en knowledge_embeddings
🔢 Embedding generado (120ms, 1536 dims)
🔍 VECTOR_SEARCH → Resultados de búsqueda vectorial
⚡ VECTOR_SEARCH → FAST PATH: FAQ detectado (score ≥ 0.65) → DONE (sin IA)
⚡ VECTOR_SEARCH → FAST PATH: intent "balance" (score ≥ 0.60) → BALANCE_FLOW (sin IA)
🧠 VECTOR_SEARCH → RAG PATH: confianza media, pasando sugerencias a GPT → AI_INTERPRETING
🧠 VECTOR_SEARCH → SIN SUGERENCIAS: confianza baja → AI_INTERPRETING (GPT decide solo)
❌ VECTOR_SEARCH → ERROR en búsqueda vectorial, fallback a AI_INTERPRETING
🤖 AI_INTERPRETING → Enviando a GPT (con sugerencias RAG)
🤖 AI_INTERPRETING → GPT respondió: intent="expense" (450ms)
🤖 AI_INTERPRETING → Decisión: "expense" → TRANSACTION_FLOW
✅ DONE → Flujo completado (6 estados, fast path: faq)
```

---

## Reglas de trabajo para la IA

1. **Leer este documento** antes de generar cualquier código.
2. **Preguntar** en qué parte del sistema se trabaja si no está claro.
3. **Respetar la arquitectura**: state machine, services, repositories.
4. **No romper** el flujo de estados ni los umbrales de confianza sin discutirlo.
5. **Mantener logs** con emojis en cada handler para trazabilidad.
6. **Kapso**: parsear `payload.message` directo, NO usar `normalizeWebhook`.
7. **Account entity** tiene campo `type` (banco/cash/inversion) — siempre mapearlo.
