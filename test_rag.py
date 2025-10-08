from agents.rag import get_retriever, get_retrieval_qa

retriever = get_retriever()

# ✅ Use updated method (invoke instead of get_relevant_documents)
docs = retriever.invoke("SumLink puzzle rules")
print(f"Docs found: {len(docs)}")

if docs:
    print("Example doc:", docs[0].page_content[:300])

qa = get_retrieval_qa()

# ✅ Use updated method (invoke instead of run)
print("QA sample:", qa.invoke("Summarize what SumLink puzzle is about"))
