# main.py
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
import os
import time
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from config import Config

app = FastAPI()

# CORS middleware for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific frontend URL if hosted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize LLM and Embeddings
llm = ChatGroq(groq_api_key=groq_api_key, model_name=Config.LANGUAGE_MODEL_NAME)
embeddings = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL_NAME)
prompt = ChatPromptTemplate.from_template(
    """
    Answer the questions based on the provided context. If the provided context does not include the answer, provide an answer based on your knowledge.
    {context}
    <context>
    Questions: {input}
    """
)

# Global variable to store vector embeddings
vectors = None

def load_vectors_from_local():
    global vectors
    vector_store_path = Config.EMBEDDINGS_DIR
    if os.path.exists(vector_store_path):
        vectors = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
        print("Loaded vector store from disk.")

load_vectors_from_local()

def process_documents(pdf_files: List[UploadFile]):
    global vectors
    docs = []
    for pdf_file in pdf_files:
        loader = PyPDFLoader(pdf_file.file)
        docs.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=Config.CHUNK_SIZE, chunk_overlap=Config.CHUNK_OVERLAB)
    final_documents = text_splitter.split_documents(docs)
    
    vectors = FAISS.from_documents(final_documents, embeddings)
    vectors.save_local(Config.EMBEDDINGS_DIR)
    return "Documents processed successfully"

# Endpoint to upload PDFs and create embeddings
@app.post("/upload/")
async def upload_files(files: List[UploadFile]):
    process_documents(files)
    return {"message": "Documents processed successfully"}

# Endpoint to ask questions
class QuestionRequest(BaseModel):
    question: str

@app.post("/ask/")
async def ask_question(request: QuestionRequest):
    if vectors is None:
        return {"error": "Vectors not loaded. Upload documents first."}
    retriever = vectors.as_retriever()
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    response = retrieval_chain.invoke({"input": request.question})
    return {"answer": response["answer"], "context": response["context"]}
