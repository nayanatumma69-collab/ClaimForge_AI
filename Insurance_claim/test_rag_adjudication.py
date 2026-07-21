import os
import sys

# Ensure local directories are visible to the interpreter path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Insurance_claim.rag.retriever import fetch_context
from Insurance_claim.schemas.llm_chains import adjudicate_chain

def run_rag_integration_test():
    print("=====================================================================")
    print("🔬 RUNNING RAG INTEGRATION TEST USING LOCAL PDF VECTOR DB")
    print("=====================================================================\n")

    # 1. Define a realistic claim query matching one of your generated Indian PDFs
    sample_claim = (
        "My home was severely flooded during the monsoon storm last week, causing "
        "structural damage to the outer living room walls. I need to file a claim for "
        "building structure repairs under my Bharat Griha Raksha policy."
    )

    print(f"📝 Simulated User Claim:\n\"{sample_claim}\"\n")
    print("🔍 Querying Chroma DB for relevant PDF context chunks...")

    # 2. Call your fetch_context function (Top 2 most relevant chunks)
    retrieved_docs = fetch_context(query=sample_claim, top_k=2)

    if not retrieved_docs:
        print("❌ Error: No context retrieved from the database. Ensure your PDFs are ingested.")
        return

    print(f"✅ Successfully retrieved {len(retrieved_docs)} relevant context chunk(s) from local PDFs.")

    # 3. Compile the retrieved documents into a single text block for the LLM
    context_block = ""
    for idx, doc in enumerate(retrieved_docs):
        source = doc.metadata.get('source_file', 'Unknown')
        category = doc.metadata.get('category', 'Unknown')
        context_block += f"--- Document Reference {idx+1} [Source: {source} | Category: {category}] ---\n"
        context_block += f"{doc.page_content}\n\n"

    print("\n📚 Compiled Context Passed to Adjudicator:")
    print(context_block)

    # 4. Invoke Anirudh's adjudication chain using the real PDF text context
    print("🤖 Invoking Adjudication LLM Chain...")
    decision_output = adjudicate_chain.invoke({
        "claim": sample_claim,
        "context": context_block
    })

    # 5. Output structured metrics derived directly from the PDF rules
    print("\n=====================================================================")
    print("⚖️ FINAL ADJUDICATION METRICS (FROM PDF EVIDENCE)")
    print("=====================================================================")
    print(f"📢 Decision    : {decision_output.decision}")
    print(f"🎯 Confidence  : {decision_output.confidence}")
    print(f"📝 Reason      : {decision_output.reason}")
    print(f"🔖 Citations   : {decision_output.evidence_citations}")
    print("=====================================================================")

if __name__ == '__main__':
    run_rag_integration_test()
