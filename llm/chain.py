# """LLM chain orchestration for GrantMatcher AI."""

# from typing import Dict, Any

# from llm.prompts import FIT_PROMPT_TEMPLATE
# import subprocess


# def build_chain() -> Any:
#     """Placeholder: construction handled at call time for simple CLI-based Ollama usage."""
#     return None


# def run_chain(project_description: str, grant: Dict[str, Any]) -> str:
#     """Run the LLM chain and return a response.

#     This attempts to call the `ollama` CLI with `llama3`. If `ollama` is not
#     available, falls back to a simple templated rationale.
#     """
#     prompt = FIT_PROMPT_TEMPLATE.format(
#         project_description=project_description,
#         title=grant.get("title", ""),
#         description=grant.get("description", ""),
#         eligibility=grant.get("eligibility", ""),
#         deadline=grant.get("deadline", ""),
#         min_amount=grant.get("min_amount", ""),
#         max_amount=grant.get("max_amount", ""),
#     )

#     # Try calling Ollama CLI
#     try:
#         proc = subprocess.run(["ollama", "run", "llama3", prompt], capture_output=True, text=True, timeout=60)
#         if proc.returncode == 0 and proc.stdout:
#             return proc.stdout.strip()
#         if proc.stderr:
#             # fall through to fallback
#             print("Ollama stderr:", proc.stderr)
#     except FileNotFoundError:
#         # ollama not installed
#         pass
#     except Exception as e:
#         print("Ollama call failed:", e)

#     # Fallback: lightweight heuristic-based rationale
#     title = grant.get("title", "this opportunity")
#     description = (grant.get("description") or "").strip()
#     reasons = []
#     if any(w in project_description.lower() for w in ["health", "outreach", "community"]):
#         if "health" in (grant.get("field") or "").lower() or "health" in description.lower():
#             reasons.append("Project focus aligns with the grant's health/outreach goals.")
#     if grant.get("deadline"):
#         reasons.append(f"Deadline: {grant.get('deadline')}")
#     if not reasons:
#         reasons.append("Potential fit — please review eligibility and scope.")

#     return f"Rationale for {title}: \n- " + "\n- ".join(reasons)




from typing import Dict, Any

import ollama  # Official Python client

def run_chain(project_description: str, grant: dict) -> str:
    """Generate fit rationale using qwen2.5:3b via Ollama Python client."""
    from llm.prompts import FIT_PROMPT_TEMPLATE
    
    prompt = FIT_PROMPT_TEMPLATE.format(
        project_description=project_description,
        title=grant.get("title", ""),
        description=grant.get("description", ""),
        eligibility=grant.get("eligibility", ""),
        deadline=grant.get("deadline", ""),
        min_amount=grant.get("min_amount", ""),
        max_amount=grant.get("max_amount", ""),
    )

    try:
        # Direct HTTP call to localhost:11434 (no subprocess, no encoding issues)
        response = ollama.chat(
            model="qwen2.5:3b",  # or "llama3:latest ~ was slow and heavy"
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()
        
    except Exception as e:
        print(f"⚠️ LLM call failed: {e}")
        # Fallback heuristic (kept for robustness)
        title = grant.get("title", "this opportunity")
        reasons = []
        if any(w in project_description.lower() for w in ["health", "outreach", "community"]):
            if "health" in (grant.get("field") or "").lower():
                reasons.append("Project focus aligns with the grant's health/outreach goals.")
        if grant.get("deadline"):
            reasons.append(f"Deadline: {grant.get('deadline')}")
        if not reasons:
            reasons.append("Potential fit — please review eligibility and scope directly.")
        return f"Rationale for {title}: \n- " + "\n- ".join(reasons)