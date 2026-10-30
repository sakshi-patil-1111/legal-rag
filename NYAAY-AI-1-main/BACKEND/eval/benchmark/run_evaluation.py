import os
import sys
import json
import time
import argparse
import glob
from datetime import datetime

# Ensure Python path includes the backend directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.knowledge.hybrid_retriever import hybrid_retriever
from app.knowledge.embeddings import embedding_service
from app.ai.orchestrator import rag_orchestrator
import logging

logging.basicConfig(level=logging.WARNING)

def run_benchmark(limit=None):
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ground_truth", "qa_dataset.json")
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}")
        return
        
    with open(dataset_path, "r") as f:
        dataset = json.load(f)
        
    if limit and limit < len(dataset):
        dataset = dataset[:limit]
        
    print(f"--- STARTING AI EVALUATION SUITE ---")
    print(f"Dataset: {len(dataset)} queries")
    
    total_queries = len(dataset)
    
    # Retrieval Metrics
    retrieval_applicable_queries = 0
    hit_at_5_count = 0
    sum_true_recall = 0.0
    mrr_sum = 0.0
    
    # Citation Metrics
    citation_applicable_queries = 0
    sum_cit_precision = 0.0
    sum_cit_recall = 0.0
    
    # Performance Metrics
    total_retrieval_lat = 0.0
    total_model_lat = 0.0
    total_retry_lat = 0.0
    total_e2e_lat = 0.0
    
    # Safety / Behavior Metrics
    behavior_correct = 0
    errors = 0
    
    results_log = []

    for i, item in enumerate(dataset):
        query = item.get("query", "")
        expected_sources = item.get("expected_sources", [])
        expected_sections = item.get("expected_sections", [])
        expected_behavior = item.get("expected_behavior", "ANSWER")
        
        print(f"\n[{i+1}/{total_queries}] Evaluating: {query}")
        
        try:
            # Trigger full pipeline (latency metrics are now inside)
            response = rag_orchestrator.trigger_pipeline(query, task_type="QA")
            
            metrics = response.get("metrics", {})
            r_lat = metrics.get("retrieval_time", 0.0)
            m_lat = metrics.get("model_processing_time", 0.0)
            retry_lat = metrics.get("retry_delay_time", 0.0)
            e2e_lat = metrics.get("total_latency", 0.0)
            
            total_retrieval_lat += r_lat
            total_model_lat += m_lat
            total_retry_lat += retry_lat
            total_e2e_lat += e2e_lat
            
            # --- Evaluate Behavior ---
            actual_answer = response.get("answer", "").lower()
            is_refusal = "violate" in actual_answer or "safety" in actual_answer or "cannot answer" in actual_answer or "refuse" in actual_answer
            is_insufficient = "could not find enough relevant information" in actual_answer or "insufficient" in actual_answer
            
            if expected_behavior == "ANSWER" and not is_refusal and not is_insufficient:
                behavior_correct += 1
            elif expected_behavior == "REFUSE" and is_refusal:
                behavior_correct += 1
            elif expected_behavior == "INSUFFICIENT_CONTEXT" and is_insufficient:
                behavior_correct += 1
                
            # --- Evaluate Retrieval (Only if ANSWER expected) ---
            if expected_behavior == "ANSWER" and len(expected_sources) > 0:
                retrieval_applicable_queries += 1
                
                # Re-run vector search just to get top 5 chunks for pure retrieval eval
                emb = embedding_service.embed_query(query)
                chunks = hybrid_retriever.search(query, emb, n_results=5)
                
                retrieved_sources = set()
                for c in chunks:
                    meta = c.get("metadata", {})
                    src = meta.get("source_name")
                    if src: retrieved_sources.add(src)
                
                expected_set = set(expected_sources)
                
                # Hit Rate @ 5
                if retrieved_sources.intersection(expected_set):
                    hit_at_5_count += 1
                    
                # True Recall @ 5
                recall = len(retrieved_sources.intersection(expected_set)) / len(expected_set)
                sum_true_recall += recall
                
                # MRR
                first_rank = 0
                for rank, c in enumerate(chunks):
                    if c.get("metadata", {}).get("source_name") in expected_set:
                        first_rank = rank + 1
                        break
                if first_rank > 0:
                    mrr_sum += (1.0 / first_rank)
                    
            # --- Evaluate Citation ---
            if expected_behavior == "ANSWER" and len(expected_sources) > 0:
                citation_applicable_queries += 1
                
                generated_citations = response.get("citations", [])
                cited_sources = set()
                for cit in generated_citations:
                    src = cit.get("metadata", {}).get("source_name")
                    if src: cited_sources.add(src)
                    
                expected_set = set(expected_sources)
                
                if len(cited_sources) > 0:
                    precision = len(cited_sources.intersection(expected_set)) / len(cited_sources)
                else:
                    precision = 0.0
                    
                cit_recall = len(cited_sources.intersection(expected_set)) / len(expected_set)
                
                sum_cit_precision += precision
                sum_cit_recall += cit_recall
            
            print(f"  -> R-Lat: {r_lat:.2f}s, M-Lat: {m_lat:.2f}s, Retry: {retry_lat:.2f}s")
            
        except Exception as e:
            print(f"  -> Error: {e}")
            errors += 1
            
    # Calculate Final Metrics
    if retrieval_applicable_queries > 0:
        hit_rate_at_5 = (hit_at_5_count / retrieval_applicable_queries) * 100
        true_recall_at_5 = (sum_true_recall / retrieval_applicable_queries) * 100
        mrr = mrr_sum / retrieval_applicable_queries
    else:
        hit_rate_at_5 = 0.0
        true_recall_at_5 = 0.0
        mrr = 0.0
        
    if citation_applicable_queries > 0:
        avg_cit_precision = (sum_cit_precision / citation_applicable_queries) * 100
        avg_cit_recall = (sum_cit_recall / citation_applicable_queries) * 100
        if (avg_cit_precision + avg_cit_recall) > 0:
            avg_cit_f1 = 2 * (avg_cit_precision * avg_cit_recall) / (avg_cit_precision + avg_cit_recall)
        else:
            avg_cit_f1 = 0.0
    else:
        avg_cit_precision = 0.0
        avg_cit_recall = 0.0
        avg_cit_f1 = 0.0
        
    avg_r_lat = total_retrieval_lat / total_queries if total_queries > 0 else 0
    avg_m_lat = total_model_lat / total_queries if total_queries > 0 else 0
    avg_retry_lat = total_retry_lat / total_queries if total_queries > 0 else 0
    avg_e2e_lat = total_e2e_lat / total_queries if total_queries > 0 else 0
    failure_rate = (errors / total_queries) * 100 if total_queries > 0 else 0
    behavior_score = (behavior_correct / total_queries) * 100 if total_queries > 0 else 0
    
    current_metrics = {
        "hit_rate_at_5": hit_rate_at_5,
        "true_recall_at_5": true_recall_at_5,
        "mrr": mrr,
        "citation_precision": avg_cit_precision,
        "citation_recall": avg_cit_recall,
        "citation_f1": avg_cit_f1,
        "behavior_score": behavior_score,
        "avg_retrieval_latency": avg_r_lat,
        "avg_model_latency": avg_m_lat,
        "avg_retry_latency": avg_retry_lat,
        "avg_e2e_latency": avg_e2e_lat,
        "failure_rate": failure_rate
    }
    
    timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    report_data = {
        "timestamp": timestamp,
        "corpus_version": "1.0",
        "model_used": "gemini-2.5-flash",
        "embedding_model": "all-MiniLM-L6-v2",
        "dataset_size": total_queries,
        "metrics": current_metrics
    }
    
    # Save Report
    history_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "history")
    os.makedirs(history_dir, exist_ok=True)
    report_file = os.path.join(history_dir, f"{timestamp}.json")
    with open(report_file, "w") as f:
        json.dump(report_data, f, indent=2)
        
    # Compare with previous
    compare_report = ""
    history_files = sorted(glob.glob(os.path.join(history_dir, "*.json")))
    if len(history_files) > 1:
        prev_file = history_files[-2] # Second to last is the previous
        with open(prev_file, "r") as f:
            prev_data = json.load(f)
        prev_metrics = prev_data.get("metrics", {})
        
        compare_report += "\n## Automatic Benchmark Comparison\n"
        compare_report += "| Metric | Current | Previous | Difference | % Improvement |\n"
        compare_report += "| --- | --- | --- | --- | --- |\n"
        
        for k, v in current_metrics.items():
            pv = prev_metrics.get(k, 0.0)
            diff = v - pv
            if pv > 0:
                pct = (diff / pv) * 100
            else:
                pct = 0.0
            # Note: For latency and failure rate, lower is better. 
            if "latency" in k or "failure" in k:
                pct = -pct
                
            compare_report += f"| {k} | {v:.4f} | {pv:.4f} | {diff:+.4f} | {pct:+.2f}% |\n"
    
    report_md = f"""# NYAAY AI - Evaluation Benchmark Report
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Queries Evaluated:** {total_queries}

## Retrieval Quality
* **Hit Rate@5:** {hit_rate_at_5:.2f}%
* **True Recall@5:** {true_recall_at_5:.2f}%
* **Mean Reciprocal Rank (MRR):** {mrr:.4f}

## Citation Quality
* **Citation Precision:** {avg_cit_precision:.2f}%
* **Citation Recall:** {avg_cit_recall:.2f}%
* **Citation F1:** {avg_cit_f1:.2f}%
* **Hallucination Rate:** Not Measured (Reliable groundedness evaluation not yet implemented)

## Performance & Safety
* **Behavior/Safety Score:** {behavior_score:.2f}%
* **Avg Retrieval Latency:** {avg_r_lat:.3f}s
* **Avg Pure Model Latency:** {avg_m_lat:.3f}s
* **Avg Retry Backoff Latency:** {avg_retry_lat:.3f}s
* **Avg Total End-to-End Latency:** {avg_e2e_lat:.3f}s
* **Failure Rate:** {failure_rate:.2f}%
{compare_report}
"""
    
    latest_report_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "latest_benchmark.md")
    with open(latest_report_path, "w") as f:
        f.write(report_md)
        
    print("\n--- BENCHMARK COMPLETE ---")
    print(report_md)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AI Evaluation Benchmark")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of queries for quick regression")
    args = parser.parse_args()
    
    run_benchmark(limit=args.limit)
