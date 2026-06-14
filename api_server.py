# api_server.py
"""
GrantMatcher AI - API Server for React Frontend
Run with: USE_MOCK=true python api_server.py
"""

import os
import subprocess
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- Import your existing logic directly ---
from retrieval.semantic_search import semantic_search
from llm.chain import run_chain

app = Flask(__name__)
CORS(app)  # Allow React (port 5173) to talk to Flask (port 8000)

# --- Config ---
USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"
OLLAMA_URL = "http://localhost:11434"

# --- Mock Data (for testing UI without LLM) ---
MOCK_GRANTS = [
	{   "id": 1,
		"title": "Community Health Outreach Grant",
		"organization": "Health Foundation",
		"field": "Health",
		"source": "manual",
		"deadline": "2026-12-31",
		"min_amount": 10000,
		"max_amount": 50000,
		"eligibility": "Nonprofits serving urban communities",
		"description": "Support for community-based health outreach programs focusing on preventive care and education.",
		"url": "https://example.org/grants/community-health-outreach"
	},
	{
        "id": 2,
		"title": "STEM Education Grant for K-12",
		"organization": "Education Trust",
		"field": "Education",
		"source": "manual",
		"deadline": "2026-09-30",
		"min_amount": 5000,
		"max_amount": 20000,
		"eligibility": "Schools and non-profit educational organizations",
		"description": "Grants to support hands-on STEM curriculum development and teacher training in under-resourced schools.",
		"url": "https://example.org/grants/stem-education-k12"
	},
	{
        "id": 3,
		"title": "Arts & Community Engagement Fund",
		"organization": "Arts Alliance",
		"field": "Arts",
		"source": "manual",
		"deadline": "2027-03-15",
		"min_amount": 2000,
		"max_amount": 15000,
		"eligibility": "Nonprofit arts organizations and community groups",
		"description": "Funding for public art projects and community engagement initiatives that increase local participation in the arts.",
		"url": "https://example.org/grants/arts-community-engagement"
	},
	{
        "id": 4,
		"title": "Climate Resilience Capacity Building",
		"organization": "Green Futures Initiative",
		"field": "Environment",
		"source": "manual",
		"deadline": "2026-11-15",
		"min_amount": 25000,
		"max_amount": 100000,
		"eligibility": "Nonprofits and community coalitions working on climate resilience",
		"description": "Support for planning, training, and implementation of community-based climate resilience efforts.",
		"url": "https://example.org/grants/climate-resilience"
	},
	{
        "id": 5,
		"title": "Small Business Recovery Grant",
		"organization": "Economic Opportunity Fund",
		"field": "Economic Development",
		"source": "manual",
		"deadline": "2026-10-31",
		"min_amount": 15000,
		"max_amount": 50000,
		"eligibility": "Small nonprofits and cooperatives supporting local entrepreneurship",
		"description": "Grants for programs that help small businesses recover and grow after economic disruption.",
		"url": "https://example.org/grants/small-business-recovery"
	},
	{
        "id": 6,
		"title": "Rural Broadband Access Grant",
		"organization": "Connectivity Trust",
		"field": "Technology",
		"source": "manual",
		"deadline": "2027-01-20",
		"min_amount": 30000,
		"max_amount": 120000,
		"eligibility": "Nonprofit organizations improving internet access in rural areas",
		"description": "Funding for broadband deployment, digital literacy, and community technology hubs.",
		"url": "https://example.org/grants/rural-broadband"
	},
	{
        "id": 7,
		"title": "Youth Mental Health Innovation Grant",
		"organization": "Wellness Futures",
		"field": "Health",
		"source": "manual",
		"deadline": "2026-08-31",
		"min_amount": 10000,
		"max_amount": 40000,
		"eligibility": "Nonprofits serving youth mental health and wellness programs",
		"description": "Support for innovative services, outreach, and partnerships that improve youth mental health outcomes.",
		"url": "https://example.org/grants/youth-mental-health"
	},
	{
        "id": 8,
		"title": "Food Security Partnership Grant",
		"organization": "Community Nourish Network",
		"field": "Social Services",
		"source": "manual",
		"deadline": "2026-12-01",
		"min_amount": 8000,
		"max_amount": 35000,
		"eligibility": "Nonprofits addressing food insecurity and local food systems",
		"description": "Funding for community kitchen programs, food distribution, and nutrition education.",
		"url": "https://example.org/grants/food-security-partnership"
	},
	{
        "id": 9,
		"title": "Workforce Training for Displaced Workers",
		"organization": "Next Career Foundation",
		"field": "Workforce Development",
		"source": "manual",
		"deadline": "2027-02-28",
		"min_amount": 20000,
		"max_amount": 75000,
		"eligibility": "Nonprofits providing job training and placement services",
		"description": "Grants for workforce development programs that support displaced and underserved workers.",
		"url": "https://example.org/grants/workforce-training"
	},
	{
        "id": 10,
		"title": "Accessible Transportation Grant",
		"organization": "Mobility for All",
		"field": "Infrastructure",
		"source": "manual",
		"deadline": "2027-05-10",
		"min_amount": 15000,
		"max_amount": 60000,
		"eligibility": "Nonprofits improving accessible transportation services",
		"description": "Funding for projects that increase transportation access for seniors, people with disabilities, and rural communities.",
		"url": "https://example.org/grants/accessible-transport"
	}
]


