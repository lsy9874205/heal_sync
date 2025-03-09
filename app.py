import os
import streamlit as st
from pypdf import PdfReader  # More reliable PDF extraction
import tempfile
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Qdrant
from langchain.schema import HumanMessage
from qdrant_client import QdrantClient, models
import requests
from openai import OpenAI
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables
load_dotenv()
openai_api_key = (os.getenv("OPENAI_API_KEY") or os.getenv("openai_api_key", "")).strip()
QDRANT_HOST = (os.getenv("QDRANT_HOST") or os.getenv("qdrant_host", "")).strip()
QDRANT_API_KEY = (os.getenv("QDRANT_API_KEY") or os.getenv("qdrant_api_key", "")).strip()

if not openai_api_key or not QDRANT_HOST or not QDRANT_API_KEY:
    st.error("Missing environment variables. Check your API keys.")
    st.stop()

# Verify Qdrant connection with correct headers
headers = {
    "api-key": QDRANT_API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

try:
    # Remove trailing :6333 if present in QDRANT_HOST and ensure https://
    base_url = QDRANT_HOST.split(':6333')[0]
    if not base_url.startswith('https://'):
        base_url = f"https://{base_url}"
    
    response = requests.get(f"{base_url}/collections", headers=headers, verify=True)
    if response.status_code != 200:
        st.error(f"Qdrant connection failed: {response.status_code} - {response.text}")
        st.error(f"Response headers: {response.headers}")
        st.stop()
except requests.exceptions.RequestException as e:
    st.error(f"Qdrant connection error: {str(e)}")
    st.error(f"Attempted URL: {base_url}")
    st.error(f"Headers used: {headers}")
    st.stop()

# Connect to Qdrant Cloud explicitly with API key
client = QdrantClient(url=base_url, api_key=QDRANT_API_KEY)

# Define collection details
OLD_COLLECTION = "combined_embeddings"     # OpenAI embeddings (1536 dimensions)
COLLECTION_NAME = "fine_tuned_embeddings"  # Fine-tuned model (384 dimensions)
VECTOR_DIMENSION = 384    # For fine-tuned embeddings

# Get the current count of vectors to use as starting ID for new uploads
try:
    collection_info = client.get_collection(COLLECTION_NAME)
    next_id = collection_info.points_count
except Exception:
    next_id = 0

# Ensure Qdrant collection exists
try:
    collection_info = client.get_collection(COLLECTION_NAME)
except Exception:
    st.warning(f"Collection `{COLLECTION_NAME}` not found. Creating it now...")
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=VECTOR_DIMENSION, distance=models.Distance.COSINE),
    )
    st.success(f"Collection `{COLLECTION_NAME}` created!")

