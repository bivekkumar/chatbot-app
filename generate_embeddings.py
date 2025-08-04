import os
import faiss
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import boto3
from dotenv import load_dotenv
load_dotenv()

# Load + Split
loader = PyMuPDFLoader("Resume.pdf")
documents = loader.load()

splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
texts = splitter.split_documents(documents)

# Embed
embedding_model = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(texts, embedding_model)

# Save locally
faiss_dir = "app/faiss_index"
os.makedirs(faiss_dir, exist_ok=True)
vectorstore.save_local(faiss_dir)

# Upload to S3
s3 = boto3.client('s3')
s3.upload_file("app/faiss_index/index.faiss", "bivek-embedding-bucket-2025", "resume/index.faiss")
s3.upload_file("app/faiss_index/index.pkl", "bivek-embedding-bucket-2025", "resume/index.pkl")