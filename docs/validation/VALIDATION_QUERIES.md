# HybridRAG Validation Query Suite

## Purpose
This document contains carefully designed natural language queries to validate the HybridRAG system's:
1. **Query Classification Accuracy**: Correct routing to Table, Text, or Hybrid pipelines
2. **Pipeline Isolation**: Table queries should ONLY use table pipeline, Text queries should ONLY use text pipeline
3. **Intelligent Combination**: Hybrid queries should use both pipelines and combine results intelligently
4. **Performance Comparison**: Demonstrate Hybrid RAG superiority over Conventional RAG for Table and Hybrid queries

---

## Table Structure Reference
```
pdf_*_world_cup_matches table:
- Match_ID / match_id (integer)
- Year (integer)
- Round (string): e.g., "Group 1", "Semi-final", "Final", "Quarter-final", "Round of 16"
- Home_Team (string)
- Away_Team (string)
- Home_Score (integer)
- Away_Score (integer)
- Winner (string): Team name or "Draw"

Data Range: 1930-1978 World Cup matches (100 rows)
```

---

## 1️⃣ TABLE QUERIES (15 queries)
**Expected Behavior**: Query classified as "Table" → Only Table Agent pipeline triggered → No Text RAG consulted

### Basic Table Queries (6)
1. What are the names of the teams which won the Final matches in the world cup matches?
2. Tell me the name and year in which a team won the Final match in the World Cup Matches
3. What was the highest Home Score by any team in World Cup Matches? Print the Year, Home Team Name, Away Team Name, Winning Team Name, number of goals scored.
4. How many matches in the World Cup ended in a draw?
5. What was the host nation for the first football World Cup?
6. What is the count of the number of rows in the data?

### Intermediate Table Queries (6)
7. How many goals did Brazil score in total (home + away)?
8. Which team won the most matches in the dataset?
9. List all Semi-final matches with scores
10. What is the average number of goals scored per match?
11. How many matches were played in each World Cup year?
12. Which rounds had the most draws?

### Advanced Table Queries (3)
13. Which teams have won a World Cup Final? (with count of championships)
14. Find all matches where the home team scored more than 5 goals
15. Which matches had the highest total goals (home + away)?

---

## 2️⃣ TEXT QUERIES (15 queries)
**Expected Behavior**: Query classified as "Text" → Only Text RAG pipeline triggered → No Table Agent consulted

### Historical & Contextual Queries (5)
1. What is the historical significance of the FIFA World Cup and when did it start?
2. Describe the format and evolution of the World Cup tournament over the years.
3. What were the major changes in World Cup organization between 1930 and 1978?
4. Explain the cultural and social impact of the FIFA World Cup.
5. What role did FIFA play in organizing the World Cup tournaments?

### Tournament Description Queries (5)
6. Which countries hosted the FIFA World Cup tournaments and what were the notable features of their hosting?
7. Describe the qualification process for the FIFA World Cup.
8. What were some of the memorable moments in early World Cup history?
9. How did World War II affect the FIFA World Cup schedule?
10. What were the opening ceremony highlights mentioned in the document?

### Player & Team Narrative Queries (5)
11. Who were some of the legendary players mentioned in the FIFA World Cup history?
12. Describe the playing styles and strategies that characterized early World Cup tournaments.
13. What factors contributed to certain teams' dominance in World Cup history?
14. How did team compositions and national squad selections evolve over time?
15. What were the notable achievements and records set by individual players in the World Cup?

---

## 3️⃣ HYBRID QUERIES (15 queries)
**Expected Behavior**: Query uses BOTH pipelines → Table Agent provides data → Text RAG provides context → Combiner Agent intelligently merges both

### Match Context + Data Queries (5)
1. Which team won the 1950 World Cup Final and what was historically significant about that tournament and match?
2. Tell me about Brazil's performance in the 1970 World Cup - both their match results and the historical context of that tournament.
3. How many goals were scored in the 1954 World Cup Final and what made that tournament memorable?
4. Which team had the highest goal difference in Quarter-final matches and what was the historical significance of their performance?
5. List the Semi-final winners from 1974 World Cup and describe the tournament atmosphere and context.

### Statistical + Narrative Queries (5)
6. What were the top-scoring teams in the 1930s World Cups and what historical factors influenced their success?
7. Compare the goal-scoring patterns between 1930-1950 World Cups with the historical context of football evolution during that period.
8. Which countries hosted World Cups in the 1960s and what were the match outcomes in those tournaments?
9. Analyze the draw percentage in World Cup matches and explain why draws were more or less common in different eras.
10. Which teams appeared most frequently in Finals and what were the historical circumstances that led to their dominance?

