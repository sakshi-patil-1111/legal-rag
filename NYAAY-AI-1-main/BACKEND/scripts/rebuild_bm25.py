import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.knowledge.bm25_manager import bm25_manager

if __name__ == '__main__':
    bm25_manager.rebuild_index("global")
