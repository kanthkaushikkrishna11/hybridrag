# HybridRAG Validation Testing Guide

## 🎯 Objective

Systematically validate the HybridRAG system to demonstrate:
1. ✅ **Accurate Query Classification**: Table/Text/Hybrid routing
2. ✅ **Pipeline Isolation**: Queries use ONLY appropriate pipelines
3. ✅ **Superior Performance**: Hybrid RAG outperforms Conventional RAG on Table & Hybrid queries
4. ✅ **Comparable Performance**: Hybrid RAG matches Conventional RAG on Text queries

---

## 📋 Prerequisites

### 1. Backend Running
```bash
# Terminal 1: Start backend
cd /Users/krishnakaushik/hybridrag/HybridRAG
source venv/bin/activate
uvicorn app:app --reload --port 8000
```

### 2. Frontend Running (Optional for manual testing)
```bash
# Terminal 2: Start frontend
cd frontend-new
npm run dev
```

### 3. FIFA World Cup PDF Uploaded
- Ensure `The FIFA World Cup_ A Historical Journey-1.pdf` is uploaded
- Check `src/backend/utils/table_schema.json` contains World Cup table entries
- Verify table name: `pdf_*_world_cup_matches` or similar

### 4. Dependencies Installed
```bash
pip install requests tabulate
```

---

## 🚀 Quick Start

### Option 1: Automated Validation (Recommended)

#### Run Quick Test (5 queries per category)
```bash
python validate_hybridrag.py --mode quick
```

#### Run Full Test (15 queries per category)
```bash
python validate_hybridrag.py --mode full
```

#### Test Specific Category
```bash
# Test only table queries
python validate_hybridrag.py --mode category --category table

# Test only text queries
python validate_hybridrag.py --mode category --category text

# Test only hybrid queries
python validate_hybridrag.py --mode category --category hybrid
```

### Option 2: Manual Testing via Frontend

1. Open frontend: `http://localhost:5173`
2. Navigate to Chat interface
3. Test queries from `VALIDATION_QUERIES.md`
4. Observe:
   - Response content
   - Response time
   - Check browser console for classification logs

### Option 3: Manual API Testing

```bash
# Test a single query
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the names of the teams which won the Final matches in the world cup matches?"}'
```

---

## 📊 Understanding Results

### Validation Script Output

```
=================================================================================================
                                  HYBRIDRAG VALIDATION SUMMARY                                   
=================================================================================================

+----------+----------+-----------------+--------------+-----------+-----------+---------+
| Category | Queries  | Classification  | Isolation    | Quality   | Avg Time  | Errors  |
+==========+==========+=================+==============+===========+===========+=========+
| Table    |       15 | 93.3%          | 86.7%        | 4.2/5     | 3.45s     |       0 |
+----------+----------+-----------------+--------------+-----------+-----------+---------+
| Text     |       15 | 100.0%         | 100.0%       | 4.5/5     | 2.18s     |       0 |
+----------+----------+-----------------+--------------+-----------+-----------+---------+
| Hybrid   |       15 | 86.7%          | 80.0%        | 4.0/5     | 4.67s     |       1 |
+----------+----------+-----------------+--------------+-----------+-----------+---------+

📊 OVERALL STATISTICS:
   Total Queries: 45
   Overall Classification Accuracy: 93.3%
   Overall Pipeline Isolation: 88.9%
```

### Key Metrics Explained

1. **Classification Accuracy**: % of queries correctly classified (Table/Text/Hybrid)
   - ✅ Target: >90%
   - ⚠️ Warning: 80-90%
   - ❌ Issue: <80%

2. **Pipeline Isolation Rate**: % of queries that used ONLY appropriate pipelines
   - ✅ Target: >85%
   - ⚠️ Warning: 75-85%
   - ❌ Issue: <75%

3. **Answer Quality**: Heuristic score (1-5) based on response characteristics
   - 5: Excellent, comprehensive answer
   - 4: Good answer with minor gaps
   - 3: Acceptable but incomplete
   - 2: Poor quality or generic
   - 1: Error or no answer

4. **Response Time**: Average time to process query
   - Table queries: 2-5s (SQL generation + execution)
   - Text queries: 1-3s (embedding + retrieval)
   - Hybrid queries: 3-7s (both pipelines + combination)

---

## 🔍 Detailed Analysis

### Check Individual Query Results

Results are saved to: `validation_results/validation_report_YYYYMMDD_HHMMSS.json`

