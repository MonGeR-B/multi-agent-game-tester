from agents.rag import get_retriever, get_retrieval_qa
from dotenv import load_dotenv
load_dotenv()


retriever = get_retriever(k=3)
docs = retriever.get_relevant_documents("SumLink puzzle rules")
print("Docs found:", len(docs))
if docs:
    print("Example doc:", docs[0].page_content[:200])

qa = get_retrieval_qa()
print("QA sample:", qa.run("Summarize what SumLink puzzle is about"))
