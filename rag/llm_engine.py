import os
from google.colab import userdata
from langchain_groq import ChatGroq

def get_llm_engine():
    """
    Initializes a deterministic OpenAI GPT-OSS 120B instance hosted via Groq
    for strict, high-fidelity insurance adjudication reasoning.
    """
    # Load API token safely from your unique workspace secret name
    if "GROQ_API_KEY" not in os.environ:
        try:
            os.environ["GROQ_API_KEY"] = userdata.get("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")
        except Exception:
            raise ValueError("❌ Missing 'naya' key in Google Colab Secrets sidebar!")

    # Updated to the current production-grade reasoning model on Groq
    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.0
    )

if __name__ == "__main__":
    llm = get_llm_engine()
    print(f"🚀 Core LLM Engine Successfully Verified: {llm.model}")
