from typing import Dict, Any
from langchain_core.documents import Document
from tavily import TavilyClient
from Insurance_claim.config import TAVILY_API_KEY

def web_search_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fallback execution node. Queries the web via Tavily to fetch missing
    regulatory mandates or specialized policy rules when internal RAG fails.
    """
    print("\n[Node: Web Fallback Search]")

    current_query = state.get("query") or state.get("claim")
    print(f"  🌐 Running Tavily search query: '{current_query}'")

    try:
        # Initialize the raw third-party Tavily API wrapper
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        response = tavily_client.search(query=current_query, max_results=2)

        web_docs = []
        for idx, result in enumerate(response.get("results", [])):
            title = result.get("title", "Web Resource")
            url = result.get("url", "N/A")
            content = result.get("content", "")

            # Wrap web data inside structural LangChain Documents so downstream nodes process seamlessly
            doc = Document(
                page_content=content,
                metadata={"source_file": f"{title} ({url})", "category": "web_fallback"}
            )
            web_docs.append(doc)

        print(f"  ✅ Extracted {len(web_docs)} fallback context snippets from the live web.")

        # Merge web results with existing context structures
        combined_docs = state.get("documents", []) + web_docs
        log_entry = f"Web fallback lookup succeeded. Added {len(web_docs)} external source elements."

    except Exception as e:
        print(f"  ❌ Tavily web search integration error: {str(e)}")
        combined_docs = state.get("documents", [])
        log_entry = f"Web fallback failed due to engine error: {str(e)}"

    return {
        "documents": combined_docs,
        "audit_trail": state.get("audit_trail", []) + [log_entry]
    }