```python
import json

# Load report
with open('validation_results/validation_report_20251101_120530.json') as f:
    report = json.load(f)

# View specific query result
for result in report['detailed_results']:
    if 'Brazil' in result['query']:
        print(f"Query: {result['query']}")
        print(f"Expected: {result['expected_category']}")
        print(f"Actual: {result['actual_category']}")
        print(f"Agents: {result['agents_called']}")
        print(f"Response: {result['response']['answer'][:200]}...")
        print()
```

### Check Backend Logs

```bash
# View real-time classification decisions
tail -f backend.log | grep -E "(Classification|Manager|Table|RAG|Combiner)"

# Search for specific query
grep "Brazil" backend.log
```

---

## 🧪 Testing Strategy

### Phase 1: Classification Validation ✅

**Goal**: Verify correct query classification

```bash
# Run quick test
python validate_hybridrag.py --mode quick

# Expected:
# - Table queries → classified as "Table"
# - Text queries → classified as "Text"  
# - Hybrid queries → classified as "Hybrid"
```

**Success Criteria**:
- Table classification accuracy: >90%
- Text classification accuracy: >95%
- Hybrid classification accuracy: >85%

### Phase 2: Pipeline Isolation Validation ✅

**Goal**: Ensure queries use ONLY appropriate pipelines

**Test Cases**:

1. **Table Query**: "How many matches in the World Cup ended in a draw?"
   - ✅ MUST call: TableAgent
   - ❌ MUST NOT call: RAGAgent
   - 🔍 Check: `agents_called` should only contain TableAgent

2. **Text Query**: "What is the historical significance of the FIFA World Cup?"
   - ✅ MUST call: RAGAgent
   - ❌ MUST NOT call: TableAgent
   - 🔍 Check: `agents_called` should only contain RAGAgent

3. **Hybrid Query**: "Which team won the 1950 World Cup Final and what was historically significant?"
   - ✅ MUST call: TableAgent, RAGAgent, CombinerAgent
   - 🔍 Check: `agents_called` should contain all three

**Success Criteria**:
- Pipeline isolation rate: >85% across all categories

### Phase 3: Answer Quality Validation ✅

**Goal**: Ensure answers are accurate and complete

**Manual Review** (sample 5 queries from each category):

1. Read query
2. Read response
3. Verify:
   - ✅ Directly answers the question
   - ✅ Uses correct data/context
   - ✅ Well-formatted and clear
   - ✅ No hallucinations

**Scoring**:
- 5: Perfect answer
- 4: Minor improvements possible
- 3: Acceptable but incomplete
- 2: Significant issues
- 1: Wrong or no answer

**Success Criteria**:
- Average quality score: >4.0 for all categories

### Phase 4: Conventional RAG Comparison 🔥

**Goal**: Demonstrate Hybrid RAG superiority

**Test Setup**:
1. Create simple text-only RAG baseline
2. Run same queries through both systems
3. Compare accuracy and quality

**Expected Results**:

| Query Type | Conventional RAG | Hybrid RAG | Improvement |
|------------|------------------|------------|-------------|
| Text       | 85-90%          | 85-90%     | ~0%         |
| Table      | 10-30%          | 90-100%    | **3-9x**    |
| Hybrid     | 30-50%          | 85-95%     | **1.7-3x**  |

---

## 🐛 Troubleshooting

### Issue: Classification Accuracy Low

**Symptoms**: Many queries misclassified

**Checks**:
1. Verify Manager Agent prompt in `src/backend/agents/manager_agent.py`
2. Check if examples in prompt are clear
3. Review Gemini API responses in logs

**Fix**:
```python
# Enhance Manager Agent classification prompt
# Add more examples
# Improve decision criteria
```

### Issue: Pipeline Isolation Failing

**Symptoms**: Table queries calling RAGAgent or vice versa

**Checks**:
1. Verify Orchestrator logic in `src/backend/services/orchestrator.py`
2. Check agent routing based on classification
3. Ensure agents are not cross-calling

**Fix**:
```python
# In orchestrator.py
if classification == "Table":
    # ONLY call table_agent
    result = await self.table_agent.process(query)
    # Do NOT call rag_agent
```

### Issue: Answer Quality Low

**Symptoms**: Answers are incomplete or wrong

**Checks**:
1. **For Table queries**: Check SQL query generation
   - View generated SQL in logs
   - Verify SQL is syntactically correct
   - Check if table schema is loaded correctly

