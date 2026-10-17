# Aegis Research Agent

A research/summarizer agent — a real backend that searches the web and
synthesizes a structured summary — paired with a polished dashboard
frontend that streams the agent's progress live.

Runs entirely on **free tiers**: DuckDuckGo search (no key needed) +
Google Gemini's free API tier (no card required).

## How it works (the actual agent architecture)

This is deliberately split into two separate steps, which is the real
definition of an "agent" — an AI that uses a tool and reasons over what
the tool returns, rather than one black-box call:

1. **TOOL STEP** — plain Python code (`search_web` in `agent.py`) searches
   the real web via DuckDuckGo. No AI involved here at all, just fetching.
2. **REASONING STEP** — Gemini reads what was found and writes a
   structured, grounded summary from it — told explicitly not to invent
   facts beyond what the search returned.

## Setup

1. Get a free Gemini API key (no card required) at
   [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. In the `backend/` folder:
   ```bash
   pip install -r requirements.txt
   export GEMINI_API_KEY=your-key-here
   python server.py
   ```
3. Open `index.html` in your browser (it calls `http://localhost:5000`)
4. Type a real topic, hit "Run Agent," and watch it actually search and reason

## Known limitations (worth knowing, not hiding)

- **DuckDuckGo search is unofficial** — there's no official API, so this
  uses the `ddgs` library, which scrapes DuckDuckGo's own search pages.
  It works well from a normal home/office internet connection. If you
  later deploy this backend to a cloud host (Render, Railway, etc.),
  DuckDuckGo has been known to rate-limit or block requests from
  datacenter IP ranges specifically — this is a documented issue with
  this approach, not a bug in this code. If that happens, options are:
  switching to a paid search API (Google Custom Search, Tavily, Bing),
  or adding retry/backoff and a fallback source.
- **Gemini's free tier has rate limits** — historically quite low without
  billing enabled (roughly 10 requests/minute on some models at time of
  writing). Fine for building and demoing, not for real traffic. Check
  your current limits in the AI Studio dashboard, since Google adjusts
  these periodically.
- **Trust scores are placeholder logic** (`_trust_score` in `agent.py`) —
  based on result order, not a real credibility model. If you want this
  to be genuinely meaningful, that's the piece to replace with real
  domain-reputation signals.
- **CORS is wide open** (`CORS(app)` with no restrictions) — fine for a
  local demo, not fine to ship as-is to production.
- **No rate limiting or auth** on the endpoint — add basic protection
  before exposing this publicly.
- The live search + Gemini call couldn't be tested end-to-end in the
  environment this was built in (its own network is locked to a fixed
  domain allowlist that doesn't include DuckDuckGo or Google's API) — the
  code is correct against the current library APIs and was unit-tested
  against mocked responses, but test it with your own key on a normal
  connection before demoing it to anyone.

## Stack

- Backend: Python, Flask, `ddgs` (DuckDuckGo search), `google-genai` (Gemini)
- Frontend: Vanilla HTML/CSS/JS, Server-Sent Events (no framework, no build step)
