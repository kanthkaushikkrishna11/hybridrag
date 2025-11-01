# 🧪 Hybrid RAG Testing Guide

**Purpose**: Validate that Hybrid RAG achieves ≥50% better performance than Conventional RAG for table and hybrid queries.

---

## 🎯 **OBJECTIVE**

Test these query types in the **Comparison Tab** of the frontend:

| Query Type | Expected Result |
|------------|-----------------|
| **Table Queries** | Hybrid RAG ≥50% better (precise SQL vs text guessing) |
| **Hybrid Queries** | Hybrid RAG ≥50% better (data + context vs text only) |
| **Text Queries** | Both similar (±1-2% difference) |

---

## 📋 **TEST QUERIES FOR FRONTEND**

Copy these queries **exactly as written** and paste into the Comparison Tab.

### **Category 1: Simple Table Queries** (Hybrid RAG should be MUCH better)

#### Test 1: Team Winners
```
What are the names of teams that won Final matches?
```
**Expected**:
- ✅ Conventional RAG: May list some teams, possibly incomplete
- ✅ Hybrid RAG: Complete, accurate list with NO duplicates (Uruguay, Italy, West Germany, Brazil, England)
- 🎯 **Target**: Hybrid RAG has complete data, Conventional is partial

#### Test 2: Draw Count
```
How many matches in the World Cup ended in a draw?
```
**Expected**:
- ✅ Conventional RAG: Might guess or say "several" (cannot count accurately)
- ✅ Hybrid RAG: Exact number from SQL query
- 🎯 **Target**: Hybrid RAG gives precise count, Conventional guesses

#### Test 3: Total Matches
```
What is the count of the number of rows in the data?
```
**Expected**:
- ✅ Conventional RAG: Cannot count documents accurately
- ✅ Hybrid RAG: Exact count (~100 matches)
- 🎯 **Target**: Hybrid RAG 100% accurate, Conventional fails

---

### **Category 2: Intermediate Table Queries** (Hybrid RAG should excel)

#### Test 4: Brazil Goals
```
How many goals did Brazil score in total (home + away)?
```
**Expected**:
- ✅ Conventional RAG: Cannot aggregate across multiple chunks
- ✅ Hybrid RAG: Precise total from SQL aggregation
- 🎯 **Target**: Hybrid RAG accurate calculation, Conventional cannot compute

#### Test 5: Semi-finals
```
List all Semi-final matches with scores
```
**Expected**:
- ✅ Conventional RAG: May list a few semi-finals from retrieved chunks
- ✅ Hybrid RAG: ALL semi-final matches with complete scores
- 🎯 **Target**: Hybrid RAG has complete list, Conventional partial

#### Test 6: Matches Per Year
```
How many matches were played in each World Cup year?
```
**Expected**:
- ✅ Conventional RAG: Cannot group and count by year
- ✅ Hybrid RAG: Complete breakdown by year
- 🎯 **Target**: Hybrid RAG structured data, Conventional fails

---

### **Category 3: Advanced Table Queries** (Hybrid RAG should dominate)

#### Test 7: Championship Counts
```
Which teams have won a World Cup Final with their championship counts?
```
**Expected**:
- ✅ Conventional RAG: May list teams but not accurate counts
- ✅ Hybrid RAG: Teams with exact win counts
- 🎯 **Target**: Hybrid RAG precise aggregation, Conventional guesses

#### Test 8: High-Scoring Matches
```
Find all matches where the home team scored more than 5 goals
```
**Expected**:
- ✅ Conventional RAG: May miss some matches
- ✅ Hybrid RAG: Complete filtered list
- 🎯 **Target**: Hybrid RAG complete data, Conventional incomplete

#### Test 9: Draw Percentage
```
What percentage of matches were draws?
```
**Expected**:
- ✅ Conventional RAG: Cannot calculate percentages
- ✅ Hybrid RAG: Exact percentage calculation
- 🎯 **Target**: Hybrid RAG calculation capability, Conventional fails

---

### **Category 4: Text Queries** (Both should be similar)

#### Test 10: Historical Significance
```
What is the historical significance of the FIFA World Cup and when did it start?
```
**Expected**:
- ✅ Both should retrieve similar context about 1930 start, Jules Rimet, global significance
- 🎯 **Target**: Quality difference ±1-2%

#### Test 11: Jules Rimet
```
Who was Jules Rimet and what was his role?
```
**Expected**:
- ✅ Both should identify him as third FIFA President, driving force
- 🎯 **Target**: Both similar quality

#### Test 12: World War II
```
Why was the World Cup not held in 1942 and 1946?
```
**Expected**:
- ✅ Both should retrieve World War II hiatus information
- 🎯 **Target**: Both similar quality

---

### **Category 5: Hybrid Queries** (Hybrid RAG should be MUCH better)

#### Test 13: 1950 World Cup (CRITICAL TEST)
```
Which team won the 1950 World Cup Final and what was historically significant about that tournament?
```
**Expected**:
- ✅ Conventional RAG: May have context OR data, but not both well
- ✅ Hybrid RAG: Uruguay won (precise data) + Maracanazo significance (context)
- 🎯 **Target**: Hybrid RAG comprehensive, Conventional incomplete

#### Test 14: Uruguay's Journey (COMPREHENSIVE TEST)
```
Provide a comprehensive overview of Uruguays World Cup journey including their match statistics and historical achievements
```
**Expected**:
- ✅ Conventional RAG: Limited stats, some context, incomplete matches
- ✅ Hybrid RAG: 
  - ALL 11 matches with scores
  - Accurate statistics (9 wins, 1 draw, 1 loss, 28-12 goals)
  - Historical context (1930 first champions, 1950 Maracanazo)
