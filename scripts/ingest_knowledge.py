# scripts/ingest_knowledge.py
import os
import json
import glob
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from dotenv import load_dotenv
load_dotenv()


# persist dir for vector DB
PERSIST_DIR = "knowledge_store"
REPORTS_GLOB = "reports/runs/**/*.json"  # will pick up your report files

def load_json_reports(pattern=REPORTS_GLOB):
    docs = []
    for path in glob.glob(pattern, recursive=True):
        try:
            with open(path, "r", encoding="utf-8") as f:
                j = json.load(f)
        except Exception:
            continue
        # stringify JSON into text (you can choose to extract fields more precisely)
        text = json.dumps(j, indent=2)
        docs.append(Document(page_content=text, metadata={"source": path}))
    return docs

def load_extra_docs(folder="knowledge_base"):
    docs = []
    if not os.path.isdir(folder):
        return docs
    for path in glob.glob(os.path.join(folder, "**/*.*"), recursive=True):
        if path.lower().endswith((".md", ".txt", ".json")):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            docs.append(Document(page_content=text, metadata={"source": path}))
    return docs

def ingest_all(persist_dir=PERSIST_DIR):
    docs = load_json_reports() + load_extra_docs()
    if not docs:
        print("No docs found to ingest. Put some JSONs in reports/runs or docs in knowledge_base/")
        return

    # split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    # embeddings + chroma
    embeddings = OpenAIEmbeddings()
    db = Chroma.from_documents(chunks, embeddings, persist_directory=persist_dir)
    db.persist()
    print(f"Persisted {len(chunks)} chunks into {persist_dir}")

if __name__ == "__main__":
    ingest_all()
