import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

PERSIST_DIR = os.environ.get("RAG_PERSIST_DIR", "knowledge_store")

def get_retriever(k=4, persist_dir=PERSIST_DIR):
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    return vectordb.as_retriever(search_kwargs={"k": k})

def get_retrieval_qa(model_name="gpt-3.5-turbo", temperature=0.0, persist_dir=PERSIST_DIR):
    llm = ChatOpenAI(model=model_name, temperature=temperature)
    retriever = get_retriever(persist_dir=persist_dir)
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type="stuff")
    return qa
