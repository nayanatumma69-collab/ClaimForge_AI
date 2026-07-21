REWRITE_PROMPT = """You are a specialized query optimization agent for an insurance vector database.
The current search query failed to return sufficient or highly relevant insurance policy context.
Analyze the user's raw statement and rewrite it to focus strictly on core insurance terminology, peril keywords, clause names, or regulatory categories. Do not include introductory conversational text.

Raw User Claim/Query:
{query}

Provide only the optimized search string.
"""