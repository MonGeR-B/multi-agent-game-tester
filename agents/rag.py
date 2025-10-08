# agents/rag.py
import os
from typing import List

# use langchain_openai and langchain_chroma consistent packages
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA

from agents.llm_provider import LLMProvider

PERSIST_DIR = os.environ.get("RAG_PERSIST_DIR", "knowledge_store")


def get_retriever(k=4, persist_dir: str = PERSIST_DIR):
    """
    Returns a retriever object (vector db as retriever).
    """
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    # as_retriever ensures consistent interface across versions
    return vectordb.as_retriever(search_kwargs={"k": k})


def get_retrieval_qa(model_name="gpt-3.5-turbo", temperature=0.0, persist_dir: str = PERSIST_DIR):
    """
    Convenience factory: returns a RetrievalQA chain (if you want to use it).
    """
    llm = ChatOpenAI(model=model_name, temperature=temperature)
    retriever = get_retriever(persist_dir=persist_dir)
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type="stuff")
    return qa


def _safe_get_docs_from_retriever(retriever, query: str, k: int = 3):
    """
    Try multiple retriever interfaces for compatibility:
    - retriever.get_relevant_documents(q)
    - retriever.get_relevant_documents if available (old)
    - retriever.invoke (some newer abstractions)
    - retriever.retrieve
    Returns list of Document-like objects.
    """
    # try common methods in order
    for fn in ("get_relevant_documents", "retrieve", "invoke"):
        method = getattr(retriever, fn, None)
        if callable(method):
            try:
                docs = method(query) if fn == "invoke" else method(query)
                # ensure docs is a list
                if docs is None:
                    continue
                if isinstance(docs, (list, tuple)):
                    return list(docs)[:k]
            except Exception:
                continue
    # nothing worked, return empty
    return []


def generate_answer_with_rag(retriever, query: str, k: int = 3, temperature: float = 0.0) -> str:
    """
    Retrieve top-k docs, assemble a short context, and ask LLM (via LLMProvider) for a concise summary.
    """
    docs = _safe_get_docs_from_retriever(retriever, query, k=k)[:k]
    context_pieces: List[str] = []
    for d in docs:
        # Document objects differ by version: try common attribute names
        content = getattr(d, "page_content", None)
        if content is None:
            content = getattr(d, "content", None)
        if content is None:
            content = str(d)
        context_pieces.append(content.strip())

    if context_pieces:
        context = "\n\n".join(context_pieces)
    else:
        context = "No prior context available."

    prompt = f"""You are a helpful test planning assistant. Use the context below (prior runs, notes, docs).

Context:
{context}

User question:
{query}

Using the context above, answer concisely and provide:
- a short (2-4 lines) summary of relevant failures and stable interactions
- numbered bullet list of 3 concise actionable test ideas (one sentence each)

Return only plain text (no JSON).
"""
    provider = LLMProvider()
    return provider.generate(prompt, temperature=temperature, max_tokens=512)
