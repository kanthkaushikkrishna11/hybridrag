# ⚡ Speed Optimization for Hybrid RAG

**Goal**: Reduce processing time while maintaining accuracy

---

## 📊 **CURRENT PERFORMANCE**

Based on testing:

| Query Type | Conventional RAG | Hybrid RAG | Slowdown |
|------------|------------------|------------|----------|
| **Simple Table** | 3-5s | 6-8s | 2x slower |
| **Complex Table** | 5-7s | 10-15s | 2x slower |
| **Text** | 7-9s | 14-18s | 2x slower |
| **Hybrid** | 8-10s | 25-45s | 3-5x slower |

**Why is Hybrid RAG slower?**
- Makes multiple LLM calls (Manager → Table/RAG → Combiner)
- Generates and executes SQL
- Orchestrates workflow through LangGraph
- Combines responses

---

## 🎯 **OPTIMIZATION STRATEGY**

### **Priority Levels**:
1. **🔴 High Impact, Easy** - Do these first
2. **🟡 Medium Impact** - Do if needed
3. **🟢 Low Priority** - Only if critical

---

## 🔴 **HIGH PRIORITY OPTIMIZATIONS**

### **1. Reduce LLM Calls with Caching** ⚡

**Problem**: Manager Agent calls LLM to classify every query, even if identical.

**Solution**: Cache query classifications
```python
# Add to manager_agent.py

from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def _get_classification_cache_key(query: str) -> str:
    return hashlib.md5(query.lower().strip().encode()).hexdigest()

def _manager_node(self, state: AgentState) -> Dict[str, Any]:
    # Check cache first
    cache_key = self._get_classification_cache_key(state.query)
    if cache_key in self._classification_cache:
        cached = self._classification_cache[cache_key]
        state.needs_table = cached['needs_table']
        state.needs_rag = cached['needs_rag']
        state.query_type = cached['query_type']
        return cached
    
    # ... existing classification logic ...
    
    # Store in cache
    self._classification_cache[cache_key] = result
    return result
```

**Expected Improvement**: Save 1-2s per repeated query

---

### **2. Parallel Agent Execution** ⚡⚡

**Problem**: For "both" queries, Table Agent and RAG Agent run sequentially.

**Solution**: Run them in parallel
```python
# In manager_agent.py, modify workflow

import asyncio

async def _execute_agents_parallel(self, state: AgentState):
    if state.needs_table and state.needs_rag:
        # Run both agents in parallel
        table_task = asyncio.create_task(
            self._async_table_node(state)
        )
        rag_task = asyncio.create_task(
            self._async_rag_node(state)
        )
        
        table_result, rag_result = await asyncio.gather(table_task, rag_task)
        
        state.table_response = table_result['table_response']
        state.rag_response = rag_result['rag_response']
    # ... else cases ...
```

**Expected Improvement**: Save 5-10s on hybrid queries (currently 25-45s → 15-25s)

---

### **3. Schema Caching** ⚡

**Problem**: Manager Agent reloads table schema from file on every query.

**Solution**: Cache schema in memory
```python
# In manager_agent.py

def __init__(self, ...):
    # ... existing init ...
    self._schema_cache = None
    self._schema_cache_time = None
    self._schema_cache_ttl = 300  # 5 minutes

def _load_table_schema(self, pdf_uuid: str = None) -> str:
    # Check cache first
    if self._schema_cache and time.time() - self._schema_cache_time < self._schema_cache_ttl:
        return self._schema_cache
    
    # Load and cache
    schema = self._load_schema_from_file(pdf_uuid)
    self._schema_cache = schema
    self._schema_cache_time = time.time()
    return schema
```

**Expected Improvement**: Save 0.1-0.3s per query

---

### **4. Use Lighter Model for Classification** ⚡

**Problem**: Using `gemini-2.5-flash` for simple routing decisions.