2. **For Text queries**: Check RAG retrieval
   - Verify embeddings are stored
   - Check if relevant chunks are retrieved
   - Review prompt template

3. **For Hybrid queries**: Check combination logic
   - Verify both agents return results
   - Check Combiner Agent prompt
   - Ensure proper merging of data + context

### Issue: Response Times Too Slow

**Symptoms**: Queries take >10s

**Optimizations**:
1. Enable embedding caching
2. Use connection pooling for database
3. Reduce context window size
4. Use faster Gemini model (gemini-1.5-flash)
5. Implement parallel agent calls for Hybrid

---

## 📈 Performance Benchmarks

### Target Performance

| Metric                    | Target    | Acceptable | Poor    |
|---------------------------|-----------|------------|---------|
| Classification Accuracy   | >90%      | 80-90%     | <80%    |
| Pipeline Isolation        | >85%      | 75-85%     | <75%    |
| Table Query Accuracy      | >90%      | 80-90%     | <80%    |
| Text Query Accuracy       | >85%      | 75-85%     | <75%    |
| Hybrid Query Accuracy     | >85%      | 75-85%     | <75%    |
| Avg Response Time (Table) | <5s       | 5-10s      | >10s    |
| Avg Response Time (Text)  | <3s       | 3-5s       | >5s     |
| Avg Response Time (Hybrid)| <7s       | 7-12s      | >12s    |

---

## 📝 Reporting Results

### Generate Report

```bash
# Run validation
python validate_hybridrag.py --mode full

# Report is auto-generated in:
# - validation_results/validation_report_YYYYMMDD_HHMMSS.json
# - validation_results.log
```

### Create Summary Document

```markdown
# HybridRAG Validation Results - [Date]

## Executive Summary
- Total Queries Tested: 45
- Overall Classification Accuracy: 93.3%
- Pipeline Isolation Rate: 88.9%
- Average Answer Quality: 4.2/5

## Category Performance

### Table Queries (15)
- Classification: 93.3% ✅
- Isolation: 86.7% ✅
- Quality: 4.2/5 ✅
- Notable: All SQL queries executed successfully

### Text Queries (15)
- Classification: 100% ✅
- Isolation: 100% ✅
- Quality: 4.5/5 ✅
- Notable: High-quality narrative responses

### Hybrid Queries (15)
- Classification: 86.7% ⚠️
- Isolation: 80.0% ⚠️
- Quality: 4.0/5 ✅
- Notable: Some queries need better combination logic

## Comparison with Conventional RAG

| Metric              | Conv RAG | Hybrid RAG | Improvement |
|---------------------|----------|------------|-------------|
| Table Accuracy      | 25%      | 93%        | **3.7x**    |
| Text Accuracy       | 87%      | 88%        | 1.01x       |
| Hybrid Accuracy     | 42%      | 86%        | **2.0x**    |

## Conclusion
✅ HybridRAG successfully demonstrates superior performance on structured data
✅ Maintains text RAG quality while adding table capabilities
✅ Intelligent combination of multiple data sources
```

---

## 🎓 Best Practices

### 1. Test Incrementally
- Start with quick mode (5 queries)
- Fix issues
- Run full validation (45 queries)

### 2. Monitor Logs
- Watch backend logs during testing
- Look for errors or warnings
- Check SQL queries for correctness

### 3. Validate Manually
- Don't rely solely on automated scoring
- Manually review sample responses
- Check edge cases

### 4. Document Issues
- Record misclassifications
- Note pipeline isolation failures
- Document incorrect answers with reasons

### 5. Iterate and Improve
- Refine Manager Agent prompt
- Improve agent response templates
- Enhance combination logic

---

## 📚 Next Steps

After validation:

1. **If results are good (>90% accuracy)**:
   - Document findings
   - Create demo queries
   - Prepare presentation

2. **If results need improvement (80-90%)**:
   - Identify weak areas
   - Refine prompts
   - Re-run validation

3. **If results are poor (<80%)**:
   - Review architecture
   - Debug agent logic
   - Check data quality
   - Verify API connectivity

---

## 🤝 Support

For issues or questions:
1. Check logs: `backend.log` and `validation_results.log`
2. Review agent code in `src/backend/agents/`
3. Verify PDF upload and table extraction
4. Test API endpoints individually

Good luck with your validation! 🚀

