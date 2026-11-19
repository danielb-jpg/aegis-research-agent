# Aegis Research Agent

A research/summarizer agent: a real backend that searches the web and synthesizes a structured summary, paired with a dashboard frontend that streams the agent's progress live.

Runs entirely on **free tiers**: DuckDuckGo search (no key needed) + Google Gemini's free API tier (no card required).

## Screenshots

**Live reasoning log:** the dashboard streams each step of the agent as it runs.

![Dashboard with the agent's live reasoning steps](aegis-research-agent/Screenshots/aegis-dashboard.png)

**Structured summary:** Overview, Key Findings and a Confidence Note.

![Structured summary](aegis-research-agent/Screenshots/aegis-summary.png)

**Sources consulted:** each result is shown with its domain and a ranking score.

![Sources consulted](aegis-research-agent/Screenshots/aegis-sources.png)

## How it works

The agent is split into two separate steps. An agent is an AI that uses a tool and reasons over what the tool returns, not one black-box call:

1. **TOOL STEP**: plain Python code (`search_web` in `agent.py`) searches the real web via DuckDuckGo. No AI involved here, just fetching.
2. **REASONING STEP**: Gemini reads what was found and writes a structured, grounded summary (Overview, Key Findings, Confidence Note). It is told explicitly not to invent facts beyond what the search returned.

## Project structure

```
aegis-research-agent/
├── backend/
├── Screenshots/
├── index.html
└── start.bat
```

## Setup

1. Get a free Gemini API key (no card required) at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Open a terminal in the `aegis-research-agent/backend` folder and run:

   ```bash
   pip install -r requirements.txt
   ```

   Set your key:

   - Windows (Command Prompt): `set GEMINI_API_KEY=your-key-here`
   - Windows (PowerShell): `$env:GEMINI_API_KEY="your-key-here"`
   - Mac/Linux: `export GEMINI_API_KEY=your-key-here`

   Then start the server:

   ```bash
   python server.py
   ```

3. Open `aegis-research-agent/index.html` in your browser (it calls `http://localhost:5000`)
4. Type a topic, hit "Run Agent," and watch it search and reason

## Known limitations

- **DuckDuckGo search is unofficial.** There is no official API, so this uses the `ddgs` library, which scrapes DuckDuckGo's search pages. It works well from a normal home/office connection. If the backend is deployed to a cloud host (Render, Railway, etc.), DuckDuckGo may rate-limit or block datacenter IPs. Options then: a paid search API (Google Custom Search, Tavily, Bing), or retry/backoff with a fallback source.
- **Gemini's free tier has rate limits.** They're low without billing enabled (roughly 10 requests/minute on some models at the time of writing). Fine for building and demoing, not for real traffic.
- **The source scores are a ranking, not a credibility model.** `_trust_score` in `agent.py` is based on result order. The next step is replacing it with real domain-reputation signals.
- **CORS is wide open** (`CORS(app)` with no restrictions). Fine for a local demo, not for production.
- **No rate limiting or auth** on the endpoint. Add basic protection before exposing this publicly.

## Testing

Tested locally on Windows with a Gemini free-tier key: live DuckDuckGo search returned multiple sources and Gemini produced a grounded summary, as shown in the screenshots above.

## Stack

- Backend: Python, Flask, `ddgs` (DuckDuckGo search), `google-genai` (Gemini)
- Frontend: Vanilla HTML/CSS/JS, Server-Sent Events (no framework, no build step)
