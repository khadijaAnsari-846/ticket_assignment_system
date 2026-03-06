# 🤖 Agentic Weekly Sprint Planner

An AI-powered swarm built with **CrewAI**, **FastAPI**, and **Streamlit** that automates project task estimation and developer allocation while learning from user feedback.

## 🚀 Key Features
* **AI Swarm Architecture**: Utilizes three specialized agents (Recruiter, Architect, and Manager) to process CVs and Project Requirements.
* **Session-Aware Allocation**: Tracks developer capacity across multiple uploads to prevent over-allocation (max 35h/week).
* **Continuous Learning**: Features a feedback loop where user corrections are stored in `agent_memory.json` and injected into the Manager's backstory for future runs.
* **RAG Integration**: Uses Gemini Embeddings and Vector Databases to query specific technical skills from uploaded PDFs.

## 🛠️ Tech Stack
* **Backend**: FastAPI, CrewAI, LangChain.
* **Frontend**: Streamlit.
* **LLMs**: Gemini (via Google Generative AI) & HuggingFace Hub.
* **Database**: ChromaDB (Vector Store).

## 🏃‍♂️ How to Run
1. **Install Dependencies**:
   ```bash
   pip install fastapi streamlit crewai langchain_google_genai pydantic



2.Start the Backend:

uvicorn main:app --reload --port 5000

3.Start the Frontend:

streamlit run frontened.py
