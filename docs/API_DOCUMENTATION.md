# API Documentation — Multilingual Ticket Translator

Base URL: `http://localhost:5000/api`

---

## Endpoints

### 1. Health Check

**GET** `/api/health`

Verifies the API is running.

**Response 200**
```json
{
  "success": true,
  "message": "Multilingual Ticket Translator API is running"
}
```

---

### 2. Process Ticket (Full AI Pipeline)

**POST** `/api/process-ticket`

Runs the complete AI Agent Loop: detect → translate → analyse → respond.

**Request Headers**
```
Content-Type: application/json
```

**Request Body**
```json
{
  "ticket_text": "எனது இணையம் வேலை செய்யவில்லை"
}
```

| Field         | Type   | Required | Max Length | Description              |
|---------------|--------|----------|------------|--------------------------|
| `ticket_text` | string | Yes      | 5000 chars | Raw customer ticket text |

**Response 200**
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
    "summary": "Customer reports internet connectivity issue.",
    "sentiment": "Negative",
    "response": "We are investigating the issue and will update you shortly.",
    "keywords": ["internet", "connectivity", "network"],
    "processing_time_ms": 1842
  }
}
```

**Response 400 — Validation Error**
```json
{
  "success": false,
  "error": "Missing required field: 'ticket_text'."
}
```

**Response 500 — Server Error**
```json
{
  "success": false,
  "error": "Processing failed: <details>"
}
```

**Field Descriptions**

| Field                | Type     | Description                                      |
|----------------------|----------|--------------------------------------------------|
| `original_text`      | string   | Echo of the customer's input                     |
| `detected_language`  | string   | BCP-47 language code (e.g., "ta", "hi", "fr")    |
| `language_name`      | string   | Human-readable language name                     |
| `translation`        | string   | English translation of the ticket                |
| `category`           | string   | Issue category (see values below)                |
| `priority`           | string   | Low / Medium / High / Critical                   |
| `summary`            | string   | One-sentence AI-generated summary                |
| `sentiment`          | string   | Customer tone: Positive/Neutral/Negative/Very Negative |
| `response`           | string   | AI-suggested agent reply                         |
| `keywords`           | string[] | Up to 5 extracted keywords                       |
| `processing_time_ms` | integer  | End-to-end pipeline time in milliseconds         |

**Category Values**
- Network Issue
- Billing Issue
- Account Issue
- Technical Support
- Hardware Issue
- Software Issue
- Shipping Issue
- Product Issue
- Service Issue
- Security Issue
- General Inquiry
- Other

---

### 3. Translate Only

**POST** `/api/translate-only`

Detects language and translates to English without AI analysis. Fast utility endpoint.

**Request Body**
```json
{
  "ticket_text": "Je ne peux pas accéder à mon compte"
}
```

**Response 200**
```json
{
  "success": true,
  "data": {
    "original_text": "Je ne peux pas accéder à mon compte",
    "detected_language": "fr",
    "english_translation": "I cannot access my account"
  }
}
```

---

### 4. Supported Languages

**GET** `/api/supported-languages`

Returns all languages the system can detect and translate.

**Response 200**
```json
{
  "success": true,
  "data": [
    { "code": "ta", "name": "Tamil" },
    { "code": "hi", "name": "Hindi" },
    { "code": "en", "name": "English" },
    { "code": "fr", "name": "French" },
    { "code": "de", "name": "German" },
    { "code": "es", "name": "Spanish" },
    { "code": "ar", "name": "Arabic" },
    { "code": "zh", "name": "Chinese" },
    { "code": "ja", "name": "Japanese" },
    { "code": "pt", "name": "Portuguese" },
    { "code": "ru", "name": "Russian" },
    { "code": "ko", "name": "Korean" }
  ]
}
```

---

## Error Codes

| HTTP Status | Meaning                                          |
|-------------|--------------------------------------------------|
| 200         | Success                                          |
| 400         | Bad request — validation failed                  |
| 404         | Route not found                                  |
| 500         | Internal server error (AI or unexpected failure) |

---

## cURL Examples

```bash
# Health check
curl http://localhost:5000/api/health

# Process a Tamil ticket
curl -X POST http://localhost:5000/api/process-ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_text": "எனது இணையம் வேலை செய்யவில்லை"}'

# Translate only
curl -X POST http://localhost:5000/api/translate-only \
  -H "Content-Type: application/json" \
  -d '{"ticket_text": "Ich kann nicht bezahlen"}'

# Supported languages
curl http://localhost:5000/api/supported-languages
```
