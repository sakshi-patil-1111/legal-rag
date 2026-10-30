import json
import os
import threading

METRICS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "metrics.json")

class MetricsTracker:
    def __init__(self):
        self.lock = threading.Lock()
        self.metrics = {
            "request_count": 0,
            "upload_failures": 0,
            "retrieval_failures": 0,
            "llm_failures": 0,
            "total_retrieval_latency_ms": 0.0,
            "total_generation_latency_ms": 0.0,
            "total_embedding_latency_ms": 0.0,
            "total_bm25_latency_ms": 0.0,
            "total_vector_latency_ms": 0.0,
            "total_pipeline_latency_ms": 0.0,
            "retrieval_count": 0,
            "generation_count": 0,
            "pipeline_count": 0
        }
        self.load()

    def load(self):
        if os.path.exists(METRICS_FILE):
            try:
                with open(METRICS_FILE, 'r') as f:
                    data = json.load(f)
                    for k, v in data.items():
                        self.metrics[k] = v
            except:
                pass

    def save(self):
        os.makedirs(os.path.dirname(METRICS_FILE), exist_ok=True)
        with open(METRICS_FILE, 'w') as f:
            json.dump(self.metrics, f, indent=4)

    def record_request(self):
        with self.lock:
            self.metrics["request_count"] += 1

    def record_failure(self, failure_type: str):
        with self.lock:
            if failure_type in self.metrics:
                self.metrics[failure_type] += 1

    def record_latency(self, metric: str, latency_ms: float):
        with self.lock:
            if f"total_{metric}_latency_ms" in self.metrics:
                self.metrics[f"total_{metric}_latency_ms"] += latency_ms
                count_key = metric if metric in ["pipeline", "retrieval", "generation"] else "pipeline"
                if f"{count_key}_count" in self.metrics:
                    self.metrics[f"{count_key}_count"] += 1

    def get_snapshot(self):
        with self.lock:
            m = self.metrics.copy()
            rc = m["retrieval_count"] or 1
            gc = m["generation_count"] or 1
            pc = m["pipeline_count"] or 1
            
            return {
                "request_count": m["request_count"],
                "active_users": 0, # Will be fetched from DB dynamically
                "failures": {
                    "upload": m["upload_failures"],
                    "retrieval": m["retrieval_failures"],
                    "llm": m["llm_failures"]
                },
                "latencies_ms": {
                    "average_retrieval": m["total_retrieval_latency_ms"] / rc,
                    "average_generation": m["total_generation_latency_ms"] / gc,
                    "average_embedding": m["total_embedding_latency_ms"] / rc,
                    "average_bm25": m["total_bm25_latency_ms"] / rc,
                    "average_vector_search": m["total_vector_latency_ms"] / rc,
                    "average_pipeline": m["total_pipeline_latency_ms"] / pc
                }
            }

global_metrics = MetricsTracker()
