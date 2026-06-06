# Architecture — Multilingual Ticket Translator

## Text Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Browser)                           │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │   index.html + style.css + app.js (Vanilla JS + Bootstrap)  │   │
│  │                                                             │   │
│  │   [Ticket Input Form]  ──── fetch() ────►  [Results Panel]  │   │
│  └──────────────────────────────┬──────────────────────────────┘   │
└─────────────────────────────────┼───────────────────────────────────┘
                                  │ HTTP POST /api/process-ticket
                                  │ JSON body: { ticket_text: "..." }
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       BACKEND (Python Flask)                        │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      Flask App (app.py)                      │  │
│  │                     CORS + Error Handlers                    │  │
│  └───────────────────────────┬──────────────────────────────────┘  │
│                              │                                      │
│  ┌───────────────────────────▼──────────────────────────────────┐  │
│  │              Routes Layer (ticket_routes.py)                  │  │
│  │   POST /process-ticket  │  POST /translate-only               │  │
│  │   GET /supported-langs  │  GET /health                        │  │
│  └───────────────────────────┬──────────────────────────────────┘  │
│                              │                                      │
│  ┌───────────────────────────▼──────────────────────────────────┐  │
│  │            Ticket Service — AI AGENT PIPELINE                 │  │
│  │                                                              │  │
│  │   INPUT                                                      │  │
│  │     │                                                        │  │
│  │     ▼                                                        │  │
│  │  ┌─────────────────────────────────────────────────────────┐ │  │
│  │  │  STEP 1: Language Detection (langdetect — offline)      │ │  │
│  │  └──────────────────────┬──────────────────────────────────┘ │  │
│  │                         │ detected_lang (e.g. "ta")           │  │
│  │                         ▼                                     │  │
│  │  ┌─────────────────────────────────────────────────────────┐ │  │
│  │  │  STEP 2: Translation (Gemini API → English)             │ │  │
│  │  └──────────────────────┬──────────────────────────────────┘ │  │
│  │                         │ english_text                        │  │
│  │                         ▼                                     │  │
│  │  ┌─────────────────────────────────────────────────────────┐ │  │
│  │  │  STEP 3: AI Analysis (Gemini API)                       │ │  │
│  │  │   → Structured JSON: category, priority, summary,       │ │  │
│  │  │     sentiment, response, keywords                       │ │  │
│  │  └──────────────────────┬──────────────────────────────────┘ │  │
│  │                         │                                     │  │
│  │                         ▼                                     │  │
│  │  ┌─────────────────────────────────────────────────────────┐ │  │
│  │  │  STEP 4: Assemble & Return Final Output                 │ │  │
│  │  └─────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Utils: validators.py    Services: gemini_service.py         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │ HTTPS requests (google-generativeai SDK)
                                    ▼
┌───────────────────────────────────────────────────────────────────┐
│                    EXTERNAL AI: Google Gemini API                  │
│                  (gemini-1.5-flash — Free Tier)                    │
│                                                                    │
│   Used for:                                                        │
│   1. Translation: [source lang text] → [English text]             │
│   2. Analysis: [English text] → [structured JSON]                  │
└───────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────┐
│                  OFFLINE LIBRARY: langdetect                       │
│                  (no API key, no network call)                     │
│                                                                    │
│   Input: raw text → Output: BCP-47 language code                  │
└───────────────────────────────────────────────────────────────────┘
```

---

## Component Responsibilities

| Component              | Responsibility                                                        |
|------------------------|-----------------------------------------------------------------------|
| `frontend/index.html`  | Single-page UI with Bootstrap — input form + results panel           |
| `frontend/js/app.js`   | Fetch API calls, progressive loading animation, result rendering     |
| `app.py`               | Flask factory, CORS, blueprint registration, error handlers           |
| `ticket_routes.py`     | Route definitions, request parsing, calls service layer              |
| `ticket_service.py`    | AI Agent Loop orchestrator — coordinates all pipeline steps          |
| `translation_service.py`| Language detection (langdetect) + Gemini translation                |
| `analysis_service.py`  | Builds Gemini prompt, parses & validates structured JSON response    |
| `gemini_service.py`    | Thin Gemini SDK wrapper — single point for API key + model config    |
| `validators.py`        | Input validation — shared across all route handlers                  |

---

## Data Flow

```
Customer types ticket in any language
         │
         ▼
[Frontend] POST /api/process-ticket { "ticket_text": "..." }
         │
         ▼
[Flask Route] validate input
         │
         ▼
[ticket_service.process_ticket_pipeline()]
   ├── detect_language(text)          → "ta"
   ├── translate_to_english(text, "ta") → "My internet is not working"
   ├── analyze_ticket(english_text)   → { category, priority, ... }
   └── assemble result dict
         │
         ▼
[Frontend] renders colour-coded result cards
```

---

## Design Decisions

1. **Single AI provider (Gemini)** — handles both translation and analysis. Reduces complexity and keeps the project within free-tier limits.

2. **Offline language detection (langdetect)** — no API quota consumed for detection. Fast, reliable for 50+ languages.

3. **Structured prompt engineering** — Gemini is instructed to return strict JSON with explicit field names and allowed values. A fallback parser handles markdown-wrapped responses.

4. **Graceful degradation** — translation failures return the original text; analysis failures return sensible defaults. The pipeline never returns a 500 for partial AI failure.

5. **Flask application factory** — `create_app()` pattern makes the app testable without starting a server.
