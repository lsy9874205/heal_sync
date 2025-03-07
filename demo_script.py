import streamlit as st
import time

def demo_heal_sync():
    """
    Demo script for HEAL SYNC presentation
    """
    
    # 1. Introduction
    st.markdown("""
    # HEAL SYNC Demo
    
    This demo will showcase:
    1. Protocol Upload & Processing
    2. Question Answering with Fine-tuned Embeddings
    3. Comparison with OpenAI Embeddings
    """)
    time.sleep(3)  # Pause for narration

    # 2. Upload Protocol
    st.markdown("### Step 1: Upload a Clinical Protocol")
    st.write("Let's upload a sample protocol PDF...")
    
    # Show sample questions
    st.markdown("""
    ### Step 2: Example Questions to Ask
    
    Try these questions:
    1. "What are the inclusion criteria?"
    2. "How is patient safety monitored?"
    3. "What data is collected at follow-up visits?"
    """)
    time.sleep(2)

    # 3. Show Search Process
    st.markdown("### Step 3: Search Results")
    st.write("Notice how the system:")
    st.write("- Searches both embedding collections")
    st.write("- Combines results for better coverage")
    st.write("- Provides context-aware responses")
    time.sleep(2)

    # 4. Compare Results
    st.markdown("""
    ### Step 4: Performance Comparison
    
    | Metric | OpenAI | Fine-tuned | Change |
    |--------|--------|------------|---------|
    | Faithfulness | 0.667 | 0.833 | ⬆️ +0.166 |
    | Answer Relevancy | 0.986 | 0.986 | = |
    | Context Precision | 1.000 | 1.000 | = |
    | Context Recall | 1.000 | 0.000 | ⬇️ -1.000 |
    """)

    # 5. Key Features
    st.markdown("""
    ### Key Features Demonstrated
    
    1. ✅ PDF Processing & Chunking
    2. ✅ Dual Embedding Search
    3. ✅ Context-Aware Responses
    4. ✅ Error Handling
    5. ✅ Performance Metrics
    """)

if __name__ == "__main__":
    demo_heal_sync() 