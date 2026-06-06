# Demo Script — Multilingual Ticket Translator (5–7 Minutes)

---

## Pre-Demo Setup (Before You Present)

- [ ] Server running: `python backend/app.py`
- [ ] Browser open at `http://localhost:5000` (or `frontend/index.html` served locally)
- [ ] `.env` file has a valid `GEMINI_API_KEY`
- [ ] Sample tickets ready (from `sample_data/sample_inputs.json`)

---

## Minute 0:30 — Introduction

> "This is the **Multilingual Ticket Translator** — an AI-powered customer support tool that accepts tickets in any language, automatically detects the language, translates it to English, and uses Gemini AI to analyse the issue and suggest a professional response.
>
> The entire stack is free and open-source: Python Flask backend, vanilla HTML/CSS/JS frontend, and Google Gemini's free tier for AI."

---

## Minute 1:00 — Architecture Walkthrough (Whiteboard / Slide)

Point to architecture diagram:

> "The system has 4 pipeline steps:
> 1. **Input** — customer types a ticket in any language
> 2. **Detect** — offline `langdetect` library identifies the language
> 3. **Translate** — Gemini API translates it to English
> 4. **Analyse** — Gemini returns structured JSON: category, priority, sentiment, and a suggested reply"

---

## Minute 2:00 — Live Demo: Tamil Ticket

1. Click the **Tamil** example button — the text `எனது இணையம் வேலை செய்யவில்லை` fills the box.
2. Click **Translate & Analyse**.
3. Watch the pipeline animation progress through the 4 steps.
4. Point out the result:
   - **Language detected**: Tamil
   - **Translation**: "My internet is not working"
   - **Category**: Network Issue
   - **Priority**: Medium (explain the priority rules)
   - **Sentiment**: Negative
   - **Suggested Response**: ready to send

> "The agent never needs to know Tamil. They read the English summary and send the suggested response — the system handled everything else."

---

## Minute 3:00 — Live Demo: Hindi Ticket

1. Click the **Hindi** example button.
2. Submit and show the result — notice sentiment may be **Very Negative** due to "बहुत परेशानी" (a lot of trouble).
3. Explain how sentiment drives priority escalation.

---

## Minute 3:45 — Live Demo: Manual Entry

1. Clear the form.
2. Type: `Je ne peux pas me connecter à mon compte` (French).
3. Submit and show French detection + Account Issue category.

> "Completely hands-free — the agent doesn't need to set any language option. It's all automatic."

---

## Minute 4:30 — Code Walkthrough (Editor)

Briefly show:

1. `backend/services/ticket_service.py` — the 4-step pipeline in ~30 lines
2. `backend/services/analysis_service.py` — the structured Gemini prompt
3. `backend/services/gemini_service.py` — the thin SDK wrapper

> "The AI Agent Loop is this `process_ticket_pipeline` function. Each step hands its output to the next — classic pipeline architecture."

---

## Minute 5:15 — Tests

```bash
cd multilingual-ticket-translator
pytest tests/ -v
```

Show 24 tests passing — validators, translation service, analysis service, API endpoints.

---

## Minute 5:45 — Future Enhancements

> "If I had more time, I'd add:
> - Ticket history dashboard
> - Agent reply translation (reply in English, customer receives their language)
> - Multi-turn conversation support using Gemini's chat API
> - Batch CSV processing
> - Authentication with role-based access"

---

## Minute 6:15 — Q&A

Be ready to answer:
- **"Why Gemini over GPT?"** — Free tier, generous quota, single API for translation + analysis
- **"Why langdetect for detection?"** — Offline, no quota, fast, reliable for 50+ languages
- **"How does the structured output work?"** — Prompt engineering with explicit JSON schema + validation/normalisation layer
- **"Is it production-ready?"** — Pipeline is solid; would need auth, rate limiting, and a database for production
