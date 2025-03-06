import json
from tabulate import tabulate
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
from datasets import Dataset
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Qdrant
from langchain.schema import HumanMessage
from dotenv import load_dotenv
import os
from qdrant_client import QdrantClient
from pathlib import Path
from difflib import SequenceMatcher

# Load environment variables
load_dotenv()

def load_test_dataset():
    """Load test dataset from heal_golden_qa_pairs.json"""
    with open('heal_golden_qa_pairs.json', 'r') as f:
        qa_pairs = json.load(f)
    
    # Convert to RAGAS format
    test_data = []
    for pair in qa_pairs:
        test_data.append({
            "question": pair["question"],
            "ground_truth": pair["answer"],
            "context": pair["context"],
            "category": pair["category"]
        })
    return test_data

def load_golden_dataset():
    test_cases_path = Path("heal_golden_qa_pairs.json")
    with open(test_cases_path) as f:
        qa_pairs = json.load(f)
        # Convert existing format to golden dataset format
        return {
            "test_cases": [
                {
                    "query": pair["question"],
                    "protocol_id": "heal_protocol_1.pdf",
                    "expected_response": {
                        "content": pair["answer"],
                        "source_sections": [pair["category"]],
                        "metrics": {
                            "faithfulness": 0.8,
                            "relevancy": 0.95
                        }
                    }
                } for pair in qa_pairs
            ]
        }

def evaluate_rag_system(client, collection_name="combined_embeddings"):
    """Evaluate current RAG system performance"""
    # Load test dataset
    test_data = load_test_dataset()
    print(f"\nEvaluating {len(test_data)} test cases...")
    
    # Initialize components
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    llm = ChatOpenAI(model="gpt-4-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))
    vectorstore = Qdrant(client=client, collection_name=collection_name, embeddings=embeddings)
    
    # Generate predictions
    results = []
    for test_case in test_data:
        print(f"\nProcessing question: {test_case['question'][:50]}...")
        # Get relevant contexts
        contexts = vectorstore.similarity_search(test_case["question"], k=3)
        context_texts = [doc.page_content for doc in contexts]
        
        # Get model answer
        prompt = f"""Question: {test_case['question']}\n\nContext: {' '.join(context_texts)}"""
        answer = llm.predict(prompt)
        print("Got answer from GPT-4")
        
        results.append({
            "question": test_case["question"],
            "contexts": context_texts,
            "answer": answer,
            "ground_truth": test_case["ground_truth"],
            "category": test_case["category"]
        })
    
    # Create dataset for RAGAS
    dataset = Dataset.from_list(results)
    
    # Run evaluation
    scores = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ]
    )
    
    # Add category-wise analysis
    category_scores = {}
    for result in results:
        cat = result["category"]
        if cat not in category_scores:
            category_scores[cat] = []
        category_scores[cat].append(result)
    
    return {
        "overall_scores": scores,
        "category_scores": category_scores,
        "raw_results": results
    }

def save_baseline(client):
    """Save baseline metrics"""
    scores = evaluate_rag_system(client)
    
    # Convert scores to JSON-serializable format
    json_scores = {
        "overall_scores": {
            "faithfulness": float(scores["overall_scores"]["faithfulness"][0]),
            "answer_relevancy": float(scores["overall_scores"]["answer_relevancy"][0]),
            "context_precision": float(scores["overall_scores"]["context_precision"][0]),
            "context_recall": float(scores["overall_scores"]["context_recall"][0])
        },
        "category_scores": {
            category: [
                {
                    "question": r["question"],
                    "answer": r["answer"],
                    "ground_truth": r["ground_truth"]
                } for r in results
            ] for category, results in scores["category_scores"].items()
        }
    }
    
    # Save detailed results
    with open("baseline_metrics.json", "w") as f:
        json.dump(json_scores, f, indent=2)
    
    # Create tables for presentation
    print("\n" + "="*50)
    print("HEAL SYNC RAG System Evaluation")
    print("="*50)
    
    # Overall metrics table
    metrics_table = [
        ["Metric", "Score"],
        ["Faithfulness", f"{scores['overall_scores']['faithfulness'][0]:.3f}"],
        ["Answer Relevancy", f"{scores['overall_scores']['answer_relevancy'][0]:.3f}"],
        ["Context Precision", f"{scores['overall_scores']['context_precision'][0]:.3f}"],
        ["Context Recall", f"{scores['overall_scores']['context_recall'][0]:.3f}"]
    ]
    print("\nOverall Performance Metrics:")
    print(tabulate(metrics_table, headers="firstrow", tablefmt="grid"))
    
    # Category-wise table
    category_table = [["Category", "Questions", "Avg. Relevancy"]]
    for category, results in scores["category_scores"].items():
        avg_relevancy = sum(float(scores['overall_scores']['answer_relevancy'][0]) for _ in results) / len(results)
        category_table.append([
            category.upper(),
            len(results),
            f"{avg_relevancy:.3f}"
        ])
    
    print("\nPerformance by Category:")
    print(tabulate(category_table, headers="firstrow", tablefmt="grid"))

