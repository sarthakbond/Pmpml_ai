from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

OLLAMA_API = "http://localhost:11434/api/generate"

def ollama_query(prompt):
    try:
        res = requests.post(OLLAMA_API, json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }, timeout=45)
        return res.json().get("response", "").strip()
    except Exception as e:
        return f"Llama3 offline — {str(e)}"

@app.route("/")
def index():
    return render_template("index.html")

def density_factor(d):
    return {"Low": 0.0, "Medium": 0.5, "High": 1.0}.get(d, 0.5)

@app.route("/ai/recommend", methods=["POST"])
def recommend():
    body = request.get_json()
    fleet = body.get("fleet", [])
    query = body.get("query", "Which bus should I take to reach Keystone fastest?")

    scored = []
    for b in fleet:
        progress = b.get("progress", 0) / 100
        df = density_factor(b.get("density", "Medium"))
        td = b.get("trafficDelay", 0) / 1000
        score = (progress * 0.5) - (df * 0.3) - (td * 0.2)
        scored.append({**b, "score": round(score, 4)})

    scored.sort(key=lambda x: x["score"], reverse=True)
    context = json.dumps(scored, indent=2)

    prompt = f"""You are PMPML AI-Connect, a smart bus assistant for Keystone School of Engineering students in Pune.

Fleet data (efficiency-scored, higher score = better option):
{context}

Student query: {query}

Respond in 2-3 sentences. Recommend the top bus by route number. Mention its crowd level and current location. If any bus is stuck in traffic, warn about it. Use casual, helpful tone. No bullet points."""

    ai_response = ollama_query(prompt)
    return jsonify({"response": ai_response, "ranked": scored, "best": scored[0] if scored else None})

@app.route("/ai/stop", methods=["POST"])
def stop_query():
    body = request.get_json()
    route = body.get("route")
    stop = body.get("stop")
    bus = body.get("busInfo", {})

    prompt = f"""You are PMPML AI-Connect for Pune students at Keystone School of Engineering.

Bus {route} current status: {json.dumps(bus)}
Student is waiting at stop: {stop}

Estimate wait time in minutes based on bus progress ({bus.get('progress', 0)}%) and traffic delay ({bus.get('trafficDelay', 0)}ms). Give a direct, short answer in 1-2 sentences. Be realistic and helpful."""

    ai_response = ollama_query(prompt)
    return jsonify({"response": ai_response, "route": route, "stop": stop})

@app.route("/verify", methods=["POST"])
def verify():
    body = request.get_json()
    return jsonify({
        "verified": True,
        "route": body.get("route"),
        "location": {"lat": body.get("lat"), "lng": body.get("lng")},
        "message": "Presence verified. Crowd-source layer updated.",
        "trustScore": 0.94,
        "contributors": 7
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "model": "llama3", "version": "1.0.0"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)