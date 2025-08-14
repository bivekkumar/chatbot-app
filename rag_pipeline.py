from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
import os
import boto3

# S3 config
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")  # Still optional if you want to override
S3_BUCKET = "bivek-embedding-bucket-2025"

def download_faiss_from_s3(folder_name, local_dir):
    """Download FAISS index files from S3 for a given folder."""
    os.makedirs(local_dir, exist_ok=True)
    
    # Use instance IAM role credentials automatically
    s3 = boto3.client("s3", region_name=AWS_REGION)
    
    for file_name in ["index.faiss", "index.pkl"]:
        s3.download_file(
            S3_BUCKET,
            f"{folder_name}/{file_name}",
            os.path.join(local_dir, file_name)
        )

def load_multiple_faiss_indexes(folder_names):
    """Load multiple FAISS indexes from S3 and merge into one."""
    embedding_model = OpenAIEmbeddings()
    merged_db = None

    for folder in folder_names:
        local_path = f"tmp/{folder}"
        download_faiss_from_s3(folder, local_path)
        db = FAISS.load_local(local_path, embedding_model, allow_dangerous_deserialization=True)
        
        if merged_db is None:
            merged_db = db
        else:
            merged_db.merge_from(db)

    return merged_db

def get_qa_chain(folder_names):
    """Create a QA chain from multiple FAISS indexes."""
    db = load_multiple_faiss_indexes(folder_names)
    retriever = db.as_retriever()
    llm = ChatOpenAI()
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever)