"""Prompt templates for GrantMatcher AI."""

FIT_PROMPT_TEMPLATE = """
You are an expert grant advisor tasked with evaluating how well a grant opportunity matches a project proposal.

Project description:
{project_description}

Grant title: {title}
Grant description: {description}
Eligibility: {eligibility}
Deadline: {deadline}
Funding range: {min_amount} - {max_amount}

Provide a concise rationale for why this grant is a good fit or not, and highlight any important eligibility or deadline considerations.
"""

SUMMARY_PROMPT_TEMPLATE = """
Summarize the grant opportunity in a way that is easy for a nonprofit grant writer to review.

Grant title: {title}
Organization: {organization}
Field: {field}
Deadline: {deadline}
Funding range: {min_amount} - {max_amount}

Return a short summary paragraph.
"""
