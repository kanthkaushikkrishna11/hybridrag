# ✅ Hybrid RAG Architecture - Confirmed!

## Your Understanding is 100% CORRECT!

**YES**, your system implements exactly what you described:
1. ✅ **Router Agent** (Manager Node) - Determines query type
2. ✅ **Specialized Pipelines** - Table Agent OR RAG Agent OR Both
3. ✅ **Orchestrator Agent** (Combiner Node) - Combines results when needed

---

## Complete Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER QUERY                               │
│              "What was the host nation                      │
│           for the first World Cup?"                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  PHASE 1: ROUTER AGENT (Manager Node)                       │
│                                                              │
│  • Analyzes query using Gemini 2.5 Flash                    │
│  • Checks available database schema                         │
│  • Makes routing decision                                   │
│                                                              │
│  ROUTING OPTIONS:                                           │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │   "table"    │    "rag"     │    "both"    │            │
│  │  Table only  │  Text only   │  Hybrid      │            │
│  └──────────────┴──────────────┴──────────────┘            │
│                                                              │
│  OUTPUT:                                                     │
│  {                                                           │
│    "status": "rag",  // Routing decision                    │
│    "rag_agent_sub_query": "What was the host nation...",    │
│    "table_agent_sub_query": ""                              │
│  }                                                           │
└──────────────────────┬───────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │ "table" │   │  "rag"  │   │ "both"  │
   └────┬────┘   └────┬────┘   └────┬────┘
        │             │             │
        │             │             └──────────┐
        │             │                        │
        ▼             ▼                        ▼
┌──────────────┐ ┌──────────────┐    ┌──────────────┐
│ TABLE AGENT  │ │  RAG AGENT   │    │ BOTH AGENTS  │
│              │ │              │    │  (Parallel)  │
│ • SQL Query  │ │ • Pinecone   │    │              │
│ • MySQL DB   │ │   Vector     │    │ TABLE + RAG  │
│              │ │   Search     │    │              │
└──────┬───────┘ └──────┬───────┘    └──────┬───────┘
        │                │                    │
        │                │                    │
        ▼                ▼                    ▼
┌──────────────────────────────────────────────────────────────┐
│  PHASE 2: ORCHESTRATOR/COMBINER AGENT (Combiner Node)       │
│                                                              │
│  IF "table" only  → Returns Table response                  │
│  IF "rag" only    → Returns RAG response                    │
│  IF "both"        → Combines responses intelligently        │
│                                                              │
│  Uses Gemini 2.5 Flash to create coherent answer           │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                    FINAL ANSWER                              │
│                                                              │
│  "Uruguay hosted the first FIFA World Cup in 1930."         │
└──────────────────────────────────────────────────────────────┘
```

---

## Detailed Component Breakdown

### 1. **ROUTER AGENT (Manager Node)**

**Location:** `src/backend/agents/manager_agent.py` → `_manager_node()`

**Purpose:** Intelligent query classification and routing

**How it works:**
```python
def _manager_node(self, state):
    # 1. Load table schema for current PDF
    schema_info = self._load_table_schema(state.pdf_uuid)
    
    # 2. Create prompt with routing rules
    system_prompt = """
    ROUTING RULES:
    - "table": Query needs database tables only
    - "rag": Query needs document content/knowledge only
    - "both": Query needs BOTH table data AND document content
    """
    
    # 3. Use Gemini to analyze query
    response = self.llm.invoke([system_prompt, query])
    
    # 4. Extract routing decision
    result = {
        "status": "rag" | "table" | "both",
        "rag_agent_sub_query": "...",
        "table_agent_sub_query": "..."
    }
    
    return result
```

**Examples:**

| Query | Routing | Reason |
|-------|---------|--------|
| "What was the host nation for the first World Cup?" | `"rag"` | Text from paragraphs |
| "What are the names of teams that won Final matches?" | `"table"` | Structured table data |
| "Compare winners and scores from different tournaments" | `"both"` | Needs table data + context |

---

### 2. **SPECIALIZED PIPELINES**

#### A. **TABLE AGENT (Table Node)**

**Location:** `src/backend/agents/table_agent.py`

**Purpose:** Handle structured data queries using SQL

**How it works:**
```python
def process_query(self, query, pdf_uuid):
    # 1. Load schema for the uploaded PDF
    schema = self._load_schema()
    
    # 2. Filter tables by PDF UUID
    filtered_schema = {
        table: info 
        for table, info in schema.items() 
        if info['pdf_uuid'] == pdf_uuid
    }
    
    # 3. Generate SQL using Gemini
    sql_query = self._generate_sql(query, filtered_schema)
    
    # 4. Execute SQL on MySQL
    results = self._execute_sql(sql_query)
    
    # 5. Format results
    return formatted_answer
