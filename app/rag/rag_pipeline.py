import os
import glob
from typing import List, Dict, Any

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

from app.models.state import SupportState
from app.models.llm_factory import get_llm
from app.utils.config import settings

# Global references
_vector_store = None
_embeddings = None

def get_embeddings():
    """
    Initializes and returns the sentence-transformer embeddings.
    """
    global _embeddings
    if _embeddings is None:
        model_name = settings.EMBEDDING_MODEL
        print(f"Initializing embedding model: {model_name} ...")
        _embeddings = HuggingFaceEmbeddings(model_name=model_name)
    return _embeddings

def initialize_vector_db(force_rebuild: bool = False) -> Chroma:
    """
    Loads PDF files from the knowledge base directory, splits them into chunks,
    generates embeddings using Sentence Transformers, and stores them in ChromaDB.
    """
    global _vector_store
    
    persist_directory = settings.CHROMA_PERSIST_DIR
    kb_directory = settings.KNOWLEDGE_BASE_DIR
    
    # If already loaded in memory and not forcing rebuild, return it
    if _vector_store is not None and not force_rebuild:
        return _vector_store
        
    embeddings = get_embeddings()
    
    # Check if database already exists on disk
    if os.path.exists(persist_directory) and not force_rebuild:
        # Check if the folder is non-empty
        if len(os.listdir(persist_directory)) > 0:
            print(f"Loading existing vector store from disk: {persist_directory}")
            _vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings
            )
            return _vector_store

    print(f"Building vector database from files in: {kb_directory} ...")
    
    # Ensure kb directory exists
    if not os.path.exists(kb_directory):
        os.makedirs(kb_directory, exist_ok=True)
        
    # Search for all PDF documents
    pdf_pattern = os.path.join(kb_directory, "*.pdf")
    pdf_files = glob.glob(pdf_pattern)
    
    documents: List[Document] = []
    
    if not pdf_files:
        print(f"WARNING: No PDF files found in {kb_directory}. Please run PDF generator first.")
        # If no PDFs, create a temporary blank vector database or empty one
        # to prevent crash. We will index a mock document.
        documents.append(Document(
            page_content="ABC Technologies Support System Knowledge Base. General policy: refunds are allowed within 30 days. Pricing plans: Basic is ₹999/month, Pro is ₹2,999/month, Enterprise is ₹8,999/month. All prices are shown in INR.",
            metadata={"source": "mock_KB.pdf"}
        ))
    else:
        for pdf_path in pdf_files:
            print(f"Loading document: {pdf_path}")
            try:
                loader = PyPDFLoader(pdf_path)
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"Error loading {pdf_path}: {e}")
                
    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunks)} chunks.")
    
    # Create Chroma DB
    os.makedirs(persist_directory, exist_ok=True)
    _vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    print("Vector database built successfully and persisted.")
    return _vector_store

def retrieve_context(query: str, top_k: int = None) -> List[Document]:
    """
    Queries ChromaDB to find the most relevant chunks.
    """
    if top_k is None:
        top_k = settings.RAG_TOP_K
        
    db = initialize_vector_db()
    try:
        results = db.similarity_search(query, k=top_k)
        return results
    except Exception as e:
        print(f"Retrieval error: {e}")
        return []

# Prompt for grounding/enriching the response
GROUNDING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a Quality and Grounding specialist at ABC Technologies.\n"
        "Your task is to enrich the agent's draft customer support response using retrieved documentation context.\n"
        "Follow these rules:\n"
        "1. Ensure all factual claims (pricing plans, refund policies, upload sizes, passwords, troubleshooting steps) in the response match the retrieved documents exactly.\n"
        "2. If the retrieved documents do not contain the answer, do not invent information; stick to what the agent draft says, or indicate that specific information is unavailable.\n"
        "3. Preserve the tone, customer name, and department signature of the original response.\n"
        "4. Do not prefix your answer with metadata like 'Enriched response:' or 'Here is the response'. Just output the refined message directly."
    )),
    ("human", (
        "Customer Name: {customer_name}\n"
        "Customer Query: {query}\n"
        "Agent Draft Response: {draft_response}\n"
        "Retrieved Documentation Context:\n"
        "{context}"
    ))
])

def rag_node(state: SupportState) -> dict:
    """
    RAG Node: retrieves relevant documents from ChromaDB and uses an LLM to
    enrich and ground the draft response generated by the department agent.
    """
    query = state.get("query", "")
    draft_response = state.get("response", "")
    customer_name = state.get("customer_name", "Valued Customer")
    
    # 1. Retrieve relevant documents
    retrieved_docs = retrieve_context(query)
    doc_texts = []
    doc_sources = []
    
    for i, doc in enumerate(retrieved_docs):
        src = doc.metadata.get("source", "unknown")
        doc_texts.append(f"Source: {os.path.basename(src)}\nContent: {doc.page_content}")
        doc_sources.append(src)
        
    context_str = "\n\n".join(doc_texts)
    
    # Store retrieved document content in the state
    retrieved_contents = [doc.page_content for doc in retrieved_docs]
    
    # 2. If no draft response, let's treat it as empty draft and write directly
    # Otherwise, enrich it.
    llm = get_llm()
    chain = GROUNDING_PROMPT | llm
    
    try:
        enriched_res = chain.invoke({
            "customer_name": customer_name,
            "query": query,
            "draft_response": draft_response,
            "context": context_str if context_str else "No relevant documents found."
        })
        final_response = enriched_res.content
    except Exception as e:
        print(f"Grounding LLM execution error: {e}. Falling back to draft response.")
        final_response = draft_response
        
    # Update metadata
    metadata = state.get("metadata", {})
    metadata["rag_sources"] = doc_sources
    
    return {
        "retrieved_documents": retrieved_contents,
        "response": final_response,
        "metadata": metadata
    }