- 🎯 **Target**: Hybrid RAG complete, Conventional partial (50%+ improvement)

#### Test 15: Brazil's Style & Stats
```
Provide Brazils match statistics and explain their footballing style
```
**Expected**:
- ✅ Conventional RAG: Good on style (Joga Bonito) but weak on stats
- ✅ Hybrid RAG: Precise match stats + Joga Bonito description
- 🎯 **Target**: Hybrid RAG combines both perfectly

---

## ✅ **VALIDATION CHECKLIST**

After testing each query, check:

### **For Table Queries:**
- [ ] Hybrid RAG provides exact numbers/complete lists
- [ ] Conventional RAG guesses or provides partial data
- [ ] No duplicate values in Hybrid RAG lists
- [ ] Route shows: `table` (verify in browser console)

### **For Text Queries:**
- [ ] Both systems provide similar quality context
- [ ] Both retrieve relevant historical information
- [ ] Route shows: `rag` (verify in browser console)

### **For Hybrid Queries:**
- [ ] Hybrid RAG combines precise data + rich context
- [ ] Conventional RAG missing either data OR context
- [ ] Hybrid RAG answer is comprehensive (all matches shown)
- [ ] Route shows: `both` (verify in browser console)

### **Quality Checks:**
- [ ] No "database error" messages
- [ ] No duplicate entries in lists
- [ ] Natural formatting (not raw SQL output)
- [ ] Processing time < 30s for complex queries

---

## 🎯 **SUCCESS CRITERIA**

### **After Testing All 15 Queries:**

| Category | Success Metric |
|----------|---------------|
| **Table Queries (9 queries)** | Hybrid RAG clearly superior in 8-9 queries (≥89% win rate = >50% better) |
| **Text Queries (3 queries)** | Both systems similar quality (±1-2 difference) |
| **Hybrid Queries (3 queries)** | Hybrid RAG clearly superior in all 3 (100% win rate = >50% better) |

---

## 📊 **HOW TO TEST IN FRONTEND**

1. **Start Frontend** (if not running):
   ```bash
   cd /Users/krishnakaushik/hybridrag/HybridRAG/frontend-new
   npm run dev
   ```

2. **Open Browser**: http://localhost:5173

3. **Go to Comparison Tab** (top navigation)

4. **Upload FIFA World Cup PDF** (if not already uploaded):
   - File: `/Users/krishnakaushik/hybridrag/HybridRAG/resources/The FIFA World Cup_ A Historical Journey-1.pdf`

5. **Test Each Query**:
   - Copy query from this guide
   - Paste into comparison input field
   - Click "Compare RAG Approaches"
   - Observe both results side-by-side

6. **Look For**:
   - **Left** (Conventional RAG): Text-based retrieval only
   - **Right** (Hybrid RAG): Smart routing with precise data
   - **Route Classification**: Check browser console for query_type

---

## 🐛 **TROUBLESHOOTING**

### Issue: "Database error while processing query"
**Fix**: Check backend logs:
```bash
tail -50 /Users/krishnakaushik/hybridrag/HybridRAG/backend.log
```

### Issue: Route shows "unknown"
**Fix**: Backend restart needed:
```bash
cd /Users/krishnakaushik/hybridrag/HybridRAG
lsof -ti:8000 | xargs kill -9
source venv/bin/activate
uvicorn app:app --reload --port 8000
```

### Issue: Duplicates still appearing
**Fix**: Check that fixes were applied:
```bash
grep -n "seen = set()" /Users/krishnakaushik/hybridrag/HybridRAG/src/backend/agents/table_agent.py
```
Should show line 293

### Issue: Slow response times
**Expected**: Hybrid RAG is 2-3x slower for comprehensive queries (acceptable trade-off for accuracy)

---

## 📈 **RESULTS TRACKING**

Create a simple table as you test:

| Query | Conventional Quality | Hybrid Quality | Winner | Improvement |
|-------|---------------------|----------------|---------|-------------|
| Test 1 (Finals) | Partial | Complete | Hybrid | 60% |
| Test 2 (Draws) | Guess | Exact | Hybrid | 80% |
| ... | ... | ... | ... | ... |

**Average improvements by category** is the key metric!

---

## 🚀 **QUICK START**

**Just want to see the most important tests? Start here:**

1. **Test 1**: "What are the names of teams that won Final matches?" (Table query - should show no duplicates)

2. **Test 14**: "Provide a comprehensive overview of Uruguays World Cup journey including their match statistics and historical achievements" (Hybrid query - should show all 11 matches)

3. **Test 10**: "What is the historical significance of the FIFA World Cup and when did it start?" (Text query - both should be similar)

These 3 tests validate the core objective!

---

## 📁 **REFERENCE DOCUMENTS**

- **Ground Truth**: `docs/GROUND_TRUTH_ANALYSIS.md` - What the correct answers should be
- **System Details**: `docs/COMPLETE_SYSTEM_OPTIMIZATION_SUMMARY.md` - All improvements made
- **Full Validation**: `docs/SYSTEMATIC_VALIDATION_PLAN.md` - Complete 25-query plan
- **Architecture**: `docs/ARCHITECTURE.md` - How the system works

---

**Ready to test! 🎯 Start with Test 1, Test 14, and Test 10 for quick validation!**

