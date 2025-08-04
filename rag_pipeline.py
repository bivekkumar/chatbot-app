from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv
load_dotenv()

def get_qa_chain():
    # Load prebuilt FAISS index
    embedding_model = OpenAIEmbeddings()
    db = FAISS.load_local("app/faiss_index", embedding_model, allow_dangerous_deserialization=True)
    
    retriever = db.as_retriever()
    llm = ChatOpenAI()
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return qa