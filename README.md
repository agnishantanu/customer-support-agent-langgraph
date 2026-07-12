# Agentic AI Project — Customer Support Agent

This project implements a LangGraph-powered customer support assistant for ABC Technologies with intent classification, conditional routing, department agents, RAG over a knowledge base, SQLite memory, human approval, supervisor review, a FastAPI backend, and a Streamlit demo UI.

## Features
- LangGraph workflow with stateful orchestration
- Intent classification for sales, technical, billing, and account requests
- Routing to specialist agents
- Retrieval-augmented generation over the company knowledge base
- SQLite conversation memory and recall for previous issues
- Human approval for refunds, cancellations, account closure, compensation, and escalation requests
- Supervisor review for quality and safety
- FastAPI chat endpoint and Streamlit UI

## Setup
1. Create and activate a Python environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Generate the knowledge base PDFs:
   ```bash
   python generate_kb_pdfs.py
   ```
4. Copy the example environment file and fill in any secrets if needed:
   ```bash
   copy .env.example .env
   ```

## Run the API
```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

## Run the UI
```bash
streamlit run app/ui/streamlit_app.py
```

## Run the Demo Workflow
```bash
python -c "from app.graphs.workflow_graph import run_support_workflow; print(run_support_workflow('Ada', 'What are your pricing plans?'))"
```

## Testing
```bash
python -m pytest -q
```

## Author

**Shantanu Agnihotri**

---

## License

This project is licensed under the MIT License. 
