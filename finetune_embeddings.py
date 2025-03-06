import json
from datasets import Dataset
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import torch
from tqdm import tqdm
from huggingface_hub import login

def load_training_data():
    """Load protocol data for fine-tuning"""
    print("\nLoading processed protocols...")
    with open('processed_protocols.json', 'r') as f:
        protocols = json.load(f)
    
    # Create training pairs
    train_examples = []
    print("\nCreating training pairs...")
    for protocol in tqdm(protocols, desc="Processing protocols"):
        # Create positive pairs (similar content should have similar embeddings)
        if 'sections' in protocol:
            for section in protocol['sections']:
                # Pair section title with content
                train_examples.append(InputExample(
                    texts=[section['title'], section['content']],
                    label=1.0  # Similar
                ))
                
                # Pair with other sections from same protocol (partial similarity)
                for other_section in protocol['sections']:
                    if other_section != section:
                        train_examples.append(InputExample(
                            texts=[section['content'], other_section['content']],
                            label=0.5  # Partially similar
                        ))
    
    print(f"\nCreated {len(train_examples)} training examples")
    return train_examples

def finetune_model(model_name="sentence-transformers/all-MiniLM-L6-v2", output_path="heal-embeddings"):
    # Load base model
    model = SentenceTransformer(model_name)
    
    # Load training data
    train_examples = load_training_data()
    
    # Create data loader
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=32)  # Larger batch size
    
    # Use cosine similarity loss
    train_loss = losses.CosineSimilarityLoss(model)
    
    print(f"\nStarting fine-tuning with {len(train_examples)} examples")
    print("Will save model every 15 minutes")
    
    # Train the model
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=1,
        warmup_steps=100,
        checkpoint_path="checkpoints",
        checkpoint_save_steps=1000,
        output_path=output_path,
        show_progress_bar=True
    )
    
    # Explicitly save the final model
    print("\nSaving final model...")
    model.save(output_path)
    return model

def upload_to_hub(model_path="heal-embeddings", repo_name="lsy9874205/heal-protocol-embeddings"):
    """Upload fine-tuned model to Hugging Face Hub"""
    print("\nUploading model to Hugging Face Hub...")
    
    # Login to Hugging Face
    login()  # Will prompt for token if not already logged in
    
    # Push model to hub
    model = SentenceTransformer(model_path)
    model.push_to_hub(repo_name)
    
    print(f"\nModel uploaded to: https://huggingface.co/{repo_name}")

if __name__ == "__main__":
    model = finetune_model()
    upload_to_hub() 