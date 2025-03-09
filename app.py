import os
import json
import streamlit as st
import pdfplumber
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Qdrant
from langchain.schema import HumanMessage
from qdrant_client import QdrantClient, models
import requests

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
QDRANT_HOST = os.getenv("QDRANT_HOST", "").strip()
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "").strip()

if not openai_api_key or not QDRANT_HOST or not QDRANT_API_KEY:
    st.error("Missing environment variables. Check your API keys.")
    st.stop()

# Connect to Qdrant Cloud
client = QdrantClient(url=QDRANT_HOST, api_key=QDRANT_API_KEY)
COLLECTION_NAME = "fine_tuned_embeddings"
VECTOR_DIMENSION = 384

# Ensure Qdrant collection exists
try:
    client.get_collection(COLLECTION_NAME)
except Exception:
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=VECTOR_DIMENSION, distance=models.Distance.COSINE),
    )

# Streamlit UI
st.title("HEAL SYNC: Clinical Protocol Analyzer")
uploaded_file = st.file_uploader("Upload a clinical protocol (PDF ONLY)", type=["pdf"])

def extract_text_and_tables(pdf_path):
    extracted_text = ""
    extracted_tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
            
            tables = page.extract_tables()
            for table in tables:
                json_table = json.dumps(table)  # Store as JSON for structured retrieval
                extracted_tables.append(json_table)
    return extracted_text, extracted_tables

if uploaded_file:
    with st.spinner("Processing PDF..."):
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        text, tables = extract_text_and_tables("temp.pdf")
        os.remove("temp.pdf")
        
        if not text.strip() and not tables:
            st.error("No readable content found in the PDF.")
            st.stop()
        
        chunks = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200).split_text(text)
        table_chunks = [RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200).split_text(tbl) for tbl in tables]
        chunks.extend([item for sublist in table_chunks for item in sublist])
        
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'}, encode_kwargs={'normalize_embeddings': True})
        points = []
        for i, chunk in enumerate(chunks):
            vector = embeddings.embed_query(chunk)
            points.append(models.PointStruct(id=i, vector=vector, payload={"content": chunk, "type": "text", "source": uploaded_file.name}))
        
        for i, table_json in enumerate(tables):
            vector = embeddings.embed_query(table_json)
            points.append(models.PointStruct(id=len(chunks) + i, vector=vector, payload={"content": table_json, "type": "table", "source": uploaded_file.name}))
        
        if points:
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            st.success("Document is ready for questions!")

query = st.text_input("Ask a question about your uploaded protocol:", placeholder="E.g., What data elements are collected?")

def search_protocol(query, file_name):
    store = Qdrant(client=client, collection_name=COLLECTION_NAME, embeddings=embeddings)
    
    text_results = store.similarity_search(query, k=6, filter=models.Filter(
        must=[models.FieldCondition(key="source", match=models.MatchValue(value=file_name)),
              models.FieldCondition(key="type", match=models.MatchValue(value="text"))]
    ))
    
    table_results = store.similarity_search(query, k=6, filter=models.Filter(
        must=[models.FieldCondition(key="source", match=models.MatchValue(value=file_name)),
              models.FieldCondition(key="type", match=models.MatchValue(value="table"))]
    ))
    
    return [res.page_content for res in text_results] + [res.page_content for res in table_results]

if query and uploaded_file:
    with st.spinner("Searching..."):
        results = search_protocol(query, uploaded_file.name)
        if results:
            context = "\n".join(results)
            prompt = f"""
            Extract all data elements collected in this study. Use the following structure:
            
            - **Domain**: (e.g., Pain Intensity, Sleep)
            - **Assessment Tool**: (e.g., NRS-11, PROMIS)
            - **Timepoints**: (e.g., Baseline, Week 6, Follow-up)
            - **Definition**: (e.g., Measure of sleep disturbance)
            
            Do NOT say \"no data elements found\" if a table exists. Instead, parse and format the table.
            
            Document excerpts:
            {context}
            Question: {query}
            """
            
            openai_client = ChatOpenAI(api_key=openai_api_key, model="gpt-4")
            response = openai_client([HumanMessage(content=prompt)])
            st.write(response.content)
        else:
            st.warning("No relevant content found.")