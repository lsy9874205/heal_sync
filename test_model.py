from sentence_transformers import SentenceTransformer
import os

def test_embeddings():
    """Test if our fine-tuned model works"""
    print("\nChecking for model...")
    if not os.path.exists("heal-embeddings"):
        print("Error: heal-embeddings directory not found!")
        return
        
    try:
        print("Loading model...")
        model = SentenceTransformer("heal-embeddings")
        
        # Test pairs
        test_pairs = [
            ("Inclusion Criteria", "Adult patients aged 18-65 years with chronic pain"),
            ("Study Design", "This is a randomized controlled trial"),
            ("Primary Endpoint", "The primary outcome measure is pain reduction")
        ]
        
        print("\nTesting embeddings...")
        for text1, text2 in test_pairs:
            # Get embeddings
            emb1 = model.encode(text1)
            emb2 = model.encode(text2)
            
            # Calculate similarity
            similarity = model.cosine_sim(emb1, emb2)
            print(f"\nSimilarity between:\n'{text1}' and\n'{text2}':\n{similarity:.4f}")
            
        print("\nModel test complete!")
        
    except Exception as e:
        print(f"Error testing model: {str(e)}")

if __name__ == "__main__":
    test_embeddings() 