# Streamlit UI
st.markdown(
    """
    <h1 style='text-align: center;'>
        <div style='display: flex; flex-direction: column; align-items: center; justify-content: center;'>
            <span style='font-size: 1.2em; letter-spacing: 0.1em;'>HEAL SYNC</span>
            <span style='font-size: 0.5em; font-weight: 300; color: #808080; letter-spacing: 0.05em; margin-top: 0.5em;'>
                (structuring, yielding, normalizing, crosswalk)
            </span>
        </div>
    </h1>
    <p style='text-align: center;'>Upload a protocol (PDF ONLY) and ask questions about its content.</p>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader("Drag and drop a PDF here", type=["pdf"])

if uploaded_file:
    with st.spinner("Processing PDF..."):
        try:
            # Save file to temporary storage
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            # Extract text using pypdf instead of PyMuPDF
            try:
                reader = PdfReader(tmp_file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            except Exception as pdf_error:
                st.error(f"Error reading PDF: {str(pdf_error)}")
                os.remove(tmp_file_path)
                st.stop()

            if not text.strip():
                st.error("The uploaded PDF contains no readable text.")
                os.remove(tmp_file_path)
                st.stop()

            # Chunk text
            splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
            chunks = splitter.split_text(text)
            st.write(f"📄 Analyzing {len(chunks)} sections (chunks) of your document...")

            # Set cache directory to a writable location
            os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
            os.environ['HF_HOME'] = '/tmp/huggingface'

            # Update embeddings to use a model that outputs 384 dimensions
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",  # This model outputs 384d vectors
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )

            # Embed and store in Qdrant with better error handling
            try:
                points = []
                for i, chunk in enumerate(chunks):
                    try:
                        vector = embeddings.embed_query(chunk)  # Now using OpenAI embeddings
                        points.append(
                            models.PointStruct(
                                id=next_id + i,
                                vector=vector,
                                payload={
                                    "page_content": chunk,
                                    "source": uploaded_file.name,
                                    "type": "user_upload"
                                }
                            )
                        )
                    except Exception as embed_error:
                        st.error(f"Error embedding chunk {i}: {str(embed_error)}")
                        continue

                if points:
                    client.upsert(collection_name=COLLECTION_NAME, points=points)
                    st.write(f"🔍 Indexing {len(points)} document sections for quick search...")
                    st.success("✨ Your document is ready for questions!")
                else:
                    st.error("No valid embeddings were created")

            except Exception as qdrant_error:
                st.error(f"Qdrant storage error: {str(qdrant_error)}")
                st.error("Request details:")
                st.json({
                    "collection": COLLECTION_NAME,
                    "num_points": len(points) if 'points' in locals() else 0,
                    "vector_dim": VECTOR_DIMENSION
                })

        except Exception as e:
            st.error(f"General error: {str(e)}")
        finally:
            # Cleanup temp file
            if 'tmp_file_path' in locals():
                os.remove(tmp_file_path)

# Initialize LLM
OPENAI_MODEL = "gpt-4-0125-preview"  # Latest GPT-4 Turbo with 128k context

# If you want to provide model options:
AVAILABLE_MODELS = {
    "gpt-4-0125-preview": {
        "name": "GPT-4 Turbo (Latest)",
        "context_length": 128000,
        "description": "Most capable and up-to-date model"
    },
    "gpt-4-1106-preview": {
        "name": "GPT-4 Turbo",
        "context_length": 128000,
        "description": "Previous Turbo version"
    },
    "gpt-4": {
        "name": "GPT-4",
        "context_length": 8192,
        "description": "Standard GPT-4"
    }
}

# OpenAI client
openai_client = OpenAI(
    api_key=openai_api_key
)

# Separate Qdrant client
qdrant_client = QdrantClient(
    url=QDRANT_HOST,
    api_key=QDRANT_API_KEY
)

# Make sure collection settings match the embedding dimensions
collection_config = {
    "name": "fine_tuned_embeddings",
    "vectors_config": {
        "size": 384,  # Match the embedding dimension
        "distance": "Cosine"
    }
}

# Check if collection exists and recreate if necessary
try:
    qdrant_client.get_collection("fine_tuned_embeddings")
except Exception:
    qdrant_client.recreate_collection(**collection_config)

# Question input
query = st.text_input("Ask a question about your uploaded protocol:", 
    placeholder="Example: What are the inclusion criteria? What data elements are being collected?")

# Keep the HEAL CDE mapping for reference
HEAL_CDE_MAPPING = {
    "Demographics": {
        "standard_name": "Demographics",
        "aliases": ["HEAL required demographics", "demographic variables"],
        "tools": []
    },
    "Pain": {
        "standard_name": "Pain Domain",
        "aliases": ["pain intensity", "pain interference", "pain catastrophizing"],
        "tools": ["BPI", "NRS-11", "PedsQL", "PCS"]
    },
    "Pain Intensity": {
        "standard_name": "Pain Intensity",
        "aliases": ["BPI Intensity", "pain severity", "magnitude of pain"],
        "tools": ["BPI", "NRS-11"]
    },
    "Pain Interference": {
        "standard_name": "Pain Interference",
        "aliases": ["BPI Interference", "effect of pain on daily activities"],
        "tools": ["BPI", "PedsQL"]
    },
    "Physical Function": {
        "standard_name": "Physical Function",
        "aliases": ["Physical Functioning", "Quality of Life", "PedsQL", "physical activity"],
        "tools": ["PedsQL", "PROMIS Physical Function"]
    },
    "Sleep": {
        "standard_name": "Sleep",
        "aliases": ["AWS+Duration", "sleep quality", "sleep disturbance"],
        "tools": ["AWS", "PROMIS Sleep Disturbance"]
    },
    "Pain Catastrophizing": {
        "standard_name": "Pain Catastrophizing",
        "aliases": ["PCS-C", "PCS-P", "pain catastrophizing scale"],
        "tools": ["PCS-C", "PCS-P"]
    },
    "Depression": {
        "standard_name": "Depression",
        "aliases": ["PHQ-8", "PHQ-9", "depressive symptoms"],
        "tools": ["PHQ (Child)", "PHQ (Parent)"]
    },
    "Anxiety": {
        "standard_name": "Anxiety",
        "aliases": ["GAD-2", "GAD-7", "anxiety symptoms"],
        "tools": ["GAD (Child)", "GAD (Parent)"]
    },
    "Treatment Satisfaction": {
        "standard_name": "Global Satisfaction with Treatment",
        "aliases": ["PGIC", "treatment efficacy", "patient global impression of change"],
        "tools": ["PGIC"]
    }
}

# When searching, try both collections
def search_all_collections(query, embeddings, current_file_name):
    results = []
    try:
        st.write("Searching document chunks...")
        new_store = Qdrant(
            client=qdrant_client,
            collection_name=COLLECTION_NAME,
            embeddings=embeddings
        )
        # Add filter to only search chunks from current document
        search_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="source",
                    match=models.MatchValue(value=current_file_name)
                )
            ]
        )
        new_results = new_store.similarity_search(
            query, 
            k=6,
            filter=search_filter  # Add the filter here
        )
        st.write(f"Found {len(new_results)} results in current document")
        results.extend(new_results)
    except Exception as e:
        st.error(f"Search error: {str(e)}")
    return results

# Add the blue styling CSS
st.markdown("""
    <style>
    .stTextInput > div[data-baseweb="input"] > div:first-child {
        transition: border-color 0.3s;
    }
    .stTextInput > div[data-baseweb="input"] > div:first-child[data-loading="true"] {
        border-color: #0066FF !important;
    }
    </style>
""", unsafe_allow_html=True)

# Main query handling
if query:
    with st.spinner("Searching for answers..."):
        if uploaded_file:
            # Check if query appears to be about general HEAL knowledge
            general_heal_keywords = ["HEAL domains", "HEAL Initiative", "CDE", "common data elements"]
            is_general_heal_query = any(keyword.lower() in query.lower() for keyword in general_heal_keywords)

            if is_general_heal_query:
                # Use general HEAL knowledge base directly
                general_prompt = f"""You are an AI assistant for the HEAL Research Dissemination Center.
                Please provide information about the HEAL Initiative, focusing on:
                - Common Data Elements (CDEs)
                - HEAL Domains
                - HEAL Initiative structure and goals
                - Data standards and harmonization
                - Clinical Research Standards
                - HEAL Supplemental Guidance
                
                Question: {query}
                """
                response = openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": general_prompt}],
                    temperature=0.7
                )
                st.write("### Results (HEAL Knowledge Base):")
                st.write(response.choices[0].message.content)
            else:
                # Search document chunks
                results = search_all_collections(query, embeddings, uploaded_file.name)
                cleaned_results = [res.page_content for res in results if hasattr(res, "page_content") and res.page_content]

                if cleaned_results:
                    # Format retrieved text
                    context = "\n".join(cleaned_results)
                    
                    prompt = f"""You are an AI assistant analyzing clinical research protocols for the HEAL Research Dissemination Center.
                    You have access to sections of a research protocol document.
                    
                    When analyzing data collection and assessments:
                    1. First identify any HEAL Common Data Elements (CDEs) and their assessment tools
                    2. Then identify ANY additional data elements, measures, or assessments being collected
                    3. Include timepoints and definitions when available
                    4. Be specific about what's found in the protocol
                    
                    Current protocol sections:
                    {context}
                    
                    Question: {query}
                    
                    Answer based ONLY on the protocol sections above, listing both HEAL-specific and other data elements found."""

                    response = openai_client.chat.completions.create(
                        model=OPENAI_MODEL,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    
                    st.write("### Results:")
                    st.write(response.choices[0].message.content)
                else:
                    # Fallback for no results
                    fallback_prompt = f"""You are an AI assistant for the HEAL Research Dissemination Center.
                    Answer the following question generally, without assuming it's about a protocol:
                    
                    Question: {query}
                    
                    If the question is about HEAL Initiative topics, provide relevant information.
                    If it's a general question, provide a helpful response.
                    If it's completely off-topic, politely redirect the user to HEAL-related topics.
                    """
                    
                    response = openai_client.chat.completions.create(
                        model=OPENAI_MODEL,
                        messages=[{"role": "user", "content": fallback_prompt}],
                        temperature=0.7
                    )
                    st.write("### Results:")
                    st.write(response.choices[0].message.content)

# In your completion function
def get_completion(prompt, model=OPENAI_MODEL):
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in completion: {str(e)}")
        return None

# For Qdrant operations, use qdrant_client
def search_vectors(query_vector):
    try:
        return qdrant_client.search(
            collection_name="fine_tuned_embeddings",
            query_vector=query_vector,
            limit=5
        )
    except Exception as e:
        print(f"Error in vector search: {str(e)}")
        return None
