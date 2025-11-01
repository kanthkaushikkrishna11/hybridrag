# src/backend/agents/combiner_agent.py

import logging
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

class CombinerAgent:
    """
    Agent responsible for intelligently combining responses from Table and RAG nodes
    """
    
    def __init__(self, gemini_api_key: str, model_name: str = "gemini-2.5-flash"):
        """
        Initialize the Combiner Agent with Gemini LLM
        
        Args:
            gemini_api_key (str): Google Gemini API key
            model_name (str): Gemini model to use (default: gemini-2.5-flash)
        """
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=gemini_api_key,
            temperature=0.3  # Slightly higher for more creative combinations
        )
        logger.info(f"Combiner Agent initialized successfully with model: {model_name}")
    
    def combine_responses(
        self, 
        original_query: str,
        table_response: Optional[str] = None,
        rag_response: Optional[str] = None
    ) -> str:
        """
        Intelligently combine responses from Table and RAG nodes
        
        Args:
            original_query (str): The original user query
            table_response (Optional[str]): Response from table processing
            rag_response (Optional[str]): Response from RAG processing
            
        Returns:
            str: Combined, coherent response
        """
        try:
            print(f"[DEBUG] Combiner Agent processing responses")
            print(f"[DEBUG] Table response present: {table_response is not None}")
            print(f"[DEBUG] RAG response present: {rag_response is not None}")
            
            # Handle single response cases
            if table_response and not rag_response:
                return self._format_single_response(table_response, "data analysis")
            
            if rag_response and not table_response:
                return self._format_single_response(rag_response, "knowledge base")
            
            # Handle combined response case
            if table_response and rag_response:
                return self._create_intelligent_combination(
                    original_query, table_response, rag_response
                )
            
            # Handle no response case
            return "I apologize, but I wasn't able to generate a response to your query. Please try rephrasing your question."
            
        except Exception as e:
            logger.error(f"Error in Combiner Agent: {e}", exc_info=True)
            return "I encountered an error while combining the responses. Please try again."
    
    def _format_single_response(self, response: str, source_type: str) -> str:
        """
        Format a single response with appropriate context
        
        Args:
            response (str): The response to format
            source_type (str): Type of source ("data analysis" or "knowledge base")
            
        Returns:
            str: Formatted response
        """
        if response.strip():
            return response
        else:
            return f"No information available from {source_type} for your query."
    
    def _create_intelligent_combination(
        self, 
        original_query: str, 
        table_response: str, 
        rag_response: str
    ) -> str:
        """
        Use Gemini to create an intelligent combination of both responses
        
        Args:
            original_query (str): Original user query
            table_response (str): Response from table processing
            rag_response (str): Response from RAG processing
            
        Returns:
            str: Intelligently combined response
        """
        try:
            system_prompt = """
            You are an expert answer synthesizer that creates comprehensive, well-formatted responses by intelligently merging:
            1. RAG Response: Historical context, narratives, background information
            2. Table Response: Statistical data, match records, numerical facts

            ⚠️ CRITICAL: PRESERVATION RULE ⚠️
            - If Table Response contains a detailed list (e.g., match-by-match data), you MUST include ALL items
            - NEVER summarize or truncate detailed data provided by Table Response
            - Your job is to ORGANIZE and FORMAT, not to REDUCE information
            
            FORMATTING RULES:
            
            1. STRUCTURE (for comprehensive queries):
               a) Start with a clear summary sentence
               b) Add historical context from RAG Response
               c) Show aggregate statistics (if present) in one line
               d) Present complete detailed data (e.g., all matches) with clean formatting
            
            2. DATA PRESENTATION:
               - Remove duplicate entries (same item appearing multiple times)
               - Remove repeated aggregate columns (if same total appears in every row, show once)
               - Convert technical formats to natural language:
                 * "Home_Score: 4, Away_Score: 2" → "4-2"
                 * "opponent: Argentina, Round: Final" → "Final vs Argentina"
               - Use bullet points for lists
            
            3. QUALITY STANDARDS:
               - Complete, not concise - include ALL data points
               - Natural, readable language
               - Professional formatting with clear sections
               - Never mention sources ("table says", "according to data")
            
            4. EXAMPLES:
            
            BAD (drops data):
            Uruguay won key matches including:
            * 1930 Final: 4-2 vs Argentina
            * 1950: Defeated Brazil
            [Missing 9 other matches!]
            
            GOOD (preserves all data):
            Uruguay's World Cup History:
            
            Historical Achievements:
            * First-ever World Cup champions (1930)
            * "Maracanazo" victory over Brazil (1950)
            
            Overall Record: 9 wins, 1 draw, 1 loss • Goals: 28 scored, 12 conceded
            
            Complete Match History:
            * 1930 Group 1: Uruguay 1-0 Peru
            * 1930 Group 3: Uruguay 4-0 Romania  
            * 1930 Semi-final: Uruguay 6-1 Yugoslavia
            * 1930 Final: Uruguay 4-2 Argentina
            [... continues for ALL 11 matches]
            
            Remember: If Table Response has N items, your output must have N items.
            """
            
            user_prompt = f"""
            Original Query: {original_query}

            General Knowledge Response: {rag_response}

            Data Analysis Response: {table_response}

            Please combine these responses into a single, coherent answer that best addresses the user's query.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            combined_response = response.content.strip()
            
            print(f"[DEBUG] Combiner Agent created intelligent combination")
            return combined_response
            
        except Exception as e:
            logger.error(f"Error creating intelligent combination: {e}")
            # Fallback to simple concatenation
            return self._simple_combination(table_response, rag_response)
    
    def _simple_combination(self, table_response: str, rag_response: str) -> str:
        """
        Fallback method for simple response combination
        
        Args:
            table_response (str): Response from table processing
            rag_response (str): Response from RAG processing
            
        Returns:
            str: Simply combined response
        """
        print(f"[DEBUG] Combiner Agent using simple combination fallback")
        
        parts = []
        
        if rag_response and rag_response.strip():
            parts.append(rag_response.strip())
        
        if table_response and table_response.strip():
            parts.append(table_response.strip())
        
        if parts:
            return "\n\n".join(parts)
        else:
            return "No response could be generated for your query."
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for the Combiner Agent
        
        Returns:
            Dict[str, Any]: Health status information
        """
        try:
            # Test LLM connection
            test_response = self.llm.invoke([HumanMessage(content="Hello")])
            
            return {
                "combiner_agent": True,
                "llm_connection": True,
                "overall_health": True
            }
        except Exception as e:
            logger.error(f"Combiner Agent health check failed: {e}")
            return {
                "combiner_agent": False,
                "llm_connection": False,
                "overall_health": False,
                "error": str(e)
            }