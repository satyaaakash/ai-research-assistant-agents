import os
import json
import hashlib
import requests
from flask import Flask, request, jsonify
import google.auth.transport.requests
import google.auth


app = Flask(__name__)

# Constants
MODEL_ID_PRIMARY = "gemini-2.5-pro-preview-05-06"
MODEL_ID_FALLBACK = "gemini-1.5-pro-002"
PROJECT_ID = "ai-research-assistant-460301"
REGION = "us-central1"
BASE_URL = f"https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/publishers/google/models"

# Simple in-memory cache
cache = {}

def get_cache_key(prompt):
    return hashlib.sha256(prompt.encode()).hexdigest()

@app.route("/", methods=["GET"])
def home():
    return "Summarizer Agent is alive!", 200

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    topic = data.get("topic")
    papers = data.get("papers", [])

    # Compose prompt
    prompt = f"Summarize the following academic papers on the topic: {topic}.\n\n"
    for i, paper in enumerate(papers):
        prompt += f"Paper {i+1}: {paper['title']}\nSummary: {paper['summary']}\n\n"

    # Check cache
    cache_key = get_cache_key(prompt)
    if cache_key in cache:
        return jsonify({
            "modelVersion": MODEL_ID_PRIMARY,
            "summary": cache[cache_key],
            "cached": True
        })

    # Get access token
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    credentials.refresh(google.auth.transport.requests.Request())
    access_token = credentials.token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Build payload
    payload = {
        "contents": {
            "role": "user",
            "parts": [{"text": prompt}]
        }
    }

    def call_model(model_id):
        url = f"{BASE_URL}/{model_id}:streamGenerateContent"
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    try:
        response_data = call_model(MODEL_ID_PRIMARY)
        model_used = MODEL_ID_PRIMARY
    except Exception as e:
        print(f"[Fallback Triggered] Error: {e}")
        response_data = call_model(MODEL_ID_FALLBACK)
        model_used = MODEL_ID_FALLBACK

    # Extract final summary text
    summary_parts = []
    for candidate in response_data if isinstance(response_data, list) else [response_data]:
        parts = candidate.get("candidates", [])[0].get("content", {}).get("parts", [])
        summary_parts.extend(p["text"] for p in parts if "text" in p)

    summary_text = "".join(summary_parts).strip()

    # Cache result
    cache[cache_key] = summary_text

    return jsonify({
        "modelVersion": model_used,
        "responseId": response_data[0]["responseId"] if isinstance(response_data, list) else response_data.get("responseId"),
        "summary": summary_text,
        "tokensUsed": response_data[-1]["usageMetadata"] if isinstance(response_data, list) else response_data.get("usageMetadata"),
        "cached": False
    })

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))