**Solution**: Use faster model for classification only
```python
# In manager_agent.py

def __init__(self, gemini_api_key: str, ...):
    # Main LLM for complex tasks
    self.llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=gemini_api_key,
        temperature=0
    )
    
    # Lighter LLM for classification only
    self.classifier_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",  # Faster for simple tasks
        google_api_key=gemini_api_key,
        temperature=0
    )
```

**Expected Improvement**: Save 0.5-1s on classification

**⚠️ Note**: This breaks fair comparison! Only implement after validation is complete.

---

### **5. Reduce top_k for Vector Search** ⚡

**Problem**: Retrieving 5 chunks may be overkill for many queries.

**Solution**: Use adaptive top_k
```python
# In rag_agent.py

def answer_question(self, question: str, top_k: int = None, ...):
    # Adaptive top_k based on query length
    if top_k is None:
        query_words = len(question.split())
        if query_words < 10:
            top_k = 3  # Simple queries need fewer chunks
        elif query_words < 20:
            top_k = 4
        else:
            top_k = 5  # Complex queries need more context
    
    # ... rest of method ...
```

**Expected Improvement**: Save 0.2-0.5s per query

---

## 🟡 **MEDIUM PRIORITY OPTIMIZATIONS**

### **6. SQL Query Optimization**

**Problem**: Table Agent generates complex SQL that may be slow.

**Solution**: Add indexes to database tables
```python
# In table_schema.json, add index hints

{
    "table_name": {
        "schema": {...},
        "indexes": ["year", "round", "home_team", "away_team", "winner"]
    }
}
```

Then create indexes:
```sql
CREATE INDEX idx_year ON table_name(year);
CREATE INDEX idx_round ON table_name(round);
CREATE INDEX idx_home_team ON table_name(home_team);
CREATE INDEX idx_away_team ON table_name(away_team);
CREATE INDEX idx_winner ON table_name(winner);
```

**Expected Improvement**: Save 0.1-0.5s on complex SQL queries

---

### **7. Connection Pooling**

**Problem**: Creating new database connections for each query.

**Solution**: Use connection pooling
```python
# In table_agent.py

from psycopg2 import pool

class TableAgent:
    def __init__(self, ...):
        # ... existing init ...
        self.connection_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=5,
            host=os.getenv('DATABASE_HOST'),
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD'),
            database=os.getenv('DATABASE_NAME'),
            port=int(os.getenv('DATABASE_PORT', 5432))
        )
    
    def _execute_sql_query(self, sql_query: str, ...):
        conn = self.connection_pool.getconn()
        try:
            # ... execute query ...
        finally:
            self.connection_pool.putconn(conn)
```

**Expected Improvement**: Save 0.1-0.2s per query

---

### **8. Streaming Responses**

**Problem**: Users wait for complete response before seeing anything.

**Solution**: Stream responses as they're generated
```python
# In routes/chat.py

from fastapi.responses import StreamingResponse

@router.post("/answer-stream")
async def answer_question_stream(request: QueryRequest):
    async def generate():
        # Stream Manager classification
        yield json.dumps({"status": "classifying"}) + "\n"
        
        # Stream Table Agent results
        if needs_table:
            yield json.dumps({"status": "querying_data"}) + "\n"
            # ... get table results ...
            yield json.dumps({"table_result": result}) + "\n"
        
        # Stream final answer
        yield json.dumps({"answer": final_answer}) + "\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

**Expected Improvement**: Better perceived performance (doesn't reduce actual time, but feels faster)

---

## 🟢 **LOW PRIORITY / ADVANCED**

### **9. GPU Acceleration for Embeddings**

**Problem**: CPU embeddings are slower than GPU.

**Solution**: Use GPU if available
```python
# In rag_agent.py

