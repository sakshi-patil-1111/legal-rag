import asyncio
import json
import logging
import os
import sys

# Ensure app is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.kanoon_service import KanoonService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

from app.database.database import get_db

async def run_benchmark():
    benchmark_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "benchmark_suite.json")
    with open(benchmark_file, "r", encoding="utf-8") as f:
        queries = json.load(f)
        
    kanoon_service = KanoonService()
    db = next(get_db())
    
    results = []
    total = len(queries)
    passed = 0
    
    logger.info(f"Starting Benchmark Evaluation for {total} queries...")
    
    for i, item in enumerate(queries):
        query = item["query"]
        expected_statutes = item["expected_statutes"]
        
        logger.info(f"[{i+1}/{total}] Query: {query}")
        
        try:
            from app.schemas.kanoon import KanoonQueryRequest
            request = KanoonQueryRequest(question=query, conversation_id=None)
            response = kanoon_service.query(request=request, user_id="benchmark_user", db=db)
            answer_text = response.answer
            
            # Simple evaluation: Did the answer cite the expected statute?
            missing_statutes = []
            for statute in expected_statutes:
                if statute.lower() not in answer_text.lower() and statute.replace("_", " ").lower() not in answer_text.lower():
                    missing_statutes.append(statute)
                    
            if not missing_statutes:
                logger.info(f" -> PASS")
                passed += 1
                status = "PASS"
            else:
                logger.error(f" -> FAIL (Missing expected authorities: {missing_statutes})")
                status = "FAIL"
                
            results.append({
                "query": query,
                "status": status,
                "expected": expected_statutes,
                "missing": missing_statutes
            })
            
        except Exception as e:
            logger.error(f" -> ERROR: {e}")
            results.append({
                "query": query,
                "status": "ERROR",
                "error": str(e)
            })
            
    accuracy = (passed / total) * 100
    logger.info("================================================")
    logger.info(f"Benchmark Complete. Score: {passed}/{total} ({accuracy:.1f}%)")
    logger.info("================================================")
    
    report_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "benchmark_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({
            "accuracy": accuracy,
            "passed": passed,
            "total": total,
            "results": results
        }, f, indent=4)
        
    logger.info(f"Report saved to {report_file}")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
