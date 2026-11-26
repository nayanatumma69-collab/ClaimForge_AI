import os
from dotenv import load_dotenv

load_dotenv(override=True)  # .env wins over old system variables


def get_key(name):
    value = os.getenv(name)
    if not value:
        try:
            import streamlit as st
            value = st.secrets[name]
        except Exception:
            raise ValueError(f"Missing {name}. Add it to .env or Streamlit secrets.")
    return value.strip()


GROQ_API_KEY = get_key("GROQ_API_KEY")
TAVILY_API_KEY = get_key("TAVILY_API_KEY")

RETRY_LIMIT = 2
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
VECTOR_DB_DIR = "vector_db"
