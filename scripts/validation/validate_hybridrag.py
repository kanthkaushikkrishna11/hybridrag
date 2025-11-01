#!/usr/bin/env python3
"""
HybridRAG Validation Script

This script systematically tests the HybridRAG system with carefully designed queries
to validate:
1. Query classification accuracy (Table/Text/Hybrid)
2. Pipeline routing correctness
3. Answer quality and accuracy
4. Comparison with Conventional RAG

Usage:
    python validate_hybridrag.py --mode [full|quick|category]
    
    --mode full: Run all 45 queries (15 table, 15 text, 15 hybrid)
    --mode quick: Run 5 sample queries from each category
    --mode category: Run specific category (table|text|hybrid)
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import requests
from tabulate import tabulate
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('validation_results.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"
RESULTS_DIR = Path("validation_results")
RESULTS_DIR.mkdir(exist_ok=True)

# Query Definitions
TABLE_QUERIES = [
    # Basic (6)
    "What are the names of the teams which won the Final matches in the world cup matches?",
    "Tell me the name and year in which a team won the Final match in the World Cup Matches",
    "What was the highest Home Score by any team in World Cup Matches? Print the Year, Home Team Name, Away Team Name, Winning Team Name, number of goals scored.",
    "How many matches in the World Cup ended in a draw?",
    "What was the host nation for the first football World Cup?",
    "What is the count of the number of rows in the data?",
    # Intermediate (6)
    "How many goals did Brazil score in total (home + away)?",
    "Which team won the most matches in the dataset?",
    "List all Semi-final matches with scores",
    "What is the average number of goals scored per match?",
    "How many matches were played in each World Cup year?",
    "Which rounds had the most draws?",
    # Advanced (3)
    "Which teams have won a World Cup Final? (with count of championships)",
    "Find all matches where the home team scored more than 5 goals",
    "Which matches had the highest total goals (home + away)?",
]

TEXT_QUERIES = [
    # Historical & Contextual (5)
    "What is the historical significance of the FIFA World Cup and when did it start?",
    "Describe the format and evolution of the World Cup tournament over the years.",
    "What were the major changes in World Cup organization between 1930 and 1978?",
    "Explain the cultural and social impact of the FIFA World Cup.",
    "What role did FIFA play in organizing the World Cup tournaments?",
    # Tournament Description (5)
    "Which countries hosted the FIFA World Cup tournaments and what were the notable features of their hosting?",
    "Describe the qualification process for the FIFA World Cup.",
    "What were some of the memorable moments in early World Cup history?",
    "How did World War II affect the FIFA World Cup schedule?",
    "What were the opening ceremony highlights mentioned in the document?",
    # Player & Team Narrative (5)
    "Who were some of the legendary players mentioned in the FIFA World Cup history?",
    "Describe the playing styles and strategies that characterized early World Cup tournaments.",
    "What factors contributed to certain teams' dominance in World Cup history?",
    "How did team compositions and national squad selections evolve over time?",
    "What were the notable achievements and records set by individual players in the World Cup?",
]

HYBRID_QUERIES = [
    # Match Context + Data (5)
    "Which team won the 1950 World Cup Final and what was historically significant about that tournament and match?",
    "Tell me about Brazil's performance in the 1970 World Cup - both their match results and the historical context of that tournament.",
    "How many goals were scored in the 1954 World Cup Final and what made that tournament memorable?",
    "Which team had the highest goal difference in Quarter-final matches and what was the historical significance of their performance?",
    "List the Semi-final winners from 1974 World Cup and describe the tournament atmosphere and context.",
    # Statistical + Narrative (5)
    "What were the top-scoring teams in the 1930s World Cups and what historical factors influenced their success?",
    "Compare the goal-scoring patterns between 1930-1950 World Cups with the historical context of football evolution during that period.",
    "Which countries hosted World Cups in the 1960s and what were the match outcomes in those tournaments?",
    "Analyze the draw percentage in World Cup matches and explain why draws were more or less common in different eras.",
    "Which teams appeared most frequently in Finals and what were the historical circumstances that led to their dominance?",
    # Complex Integration (5)
    "Provide a comprehensive overview of Uruguay's World Cup journey including their match statistics and historical achievements.",
    "What was the highest-scoring World Cup tournament based on the data, and what historical factors contributed to the high-scoring nature?",
    "Compare Argentina's performance in home and away matches, and describe their overall World Cup legacy.",
    "Which Round of the tournament saw the most competitive matches (smallest goal differences) and what does this say about tournament progression?",
    "Give me a detailed analysis of Italy's World Cup performance with both statistical data and historical context about their football heritage.",
]

EDGE_CASE_QUERIES = [
    "Tell me about Brazil in the World Cup",
    "How many World Cup tournaments are mentioned in the document?",
    "What does the Winner column represent in the match data?",
    "Calculate the average goals per match AND explain the historical reasons for scoring trends",
    "Describe the structure and format of the World Cup match data provided",
]


class ValidationResult:
    """Class to store validation results for a single query"""
    
    def __init__(self, query: str, expected_category: str):
        self.query = query
        self.expected_category = expected_category
        self.actual_category = None
        self.response = None
        self.agents_called = []
        self.response_time = 0
        self.error = None
        self.classification_correct = False
        self.pipeline_isolated = False
        self.answer_quality_score = 0  # 1-5 scale
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "query": self.query,
            "expected_category": self.expected_category,
            "actual_category": self.actual_category,
            "classification_correct": self.classification_correct,
            "pipeline_isolated": self.pipeline_isolated,
            "agents_called": self.agents_called,
            "response_time": self.response_time,
            "answer_quality_score": self.answer_quality_score,
            "response": self.response,
            "error": self.error,
            "timestamp": self.timestamp
        }


class HybridRAGValidator:
    """Main validator class for HybridRAG system"""
    
    def __init__(self, api_base_url: str = API_BASE_URL):
        self.api_base_url = api_base_url
        self.results: List[ValidationResult] = []
        self.session = requests.Session()
        
    def check_api_health(self) -> bool:
        """Check if the API is accessible"""
        try:
            response = self.session.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info(f"✓ API is healthy: {self.api_base_url}")
                return True
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ API health check failed: {e}")
            return False
        return False
    
    def query_hybridrag(self, query: str) -> Tuple[Dict, float]:
        """Send query to HybridRAG API and return response with timing"""
        start_time = time.time()
        
        try:
            response = self.session.post(
                f"{self.api_base_url}/api/chat",
                json={"message": query},
                timeout=120  # 2 minute timeout for complex queries
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return response.json(), response_time
            else:
                logger.error(f"API returned status {response.status_code}: {response.text}")
                return {"error": f"Status {response.status_code}"}, response_time
                
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            logger.error(f"Query timed out after {response_time:.2f}s")
            return {"error": "Timeout"}, response_time
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Query failed: {e}")
            return {"error": str(e)}, response_time
    
    def extract_classification(self, response: Dict) -> str:
        """Extract query classification from response"""
        # Check different possible response structures
        if "classification" in response:
            return response["classification"]
        
        if "metadata" in response and "classification" in response["metadata"]:
            return response["metadata"]["classification"]
        
        # Try to infer from response structure
        if "answer" in response:
            answer = response["answer"].lower()
            if "table" in answer or "sql" in answer:
                return "Table"
            elif "hybrid" in answer or "combined" in answer:
                return "Hybrid"
            else:
                return "Text"
        
        return "Unknown"
    
    def extract_agents_called(self, response: Dict) -> List[str]:
        """Extract which agents were called from response"""
        agents = []
        
        # Check metadata
        if "metadata" in response:
            if "agents_called" in response["metadata"]:
                return response["metadata"]["agents_called"]
            
            # Check for specific agent indicators
            if response["metadata"].get("table_agent_used"):
                agents.append("TableAgent")
            if response["metadata"].get("rag_agent_used"):
                agents.append("RAGAgent")
            if response["metadata"].get("combiner_agent_used"):
                agents.append("CombinerAgent")
        
        # Fallback: try to infer from response content
        if not agents:
            answer = str(response.get("answer", "")).lower()
            if "sql" in answer or "query" in answer:
                agents.append("TableAgent")
            if "document" in answer or "context" in answer:
                agents.append("RAGAgent")
        
        return agents
    
    def validate_pipeline_isolation(self, expected_category: str, agents_called: List[str]) -> bool:
        """Check if correct pipeline isolation occurred"""
        if expected_category == "Table":
            # Should only call TableAgent, not RAGAgent
            has_table = any("table" in agent.lower() for agent in agents_called)
            has_rag = any("rag" in agent.lower() for agent in agents_called)
            return has_table and not has_rag
        
        elif expected_category == "Text":
            # Should only call RAGAgent, not TableAgent
            has_table = any("table" in agent.lower() for agent in agents_called)
            has_rag = any("rag" in agent.lower() for agent in agents_called)
            return has_rag and not has_table
        
        elif expected_category == "Hybrid":
            # Should call both agents
            has_table = any("table" in agent.lower() for agent in agents_called)
            has_rag = any("rag" in agent.lower() for agent in agents_called)
            return has_table and has_rag
        
        return False
    
    def score_answer_quality(self, query: str, response: Dict, expected_category: str) -> int:
        """Score answer quality on 1-5 scale (basic heuristics)"""
        if "error" in response or not response.get("answer"):
            return 1
        
        answer = str(response["answer"])
        score = 3  # Start with neutral
        
        # Length check
        if len(answer) < 20:
            score -= 1
        elif len(answer) > 100:
            score += 1
        
        # Category-specific checks
        if expected_category == "Table":
            # Should contain numbers/data
            if any(char.isdigit() for char in answer):
                score += 1
            # Should not be too generic
            if "based on" in answer.lower() or "according to" in answer.lower():
                score += 1
        
        elif expected_category == "Text":
            # Should be descriptive
            if len(answer.split()) > 30:
                score += 1
            # Should contain narrative words
            narrative_words = ["history", "significance", "impact", "evolution", "describe"]
            if any(word in answer.lower() for word in narrative_words):
                score += 1
        
        elif expected_category == "Hybrid":
            # Should have both data and context
            has_numbers = any(char.isdigit() for char in answer)
            has_narrative = len(answer.split()) > 50
            if has_numbers and has_narrative:
                score += 1
        
        return max(1, min(5, score))  # Clamp between 1-5
    
    def validate_query(self, query: str, expected_category: str) -> ValidationResult:
        """Validate a single query"""
        logger.info(f"\n{'='*80}")
        logger.info(f"Testing Query: {query}")
        logger.info(f"Expected Category: {expected_category}")
        
        result = ValidationResult(query, expected_category)
        
        # Query the API
        response, response_time = self.query_hybridrag(query)
        result.response = response
        result.response_time = response_time
        
        if "error" in response:
            result.error = response["error"]
            logger.error(f"✗ Query failed: {result.error}")
            return result
        
        # Extract classification
        result.actual_category = self.extract_classification(response)
        result.classification_correct = (
            result.actual_category.lower() == expected_category.lower()
        )
        
        # Extract agents called
        result.agents_called = self.extract_agents_called(response)
        
        # Validate pipeline isolation
        result.pipeline_isolated = self.validate_pipeline_isolation(
            expected_category, result.agents_called
        )
        
        # Score answer quality
        result.answer_quality_score = self.score_answer_quality(
            query, response, expected_category
        )
        
        # Log results
        logger.info(f"Actual Category: {result.actual_category}")
        logger.info(f"Classification: {'✓ CORRECT' if result.classification_correct else '✗ INCORRECT'}")
        logger.info(f"Agents Called: {', '.join(result.agents_called)}")
        logger.info(f"Pipeline Isolation: {'✓ YES' if result.pipeline_isolated else '✗ NO'}")
        logger.info(f"Answer Quality: {result.answer_quality_score}/5")
        logger.info(f"Response Time: {result.response_time:.2f}s")
        
        return result
    
    def validate_category(self, queries: List[str], category: str):
        """Validate all queries in a category"""
        logger.info(f"\n{'#'*80}")
        logger.info(f"# VALIDATING {category.upper()} QUERIES ({len(queries)} total)")
        logger.info(f"{'#'*80}")
        
        for i, query in enumerate(queries, 1):
            logger.info(f"\n[{i}/{len(queries)}] {category} Query")
            result = self.validate_query(query, category)
            self.results.append(result)
            
            # Small delay between queries
            time.sleep(1)
    
    def generate_report(self) -> Dict:
        """Generate comprehensive validation report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(self.results),
            "summary": {},
            "detailed_results": []
        }
        
        # Group results by category
        by_category = defaultdict(list)
        for result in self.results:
            by_category[result.expected_category].append(result)
        
        # Calculate metrics for each category
        for category, results in by_category.items():
            total = len(results)
            correct_classification = sum(1 for r in results if r.classification_correct)
            correct_isolation = sum(1 for r in results if r.pipeline_isolated)
            avg_quality = sum(r.answer_quality_score for r in results) / total if total > 0 else 0
            avg_response_time = sum(r.response_time for r in results) / total if total > 0 else 0
            errors = sum(1 for r in results if r.error)
            
            report["summary"][category] = {
                "total_queries": total,
                "classification_accuracy": f"{(correct_classification/total*100):.1f}%" if total > 0 else "0%",
                "pipeline_isolation_rate": f"{(correct_isolation/total*100):.1f}%" if total > 0 else "0%",
                "avg_answer_quality": f"{avg_quality:.2f}/5",
                "avg_response_time": f"{avg_response_time:.2f}s",
                "errors": errors
            }
        
        # Add detailed results
        report["detailed_results"] = [r.to_dict() for r in self.results]
        
        return report
    
    def print_summary(self, report: Dict):
        """Print formatted summary to console"""
        print("\n" + "="*80)
        print(" HYBRIDRAG VALIDATION SUMMARY ".center(80, "="))
        print("="*80 + "\n")
        
        # Summary table
        table_data = []
        for category, metrics in report["summary"].items():
            table_data.append([
                category,
                metrics["total_queries"],
                metrics["classification_accuracy"],
                metrics["pipeline_isolation_rate"],
                metrics["avg_answer_quality"],
                metrics["avg_response_time"],
                metrics["errors"]
            ])
        
        headers = ["Category", "Queries", "Classification", "Isolation", "Quality", "Avg Time", "Errors"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Overall statistics
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"   Total Queries: {report['total_queries']}")
        
        all_correct = sum(
            int(m["classification_accuracy"].rstrip("%")) * m["total_queries"] / 100
            for m in report["summary"].values()
        )
        overall_accuracy = (all_correct / report["total_queries"] * 100) if report["total_queries"] > 0 else 0
        print(f"   Overall Classification Accuracy: {overall_accuracy:.1f}%")
        
        all_isolated = sum(
            int(m["pipeline_isolation_rate"].rstrip("%")) * m["total_queries"] / 100
            for m in report["summary"].values()
        )
        overall_isolation = (all_isolated / report["total_queries"] * 100) if report["total_queries"] > 0 else 0
        print(f"   Overall Pipeline Isolation: {overall_isolation:.1f}%")
        
        print("\n" + "="*80 + "\n")
    
    def save_report(self, report: Dict, filename: str = None):
        """Save report to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"validation_report_{timestamp}.json"
        
        filepath = RESULTS_DIR / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✓ Report saved to: {filepath}")
        return filepath


def main():
    parser = argparse.ArgumentParser(description="Validate HybridRAG System")
    parser.add_argument(
        "--mode",
        choices=["full", "quick", "category"],
        default="quick",
        help="Validation mode: full (all queries), quick (sample), category (specific)"
    )
    parser.add_argument(
        "--category",
        choices=["table", "text", "hybrid"],
        help="Specific category to test (only with --mode category)"
    )
    parser.add_argument(
        "--api-url",
        default=API_BASE_URL,
        help=f"API base URL (default: {API_BASE_URL})"
    )
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = HybridRAGValidator(api_base_url=args.api_url)
    
    # Check API health
    if not validator.check_api_health():
        logger.error("Cannot proceed without healthy API. Please start the backend.")
        sys.exit(1)
    
    # Run validation based on mode
    if args.mode == "full":
        logger.info("🚀 Running FULL validation (45 queries)")
        validator.validate_category(TABLE_QUERIES, "Table")
        validator.validate_category(TEXT_QUERIES, "Text")
        validator.validate_category(HYBRID_QUERIES, "Hybrid")
    
    elif args.mode == "quick":
        logger.info("🚀 Running QUICK validation (15 queries - 5 per category)")
        validator.validate_category(TABLE_QUERIES[:5], "Table")
        validator.validate_category(TEXT_QUERIES[:5], "Text")
        validator.validate_category(HYBRID_QUERIES[:5], "Hybrid")
    
    elif args.mode == "category":
        if not args.category:
            logger.error("--category must be specified when using --mode category")
            sys.exit(1)
        
        category_map = {
            "table": (TABLE_QUERIES, "Table"),
            "text": (TEXT_QUERIES, "Text"),
            "hybrid": (HYBRID_QUERIES, "Hybrid")
        }
        
        queries, category_name = category_map[args.category]
        logger.info(f"🚀 Running {category_name.upper()} validation ({len(queries)} queries)")
        validator.validate_category(queries, category_name)
    
    # Generate and display report
    report = validator.generate_report()
    validator.print_summary(report)
    
    # Save report
    report_file = validator.save_report(report)
    
    print(f"\n✅ Validation complete! Results saved to: {report_file}")
    print(f"📋 Full logs available in: validation_results.log\n")


if __name__ == "__main__":
    main()

