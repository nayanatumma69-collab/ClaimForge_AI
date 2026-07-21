import os
from dotenv import load_dotenv

# Load environmental variables if present
load_dotenv()

# Centralized API Keys configuration
# Replace placeholder values with your live credentials inside Colab secrets
GROQ_API_KEY = os.getenv("GROQ_API_KEY","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")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY","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")

# RAG Threshold Configurations
RETRY_LIMIT = 2
EMBEDDING_MODEL_NAME = "openai/gpt-oss-120b"
VECTOR_DB_DIR = "Insurance_claim/vector_db"

print("⚙️ Configuration keys loaded successfully.")
