# Quick Fix: Resolving Gemini API Quota Issues

## Current Problem
Your Gemini API free tier has exceeded its daily limit of 50 requests. This is causing all queries to fail.

## Immediate Solutions (Choose One)

### Option 1: Wait for Quota Reset ⏰
**Simplest but slowest**
- Wait ~24 hours for the free tier quota to reset
- No code changes needed
- Good for: Testing and development

### Option 2: Switch to Gemini 1.5 Flash (Recommended) ⚡
**Faster model with higher limits**

The system is currently using `gemini-2.5-pro` which has stricter limits. Switch to `gemini-1.5-flash` which has:
- Higher rate limits (1500 requests/day)
- Faster responses
- Still excellent quality

**Files to modify** (5 locations):

1. **src/backend/agents/manager_agent.py** (line 42)
   ```python
   # Change from:
   model="gemini-2.5-pro",
   # To:
   model="gemini-1.5-flash",
   ```

2. **src/backend/agents/combiner_agent.py** (line 23)
   ```python
   # Change from:
   model="gemini-2.5-pro",
   # To:
   model="gemini-1.5-flash",
   ```

3. **src/backend/agents/rag_agent.py** (line 81)
   ```python
   # Change from:
   self.llm = genai.GenerativeModel("gemini-2.5-pro")
   # To:
   self.llm = genai.GenerativeModel("gemini-1.5-flash")
   ```

4. **src/backend/agents/table_agent.py** (line 28)
   ```python
   # Change from:
   model="gemini-2.5-pro",
   # To:
   model="gemini-1.5-flash",
   ```

5. **src/backend/utils/pdf_processor.py** (line 76)
   ```python
   # Change from:
   self.model = genai.GenerativeModel('gemini-2.5-pro')
   # To:
   self.model = genai.GenerativeModel('gemini-1.5-flash')
   ```

**After making changes:**
```bash
# Restart the backend
cd /Users/krishnakaushik/hybridrag/HybridRAG
# Kill the current backend (Ctrl+C or find process)
# Then restart
python app.py
```

### Option 3: Use a Different API Key 🔑
**If you have multiple Google accounts**
1. Go to https://aistudio.google.com/apikey
2. Create a new API key from a different Google account
3. Update your `.env` file:
   ```bash
   GEMINI_API_KEY=your_new_api_key_here
   ```
4. Restart the backend

### Option 4: Upgrade to Paid Tier 💳
**For production use**
1. Go to https://ai.google.dev/pricing
2. Set up billing on your Google Cloud project
3. Paid tier gets much higher limits:
   - Up to 360 requests/minute
   - No daily cap
   - Better support

---

## Quick Model Comparison

| Model | Free Tier Limit | Speed | Quality | Best For |
|-------|----------------|-------|---------|----------|
| gemini-1.5-flash | 1500/day | ⚡⚡⚡ Fast | ⭐⭐⭐ Good | Development, most queries |
| gemini-2.5-flash | 1500/day | ⚡⚡⚡ Fast | ⭐⭐⭐⭐ Better | Balanced performance |
| gemini-2.5-pro | 50/day | ⚡⚡ Medium | ⭐⭐⭐⭐⭐ Best | Complex reasoning, low volume |

**Recommendation**: Use `gemini-1.5-flash` for development and testing. It's 30x more quota and still excellent quality!

---

## Automated Fix Script

I can create a script to automatically switch all models to `gemini-1.5-flash`. Would you like me to do that?

---

## Verification

After applying the fix, verify it worked:

```bash
curl -s http://localhost:8010/health | python3 -m json.tool
```

Look for:
- `"overall_health": true` (instead of false)
- `"manager_agent": true` (instead of false)
- No error messages about quota

---

## Still Having Issues?

If you're still seeing errors after trying these solutions:

1. **Check your API key is valid**:
   ```bash
   echo $GEMINI_API_KEY
   ```

2. **Check backend logs** for specific error messages

3. **Try a simple test query**:
   ```bash
   curl -X POST http://localhost:8010/answer \
     -H "Content-Type: application/json" \
     -d '{"query": "test", "pdf_uuid": "test123"}'
   ```

4. **Contact me** with the error message and I'll help debug further!

