import os
import sys

# Ensure app is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.corpus.manifest import CorpusManifestManager

def print_health_report():
    manager = CorpusManifestManager()
    manifest = manager.manifest
    stats = manifest.get("corpus_stats", {})
    acts = manifest.get("acts", {})
    
    total_acts_target = 134 # Target from our Phase B plan
    current_acts = stats.get("total_acts", 0)
    percent = (current_acts / total_acts_target) * 100 if total_acts_target else 0
    
    total_chunks = stats.get("total_chunks", 0)
    domains_covered = len(stats.get("domains_covered", []))
    batches_completed = len(stats.get("batches_completed", []))
    
    # Calculate avg quality score
    scores = [a.get("quality_score", 0) for a in acts.values() if a.get("quality_score")]
    avg_quality = sum(scores) / len(scores) if scores else 0
    
    last_update = manifest.get("last_updated", "Unknown")
    version = f"v{batches_completed}.{current_acts}"
    
    # Needs review count
    needs_review = sum(1 for a in acts.values() if a.get("quality_score", 100) < 70)
    
    print("========================================================")
    print("||         NYAAY AI Corpus Health Report              ||")
    print("========================================================")
    print(f"|| Total Acts          | {current_acts} / {total_acts_target} ({percent:.1f}%)".ljust(54) + "||")
    print(f"|| Total Chunks        | {total_chunks}".ljust(54) + "||")
    print(f"|| Domains Covered     | {domains_covered} / 17".ljust(54) + "||")
    print(f"|| Batches Completed   | {batches_completed} / 13".ljust(54) + "||")
    print(f"|| Quality Score (avg) | {avg_quality:.1f} / 100".ljust(54) + "||")
    print(f"|| Last Updated        | {last_update[:10]}".ljust(54) + "||")
    print(f"|| Corpus Version      | {version}".ljust(54) + "||")
    print("========================================================")
    print(f"|| Acts Needing Review | {needs_review}".ljust(54) + "||")
    print(f"|| Duplicate Flags     | {0} (Placeholder)".ljust(54) + "||")
    print(f"|| Integrity Issues    | {0} (Placeholder)".ljust(54) + "||")
    print("========================================================")

if __name__ == "__main__":
    print_health_report()
