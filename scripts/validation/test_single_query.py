#!/usr/bin/env python3
"""
Single Query Testing Helper

Simple script to test individual queries interactively and see detailed results.

Usage:
    python test_single_query.py
    python test_single_query.py --query "Your query here"
"""

import argparse
import json
import requests
import sys
from datetime import datetime

API_URL = "http://localhost:8000"

# Sample queries for quick testing
SAMPLE_QUERIES = {
    "1": ("Table", "How many matches in the World Cup ended in a draw?"),
    "2": ("Table", "Which team won the most matches in the dataset?"),
    "3": ("Table", "List all Semi-final matches with scores"),
    "4": ("Text", "What is the historical significance of the FIFA World Cup?"),
    "5": ("Text", "How did World War II affect the World Cup schedule?"),
    "6": ("Text", "What factors contributed to certain teams' dominance?"),
    "7": ("Hybrid", "Which team won the 1950 World Cup Final and what was historically significant?"),
    "8": ("Hybrid", "Tell me about Brazil's performance in 1970 with match results and context."),
    "9": ("Hybrid", "What were the top-scoring teams in the 1930s and what factors influenced their success?"),
}

def check_api_health():
    """Check if API is accessible"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy\n")
            return True
        else:
            print(f"⚠️  API returned status {response.status_code}\n")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API at {API_URL}")
        print(f"   Error: {e}\n")
        print("   Make sure backend is running:")
        print("   uvicorn app:app --reload --port 8000\n")
        return False

def query_api(query_text: str):
    """Send query to API and return response"""
    print(f"\n{'='*80}")
    print(f"📤 QUERY: {query_text}")
    print(f"{'='*80}\n")
    
    print("⏳ Sending query to HybridRAG...\n")
    
    try:
        start_time = datetime.now()
        response = requests.post(
            f"{API_URL}/api/chat",
            json={"message": query_text},
            timeout=120
        )
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract information
            answer = data.get("answer", "No answer provided")
            classification = data.get("classification", data.get("metadata", {}).get("classification", "Unknown"))
            
            # Display results
            print(f"✅ RESPONSE RECEIVED ({response_time:.2f}s)\n")
            print(f"{'─'*80}")
            print(f"📊 CLASSIFICATION: {classification}")
            print(f"{'─'*80}\n")
            print(f"💬 ANSWER:\n{answer}\n")
            print(f"{'─'*80}\n")
            
            # Show metadata if available
            if "metadata" in data:
                metadata = data["metadata"]
                print(f"📋 METADATA:")
                for key, value in metadata.items():
                    if key != "classification":
                        print(f"   {key}: {value}")
                print()
            
            # Show full JSON for debugging
            print(f"🔍 FULL RESPONSE (JSON):")
            print(json.dumps(data, indent=2))
            print(f"\n{'='*80}\n")
            
            return data
            
        else:
            print(f"❌ ERROR: API returned status {response.status_code}")
            print(f"Response: {response.text}\n")
            return None
            
    except requests.exceptions.Timeout:
        print(f"⏱️  ERROR: Query timed out after 120 seconds\n")
        return None
    except Exception as e:
        print(f"❌ ERROR: {e}\n")
        return None

def interactive_mode():
    """Run in interactive mode"""
    print("\n" + "="*80)
    print(" HYBRIDRAG SINGLE QUERY TESTER ".center(80, "="))
    print("="*80 + "\n")
    
    # Check API health
    if not check_api_health():
        sys.exit(1)
    
    while True:
        # Show menu
        print("📋 SAMPLE QUERIES:")
        print()
        for key, (category, query) in SAMPLE_QUERIES.items():
            print(f"  [{key}] ({category:6s}) {query[:60]}{'...' if len(query) > 60 else ''}")
        print()
        print("  [C] Enter custom query")
        print("  [Q] Quit")
        print()
        
        # Get user choice
        choice = input("Select option: ").strip().upper()
        
        if choice == 'Q':
            print("\n👋 Goodbye!\n")
            break
        
        elif choice == 'C':
            custom_query = input("\nEnter your query: ").strip()
            if custom_query:
                query_api(custom_query)
            else:
                print("⚠️  Empty query, try again\n")
        
        elif choice in SAMPLE_QUERIES:
            category, query = SAMPLE_QUERIES[choice]
            print(f"\n📌 Selected: {category} Query")
            query_api(query)
        
        else:
            print("⚠️  Invalid choice, try again\n")
        
        # Ask to continue
        print()
        cont = input("Test another query? [Y/n]: ").strip().lower()
        if cont in ['n', 'no']:
            print("\n👋 Goodbye!\n")
            break
        print()

def main():
    parser = argparse.ArgumentParser(description="Test single queries against HybridRAG")
    parser.add_argument(
        "--query",
        type=str,
        help="Query text to test (if not provided, runs in interactive mode)"
    )
    parser.add_argument(
        "--api-url",
        default=API_URL,
        help=f"API base URL (default: {API_URL})"
    )
    
    args = parser.parse_args()
    
    # Update API URL if provided
    global API_URL
    API_URL = args.api_url
    
    if args.query:
        # Single query mode
        print("\n" + "="*80)
        print(" HYBRIDRAG SINGLE QUERY TESTER ".center(80, "="))
        print("="*80 + "\n")
        
        if not check_api_health():
            sys.exit(1)
        
        query_api(args.query)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()

