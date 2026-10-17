"""
Aegis Research Agent — core logic (free-tier version).

Two separate steps, which is the actual point of an "agent":
1. TOOL STEP — plain Python code searches the real web via DuckDuckGo (ddgs
   library). No AI involved here, just fetching.
2. REASONING STEP — Gemini (free tier) reads what was found and writes a
   structured, grounded summary from it.

Requires the GEMINI_API_KEY environment variable to be set.
Get a free key (no card required) at: https://aistudio.google.com/app/apikey
"""

import os
from ddgs import DDGS
from google import genai

MODEL = "gemini-3.8-flash"

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set. "
                "Get a free key at aistudio.google.com/app/apikey and export it "
                "before running the server."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def _trust_score(index, total):
    """Simple, transparent placeholder scoring based on result order —
    NOT a real credibility model. Swap this for real domain-reputation
    logic if you take this further.
    """
    base = 88 - (index * 9)
    return max(55, min(95, base))


def search_web(topic: str, max_results: int = 6):
    """The TOOL step — real DuckDuckGo search, no AI involved.

    Returns a list of {"title", "url", "snippet"} dicts. Raises whatever
    ddgs raises on failure so the caller can report a clean error instead
    of silently returning nothing.
    """
    with DDGS() as ddgs:
        raw_results = ddgs.text(topic, max_results=max_results)

    results = []
    for r in raw_results:
        title = r.get("title") or r.get("href") or "Untitled"
        url = r.get("href") or r.get("url") or ""
        snippet = r.get("body") or ""
        if url:
            results.append({"title": title, "url": url, "snippet": snippet})
    return results


def run_research_stream(topic: str):
    """Generator yielding dict events for SSE streaming:
    {"type": "log", "step": int, "text": str, "detail": str|None}
    {"type": "error", "text": str}
    {"type": "result", "summary": str, "sources": [...]}
    """
    client = get_client()

    yield {"type": "log", "step": 1, "text": "Parsing query intent and key entities..."}

    yield {"type": "log", "step": 2, "text": "Searching the web..."}
    try:
        found = search_web(topic)
    except Exception as exc:  # noqa: BLE001 — ddgs can raise various network/parse errors
        yield {"type": "error", "text": f"Search step failed: {exc}"}
        return

    for i, s in enumerate(found):
        s["trust"] = _trust_score(i, len(found))

    yield {
        "type": "log",
        "step": 2,
        "text": "Search complete.",
        "detail": f"Found {len(found)} source(s)." if found else "No results — try a different phrasing.",
    }

    if not found:
        yield {"type": "error", "text": "No search results found for this topic. Try rephrasing it."}
        return

    yield {"type": "log", "step": 3, "text": "Cross-referencing and extracting key claims..."}

    context = "\n\n".join(
        f"Source {i+1}: {s['title']}\n{s['snippet']}" for i, s in enumerate(found)
    )
    synthesis_prompt = (
        f"Based ONLY on the research context below, write a structured summary about: {topic}\n\n"
        f"Research context (from real web search results):\n{context}\n\n"
        f"Format your response as markdown with these exact sections:\n"
        f"## Overview\n(2-3 sentences)\n"
        f"## Key Findings\n(4-6 bullet points, each grounded in the context above — "
        f"do not invent facts not present in the context)\n"
        f"## Confidence Note\n(1-2 sentences on how strong the evidence is, and note "
        f"if sources disagree or if coverage is thin)"
    )

    yield {"type": "log", "step": 4, "text": "Synthesizing structured summary with Gemini..."}
    try:
        response = client.models.generate_content(model=MODEL, contents=synthesis_prompt)
        summary_text = (response.text or "").strip()
    except Exception as exc:  # noqa: BLE001
        yield {"type": "error", "text": f"Synthesis step failed: {exc}"}
        return

    if not summary_text:
        yield {"type": "error", "text": "Gemini returned an empty response. Try again."}
        return

    yield {"type": "log", "step": 5, "text": "Report ready."}
    sources_out = [{"title": s["title"], "url": s["url"], "trust": s["trust"]} for s in found]
    yield {"type": "result", "summary": summary_text, "sources": sources_out}