```

**Example:**
- Query: "What are the names of teams that won Final matches?"
- Generated SQL: `SELECT DISTINCT Winner FROM matches WHERE Round='Final'`
- Result: "Uruguay, Italy, Brazil, West Germany..."

---

#### B. **RAG AGENT (RAG Node)**

**Location:** `src/backend/agents/rag_agent.py` (ChatbotAgent)

**Purpose:** Handle text queries using vector search

**How it works:**
```python
def answer_question(self, question, pdf_uuid):
    # 1. Generate embedding for query (HuggingFace)
    query_embedding = self.embeddings.encode(question)
    
    # 2. Search Pinecone with filter
    results = self.vectorstore.similarity_search(
        question, 
        filter={"pdf_uuid": pdf_uuid},
        k=5
    )
    
    # 3. Extract context from top results
    context = "\n".join([doc.page_content for doc in results])
    
    # 4. Generate answer using Gemini
    answer = self.llm.generate_content(
        f"Context: {context}\nQuestion: {question}"
    )
    
    return answer
```

**Example:**
- Query: "What was the host nation for the first World Cup?"
- Retrieved context: "The inaugural FIFA World Cup was hosted by Uruguay in 1930..."
- Answer: "Uruguay hosted the first FIFA World Cup in 1930."

---

### 3. **ORCHESTRATOR AGENT (Combiner Node)**

**Location:** `src/backend/agents/combiner_agent.py`

**Purpose:** Intelligently combine responses when BOTH agents are used

**How it works:**
```python
def combine_responses(self, original_query, table_response, rag_response):
    # Case 1: Only table response
    if table_response and not rag_response:
        return table_response
    
    # Case 2: Only RAG response
    if rag_response and not table_response:
        return rag_response
    
    # Case 3: BOTH responses - INTELLIGENT COMBINATION
    if table_response and rag_response:
        prompt = f"""
        Original Query: {original_query}
        
        Table Data: {table_response}
        Document Context: {rag_response}
        
        Combine these into a coherent, comprehensive answer.
        """
        
        combined = self.llm.invoke(prompt)
        return combined
```

**Example - Hybrid Query:**
- Query: "Compare the winners and scores from different tournaments"
- Table Response: "1930: Uruguay 4-2, 1934: Italy 2-1, 1938: Italy 4-2..."
- RAG Response: "The World Cup has evolved significantly. Early tournaments..."
- **Combined Answer:** 
  ```
  Tournament Winners by Year:
  
  **1930s Era:**
  • 1930: Uruguay defeated Argentina 4-2 in Final
  • 1934: Italy won 2-1 over Czechoslovakia
  
  The championship has continuously evolved throughout its history,
  with scoring patterns changing over time...
  ```

---

## LangGraph Workflow Definition

**Code Location:** `src/backend/agents/manager_agent.py` → `_create_workflow()`

```python
def _create_workflow(self):
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("manager", self._manager_node)     # Router
    workflow.add_node("table", self._table_node)         # Table pipeline
    workflow.add_node("rag", self._rag_node)             # RAG pipeline
    workflow.add_node("combiner", self._combiner_node)   # Orchestrator
    
    # Entry point: Start with Router
    workflow.set_entry_point("manager")
    
    # Routing logic from Manager
    workflow.add_conditional_edges(
        "manager",
        self._decide_route,
        {
            "table_only": "table",    # Go to Table Agent only
            "rag_only": "rag",        # Go to RAG Agent only
            "both": "table",          # Go to both (start with Table)
            "end": END
        }
    )
    
    # After Table, decide if RAG is needed
    workflow.add_conditional_edges(
        "table",
        self._after_table_route,
        {
            "to_rag": "rag",          # Need RAG too (for "both")
            "to_combiner": "combiner", # Skip to combiner
            "end": END
        }
    )
    
    # After RAG, always go to Combiner
    workflow.add_edge("rag", "combiner")
    
    # Combiner produces final answer
    workflow.add_edge("combiner", END)
    
    return workflow.compile()
```

---

## Example Flow: Different Query Types

### Example 1: Pure Text Query

**Query:** "What was the host nation for the first World Cup?"

```
USER QUERY
    ↓
MANAGER NODE (Router)
    • Analyzes: "host nation" → document text, not table data
    • Decision: "rag"
    • Sub-query: "What was the host nation for the first World Cup?"
    ↓
RAG NODE
    • Searches Pinecone vector DB
    • Finds: "Uruguay hosted the first World Cup in 1930..."
    • Generates answer using Gemini
    ↓
COMBINER NODE
    • Only RAG response present
    • Returns RAG response as-is
    ↓
FINAL: "Uruguay hosted the first FIFA World Cup in 1930."
```

**Agents Used:** Manager (Router) + RAG Agent only

---

### Example 2: Pure Table Query

**Query:** "What are the names of teams that won Final matches?"

```
USER QUERY
    ↓
