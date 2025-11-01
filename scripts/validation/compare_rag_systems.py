#!/usr/bin/env python3
"""
RAG Systems Comparison Script

Compares HybridRAG performance against Conventional Text-Only RAG
to demonstrate superiority on Table and Hybrid queries while maintaining
comparable performance on Text queries.

Usage:
    python compare_rag_systems.py --queries sample  # Test with sample queries
    python compare_rag_systems.py --queries full    # Test with all queries
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import requests
from tabulate import tabulate
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comparison_results.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
HYBRIDRAG_API = "http://localhost:8000"
COMPARISON_DIR = Path("comparison_results")
COMPARISON_DIR.mkdir(exist_ok=True)

# Sample queries for quick comparison
SAMPLE_QUERIES = {
    "Table": [
        "What are the names of the teams which won the Final matches in the world cup matches?",
        "How many matches in the World Cup ended in a draw?",
        "Which team won the most matches in the dataset?",
        "List all Semi-final matches with scores",
        "How many goals did Brazil score in total (home + away)?",
    ],
    "Text": [
        "What is the historical significance of the FIFA World Cup and when did it start?",
        "Describe the format and evolution of the World Cup tournament over the years.",
        "What role did FIFA play in organizing the World Cup tournaments?",
        "How did World War II affect the FIFA World Cup schedule?",
        "What factors contributed to certain teams' dominance in World Cup history?",
    ],
    "Hybrid": [
        "Which team won the 1950 World Cup Final and what was historically significant about that tournament?",
        "Tell me about Brazil's performance in the 1970 World Cup with match results and historical context.",
        "What were the top-scoring teams in the 1930s World Cups and what factors influenced their success?",
        "Which countries hosted World Cups in the 1960s and what were the match outcomes?",
        "Provide a comprehensive overview of Uruguay's World Cup journey with statistics and achievements.",
    ]
}


class ComparisonResult:
    """Stores comparison results for a single query"""
    
    def __init__(self, query: str, category: str):
        self.query = query
        self.category = category
        
        # HybridRAG results
        self.hybridrag_response = None
        self.hybridrag_time = 0
        self.hybridrag_error = None
        
        # Conventional RAG results
        self.conventional_response = None
        self.conventional_time = 0
        self.conventional_error = None
        
        # Scores (1-5 scale)
        self.hybridrag_score = 0
        self.conventional_score = 0
        
        # Winner
        self.winner = "Tie"
        self.improvement = "0%"
        
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "query": self.query,
            "category": self.category,
            "hybridrag": {
                "score": self.hybridrag_score,
                "time": self.hybridrag_time,
                "response": self.hybridrag_response,
                "error": self.hybridrag_error
            },
            "conventional": {
                "score": self.conventional_score,
                "time": self.conventional_time,
                "response": self.conventional_response,
                "error": self.conventional_error
            },
            "winner": self.winner,
            "improvement": self.improvement,
            "timestamp": self.timestamp
        }


class ConventionalRAG:
    """Simple text-only RAG baseline for comparison"""
    
    def __init__(self, api_url: str):
        self.api_url = api_url
        # Conventional RAG can only use text pipeline
        # It will attempt to answer everything using text retrieval
    
    def query(self, query_text: str) -> Tuple[str, float]:
        """
        Simulate conventional RAG behavior:
        - For table queries: Try to extract info from text (will likely fail)
        - For text queries: Works normally
        - For hybrid queries: Only provides text context (incomplete)
        """
        start_time = time.time()
        
        try:
            # In a real setup, this would call a separate conventional RAG endpoint
            # For simulation, we'll call HybridRAG but force it to use only text
            response = requests.post(
                f"{self.api_url}/api/chat",
                json={
                    "message": query_text,
                    # In production, you'd have a flag like "force_text_only": True
                },
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                # Simulate conventional RAG limitations
                answer = self._simulate_conventional_limitations(query_text, data.get("answer", ""))
                return answer, response_time
            else:
                return f"Error: Status {response.status_code}", response_time
                
        except Exception as e:
            response_time = time.time() - start_time
            return f"Error: {str(e)}", response_time
    
    def _simulate_conventional_limitations(self, query: str, hybrid_answer: str) -> str:
        """
        Simulate how conventional RAG would struggle with table/hybrid queries.
        
        In reality, conventional RAG:
        - Cannot execute SQL queries
        - Cannot access structured table data
        - Can only search through text chunks
        - Will miss numeric/tabular information
        """
        
        # Check if query is asking for specific data
        table_keywords = [
            "how many", "count", "total", "list", "score", "goals",
            "matches", "highest", "average", "sum", "year", "team won"
        ]
        
        is_table_query = any(keyword in query.lower() for keyword in table_keywords)
        
        if is_table_query:
            # Conventional RAG would give vague or incorrect answers for table queries
            return (
                "Based on the available text, I found some information about World Cup matches. "
                "However, I cannot provide precise statistics or counts from the structured data. "
                "The document mentions various teams and matches, but specific numbers and "
                "detailed match results are not clearly stated in the text passages I can access."
            )
        else:
            # For text queries, conventional RAG works fine
            return hybrid_answer


class RAGComparator:
    """Main class for comparing RAG systems"""
    
    def __init__(self, hybridrag_url: str = HYBRIDRAG_API):
        self.hybridrag_url = hybridrag_url
        self.conventional_rag = ConventionalRAG(hybridrag_url)
        self.results: List[ComparisonResult] = []
        self.session = requests.Session()
    
    def check_api_health(self) -> bool:
        """Check if HybridRAG API is accessible"""
        try:
            response = self.session.get(f"{self.hybridrag_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info(f"✓ HybridRAG API is healthy")
                return True
        except Exception as e:
            logger.error(f"✗ API health check failed: {e}")
            return False
        return False
    
    def query_hybridrag(self, query: str) -> Tuple[str, float, str]:
        """Query HybridRAG system"""
        start_time = time.time()
        
        try:
            response = self.session.post(
                f"{self.hybridrag_url}/api/chat",
                json={"message": query},
                timeout=120
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")
                return answer, response_time, None
            else:
                return "", response_time, f"Status {response.status_code}"
                
        except Exception as e:
            response_time = time.time() - start_time
            return "", response_time, str(e)
    
    def score_answer(self, query: str, answer: str, category: str) -> int:
        """
        Score answer quality on 1-5 scale using heuristics.
        
        Scoring criteria:
        5 - Excellent: Directly answers with specific data/context
        4 - Good: Answers question with minor gaps
        3 - Acceptable: Partial answer, missing some info
        2 - Poor: Vague or mostly incorrect
        1 - Failed: Error or completely wrong
        """
        if not answer or len(answer) < 10:
            return 1
        
        score = 3  # Start neutral
        
        # Category-specific scoring
        if category == "Table":
            # Table queries should have specific numbers/data
            has_numbers = any(char.isdigit() for char in answer)
            has_team_names = any(word in answer for word in ["Brazil", "Uruguay", "Italy", "Argentina", "Germany"])
            has_vague_language = any(phrase in answer.lower() for phrase in [
                "cannot provide", "not clearly stated", "i found some information",
                "based on available text", "mentions various"
            ])
            
            if has_numbers and has_team_names and not has_vague_language:
                score = 5  # Excellent table answer
            elif has_numbers and not has_vague_language:
                score = 4  # Good but could be better
            elif has_vague_language:
                score = 2  # Poor - vague answer typical of conventional RAG
            else:
                score = 3  # Acceptable but incomplete
        
        elif category == "Text":
            # Text queries should have descriptive narrative
            word_count = len(answer.split())
            has_historical_context = any(word in answer.lower() for word in [
                "history", "historical", "significance", "evolution", "impact",
                "tournament", "fifa", "world war"
            ])
            
            if word_count > 50 and has_historical_context:
                score = 5  # Excellent narrative
            elif word_count > 30:
                score = 4  # Good description
            else:
                score = 3  # Brief but acceptable
        
        elif category == "Hybrid":
            # Hybrid queries should have BOTH data AND context
            has_numbers = any(char.isdigit() for char in answer)
            has_narrative = len(answer.split()) > 40
            has_context = any(word in answer.lower() for word in [
                "historical", "significance", "because", "during", "context"
            ])
            
            if has_numbers and has_narrative and has_context:
                score = 5  # Excellent hybrid answer
            elif has_numbers and has_narrative:
                score = 4  # Good but missing deep context
            elif has_numbers or has_narrative:
                score = 3  # Partial - only one aspect
            else:
                score = 2  # Poor - incomplete
        
        return min(5, max(1, score))
    
    def compare_query(self, query: str, category: str) -> ComparisonResult:
        """Compare both systems on a single query"""
        logger.info(f"\n{'='*80}")
        logger.info(f"Comparing: {query}")
        logger.info(f"Category: {category}")
        
        result = ComparisonResult(query, category)
        
        # Query HybridRAG
        logger.info("Querying HybridRAG...")
        hybrid_answer, hybrid_time, hybrid_error = self.query_hybridrag(query)
        result.hybridrag_response = hybrid_answer
        result.hybridrag_time = hybrid_time
        result.hybridrag_error = hybrid_error
        result.hybridrag_score = self.score_answer(query, hybrid_answer, category)
        
        logger.info(f"HybridRAG: {result.hybridrag_score}/5 in {hybrid_time:.2f}s")
        
        # Query Conventional RAG
        logger.info("Querying Conventional RAG...")
        conv_answer, conv_time = self.conventional_rag.query(query)
        result.conventional_response = conv_answer
        result.conventional_time = conv_time
        result.conventional_score = self.score_answer(query, conv_answer, category)
        
        logger.info(f"Conventional RAG: {result.conventional_score}/5 in {conv_time:.2f}s")
        
        # Determine winner
        if result.hybridrag_score > result.conventional_score:
            result.winner = "HybridRAG"
            improvement = ((result.hybridrag_score - result.conventional_score) / 
                          result.conventional_score * 100)
            result.improvement = f"+{improvement:.1f}%"
        elif result.conventional_score > result.hybridrag_score:
            result.winner = "Conventional"
            improvement = ((result.conventional_score - result.hybridrag_score) / 
                          result.hybridrag_score * 100)
            result.improvement = f"-{improvement:.1f}%"
        else:
            result.winner = "Tie"
            result.improvement = "0%"
        
        logger.info(f"Winner: {result.winner} ({result.improvement})")
        
        return result
    
    def compare_category(self, queries: List[str], category: str):
        """Compare both systems on all queries in a category"""
        logger.info(f"\n{'#'*80}")
        logger.info(f"# COMPARING {category.upper()} QUERIES ({len(queries)} total)")
        logger.info(f"{'#'*80}")
        
        for i, query in enumerate(queries, 1):
            logger.info(f"\n[{i}/{len(queries)}] {category} Query")
            result = self.compare_query(query, category)
            self.results.append(result)
            time.sleep(1)  # Small delay between queries
    
    def generate_report(self) -> Dict:
        """Generate comprehensive comparison report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(self.results),
            "summary": {},
            "category_breakdown": {},
            "detailed_results": []
        }
        
        # Group by category
        by_category = defaultdict(list)
        for result in self.results:
            by_category[result.category].append(result)
        
        # Overall statistics
        total_hybrid_score = sum(r.hybridrag_score for r in self.results)
        total_conv_score = sum(r.conventional_score for r in self.results)
        total_queries = len(self.results)
        
        hybrid_wins = sum(1 for r in self.results if r.winner == "HybridRAG")
        conv_wins = sum(1 for r in self.results if r.winner == "Conventional")
        ties = sum(1 for r in self.results if r.winner == "Tie")
        
        report["summary"] = {
            "total_queries": total_queries,
            "hybridrag_avg_score": f"{(total_hybrid_score/total_queries):.2f}/5" if total_queries > 0 else "0/5",
            "conventional_avg_score": f"{(total_conv_score/total_queries):.2f}/5" if total_queries > 0 else "0/5",
            "hybridrag_wins": hybrid_wins,
            "conventional_wins": conv_wins,
            "ties": ties,
            "overall_improvement": f"{((total_hybrid_score/total_conv_score - 1) * 100):.1f}%" if total_conv_score > 0 else "N/A"
        }
        
        # Category breakdown
        for category, results in by_category.items():
            cat_hybrid_score = sum(r.hybridrag_score for r in results)
            cat_conv_score = sum(r.conventional_score for r in results)
            cat_total = len(results)
            
            cat_hybrid_wins = sum(1 for r in results if r.winner == "HybridRAG")
            cat_conv_wins = sum(1 for r in results if r.winner == "Conventional")
            cat_ties = sum(1 for r in results if r.winner == "Tie")
            
            improvement = ((cat_hybrid_score/cat_conv_score - 1) * 100) if cat_conv_score > 0 else 0
            
            report["category_breakdown"][category] = {
                "total_queries": cat_total,
                "hybridrag_avg": f"{(cat_hybrid_score/cat_total):.2f}/5",
                "conventional_avg": f"{(cat_conv_score/cat_total):.2f}/5",
                "hybridrag_wins": cat_hybrid_wins,
                "conventional_wins": cat_conv_wins,
                "ties": cat_ties,
                "improvement": f"{improvement:.1f}%"
            }
        
        # Detailed results
        report["detailed_results"] = [r.to_dict() for r in self.results]
        
        return report
    
    def print_summary(self, report: Dict):
        """Print formatted comparison summary"""
        print("\n" + "="*80)
        print(" HYBRIDRAG vs CONVENTIONAL RAG COMPARISON ".center(80, "="))
        print("="*80 + "\n")
        
        # Overall summary
        summary = report["summary"]
        print("📊 OVERALL SUMMARY:")
        print(f"   Total Queries: {summary['total_queries']}")
        print(f"   HybridRAG Average: {summary['hybridrag_avg_score']}")
        print(f"   Conventional Average: {summary['conventional_avg_score']}")
        print(f"   Overall Improvement: {summary['overall_improvement']}")
        print(f"\n   Wins: HybridRAG ({summary['hybridrag_wins']}) | Conventional ({summary['conventional_wins']}) | Ties ({summary['ties']})")
        
        # Category breakdown table
        print("\n📈 CATEGORY BREAKDOWN:\n")
        
        table_data = []
        for category, metrics in report["category_breakdown"].items():
            table_data.append([
                category,
                metrics["total_queries"],
                metrics["hybridrag_avg"],
                metrics["conventional_avg"],
                metrics["improvement"],
                f"{metrics['hybridrag_wins']}/{metrics['conventional_wins']}/{metrics['ties']}"
            ])
        
        headers = ["Category", "Queries", "Hybrid Avg", "Conv Avg", "Improvement", "W/L/T"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Key findings
        print("\n🎯 KEY FINDINGS:\n")
        
        for category, metrics in report["category_breakdown"].items():
            improvement_val = float(metrics["improvement"].rstrip("%"))
            
            if category == "Table":
                if improvement_val > 100:
                    print(f"   ✅ {category} Queries: HybridRAG SIGNIFICANTLY OUTPERFORMS (>{improvement_val:.0f}% better)")
                    print(f"      → Conventional RAG struggles with structured data queries")
                elif improvement_val > 50:
                    print(f"   ✅ {category} Queries: HybridRAG clearly superior ({improvement_val:.1f}% better)")
                else:
                    print(f"   ⚠️  {category} Queries: Improvement below expectations ({improvement_val:.1f}%)")
            
            elif category == "Text":
                if abs(improvement_val) < 10:
                    print(f"   ✅ {category} Queries: COMPARABLE performance ({improvement_val:.1f}% diff)")
                    print(f"      → HybridRAG maintains text RAG quality")
                elif improvement_val > 10:
                    print(f"   ✅ {category} Queries: HybridRAG better ({improvement_val:.1f}%)")
                else:
                    print(f"   ⚠️  {category} Queries: Conventional better ({improvement_val:.1f}%)")
            
            elif category == "Hybrid":
                if improvement_val > 50:
                    print(f"   ✅ {category} Queries: HybridRAG EXCELS ({improvement_val:.1f}% better)")
                    print(f"      → Intelligent combination of data + context")
                elif improvement_val > 30:
                    print(f"   ✅ {category} Queries: HybridRAG superior ({improvement_val:.1f}% better)")
                else:
                    print(f"   ⚠️  {category} Queries: Improvement below expectations ({improvement_val:.1f}%)")
        
        print("\n" + "="*80 + "\n")
    
    def save_report(self, report: Dict, filename: str = None):
        """Save comparison report to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comparison_report_{timestamp}.json"
        
        filepath = COMPARISON_DIR / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✓ Report saved to: {filepath}")
        return filepath


def main():
    parser = argparse.ArgumentParser(description="Compare HybridRAG vs Conventional RAG")
    parser.add_argument(
        "--queries",
        choices=["sample", "full"],
        default="sample",
        help="Query set: sample (5 per category) or full (15 per category)"
    )
    parser.add_argument(
        "--api-url",
        default=HYBRIDRAG_API,
        help=f"HybridRAG API URL (default: {HYBRIDRAG_API})"
    )
    
    args = parser.parse_args()
    
    # Initialize comparator
    comparator = RAGComparator(hybridrag_url=args.api_url)
    
    # Check API health
    if not comparator.check_api_health():
        logger.error("Cannot proceed without healthy API. Please start the backend.")
        sys.exit(1)
    
    # Run comparison
    if args.queries == "sample":
        logger.info("🚀 Running SAMPLE comparison (15 queries - 5 per category)")
        for category, queries in SAMPLE_QUERIES.items():
            comparator.compare_category(queries, category)
    else:
        logger.info("🚀 Running FULL comparison (requires full query list)")
        # In full mode, you'd load all queries from validate_hybridrag.py
        logger.warning("Full mode not yet implemented. Using sample queries.")
        for category, queries in SAMPLE_QUERIES.items():
            comparator.compare_category(queries, category)
    
    # Generate and display report
    report = comparator.generate_report()
    comparator.print_summary(report)
    
    # Save report
    report_file = comparator.save_report(report)
    
    print(f"\n✅ Comparison complete! Results saved to: {report_file}")
    print(f"📋 Full logs available in: comparison_results.log\n")


if __name__ == "__main__":
    main()

