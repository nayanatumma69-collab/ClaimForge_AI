# ClaimForge AI – Insurance Claims Adjudication Agent

An AI-powered insurance claims adjudication system built using **LangGraph, LangChain, Retrieval-Augmented Generation (RAG), and LLMs**.

ClaimForge AI helps analyze insurance claim documents, retrieve relevant policy information, verify claim details, and support claim review through an intelligent agent workflow.

## 🚀 Live Demo

[Launch ClaimForge AI](https://claimforge-ai.streamlit.app/)

## 🎯 Project Overview

Insurance claim assessment often involves reviewing multiple documents, checking policy conditions, and validating claim information.

ClaimForge AI uses an agentic AI workflow to assist this process. It retrieves relevant information from documents, evaluates the relevance of retrieved context, and supports claim verification. When confidence is insufficient, the workflow can escalate the case for human review.

## ✨ Key Features

- **Document-based RAG:** Retrieves relevant information from insurance documents.
- **Intelligent Retrieval:** Uses ChromaDB and HuggingFace embeddings.
- **Relevance Grading:** Evaluates whether retrieved context is useful.
- **Query Rewriting:** Refines queries when the retrieved information is insufficient.
- **Claim Verification:** Supports verification of claim details against retrieved policy information.
- **Confidence Scoring:** Helps identify cases requiring additional review.
- **Human-in-the-Loop:** Escalates uncertain cases for human assessment.
- **Audit Trail:** Maintains traceability of the claim review workflow.

## 🧠 AI Workflow

1. **Retrieve:** Search relevant information from the document knowledge base.
2. **Grade:** Evaluate the relevance of retrieved information.
3. **Rewrite:** Improve the search query when the context is insufficient.
4. **Verify:** Analyze claim details using relevant retrieved information.
5. **Evaluate Confidence:** Assess whether the result is sufficiently supported.
6. **Human Review:** Escalate uncertain cases for human assessment.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core development |
| LangGraph | Agent workflow orchestration |
| LangChain | LLM and retrieval integration |
| Groq | LLM inference |
| ChromaDB | Vector database |
| HuggingFace | Embeddings |
| Tavily | Search integration |
| Pydantic | Structured data validation |
| PyPDF | PDF document processing |
| Streamlit | User interface |

## 🏗️ Architecture

The application follows an agentic retrieval and verification workflow:

**User Input → Document Retrieval → Relevance Grading → Query Rewriting (if needed) → Claim Verification → Confidence Evaluation → Final Review / Human Escalation**

## ⚙️ Getting Started

### Prerequisites

- Python 3.10 or a compatible version
- Git
- API credentials required by the application

### Installation

Clone the repository:

```bash
git clone https://github.com/nayanatumma69-collab/ClaimForge_AI.git
```

Navigate to the project directory:

```bash
cd ClaimForge_AI
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Configure the API credentials required by the project using environment variables or Streamlit secrets. Never commit API keys or passwords to GitHub.

Run the application using the Streamlit entry-point file:

```bash
streamlit run app.py
```

*Note: Confirm the actual entry-point filename and requirements file in your repository before running these commands.*

## 💡 What I Learned

- Building agentic workflows using LangGraph.
- Implementing RAG-based document retrieval.
- Working with vector databases and embeddings.
- Designing relevance grading and query rewriting workflows.
- Integrating LLMs into practical applications.
- Implementing human-in-the-loop review for uncertain decisions.

## 🔮 Future Enhancements

- Add more insurance document formats.
- Improve retrieval evaluation and validation.
- Expand claim verification workflows.
- Enhance monitoring and workflow observability.
- Add more detailed claim review analytics.

## 👩‍💻 Author

**Nayana Tumma**

Aspiring GenAI & Agentic AI Engineer

- [LinkedIn](https://www.linkedin.com/in/nayana-tumma-23187687)
- [GitHub](https://github.com/nayanatumma69-collab)

---

*Built as a practical project exploring Generative AI, Agentic AI, RAG, and intelligent workflow automation.*
