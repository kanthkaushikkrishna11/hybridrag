import logging
import json
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel
import os
import concurrent.futures
import time
try:
    from urllib.parse import urlparse, parse_qs
except ImportError as e:
    logging.error(f"Failed to import urllib.parse: {e}")
    raise

logger = logging.getLogger(__name__)


class AgentState(BaseModel):
    """State object for the LangGraph workflow"""
    query: str
    response: str = ""
    needs_table: bool = False
    needs_rag: bool = False
    table_response: str = ""
    rag_response: str = ""
    pdf_uuid: Optional[str] = None
    table_sub_query: str = ""
    rag_sub_query: str = ""
    query_type: str = "unknown"  # Classification: "table", "rag", or "both"

    class Config:
        arbitrary_types_allowed = True


class ManagerAgent:
    """
    Manager Agent using LangGraph to orchestrate between Table and RAG nodes
    """

    def __init__(self, gemini_api_key: str, chatbot_agent=None):
        """Initialize the Manager Agent with Gemini LLM and optional ChatbotAgent"""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=gemini_api_key,
            temperature=0.1
        )
        self.chatbot_agent = chatbot_agent

        # Initialize Combiner Agent
        try:
            from .combiner_agent import CombinerAgent
            self.combiner_agent = CombinerAgent(gemini_api_key, model_name="gemini-2.5-flash")
            logger.info(
                "Combiner Agent initialized successfully in Manager Agent")
        except Exception as e:
            logger.error(f"Failed to initialize Combiner Agent: {e}")
            self.combiner_agent = None

        # ⚡ SPEED OPTIMIZATION: Caching
        self._schema_cache = None
        self._schema_cache_time = None
        self._schema_cache_ttl = 300  # 5 minutes
        self._classification_cache = {}  # Query -> classification mapping
        self._cache_max_size = 100
        
        self.workflow = self._create_workflow()
        try:
            from .table_agent import TableAgent
            if not os.path.exists(os.path.join(os.path.dirname(__file__), 'table_agent.py')):
                raise FileNotFoundError("table_agent.py not found in agents directory")
            self.table_agent = TableAgent(gemini_api_key)
            logger.info("Table Agent initialized successfully in Manager Agent")

        except ImportError as e:
            logger.error(f"Failed to import TableAgent: {e}", exc_info=True)
            self.table_agent = None
        except FileNotFoundError as e:
            logger.error(f"TableAgent file error: {e}", exc_info=True)
            self.table_agent = None
        except Exception as e:
            logger.error(f"Failed to initialize TableAgent: {e}", exc_info=True)
            self.table_agent = None

    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("manager", self._manager_node)
        workflow.add_node("table", self._table_node)
        workflow.add_node("rag", self._rag_node)
        workflow.add_node("parallel", self._parallel_node)  # ⚡ NEW: Parallel execution node
        workflow.add_node("combiner", self._combiner_node)

        # Add edges
        workflow.set_entry_point("manager")
        workflow.add_conditional_edges(
            "manager",
            self._decide_route,
            {
                "table_only": "table",
                "rag_only": "rag",
                "both": "parallel",  # ⚡ OPTIMIZED: Route to parallel node for "both"
                "end": END
            }
        )

        workflow.add_conditional_edges(
            "table",
            self._after_table_route,
            {
                "to_rag": "rag",
                "to_combiner": "combiner",
                "end": END
            }
        )

        workflow.add_edge("rag", "combiner")
        workflow.add_edge("parallel", "combiner")  # ⚡ Parallel goes directly to combiner
        workflow.add_edge("combiner", END)

        return workflow.compile()

    def _manager_node(self, state: AgentState) -> Dict[str, Any]:
        """Manager node that analyzes the query and decides routing"""
        print(f"[DEBUG] Manager Node called with query: {state.query}")

        schema_info = self._load_table_schema(state.pdf_uuid)
        system_prompt = f"""
        You are a query analyzer that routes queries and generates sub-queries for specialized agents.

        AVAILABLE DATABASE SCHEMA:
        {schema_info}

        Your task is to:
        1. Determine the routing strategy
        2. Generate specific sub-queries for each agent

        ROUTING RULES - Read Carefully:
        
        ✅ Use "table" when:
        - Query asks for specific data/statistics/counts that exist in the database
        - Examples: "List all winners", "How many matches", "Which teams scored X goals"
        - Key words: list, count, statistics, data, total, average, specific numbers
        
        ✅ Use "rag" when:
        - Query asks for historical context, significance, explanations, or general knowledge
        - Query asks "what is", "why", "how did X happen", "what was the significance"
        - Information is typically found in text documents, not structured tables
        - Examples: "What is the historical significance", "When did X start", "Explain the importance"
        - Key words: significance, history, context, background, importance, meaning, why, explain
        
        ✅ Use "both" when:
        - Query EXPLICITLY asks for BOTH statistics/data (from tables) AND historical context/achievements (from documents)
        - Query contains keywords from BOTH categories above
        - Examples: "Provide comprehensive overview including match statistics AND historical achievements"
        - Key indicator: Query asks for data analysis PLUS contextual narrative

        CRITICAL DECISION RULES:
        - If query asks "when did X start" or "what year" → Check if this is general knowledge (rag) or requires database lookup (table)
        - If query says "comprehensive overview" with BOTH "statistics" AND "historical/achievements" → Use "both"
        - If query is purely about concepts, significance, or history → Use "rag" even if it mentions years/dates
        - Default to simplest routing (avoid "both" unless truly necessary)

        RESPONSE FORMAT:
        Return ONLY a valid JSON object (no markdown, no explanations) with:
        {{
        "status": "rag" | "table" | "both",
        "rag_agent_sub_query": "Clear sub-query for RAG if needed",
        "table_agent_sub_query": "Clear sub-query for Table agent if needed"
        }}

        SUB-QUERY GUIDELINES:
        - For RAG queries: Generate natural language questions about general knowledge, concepts, or document content
        - For Table queries: Generate natural language questions about data that can be found in the database tables
        - DO NOT generate SQL queries - only natural language questions that the table agent will convert to SQL
        - Focus on what specific data or information each agent should retrieve
        - For "both" status: Create complementary sub-queries that together answer the original question

        EXAMPLES:
        
        Example 1:
        Original: "What is the historical significance of the FIFA World Cup and when did it start?"
        {{
        "status": "rag",
        "rag_agent_sub_query": "What is the historical significance of the FIFA World Cup and when did it start?",
        "table_agent_sub_query": ""
        }}
        Reason: Asks about significance (context) and start year (general knowledge), not database statistics
        
        Example 2:
        Original: "Provide a comprehensive overview of Uruguay's World Cup journey including their match statistics and historical achievements"
        {{
        "status": "both",
        "rag_agent_sub_query": "What are Uruguay's historical World Cup achievements and significant moments?",
        "table_agent_sub_query": "Provide all match statistics for Uruguay including wins, losses, goals, and match details"
        }}
        Reason: EXPLICITLY asks for BOTH match statistics (table data) AND historical achievements (context/narrative)
        
        Example 3:
        Original: "What are the names of teams that won Final matches?"
        {{
        "status": "table",
        "rag_agent_sub_query": "",
        "table_agent_sub_query": "What are the names of teams that won Final matches?"
        }}
        Reason: Pure data query asking for list of winners from database

        Example 4:
        Original: "How many times did Brazil win the FIFA World Cup and what leagues does Europe have?"
        {{
        "status": "both",
        "rag_agent_sub_query": "What are the major football leagues in Europe?",
        "table_agent_sub_query": "How many times did Brazil win the World Cup according to the data?"
        }}
        Reason: Two separate questions - one needs data (Brazil wins), one needs general knowledge (European leagues)
        """

        # ⚡ SPEED OPTIMIZATION: Check classification cache
        import hashlib
        query_hash = hashlib.md5(state.query.lower().strip().encode()).hexdigest()
        
        try:
            if query_hash in self._classification_cache:
                logger.debug(f"✅ Using cached classification for query: {state.query[:50]}...")
                cached_result = self._classification_cache[query_hash]
                decision = cached_result['decision']
                rag_sub_query = cached_result.get('rag_sub_query', '')
                table_sub_query = cached_result.get('table_sub_query', '')
                result = cached_result
            else:
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=f"Original Query: {state.query}")
                ]

                response = self.llm.invoke(messages)
                logger.info(f"the manager llm output before json extraction: {response}")
                
                # Extract JSON from response, handling markdown code blocks
                content = response.content.strip()
                
                # Remove markdown code block markers if present
                if content.startswith('```json'):
                    content = content.replace('```json\n', '').replace('```', '').strip()
                elif content.startswith('```'):
                    content = content.replace('```\n', '').replace('```', '').strip()
                
                # Try to find JSON within the content if still not valid
                if not content.startswith('{'):
                    # Look for JSON block within the content
                    start_idx = content.find('{')
                    end_idx = content.rfind('}')
                    if start_idx != -1 and end_idx != -1:
                        content = content[start_idx:end_idx+1]
                
                logger.info(f"Cleaned content for JSON parsing: {content}")
                result = json.loads(content)
                
                decision = result.get("status", "rag").lower()
                rag_sub_query = result.get("rag_agent_sub_query", "")
                table_sub_query = result.get("table_agent_sub_query", "")

                # ⚡ SPEED OPTIMIZATION: Store in cache
                cache_entry = {
                    'decision': decision,
                    'rag_sub_query': rag_sub_query,
                    'table_sub_query': table_sub_query,
                    'status': decision
                }
                self._classification_cache[query_hash] = cache_entry
                
                # Limit cache size
                if len(self._classification_cache) > self._cache_max_size:
                    # Remove oldest entry (simple FIFO)
                    self._classification_cache.pop(next(iter(self._classification_cache)))
                logger.debug(f"✅ Cached classification for query: {state.query[:50]}...")

                logger.info(f"the manager llm output after json extraction: {result}")
                
            # Set flags and sub-queries based on decision
            if decision == "table":
                state.needs_table = True
                state.needs_rag = False
                state.table_sub_query = table_sub_query or state.query
                state.query_type = "table"
            elif decision == "rag":
                state.needs_table = False
                state.needs_rag = True
                state.rag_sub_query = rag_sub_query or state.query
                state.query_type = "rag"
            elif decision == "both":
                state.needs_table = True
                state.needs_rag = True
                state.table_sub_query = table_sub_query or state.query
                state.rag_sub_query = rag_sub_query or state.query
                state.query_type = "both"
            else:
                # Default to RAG for unknown cases
                state.needs_table = False
                state.needs_rag = True
                state.rag_sub_query = state.query
                state.query_type = "rag"

            print(f"[DEBUG] Manager decision: {decision}")
            print(f"[DEBUG] Query type: {state.query_type}")
            print(f"[DEBUG] Table sub-query: {getattr(state, 'table_sub_query', 'None')}")
            print(f"[DEBUG] RAG sub-query: {getattr(state, 'rag_sub_query', 'None')}")

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error in manager node: {e}")
            # Default to RAG on error
            state.needs_table = False
            state.needs_rag = True
            state.rag_sub_query = state.query

        return {
            "needs_table": state.needs_table, 
            "needs_rag": state.needs_rag,
            "table_sub_query": getattr(state, 'table_sub_query', ''),
            "rag_sub_query": getattr(state, 'rag_sub_query', ''),
            "query_type": state.query_type
        }

    def _table_node(self, state: AgentState) -> Dict[str, Any]:
        """Table node for handling data queries using TableAgent"""
        query_to_use = getattr(state, 'table_sub_query', '') or state.query
        print(f"[DEBUG] Table Node called with sub-query: {query_to_use}")

        try:
            if self.table_agent:
                table_response = self.table_agent.process_query(query_to_use, state.pdf_uuid)
                print(f"[DEBUG] Table Node response from TableAgent: {table_response}")
            else:
                logger.error("TableAgent not initialized")
                table_response = f"Error: Table processing unavailable for query: {query_to_use}"
                print(f"[DEBUG] Table Node error: TableAgent not initialized")
        except Exception as e:
            logger.error(f"Error in table node: {e}")
            table_response = f"Error processing data query: {query_to_use}"
            print(f"[DEBUG] Table Node error response: {table_response}")

        return {"table_response": table_response}
    


    def _rag_node(self, state: AgentState) -> Dict[str, Any]:
        """RAG node for handling knowledge queries using ChatbotAgent"""
        query_to_use = getattr(state, 'rag_sub_query', '') or state.query
        print(f"[DEBUG] RAG Node called with sub-query: {query_to_use}")
        
        try:
            if self.chatbot_agent:
                # Use the ChatbotAgent's answer_question function with PDF UUID
                response = self.chatbot_agent.answer_question(query_to_use, pdf_uuid=state.pdf_uuid)
                rag_response = response.get("answer", f"RAG processing: {query_to_use}")
                print(f"[DEBUG] RAG Node response from ChatbotAgent: {rag_response}")
            else:
                # Fallback if no ChatbotAgent is available
                rag_response = f"RAG processing: {query_to_use}"
                print(f"[DEBUG] RAG Node response (fallback): {rag_response}")
        except Exception as e:
            logger.error(f"Error in RAG node: {e}")
            rag_response = f"RAG processing error: {query_to_use}"
            print(f"[DEBUG] RAG Node error response: {rag_response}")
        
        return {"rag_response": rag_response}
    
    def _parallel_node(self, state: AgentState) -> Dict[str, Any]:
        """
        ⚡ SPEED OPTIMIZATION: Execute Table and RAG agents in parallel for 'both' queries
        This saves 5-10s on hybrid queries by running both agents concurrently
        """
        print(f"[DEBUG] Parallel Node called - executing Table and RAG agents concurrently")
        logger.info("⚡ Executing Table and RAG agents in parallel")
        
        table_response = ""
        rag_response = ""
        
        def run_table():
            """Execute table agent"""
            try:
                query_to_use = getattr(state, 'table_sub_query', '') or state.query
                print(f"[DEBUG] Parallel - Table Agent executing: {query_to_use}")
                
                if self.table_agent:
                    response = self.table_agent.process_query(query_to_use, state.pdf_uuid)
                    result = response if isinstance(response, str) else str(response)
                    print(f"[DEBUG] Parallel - Table Agent completed")
                    return result
                else:
                    return f"Table processing: {query_to_use}"
            except Exception as e:
                logger.error(f"Error in parallel table execution: {e}")
                return f"Table processing error: {query_to_use}"
        
        def run_rag():
            """Execute RAG agent"""
            try:
                query_to_use = getattr(state, 'rag_sub_query', '') or state.query
                print(f"[DEBUG] Parallel - RAG Agent executing: {query_to_use}")
                
                if self.chatbot_agent:
                    response = self.chatbot_agent.answer_question(query_to_use, pdf_uuid=state.pdf_uuid)
                    result = response.get("answer", f"RAG processing: {query_to_use}")
                    print(f"[DEBUG] Parallel - RAG Agent completed")
                    return result
                else:
                    return f"RAG processing: {query_to_use}"
            except Exception as e:
                logger.error(f"Error in parallel RAG execution: {e}")
                return f"RAG processing error: {query_to_use}"
        
        # Execute both agents in parallel using ThreadPoolExecutor
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both tasks
            table_future = executor.submit(run_table)
            rag_future = executor.submit(run_rag)
            
            # Wait for both to complete
            table_response = table_future.result()
            rag_response = rag_future.result()
        
        elapsed_time = time.time() - start_time
        logger.info(f"⚡ Parallel execution completed in {elapsed_time:.2f}s")
        print(f"[DEBUG] Parallel execution completed in {elapsed_time:.2f}s")
        
        return {
            "table_response": table_response,
            "rag_response": rag_response
        }
    
    def _combiner_node(self, state: AgentState) -> Dict[str, Any]:
        """Combiner node to merge responses from Table and RAG nodes using CombinerAgent"""
        print(f"[DEBUG] Combiner Node called")
        
        try:
            if self.combiner_agent:
                # Use the intelligent CombinerAgent
                combined_response = self.combiner_agent.combine_responses(
                    original_query=state.query,
                    table_response=state.table_response if state.table_response else None,
                    rag_response=state.rag_response if state.rag_response else None
                )
                print(f"[DEBUG] Combiner Node using CombinerAgent: {combined_response[:100]}...")
            else:
                # Fallback to simple combination
                combined_response = ""
                
                if state.table_response and state.rag_response:
                    combined_response = f"{state.rag_response}\n\n{state.table_response}"
                elif state.table_response:
                    combined_response = state.table_response
                elif state.rag_response:
                    combined_response = state.rag_response
                else:
                    combined_response = "No response generated"
                
                print(f"[DEBUG] Combiner Node using fallback combination: {combined_response}")
        
        except Exception as e:
            logger.error(f"Error in combiner node: {e}")
            # Simple fallback on error
            combined_response = state.rag_response or state.table_response or "Error generating response"
            print(f"[DEBUG] Combiner Node error fallback: {combined_response}")
        
        return {"response": combined_response}
    
    def _decide_route(self, state: AgentState) -> str:
        """Decide which route to take based on manager analysis"""
        if state.needs_table and state.needs_rag:
            return "both"
        elif state.needs_table:
            return "table_only"
        elif state.needs_rag:
            return "rag_only"
        else:
            return "end"
    
    def _after_table_route(self, state: AgentState) -> str:
        """Decide route after table processing"""
        if state.needs_rag:
            return "to_rag"
        else:
            return "to_combiner"
    
    def process_query(self, query: str, pdf_uuid: str = None) -> Dict[str, Any]:
        """
        Process a user query through the LangGraph workflow
        
        Args:
            query (str): The user's question
            pdf_uuid (str, optional): UUID of the PDF being queried
            
        Returns:
            Dict[str, Any]: Response containing answer and metadata
        """
        try:
            print(f"[DEBUG] Manager Agent processing query: {query} for PDF: {pdf_uuid}")
            
            # Create initial state
            initial_state = AgentState(query=query, pdf_uuid=pdf_uuid)
            
            # Run the workflow
            result = self.workflow.invoke(initial_state)
            
            # Extract values from the AddableValuesDict result
            final_response = result.get("response", "No response generated")
            needs_table = result.get("needs_table", False)
            needs_rag = result.get("needs_rag", False)
            query_type = result.get("query_type", "unknown")
            
            print(f"[DEBUG] Manager Agent final result: {final_response}")
            print(f"[DEBUG] Query classification: {query_type}")
            
            return {
                "answer": final_response,
                "success": True,
                "error": None,
                "query_type": query_type,  # Add for comparison endpoint
                "metadata": {
                    "used_table": needs_table,
                    "used_rag": needs_rag,
                    "query_type": query_type
                }
            }
            
        except Exception as e:
            logger.error(f"Error in Manager Agent: {e}", exc_info=True)
            
            # Check if it's a quota/rate limit error
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str or "resourceexhausted" in error_str:
                return {
                    "answer": "⚠️ **GEMINI API QUOTA EXCEEDED**\n\n" +
                             "The daily API request limit has been reached. Please try again later or contact support.\n\n" +
                             "**Details:**\n" +
                             "- Free tier limit: 250 requests/day\n" +
                             "- Quota resets at midnight UTC\n" +
                             "- Current error: API quota exceeded",
                    "success": False,
                    "error": "QUOTA_EXCEEDED",
                    "error_type": "quota_exceeded",
                    "metadata": {"quota_exceeded": True}
                }
            
            # Generic error for other exceptions
            return {
                "answer": "I encountered an error while processing your question. Please try again.",
                "success": False,
                "error": str(e),
                "metadata": {}
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for the Manager Agent"""
        try:
            # Test LLM connection
            test_response = self.llm.invoke([HumanMessage(content="Hello")])
            
            # Check combiner agent health
            combiner_health = True
            if self.combiner_agent:
                combiner_status = self.combiner_agent.health_check()
                combiner_health = combiner_status.get("overall_health", False)
            
            return {
                "manager_agent": True,
                "llm_connection": True,
                "workflow_ready": self.workflow is not None,
                "combiner_agent": combiner_health,
                "chatbot_agent_available": self.chatbot_agent is not None,
                "overall_health": True
            }
        except Exception as e:
            logger.error(f"Manager Agent health check failed: {e}")
            return {
                "manager_agent": False,
                "llm_connection": False,
                "workflow_ready": False,
                "combiner_agent": False,
                "chatbot_agent_available": False,
                "overall_health": False,
                "error": str(e)
            }
    

    def _load_table_schema(self, pdf_uuid: str = None) -> str:
        """Load table schema from JSON file with better error handling and path resolution"""
        import time
        
        # ⚡ SPEED OPTIMIZATION: Check cache first
        cache_key = f"schema_{pdf_uuid or 'all'}"
        if (self._schema_cache and 
            self._schema_cache_time and 
            time.time() - self._schema_cache_time < self._schema_cache_ttl and
            cache_key in self._schema_cache):
            logger.debug(f"✅ Using cached schema for {cache_key}")
            return self._schema_cache[cache_key]
        
        try:
            # Try multiple possible paths for the schema file
            possible_paths = [
                os.path.join(os.path.dirname(__file__), '..', 'utils', 'table_schema.json'),
                os.path.join(os.getcwd(), 'src', 'backend', 'utils', 'table_schema.json'),
                'src/backend/utils/table_schema.json',
                './src/backend/utils/table_schema.json'
            ]
            
            schema_path = None
            for path in possible_paths:
                abs_path = os.path.abspath(path)
                logger.debug(f"Checking schema path: {abs_path}")
                if os.path.exists(abs_path):
                    schema_path = abs_path
                    logger.info(f"Found schema file at: {schema_path}")
                    break
            
            if not schema_path:
                logger.error("Schema file not found in any expected location")
                logger.error(f"Searched paths: {[os.path.abspath(p) for p in possible_paths]}")
                return "Database schema not available - file not found"
            
            with open(schema_path, 'r') as f:
                schema_data = json.load(f)
            
            if not schema_data:
                logger.warning("Schema file is empty")
                return "Database schema not available - empty schema"
            
            # Filter by PDF UUID if provided
            if pdf_uuid:
                filtered_schema = {
                    table_name: table_info for table_name, table_info in schema_data.items()
                    if table_info.get('pdf_uuid') == pdf_uuid
                }
                schema_data = filtered_schema
                
                if not schema_data:
                    logger.info(f"No schemas found for PDF UUID: {pdf_uuid}")
                    return f"No database schemas available for the current document (UUID: {pdf_uuid})"
            
            # Convert schema to detailed readable format for the LLM
            schema_info = ""
            for table_name, table_info in schema_data.items():
                schema_info += f"\nTable: {table_name}\n"
                schema_info += f"Description: {table_info.get('description', 'No description')}\n"
                schema_info += f"Columns:\n"
                
                if 'schema' in table_info:
                    for column_name, column_type in table_info['schema'].items():
                        schema_info += f"  - {column_name} ({column_type})\n"
                
                schema_info += f"Created: {table_info.get('created_at', 'Unknown')}\n"
                schema_info += "-" * 50 + "\n"
            
            logger.info(f"Successfully loaded schema with {len(schema_data)} tables")
            
            # ⚡ SPEED OPTIMIZATION: Store in cache
            if not isinstance(self._schema_cache, dict):
                self._schema_cache = {}
            self._schema_cache[cache_key] = schema_info
            self._schema_cache_time = time.time()
            logger.debug(f"✅ Cached schema for {cache_key}")
            
            return schema_info
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schema file: {e}")
            return "Database schema not available - invalid JSON format"
        except Exception as e:
            logger.error(f"Failed to load table schema: {e}")
            return "Database schema not available"