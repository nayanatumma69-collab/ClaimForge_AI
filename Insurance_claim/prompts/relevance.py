RELEVANCE_PROMPT = """You are an expert insurance compliance auditor evaluating document relevance.
Analyze the provided document chunk against the user's search query. Determine if the document contains structural rules, coverage details, exclusions, or regulations that directly apply to evaluating the claim query.

Search Query:
{query}

Retrieved Document Chunk:
{document}

Provide a strict binary score ('yes' or 'no') and a short, fact-driven rationale.
"""