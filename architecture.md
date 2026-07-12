# Architecture — AI Powered Customer Support Automation System

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                          │
│  ┌──────────────┐    ┌──────────────┐                               │
│  │  Streamlit UI │    │  FastAPI      │                              │
│  │  (app/ui/)    │◄──►│  (app/api/)   │                              │
│  └──────────────┘    └──────┬───────┘                               │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────────┐
│                      ORCHESTRATION LAYER                            │
│                              │                                      │
│  ┌───────────────────────────▼──────────────────────────────────┐   │
│  │              LangGraph State Machine (app/graphs/)           │   │
│  │                                                               │   │
│  │  intake → classify → route → department → rag → approval     │   │
│  │          → supervisor → memory → response                    │   │
│  └───────────────────────────┬──────────────────────────────────┘   │
│                              │                                      │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────────┐
│                        PROCESSING LAYER                             │
│                              │                                      │
│  ┌──────────────┐  ┌────────┴──────┐  ┌──────────────┐             │
│  │ Intent Node  │  │ Dept Agents   │  │ Supervisor   │             │
│  │ (app/nodes/) │  │ (app/agents/) │  │ (app/agents/)│             │
│  └──────────────┘  └───────────────┘  └──────────────┘             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────────┐
│                          DATA LAYER                                 │
│                              │                                      │
│  ┌──────────────┐  ┌────────┴──────┐  ┌──────────────┐             │
│  │ ChromaDB     │  │  SQLite       │  │ LLM Provider │             │
│  │ (app/rag/)   │  │ (app/memory/) │  │ (app/models/)│             │
│  └──────────────┘  └───────────────┘  └──────────────┘             │
│                                                                     │
│  ┌──────────────────────────────────┐                               │
│  │ Knowledge Base (knowledge_base/) │                               │
│  │ PDFs: policy, pricing, tech, faq │                               │
│  └──────────────────────────────────┘                               │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Presentation Layer
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Streamlit UI | Streamlit | Interactive demo interface for customer support chat |
| FastAPI Backend | FastAPI | REST API exposing the LangGraph workflow as HTTP endpoints |

### Orchestration Layer
| Component | Technology | Purpose |
|-----------|-----------|---------|
| LangGraph Graph | LangGraph | Stateful workflow engine connecting all nodes via edges and conditional routing |

### Processing Layer
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Intent Classifier | LangChain + LLM | Classifies customer intent into sales/technical/billing/account |
| Department Agents | LangChain + LLM | Four specialised agents, each with domain-specific system prompts |
| Supervisor Agent | LangChain + LLM | Validates response quality, tone, accuracy, and safety |
| Human Approval | Custom Node | Intercepts high-risk requests for human sign-off |

### Data Layer
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Vector Store | ChromaDB + FAISS (optional) | Stores document embeddings for semantic retrieval |
| Embeddings | Sentence-Transformers | Generates vector embeddings from document chunks |
| SQLite | sqlite3 | Stores conversation history, messages, and metadata |
| LLM Provider | OpenAI / IBM Granite | Pluggable LLM backend via factory pattern |
| Knowledge Base | PDF files | Company policy, pricing guide, technical manual, FAQ |

## LLM Provider Strategy

The system uses a **factory pattern** in `app/models/llm_factory.py`:

```python
def get_llm(provider: str = None):
    if provider == "openai":
        return ChatOpenAI(...)
    elif provider == "ibm":
        return WatsonxLLM(...)
```

The provider is selected via the `LLM_PROVIDER` environment variable, making it
trivial to switch between OpenAI and IBM Granite without changing any node code.

## Data Flow

1. **Streamlit/FastAPI** receives customer query
2. **Intake Node** initialises state with conversation_id
3. **Intent Classifier** determines intent via LLM (keyword fallback)
4. **Conditional Router** sends state to the correct department agent
5. **Department Agent** generates a draft response
6. **RAG Node** retrieves relevant document chunks and enriches the response
7. **Approval Check** determines if human sign-off is required
8. **Human Approval Node** (conditional) pauses for approval
9. **Supervisor** validates and optionally rewrites the response
10. **Memory Node** persists conversation to SQLite
11. **Final Response Node** returns the completed response

## Security Considerations

- API keys stored in `.env`, never committed to version control
- Human approval required for financially impactful actions
- Supervisor layer prevents hallucinated or unsafe responses
- SQLite database is local, no external data exposure
