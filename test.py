# test_llm.py
from llm.chain import run_chain

# Minimal test grant
test_grant = {
    "title": "Test Health Grant",
    "description": "Supports community health programs",
    "eligibility": "Nonprofits",
    "deadline": "2026-12-31",
    "min_amount": 10000,
    "max_amount": 50000
}

print("🔍 Testing LLM rationale generation...")
result = run_chain("youth health outreach", test_grant)
print("\n✅ LLM Output:")
print(result)