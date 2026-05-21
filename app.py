"""Entry point for the GrantMatcher AI application."""

import streamlit as st

from retrieval.semantic_search import semantic_search


def main() -> None:
    st.set_page_config(page_title="GrantMatcher AI", layout="wide")
    st.title("GrantMatcher AI")
    st.write("Search and match grant opportunities with semantic retrieval and LLM reasoning.")

    project_description = st.text_area("Project description", height=220)
    field_filter = st.text_input("Field / topic (optional)")

    if st.button("Search grants"):
        if not project_description.strip():
            st.warning("Please enter a project description to search.")
            return

        results = semantic_search(project_description, top_k=5)
        if not results:
            st.info("No matching grants found. Make sure the database is seeded and Chroma is synced.")
            return

        for grant in results:
            title = grant.get("title", "Untitled grant")
            with st.expander(title):
                st.write("**Organization:**", grant.get("organization"))
                st.write("**Field:**", grant.get("field"))
                st.write("**Deadline:**", grant.get("deadline"))
                st.write("**Funding range:**", f"{grant.get('min_amount')} - {grant.get('max_amount')}")
                st.write("**Description:**", grant.get("description"))
                st.write("**URL:**", grant.get("url"))


if __name__ == "__main__":
    main()