def get_rag_response(query, protocol_id=None):
    """Get response from RAG system"""
    # Initialize components
    llm = ChatOpenAI(model="gpt-4-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))
    client = QdrantClient(url=os.getenv("QDRANT_HOST"), api_key=os.getenv("QDRANT_API_KEY"))
    
    # Search both collections
    results = []
    try:
        # Search original embeddings
        old_store = Qdrant(
            client=client,
            collection_name="combined_embeddings",
            embeddings=OpenAIEmbeddings()
        )
        results.extend(old_store.similarity_search(query, k=3))
        
        # Search fine-tuned embeddings
        new_store = Qdrant(
            client=client,
            collection_name="fine_tuned_embeddings",
            embeddings=HuggingFaceEmbeddings(
                model_name="lsy9874205/heal-protocol-embeddings",
                cache_folder="/tmp/embeddings_cache"
            )
        )
        results.extend(new_store.similarity_search(query, k=3))
    except Exception as e:
        print(f"Search error: {str(e)}")
    
    # Format context and get response
    if results:
        context = "\n".join([r.page_content for r in results])
        prompt = f"""You are analyzing clinical research protocols.
        
        Context: {context}
        
        Question: {query}
        
        Answer based ONLY on the provided context:"""
        
        response = llm([HumanMessage(content=prompt)])
        return response.content
    return "No relevant information found."

def compare_faithfulness(actual, expected):
    """Compare faithfulness of response to expected answer"""
    # Use sequence matcher for similarity
    matcher = SequenceMatcher(None, 
        actual.lower().strip(), 
        expected["content"].lower().strip()
    )
    return matcher.ratio()

def compare_relevancy(actual, expected):
    """Check if response contains key points from expected answer"""
    # Convert expected content to lowercase for comparison
    actual_lower = actual.lower()
    expected_lower = expected["content"].lower()
    
    # Split into key points (assuming numbered or bulleted lists)
    expected_points = [p.strip() for p in expected_lower.split("\n") if p.strip()]
    
    # Count how many key points are covered
    points_covered = sum(1 for point in expected_points if point in actual_lower)
    return points_covered / len(expected_points) if expected_points else 0

def evaluate_against_golden_dataset():
    test_cases = load_golden_dataset()
    results = []
    
    for case in test_cases["test_cases"]:
        # Get response from your RAG system
        response = get_rag_response(case["query"], case["protocol_id"])
        
        # Compare with expected response
        metrics = {
            "faithfulness": compare_faithfulness(response, case["expected_response"]),
            "relevancy": compare_relevancy(response, case["expected_response"]),
            "matches_expected": response.strip() == case["expected_response"]["content"].strip()
        }
        
        results.append({
            "query": case["query"],
            "expected": case["expected_response"]["content"],
            "actual": response,
            "metrics": metrics
        })
    
    # Print evaluation results
    print("\n=== Golden Dataset Evaluation Results ===\n")
    for result in results:
        print(f"Query: {result['query']}")
        print(f"Metrics: Faithfulness={result['metrics']['faithfulness']:.2f}, " 
              f"Relevancy={result['metrics']['relevancy']:.2f}")
        print("Expected:", result['expected'][:100] + "...")
        print("Actual:", result['actual'][:100] + "...")
        print("-" * 80 + "\n")
    
    return results

if __name__ == "__main__":
    # Initialize Qdrant client
    QDRANT_HOST = os.getenv("QDRANT_HOST")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    
    # Remove :6333 from host if present
    base_url = QDRANT_HOST.split(':6333')[0]
    if not base_url.startswith('https://'):
        base_url = f"https://{base_url}"
    
    client = QdrantClient(url=base_url, api_key=QDRANT_API_KEY)
    
    # Run and save baseline evaluation
    save_baseline(client) 