### Complex Integration Queries (5)
11. Provide a comprehensive overview of Uruguay's World Cup journey including their match statistics and historical achievements.
12. What was the highest-scoring World Cup tournament based on the data, and what historical factors contributed to the high-scoring nature?
13. Compare Argentina's performance in home and away matches, and describe their overall World Cup legacy.
14. Which Round of the tournament saw the most competitive matches (smallest goal differences) and what does this say about tournament progression?
15. Give me a detailed analysis of Italy's World Cup performance with both statistical data and historical context about their football heritage.

---

## 4️⃣ EDGE CASE & VALIDATION QUERIES (5 additional)
**To test boundary conditions and ensure robust classification**

1. **Ambiguous Query**: "Tell me about Brazil in the World Cup" 
   - Could be Text or Hybrid - system should make intelligent choice

2. **Numeric but Text**: "How many World Cup tournaments are mentioned in the document?"
   - Requires reading text content, not table counting

3. **Contextual Table**: "What does the Winner column represent in the match data?"
   - Asks about table structure/meaning, not data query

4. **Combined Statistics**: "Calculate the average goals per match AND explain the historical reasons for scoring trends"
   - Clear hybrid: calculation + narrative

5. **Pure Description**: "Describe the structure and format of the World Cup match data provided"
   - Pure text about the data, not querying the data itself

---

## 5️⃣ EXPECTED OUTCOMES

### Success Criteria:

#### Text Queries:
- ✅ Conventional RAG Performance: **~80-90%** accuracy
- ✅ Hybrid RAG Performance: **~80-90%** accuracy
- ✅ **Result**: Similar performance (both rely on text chunks)

#### Table Queries:
- ❌ Conventional RAG Performance: **~10-30%** accuracy (fails on structured data)
- ✅ Hybrid RAG Performance: **~90-100%** accuracy (dedicated table pipeline)
- ✅ **Result**: Hybrid RAG vastly superior (3-9x better)

#### Hybrid Queries:
- ❌ Conventional RAG Performance: **~30-50%** accuracy (gets partial info)
- ✅ Hybrid RAG Performance: **~85-95%** accuracy (combines both sources)
- ✅ **Result**: Hybrid RAG significantly superior (1.7-3x better)

---

## 6️⃣ VALIDATION METHODOLOGY

### For Each Query:
1. **Run through Hybrid RAG system**
2. **Check classification log**: Verify correct pipeline routing
3. **Inspect agent calls**: Ensure only appropriate agents are invoked
4. **Evaluate answer quality**: Check accuracy and completeness
5. **Compare with Conventional RAG**: Run same query through text-only RAG
6. **Score and document**: Record classification accuracy and answer quality

### Metrics to Track:
- ✅ Classification Accuracy: % of correctly routed queries
- ✅ Pipeline Isolation: % of queries that ONLY use designated pipeline
- ✅ Answer Accuracy: Qualitative scoring (1-5 scale)
- ✅ Comparative Performance: Hybrid vs Conventional RAG score difference

---

## 7️⃣ TESTING INSTRUCTIONS

### Step 1: Prepare Environment
```bash
# Ensure HybridRAG backend is running
# Ensure FIFA World Cup PDF is uploaded and processed
# Verify table_schema.json contains World Cup table info
```

### Step 2: Test Each Category
```python
# Pseudo-code for testing
for query in [table_queries, text_queries, hybrid_queries]:
    # 1. Submit query to HybridRAG
    response = hybridrag_api.query(query)
    
    # 2. Check logs for classification
    classification = check_manager_agent_log()
    
    # 3. Verify pipeline routing
    agents_called = check_which_agents_invoked()
    
    # 4. Validate answer
    accuracy_score = evaluate_answer(response, expected_answer)
    
    # 5. Compare with conventional RAG
    conventional_response = conventional_rag.query(query)
    conventional_score = evaluate_answer(conventional_response, expected_answer)
    
    # 6. Record results
    log_results(query, classification, agents_called, 
                accuracy_score, conventional_score)
```

### Step 3: Analyze Results
- Generate confusion matrix for classification
- Calculate performance metrics for each query type
- Create comparative charts (Hybrid vs Conventional)
- Document edge cases and failure modes

---

## 8️⃣ NOTES

- **Table queries** are designed to ONLY be answerable through SQL queries on the structured data
- **Text queries** are designed to require semantic understanding of narrative content
- **Hybrid queries** are carefully crafted to REQUIRE both data + context for complete answers
- Expected behavior: Clear separation for Table/Text, intelligent combination for Hybrid
- Goal: Demonstrate that Hybrid RAG excels at structured data while maintaining text RAG quality