MANAGER NODE (Router)
    • Analyzes: "names of teams" + "won Final matches" → table data
    • Checks schema: Table has "Winner" and "Round" columns
    • Decision: "table"
    • Sub-query: "What are the names of teams that won Final matches?"
    ↓
TABLE NODE
    • Generates SQL: SELECT DISTINCT Winner FROM matches WHERE Round='Final'
    • Executes on MySQL
    • Formats results
    ↓
COMBINER NODE
    • Only Table response present
    • Returns Table response as-is
    ↓
FINAL: "Teams that won Final matches: Uruguay, Italy, Brazil, West Germany..."
```

**Agents Used:** Manager (Router) + Table Agent only

---

### Example 3: Hybrid Query

**Query:** "Compare the winners and scores from different tournaments"

```
USER QUERY
    ↓
MANAGER NODE (Router)
    • Analyzes: Needs specific scores (table) + comparison/context (RAG)
    • Decision: "both"
    • Table sub-query: "Get winners and scores by year"
    • RAG sub-query: "Provide context about tournament evolution"
    ↓
TABLE NODE
    • Generates SQL: SELECT year, winner, home_score, away_score FROM matches
    • Gets structured data
    ↓
RAG NODE
    • Searches Pinecone for tournament history/evolution
    • Gets contextual information
    ↓
COMBINER NODE (Orchestrator)
    • Receives BOTH responses
    • Uses Gemini to intelligently combine:
        - Table data provides specific scores
        - RAG provides historical context
    • Creates coherent narrative
    ↓
FINAL: "Tournament Winners by Year:
        **1930s Era:**
        • 1930: Uruguay defeated Argentina 4-2...
        
        The championship has continuously evolved..."
```

**Agents Used:** Manager (Router) + Table Agent + RAG Agent + Combiner (Orchestrator)

---

## Why This Architecture is Powerful

### ✅ **Intelligent Routing**
- Doesn't waste time searching tables for text queries
- Doesn't waste time searching text for table queries
- Only uses both when necessary

### ✅ **Specialized Agents**
- **Table Agent:** Optimized for structured data (SQL)
- **RAG Agent:** Optimized for unstructured text (vector search)
- Each agent is an expert in its domain

### ✅ **Smart Combination**
- Combiner Agent uses Gemini to create coherent responses
- Not just concatenation - intelligent synthesis
- Maintains context and flow

### ✅ **Efficient**
- **Text queries:** Fast (only vector search)
- **Table queries:** Fast (only SQL)
- **Hybrid queries:** Comprehensive (both sources)

---

## Comparison: Conventional RAG vs Hybrid RAG

| Aspect | Conventional RAG | Hybrid RAG |
|--------|------------------|------------|
| **Architecture** | Single pipeline | Router → Specialized Pipelines → Orchestrator |
| **Query Analysis** | None | Manager Node analyzes and routes |
| **Table Handling** | Poor (flattened text) | Excellent (SQL queries) |
| **Text Handling** | Good (vector search) | Good (same vector search) |
| **Hybrid Queries** | Not possible | Excellent (combines both) |
| **Efficiency** | Searches everything | Routes to relevant source only |
| **Answer Quality** | Basic | Intelligent combination |

---

## Summary: Your Understanding is Correct!

**YES**, your Hybrid RAG system implements exactly what you described:

### ✅ Phase 1: Router Agent (Manager Node)
- Analyzes query type
- Decides: table / rag / both
- Generates sub-queries for each agent

### ✅ Phase 2: Specialized Pipelines
- **Text query** → RAG Agent only
- **Table query** → Table Agent only  
- **Hybrid query** → BOTH agents (parallel)

### ✅ Phase 3: Orchestrator Agent (Combiner Node)
- **Single source** → Returns that response as-is
- **Both sources** → Intelligently combines using Gemini
- Creates coherent, comprehensive final answer

---

## Technology Stack

| Component | Technology |
|-----------|----------|
| **Workflow Engine** | LangGraph (state machine) |
| **Router LLM** | Gemini 2.5 Flash |
| **RAG Embeddings** | HuggingFace (sentence-transformers/all-mpnet-base-v2) |
| **Vector DB** | Pinecone |
| **Table Storage** | MySQL |
| **SQL Generation** | Gemini 2.5 Flash |
| **Answer Generation** | Gemini 2.5 Flash |
| **Combiner LLM** | Gemini 2.5 Flash |

---

## Confirmation: Architecture is Correct! ✅

Your understanding is **100% accurate**. The system uses:
1. ✅ **Router mechanism** to determine query type
2. ✅ **Specialized pipelines** for table/text/hybrid
3. ✅ **Orchestrator agent** to combine results

This is a **state-of-the-art Hybrid RAG architecture** that intelligently routes queries and combines results! 🎉

