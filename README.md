# Multilingual Ticket Translator

> An AI-powered customer support tool that accepts tickets in any language, automatically detects the language, translates to English, and uses Gemini AI to analyse the issue and generate a structured response.

---

## Live Demo Flow

```
Customer writes in Tamil → System detects Tamil → Translates to English
→ Gemini analyses → Returns: Category + Priority + Summary + Sentiment + Suggested Reply
```

---

## Tech Stack

| Layer      | Technology                                    |
|------------|-----------------------------------------------|
| Frontend   | HTML5, CSS3, Bootstrap 5, Vanilla JavaScript  |
| Backend    | Python 3.10+, Flask 3, Flask-CORS             |
| AI         | Google Gemini API (gemini-1.5-flash, free)    |
| Detection  | langdetect (offline, no API key)              |
| Testing    | pytest + pytest-flask                         |

---

## Project Structure

```
multilingual-ticket-translator/
│
├── frontend/
│   ├── index.html          # Single-page UI
│   ├── css/style.css       # Custom styles
│   └── js/app.js           # Fetch API + result rendering
│
├── backend/
│   ├── app.py              # Flask application factory
│   ├── routes/
│   │   ├── ticket_routes.py
│   │   └── health_routes.py
│   ├── services/
│   │   ├── ticket_service.py        # AI Agent Pipeline orchestrator
│   │   ├── translation_service.py   # Language detection + translation
│   │   ├── analysis_service.py      # Gemini analysis + JSON parsing
│   │   └── gemini_service.py        # Gemini SDK wrapper
│   └── utils/
│       └── validators.py            # Input validation
│
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_validators.py
│   ├── test_translation_service.py
│   ├── test_analysis_service.py
│   └── test_api_endpoints.py
│
├── sample_data/
│   ├── sample_inputs.json
│   ├── sample_outputs.json
│   └── sample_tickets.csv
│
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── ARCHITECTURE.md
│   └── DEMO_SCRIPT.md
│
├── requirements.txt
├── .env.example
├── AI_USAGE_NOTE.md
└── README.md
```

---

## Quick Start

### 1. Clone and set up

```bash
git clone https://github.com/your-username/multilingual-ticket-translator.git
cd multilingual-ticket-translator

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_key_here
```

Get a free key at: https://aistudio.google.com/app/apikey

### 3. Start the backend

```bash
cd backend
python app.py
```

Server starts at `http://localhost:5000`

### 4. Open the frontend

Open `frontend/index.html` in your browser, or serve it with any static server:

```bash
# Python simple server from project root
python -m http.server 3000 --directory frontend
# Then open http://localhost:3000
```

---

## Running Tests

```bash
# From project root
pytest tests/ -v
```

Expected output: **24 tests passing**

```
tests/test_health.py::test_health_returns_200               PASSED
tests/test_validators.py::test_valid_input                  PASSED
tests/test_validators.py::test_missing_ticket_text_key      PASSED
tests/test_validators.py::test_empty_ticket_text            PASSED
tests/test_validators.py::test_none_body                    PASSED
tests/test_validators.py::test_text_exceeds_max_length      PASSED
tests/test_validators.py::test_non_string_ticket_text       PASSED
tests/test_translation_service.py::test_detect_english      PASSED
...
```

---

## API Endpoints

| Method | Endpoint                    | Description                            |
|--------|-----------------------------|----------------------------------------|
| GET    | /api/health                 | Health check                           |
| POST   | /api/process-ticket         | Full AI pipeline (detect+translate+AI) |
| POST   | /api/translate-only         | Detect & translate (no AI analysis)    |
| GET    | /api/supported-languages    | List of supported input languages      |

Full documentation: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

---

## Example

**Input (Tamil ticket)**
```json
POST /api/process-ticket
{
  "ticket_text": "எனது இணையம் வேலை செய்யவில்லை"
}
```

**Output**
```json
{
  "success": true,
  "data": {
    "original_text": "எனது இணையம் வேலை செய்யவில்லை",
    "detected_language": "ta",
    "language_name": "Tamil",
    "translation": "My internet is not working",
    "category": "Network Issue",
    "priority": "Medium",
    "summary": "Customer reports that their internet connection is not functioning.",
    "sentiment": "Negative",
    "response": "We are sorry to hear about your internet issue. Our team is investigating.",
    "keywords": ["internet", "connectivity", "network"],
    "processing_time_ms": 1842
  }
}
```

---

## AI Agent Loop

```
User Input (any language)
    │
    ▼  [langdetect — offline]
Detect Language
    │
    ▼  [Gemini API]
Translate → English
    │
    ▼  [Gemini API + structured prompt]
AI Analysis
    │  category · priority · summary · sentiment · keywords
    ▼
Generate Suggested Response
    │
    ▼
Structured JSON Output
```

---

## Supported Languages (Detection)

Tamil, Hindi, English, French, German, Spanish, Arabic, Chinese, Japanese, Portuguese, Russian, Korean, Italian, Dutch, Turkish, Vietnamese, Thai, Indonesian, Malay — and more via `langdetect`.

---

## Future Enhancements

- [ ] Ticket history dashboard with charts
- [ ] Agent reply translation (reply in English → send in customer's language)
- [ ] Multi-turn conversation using Gemini's chat API
- [ ] Batch processing from CSV upload
- [ ] Authentication + role-based access (Admin / Agent)
- [ ] Redis caching for repeated translations
- [ ] Export results as PDF report
- [ ] Webhook for real-time ticket ingestion

---

## License

MIT

---

## Acknowledgements

- [Google Gemini](https://ai.google.dev/) — AI translation and analysis
- [langdetect](https://github.com/Mimino666/langdetect) — Offline language detection
- [Bootstrap](https://getbootstrap.com/) — Frontend UI framework
- [Flask](https://flask.palletsprojects.com/) — Backend web framework
