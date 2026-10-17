"""
Aegis Research Agent — server.

Exposes POST /api/research which streams Server-Sent Events (SSE) as the
agent works, then a final "result" event with the structured summary.

Run:
    export ANTHROPIC_API_KEY=your-key-here
    pip install -r requirements.txt
    python server.py

Then open the frontend (index.html) — it calls http://localhost:5000/api/research.
"""

import json
from flask import Flask, request, Response, jsonify
from flask_cors import CORS

from agent import run_research_stream

app = Flask(__name__)
CORS(app)  # allow the static frontend (opened via file:// or another port) to call this


@app.route("/api/research", methods=["POST"])
def research():
    data = request.get_json(silent=True) or {}
    topic = (data.get("topic") or "").strip()

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    def generate():
        try:
            for event in run_research_stream(topic):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as exc:  # noqa: BLE001 — never let the stream die silently
            yield f"data: {json.dumps({'type': 'error', 'text': str(exc)})}\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
