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
from langchain.chat_models import OpenAI

# Load environment variables
load_dotenv()
openai_api_key = (os.getenv("OPENAI_API_KEY") or os.getenv("openai_api_key", "")).strip()
QDRANT_HOST = (os.getenv("QDRANT_HOST") or os.getenv("qdrant_host", "")).strip()
QDRANT_API_KEY = (os.getenv("QDRANT_API_KEY") or os.getenv("qdrant_api_key", "")).strip()

# Ensure required environment variables are set
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
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=300)
            chunks = splitter.split_text(text)
            st.write(f"Created {len(chunks)} chunks from the PDF")

            # Set cache directory to a writable location
            os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
            os.environ['HF_HOME'] = '/tmp/huggingface'

            # Initialize embeddings with explicit cache location
            embeddings = HuggingFaceEmbeddings(
                model_name="lsy9874205/heal-protocol-embeddings",
                cache_folder="/tmp/embeddings_cache"
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
                    st.write(f"Stored {len(points)} chunks in Qdrant")
                    st.success("PDF processed successfully")
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

# In your OpenAI client configuration
client = OpenAI(
    api_key=openai_api_key,
    default_model=OPENAI_MODEL  # Set the default model
)

# Initialize embeddings outside the file upload block
embeddings = HuggingFaceEmbeddings(
    model_name="lsy9874205/heal-protocol-embeddings",
    cache_folder="/tmp/embeddings_cache"
)

# Question input
query = st.text_input("Ask a question about your document:")

# When searching, try both collections
def search_all_collections(query, embeddings):
    results = []
    try:
        st.write("Searching original embeddings collection...")
        # Search old collection with OpenAI embeddings
        old_store = Qdrant(
            client=client,
            collection_name=OLD_COLLECTION,
            embeddings=OpenAIEmbeddings()
        )
        old_results = old_store.similarity_search(query, k=6)
        st.write(f"Found {len(old_results)} results in original embeddings")
        results.extend(old_results)
        
        st.write("Searching fine-tuned embeddings collection...")
        # Search new collection with fine-tuned embeddings
        new_store = Qdrant(
            client=client,
            collection_name=COLLECTION_NAME,
            embeddings=embeddings
        )
        new_results = new_store.similarity_search(query, k=6)
        st.write(f"Found {len(new_results)} results in fine-tuned embeddings")
        results.extend(new_results)
    except Exception as e:
        st.error(f"Search error: {str(e)}")
    return results

if query:
    with st.spinner("Searching for answers..."):
        if uploaded_file:  # If a document is uploaded, use RAG
            results = search_all_collections(query, embeddings)

            # Ensure valid retrieved results
            cleaned_results = [res.page_content for res in results if hasattr(res, "page_content") and res.page_content]

            if not cleaned_results:
                # Fallback to general LLM response
                fallback_prompt = f"""You are an AI assistant for the HEAL Research Dissemination Center.
                The user has asked a question about a clinical research protocol, but I couldn't find relevant sections in the document.
                
                Please provide a general response about how this topic typically appears in clinical protocols.
                If the question is completely unrelated to clinical protocols, politely redirect the user.
                
                Question: {query}
                """
                response = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": fallback_prompt}],
                    temperature=0.7,
                    max_tokens=None,  # GPT-4 Turbo will automatically optimize
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                st.write("### SYNC Response (General Knowledge):")
                st.write("I couldn't find specific information about this in your protocol, but here's a general response:")
                st.write(response.choices[0].message.content)
            else:
                # Format retrieved text
                context = "\n".join(cleaned_results)

                # Send context + query to LLM
                prompt = f"""You are an AI assistant analyzing clinical research protocols for the HEAL Research Dissemination Center.
                You have access to sections of a research protocol document.
                
                When answering questions:
                1. Focus on the specific details found in the protocol
                2. Reference relevant sections (like Methods, Eligibility, etc.)
                3. Be precise about what the protocol states
                4. If information isn't in the provided sections, say "That information isn't in the sections I can access"
                
                Current protocol sections:
                {context}
                
                Question: {query}
                
                Answer based ONLY on the protocol sections above:"""
                response = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=None,  # GPT-4 Turbo will automatically optimize
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )

                # Display response
                st.write("### SYNC Response:")
                st.write(response.choices[0].message.content)
        else:  # No document uploaded, use general chat
            general_prompt = f"""You are an AI assistant for the HEAL Research Dissemination Center.
            You help users understand clinical research protocols and common data elements.
            
            Question: {query}
            
            Provide a helpful response about clinical protocols or HEAL Initiative topics:"""
            
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": general_prompt}],
                temperature=0.7,
                max_tokens=None,  # GPT-4 Turbo will automatically optimize
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            st.write("### SYNC Response:")
            st.write(response.choices[0].message.content)
