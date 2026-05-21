"""LLM chain orchestration for GrantMatcher AI."""

from typing import Dict, Any

from llm.prompts import FIT_PROMPT_TEMPLATE


def build_chain() -> Any:
    """Build and return the LLM chain for grant matching."""
    # TODO: implement LangChain / Ollama chain construction
    print("Building LLM chain")
    return None


def run_chain(project_description: str, grant: Dict[str, Any]) -> str:
    """Run the LLM chain and return a response."""
    prompt = FIT_PROMPT_TEMPLATE.format(
        project_description=project_description,
        title=grant.get("title", ""),
        description=grant.get("description", ""),
        eligibility=grant.get("eligibility", ""),
        deadline=grant.get("deadline", ""),
        min_amount=grant.get("min_amount", ""),
        max_amount=grant.get("max_amount", ""),
    )
    print(f"Running chain with prompt:\n{prompt}")
    return "LLM reasoning output placeholder"
