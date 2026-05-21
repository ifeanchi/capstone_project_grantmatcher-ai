"""Entry point for the GrantMatcher AI application."""

import streamlit as st

from llm.chain import run_chain
from retrieval.semantic_search import semantic_search


def format_currency(min_amount, max_amount):
    if min_amount and max_amount:
        return f"${min_amount:,} – ${max_amount:,}"
    if min_amount:
        return f"From ${min_amount:,}"
    if max_amount:
        return f"Up to ${max_amount:,}"
    return "Not specified"


def render_grant_card(grant, project_description):
    title = grant.get("title", "Untitled opportunity")
    organization = grant.get("organization", "Unknown")
    field = grant.get("field", "General")
    deadline = grant.get("deadline") or "Open"
    funding = format_currency(grant.get("min_amount"), grant.get("max_amount"))
    source = grant.get("source") or "Source not available"
    description = grant.get("description") or "No description provided."
    eligibility = grant.get("eligibility") or "Eligibility details unavailable."
    url = grant.get("url") or ""

    card_style = "border: 1px solid #e2e8f0; border-radius: 14px; padding: 22px; margin-bottom: 18px; background: #ffffff;"
    st.markdown(f"<div style='{card_style}'>", unsafe_allow_html=True)
    st.markdown(f"### {title}")
    st.markdown(
        f"**Organization:** {organization}  \n"
        f"**Field:** {field}  \n"
        f"**Deadline:** {deadline}  \n"
        f"**Funding:** {funding}  \n"
        f"**Source:** {source}"
    )
    st.markdown(f"**Eligibility:** {eligibility}")
    st.markdown(f"**Description:** {description}")
    if url:
        st.markdown(f"**URL:** [Open opportunity]({url})")

    with st.expander("View grant fit rationale"):
        try:
            rationale = run_chain(project_description, grant)
            st.write(rationale)
        except Exception as exc:
            st.error("Unable to generate rationale at this time.")
            st.write(str(exc))

    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title="GrantMatcher AI", layout="wide")
    st.markdown(
        """
        <style>
            .app-title { color: #0f172a; font-size: 42px; font-weight: 700; }
            .app-subtitle { color: #475569; font-size: 18px; margin-bottom: 24px; }
            .stButton>button { background-color: #2563eb; color: white; }
            .stButton>button:hover { background-color: #1d4ed8; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    header_col, info_col = st.columns([3, 1])
    with header_col:
        st.markdown('<div class="app-title">GrantMatcher AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="app-subtitle">Quickly discover grant opportunities that fit your project with semantic search and AI-powered reasoning.</div>', unsafe_allow_html=True)

    with info_col:
        st.markdown("#### How it works")
        st.markdown(
            "- Describe your project or program in plain language.  \n"
            "- Optional: add a field or topic to narrow results.  \n"
            "- Review top grant matches and AI-generated fit rationale."
        )

    st.divider()

    with st.form(key="search_form"):
        project_description = st.text_area("Project description", height=260, placeholder="Describe your program, population served, outcomes, and timeline.")
        field_filter = st.text_input("Field / topic (optional)", placeholder="e.g. health, education, climate, arts")
        submit = st.form_submit_button("Search grants")

    if not submit:
        st.info("Enter a project description to begin searching for grants.")
        return

    if not project_description.strip():
        st.warning("Please enter a project description to search.")
        return

    with st.spinner("Searching grant opportunities..."):
        results = semantic_search(project_description, top_k=6)

    if field_filter:
        results = [grant for grant in results if field_filter.lower() in str(grant.get("field", "")).lower() or field_filter.lower() in str(grant.get("title", "")).lower()]

    if not results:
        st.warning("No matching grants found. Verify your database has grant records and try a broader description.")
        return

    st.markdown(f"#### Top {len(results)} matches")
    for grant in results:
        render_grant_card(grant, project_description)

    st.markdown("---")
    st.markdown("*GrantMatcher AI uses local semantic search with SQLite fallback to keep matching fast and reliable.*")


if __name__ == "__main__":
    main()