@app.route("/api/health/ollama", methods=["GET"])
def check_ollama():
    """Check if Ollama is running"""
    if USE_MOCK:
        return jsonify({"status": "mock", "message": "Mock mode enabled - skipping Ollama check"}), 200
    
    try:
        # Check if Ollama is up
        subprocess.run(["curl", "-s", OLLAMA_URL], check=True, stdout=subprocess.PIPE, timeout=2)
        
        # Check if llama3 is installed
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if "llama3" not in result.stdout.lower():
            return jsonify({"status": "warning", "message": "Ollama running, but 'llama3' model not found. Run 'ollama pull llama3'."}), 200
            
        return jsonify({"status": "ok", "message": "Ollama is ready"}), 200
    except Exception:
        return jsonify({"status": "error", "message": "Could not connect to Ollama"}), 500



@app.route("/api/search", methods=["POST"])
def search_grants():
    data = request.json or {}
    query = data.get("query", "").strip().lower()
    
    if not query:
        return jsonify({"error": "Query required"}), 400

    # --- MOCK MODE: Fast UI testing, NO LLM CALLS ---
    if USE_MOCK:
        time.sleep(0.5)  # Simulate network delay
        
        query_words = set(query.split())
        scored = []
        
        for grant in MOCK_GRANTS:
            # Score based on keyword overlap (simulates semantic ranking)
            text = f"{grant.get('title', '')} {grant.get('field', '')} {grant.get('description', '')}".lower()
            grant_words = set(text.split())
            overlap = len(query_words.intersection(grant_words))
            
            base_score = 70
            score = min(95, base_score + (overlap * 7))
            import random
            score += random.uniform(0, 4)  # Small randomness for realism
            
            # ✅ Generate a realistic-looking placeholder rationale
            field = grant.get("field", "this initiative")
            placeholder_rationale = (
                f"🧪 Demo mode: This {field.lower()} grant shows strong keyword alignment with your query. "
                f"In live mode, Llama 3 would analyze eligibility, scope, and strategic fit to generate a custom rationale."
            )
            
            scored.append({
                **grant,
                "rationale": placeholder_rationale,  # ✅ Now included!
                "relevance_score": round(score, 1),
                "_source": "mock"
            })
        
        # Sort by score and return top 3
        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        return jsonify(scored[:3]), 200

    # --- LIVE MODE: REAL SEMANTIC SEARCH + REAL LLM RATIONALES ---
    try:
        # 1. Your existing semantic search
        results = semantic_search(query, top_k=3)
        
        if not results:
            return jsonify([]), 200
        
        # 2. Generate REAL rationales using your run_chain() function
        final_results = []
        for grant in results:
            try:
                # This is where the LLM (Llama 3 ~ for now use qwen2.5:3b) actually runs
                rationale = run_chain(query, grant)
                
                # Fallback if LLM returns empty
                if not rationale or not rationale.strip():
                    rationale = "⚠️ LLM returned empty. Check Ollama is running: ollama serve"
                    
            except Exception as e:
                print(f"LLM error: {e}")
                rationale = f"⚠️ LLM failed: {str(e)}"
            
            # Convert similarity/distance to 0-100 score
            score = grant.get("_similarity", 0.75)
            if "_distance" in grant:
                score = max(0, min(100, 100 - (grant["_distance"] * 50)))
            
            final_results.append({
                **grant,
                "rationale": rationale,  # ✅ REAL LLM OUTPUT
                "relevance_score": round(float(score), 1),
                "_source": "live"
            })
        
        return jsonify(final_results), 200
        
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print(f" Starting GrantMatcher API on http://localhost:8000")
    print(f"   Mode: {'MOCK (Fake Data)' if USE_MOCK else 'LIVE (Ollama)'}")
    app.run(port=8000, debug=True)