self.embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)
```

**Expected Improvement**: Save 0.3-0.5s per query (only if GPU available)

---

### **10. Prompt Optimization**

**Problem**: Long system prompts increase token count and processing time.

**Solution**: Compress prompts while maintaining clarity
- Remove examples that LLM doesn't need
- Use shorter instruction phrases
- Remove redundant explanations

**Expected Improvement**: Save 0.2-0.4s per LLM call

---

## 📊 **IMPLEMENTATION PRIORITY**

### **Phase 1: Quick Wins (Implement First)** 🔴
1. ✅ Schema Caching (0.1-0.3s saved)
2. ✅ Classification Caching (1-2s saved)
3. ✅ Reduce top_k adaptively (0.2-0.5s saved)

**Total savings: 1.3-2.8s**

### **Phase 2: Structural Improvements** 🟡
4. Parallel Agent Execution (5-10s saved on hybrid queries)
5. Connection Pooling (0.1-0.2s saved)
6. SQL Indexes (0.1-0.5s saved)

**Total savings: 5.3-10.7s**

### **Phase 3: Advanced** 🟢
7. Streaming responses (perceived improvement)
8. GPU acceleration (if available)
9. Prompt optimization

---

## 🎯 **EXPECTED RESULTS AFTER OPTIMIZATION**

| Query Type | Current | After Phase 1 | After Phase 2 | Target |
|------------|---------|---------------|---------------|--------|
| **Simple Table** | 6-8s | 4-6s | 3-5s | ✅ <5s |
| **Complex Table** | 10-15s | 8-12s | 7-10s | ✅ <10s |
| **Text** | 14-18s | 12-15s | 10-13s | ✅ <15s |
| **Hybrid** | 25-45s | 23-42s | 15-25s | ⚠️ <20s (stretch) |

---

## ⚠️ **IMPORTANT CONSIDERATIONS**

### **1. Fair Comparison**
- **Don't optimize until after validation!**
- Optimizations may make comparison invalid if not applied to both systems
- Document any changes that affect comparison

### **2. Accuracy vs Speed Trade-off**
- Reducing top_k may reduce context quality
- Caching classifications assumes queries are identical
- Lighter models may reduce classification accuracy

### **3. Testing Required**
- Test each optimization independently
- Measure actual time savings
- Ensure accuracy isn't degraded

---

## 🛠️ **HOW TO IMPLEMENT**

### **Step 1: Baseline Measurement**
```bash
# Run validation and measure current times
python3 scripts/validate_all_queries.py > baseline_times.json
```

### **Step 2: Implement Phase 1 Optimizations**
```bash
# Make code changes
# Test each optimization

# Measure new times
python3 scripts/validate_all_queries.py > phase1_times.json

# Compare
python3 -c "
import json
baseline = json.load(open('baseline_times.json'))
phase1 = json.load(open('phase1_times.json'))
print(f'Average improvement: {calculate_improvement(baseline, phase1)}')
"
```

### **Step 3: Iterate**
- If Phase 1 achieves targets → Stop
- If not → Implement Phase 2
- Continuously measure and adjust

---

## 🚀 **RECOMMENDED APPROACH**

### **For Testing Phase (Now)**:
- ❌ **Don't optimize yet!**
- Complete validation first
- Measure baseline performance
- Document improvement opportunities

### **After Validation Complete**:
1. Implement **Schema Caching** (easy, safe)
2. Implement **Classification Caching** (easy, big win)
3. Measure improvements
4. Decide if more optimization needed

### **If More Speed Needed**:
4. Implement **Parallel Agent Execution** (complex, big win for hybrid queries)
5. Implement **Connection Pooling** (medium complexity)
6. Consider **Streaming** for better UX

---

## ✅ **SUMMARY**

**Is speed optimization possible?** ✅ **Yes!**

**Quick wins available**:
- Schema caching: 0.1-0.3s
- Classification caching: 1-2s  
- Adaptive top_k: 0.2-0.5s
- **Total: 1.3-2.8s saved**

**Big wins available** (more complex):
- Parallel execution: 5-10s saved on hybrid queries
- Connection pooling: 0.1-0.2s
- **Total: 5.3-10.7s saved**

**Realistic targets**:
- Simple queries: <5s (achievable)
- Complex queries: <10s (achievable)
- Hybrid queries: <20s (stretch goal)

**When to implement**: After validation is complete to maintain fair comparison.

---

**Current recommendation**: Focus on validation first, optimize second. The architecture advantage is more important than speed! 🎯

