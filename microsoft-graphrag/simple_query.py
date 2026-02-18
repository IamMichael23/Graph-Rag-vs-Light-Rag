"""
Simple GraphRAG Query Script for GraphRAG 3.x
Run with: python simple_query.py
"""

import subprocess
import sys

# Configuration
ROOT_DIR = "."  # Current directory (already has GraphRAG setup)
METHOD = "global"  # Options: global, local, drift, basic
QUESTION = "What are the top themes in this story?"  # CHANGE THIS

def query_graphrag(question, method="global", root="./ragtest"):
    """Query GraphRAG using CLI"""
    print(f"🔍 Question: {question}")
    print(f"⏳ Running {method} search...\n")

    # Run graphrag query command
    cmd = [
        sys.executable, "-m", "graphrag", "query",
        "--root", root,
        "--method", method,
        question
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Print output
    if result.returncode == 0:
        print("="*80)
        print("ANSWER:")
        print("="*80)
        print(result.stdout)
        print("="*80)
    else:
        print("❌ Error:")
        print(result.stderr)
        print("\nMake sure you've run indexing first:")
        print(f"  python -m graphrag index --root {root}")

    return result

if __name__ == "__main__":
    # Run the query
    query_graphrag(QUESTION, METHOD, ROOT_DIR)
