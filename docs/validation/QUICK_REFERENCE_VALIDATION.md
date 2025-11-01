# 🚀 HybridRAG Validation Quick Reference

## One-Command Quick Start

```bash
# Test everything (recommended first run)
python validate_hybridrag.py --mode quick && python compare_rag_systems.py --queries sample
```

---

## Essential Commands

### Validation Scripts

```bash
# Quick validation (15 queries - 5 per category)
python validate_hybridrag.py --mode quick

# Full validation (45 queries - 15 per category)
python validate_hybridrag.py --mode full

# Test specific category only
python validate_hybridrag.py --mode category --category table
python validate_hybridrag.py --mode category --category text
python validate_hybridrag.py --mode category --category hybrid
```

### Comparison Scripts

```bash
# Quick comparison (15 queries)
python compare_rag_systems.py --queries sample

# Full comparison (all queries)
python compare_rag_systems.py --queries full
```

### Manual Testing

```bash
# Test single query via API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Your query here"}'

# Check API health
curl http://localhost:8000/health

# View real-time logs
tail -f backend.log | grep -E "(Classification|Manager)"
```

---

## Sample Test Queries

### Table Query (Copy-Paste Ready)
```
How many matches in the World Cup ended in a draw?
```

### Text Query (Copy-Paste Ready)
```
What is the historical significance of the FIFA World Cup?
```

### Hybrid Query (Copy-Paste Ready)
```
Which team won the 1950 World Cup Final and what was historically significant about that tournament?
```

---

## Expected Results Cheatsheet

### ✅ Good Results
- Classification Accuracy: **>90%**
- Pipeline Isolation: **>85%**
- Answer Quality: **>4.0/5**
- Table vs Conv: **>100% improvement**
- Hybrid vs Conv: **>50% improvement**

### ⚠️ Needs Improvement
- Classification: 80-90%
- Isolation: 75-85%
- Quality: 3.0-4.0/5
- Check logs for errors

### ❌ Troubleshoot
- Classification: <80%
- Isolation: <75%
- Quality: <3.0/5
- Review agent prompts

---

## Quick Diagnosis

### Is backend running?
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### Is PDF uploaded?
```bash
cat src/backend/utils/table_schema.json | grep world_cup
# Expected: Should show table schema
```

### Are there errors?
```bash
tail -20 backend.log
# Check for recent errors
```

---

## Common Issues & Fixes

### Backend not responding
```bash
# Terminal 1: Start backend
cd /Users/krishnakaushik/hybridrag/HybridRAG
source venv/bin/activate
uvicorn app:app --reload --port 8000
```

### Dependencies missing
```bash
pip install requests tabulate
```

### PDF not uploaded
```bash
# Upload via frontend at http://localhost:5173
# Or check if file exists: The FIFA World Cup_ A Historical Journey-1.pdf
```

---

## Results Location

After running tests:

- **Validation Results**: `validation_results/validation_report_*.json`
- **Comparison Results**: `comparison_results/comparison_report_*.json`
- **Logs**: `validation_results.log`, `comparison_results.log`
- **Backend Logs**: `backend.log`

---

## Quick Analysis

### View validation summary
```bash
# After running validation
python -c "
import json
with open('validation_results/$(ls -t validation_results/*.json | head -1)', 'r') as f:
    r = json.load(f)
    print(f\"Classification: {sum(d['classification_correct'] for d in r['detailed_results'])/len(r['detailed_results'])*100:.1f}%\")
"
```

### Check latest results
```bash
# View most recent report
ls -lt validation_results/*.json | head -1
ls -lt comparison_results/*.json | head -1
```

---

## Testing Workflow

```
┌─────────────────────────────────────────────┐
│  1. START BACKEND                           │
│     uvicorn app:app --reload --port 8000    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  2. VERIFY PDF UPLOADED                     │
│     Check table_schema.json                 │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  3. RUN QUICK VALIDATION                    │
│     python validate_hybridrag.py --mode quick│
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  4. RUN COMPARISON                          │
│     python compare_rag_systems.py --queries sample│
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  5. REVIEW RESULTS                          │
│     Check summary tables and logs           │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  6. MANUAL VERIFICATION (optional)          │
│     Test 3-5 queries via frontend           │
└─────────────────────────────────────────────┘
```

---

## Performance Targets Quick Reference

| Query Type | Classification | Isolation | Quality | Improvement |
|-----------|----------------|-----------|---------|-------------|
| **Table**  | >90%          | >85%      | >4.0/5  | >100%       |
| **Text**   | >95%          | >90%      | >4.0/5  | ±10%        |
| **Hybrid** | >85%          | >80%      | >3.8/5  | >50%        |

---

## Key Files Reference

```
HybridRAG/
├── VALIDATION_QUERIES.md          ← All 45 test queries
├── VALIDATION_TESTING_GUIDE.md    ← Detailed methodology
├── README_VALIDATION.md           ← Comprehensive guide
├── QUICK_REFERENCE_VALIDATION.md  ← This file
├── validate_hybridrag.py          ← Validation script
├── compare_rag_systems.py         ← Comparison script
├── validation_results/            ← Generated reports
├── comparison_results/            ← Generated comparisons
└── backend.log                    ← System logs
```

---

## Emergency Troubleshooting

### Nothing works?
```bash
# 1. Check Python environment
source venv/bin/activate
which python

# 2. Check dependencies
pip list | grep -E "(requests|tabulate|fastapi|uvicorn)"

# 3. Restart backend
pkill -f uvicorn
sleep 2
uvicorn app:app --reload --port 8000 &

# 4. Wait 5 seconds
sleep 5

# 5. Test health
curl http://localhost:8000/health

# 6. Try again
python validate_hybridrag.py --mode quick
```

---

## Success Indicators

When you see this, you're good! ✅

```
+----------+----------+-----------------+--------------+-----------+
| Category | Queries  | Classification  | Isolation    | Quality   |
+==========+==========+=================+==============+===========+
| Table    |       15 | 93.3%          | 86.7%        | 4.2/5     |
| Text     |       15 | 100.0%         | 100.0%       | 4.5/5     |
| Hybrid   |       15 | 86.7%          | 80.0%        | 4.0/5     |
+----------+----------+-----------------+--------------+-----------+

🎯 KEY FINDINGS:
   ✅ Table Queries: HybridRAG SIGNIFICANTLY OUTPERFORMS (>140% better)
   ✅ Text Queries: COMPARABLE performance (+4.5% diff)
   ✅ Hybrid Queries: HybridRAG EXCELS (+66.7% better)
```

---

## Support Checklist

Before asking for help:
- [ ] Backend is running (`curl http://localhost:8000/health`)
- [ ] PDF is uploaded and processed
- [ ] Dependencies are installed (`pip list`)
- [ ] Checked logs for errors (`tail backend.log`)
- [ ] Tried restarting backend

---

**Last Updated**: 2025-11-01  
**Version**: 1.0  
**Status**: Production Ready

---

## 💡 Pro Tips

1. **Start Small**: Always run `--mode quick` first before full tests
2. **Monitor Logs**: Keep `tail -f backend.log` running during tests
3. **Save Results**: Results are timestamped - you can compare multiple runs
4. **Manual Verify**: Always manually check 2-3 sample responses
5. **Document Issues**: Note any misclassifications for prompt tuning

---

**Need more detail?** See `VALIDATION_TESTING_GUIDE.md`  
**Need query list?** See `VALIDATION_QUERIES.md`  
**Need full guide?** See `README_VALIDATION.md`

