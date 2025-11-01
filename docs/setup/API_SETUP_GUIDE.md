# 🔐 API Keys Setup Guide - Hybrid RAG Project

This guide will walk you through getting all required API keys for the Hybrid RAG system.

---

## ⭐ **Step 1: Google Gemini API Key** (FREE - 5 minutes)

### **What is Gemini?**
Google's AI model used for:
- Understanding queries
- Generating SQL from natural language
- Inferring table schemas from PDFs
- Combining responses intelligently

### **Free Tier:**
- ✅ 60 requests per minute
- ✅ No credit card required
- ✅ Unlimited usage for testing

### **Setup Instructions:**

**A. Visit Google AI Studio:**
```
https://makersuite.google.com/app/apikey
```

**B. Sign in with your Google Account**
- Use any Gmail account (personal or work)

**C. Create API Key:**
1. Click the **"Create API Key"** button (blue button)
2. Select **"Create API key in new project"** (or use existing project)
3. Your key will be generated instantly

**D. Copy Your Key:**
```
Example: AIzaSyCXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**E. Test Your Key (Optional):**
```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Say hello"}]}]}'
```

If you see a response, your key works! ✅

**⚠️ Security Note:**
- Never commit this key to GitHub
- Keep it in `.env` file only

---

## 📌 **Step 2: Pinecone Vector Database** (FREE - 10 minutes)

### **What is Pinecone?**
Vector database used for:
- Storing text embeddings (768-dimensional vectors)
- Semantic search (finding similar content)
- Fast similarity queries

### **Free Tier:**
- ✅ 1 free index
- ✅ 100K vectors
- ✅ Up to 5 queries per second
- ✅ Perfect for testing and demos

### **Setup Instructions:**

**A. Sign Up:**
```
https://www.pinecone.io/
```
- Click **"Start Free"**
- Sign up with email or GitHub

**B. Create Your First Index:**

1. **After login, click "Create Index"**

2. **Configure Index:**
   ```
   Index Name:     hybridrag-index
   Dimensions:     768
   Metric:         cosine
   Pod Type:       Starter (free)
   Environment:    gcp-starter
   ```

3. **Why these settings?**
   - **768 dimensions**: Matches Google Gemini's `embedding-001` model
   - **cosine metric**: Best for text similarity
   - **Starter pod**: Free tier option

4. **Click "Create Index"**
   - Takes ~30 seconds to provision

**C. Get Your API Key:**

1. Go to **"API Keys"** in left sidebar
2. Copy your default API key
3. Or click **"Create API Key"** for a new one

```
Example: pcsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**D. Note Your Environment:**
```
Usually: gcp-starter (or aws-starter, azure-starter)
```

**E. Test Connection (Optional):**
```python
from pinecone import Pinecone

pc = Pinecone(api_key="YOUR_API_KEY")
print(pc.list_indexes())
# Should show: ['hybridrag-index']
```

---

## 🗄️ **Step 3: Supabase PostgreSQL Database** (FREE - 10 minutes)

### **What is Supabase?**
PostgreSQL database used for:
- Storing extracted table data from PDFs
- Running SQL queries for structured data
- Schema management

### **Free Tier:**
- ✅ 500MB database storage
- ✅ 2GB bandwidth
- ✅ Unlimited API requests
- ✅ Perfect for development

### **Setup Instructions:**

**A. Sign Up:**
```
https://supabase.com/
```
- Click **"Start your project"**
- Sign up with GitHub (recommended) or email

**B. Create New Project:**

1. Click **"New Project"**

2. **Fill in details:**
   ```
   Name:           HybridRAG
   Database Password: [Choose a strong password - SAVE IT!]
   Region:         Choose closest to you (e.g., US East, EU West)
   Pricing Plan:   Free
   ```

3. Click **"Create new project"**
   - Takes ~2 minutes to provision

**C. Get Connection Details:**

1. Go to **Settings** (gear icon) → **Database**

2. Scroll to **"Connection string"** section

3. Select **"URI"** tab

4. You'll see something like:
   ```
   postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
   ```

5. **Extract these values:**
   ```
   DATABASE_HOST:     aws-0-us-east-1.pooler.supabase.com
   DATABASE_PORT:     5432
   DATABASE_NAME:     postgres
   DATABASE_USER:     postgres.[PROJECT-REF]
   DATABASE_PASSWORD: [Your chosen password]
   ```

**D. Alternative - Connection Pooler (Recommended):**

1. In **Database Settings**, find **"Connection Pooler"** section

2. Use **Transaction Mode** settings:
   ```
   Host:     aws-0-us-east-1.pooler.supabase.com
   Port:     6543  (Note: Different port for pooler!)
   Database: postgres
   User:     postgres.[PROJECT-REF]
   Password: [Same password]
   ```

**E. Test Connection (Optional):**

**Using psql:**
```bash
psql "postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
```

**Using Python:**
```python
import psycopg2

conn = psycopg2.connect(
    host="aws-0-us-east-1.pooler.supabase.com",
    port=6543,
    database="postgres",
    user="postgres.[PROJECT-REF]",
    password="YOUR_PASSWORD"
)
print("✅ Connected!")
conn.close()
```

---

## ✅ **Step 4: Create .env File**

Once you have all three sets of credentials, create a `.env` file in your project root:

```bash
cd /Users/krishnakaushik/hybridrag/HybridRAG
nano .env
```

**Paste this template and fill in YOUR actual values:**

```bash
# =============================================================================
# GOOGLE GEMINI AI
# =============================================================================
GEMINI_API_KEY=AIzaSyCXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# =============================================================================
# PINECONE VECTOR DATABASE
# =============================================================================
PINECONE_API_KEY=pcsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
PINECONE_INDEX=hybridrag-index
PINECONE_CLOUD=gcp-starter
PINECONE_REGION=us-east-1

# =============================================================================
# SUPABASE POSTGRESQL DATABASE
# =============================================================================
DATABASE_HOST=aws-0-us-east-1.pooler.supabase.com
DATABASE_PORT=6543
DATABASE_NAME=postgres
DATABASE_USER=postgres.xxxxxxxxxxxxxxxxxxx
DATABASE_PASSWORD=your_strong_password_here

# =============================================================================
# FASTAPI SERVER
# =============================================================================
PORT=8010
HOST=0.0.0.0
DEBUG=True

# =============================================================================
# STREAMLIT FRONTEND
# =============================================================================
ENDPOINT=http://localhost:8010

# =============================================================================
# LOGGING
# =============================================================================
LOG_LEVEL=INFO
```

**Save and exit:**
- Press `Ctrl+X`
- Press `Y` to confirm
- Press `Enter` to save

---

## 🧪 **Step 5: Verify Configuration**

Run this verification script:

```bash
cd /Users/krishnakaushik/hybridrag/HybridRAG
source venv/bin/activate
python << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

print("\n🔍 Checking Environment Variables...\n")

required_vars = [
    "GEMINI_API_KEY",
    "PINECONE_API_KEY",
    "PINECONE_INDEX",
    "DATABASE_HOST",
    "DATABASE_PASSWORD",
    "DATABASE_USER",
    "ENDPOINT"
]

for var in required_vars:
    value = os.getenv(var)
    if value and value not in ["Your_api_key", "your_index_name", "password_here"]:
        print(f"✅ {var}: Set ({value[:10]}...)")
    else:
        print(f"❌ {var}: Not set or using placeholder")

print("\n" + "="*50)
print("Configuration check complete!")
print("="*50 + "\n")
EOF
```

---

## 🚀 **Step 6: Start Your Application**

**Terminal 1 - Backend:**
```bash
cd /Users/krishnakaushik/hybridrag/HybridRAG
source venv/bin/activate
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd /Users/krishnakaushik/hybridrag/HybridRAG
source venv/bin/activate
streamlit run src/frontend/streamlit_app.py
```

**Access the app:**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8010
- Health Check: http://localhost:8010/health

---

## 🆘 **Troubleshooting**

### **Issue: Gemini API 429 Error**
**Solution:** Free tier has rate limits (60 requests/min). Wait a minute between tests.

### **Issue: Pinecone Index Not Found**
**Solution:** 
1. Check index name matches exactly
2. Wait 30 seconds after creation
3. Verify it appears in dashboard

### **Issue: Database Connection Failed**
**Solution:**
1. Check password is correct
2. Use connection pooler port (6543, not 5432)
3. Verify IP whitelist in Supabase settings (should allow all for development)

### **Issue: .env Not Loading**
**Solution:**
```bash
# Verify .env exists
ls -la .env

# Check format (no spaces around =)
cat .env | grep "="

# Restart servers after .env changes
```

---

## 📊 **Quick Reference Card**

| Service | What It Does | Cost | Limit |
|---------|-------------|------|-------|
| **Gemini** | AI/LLM | FREE | 60 req/min |
| **Pinecone** | Vectors | FREE | 100K vectors |
| **Supabase** | Database | FREE | 500MB storage |

---

## ✅ **Checklist**

- [ ] Google Gemini API key obtained
- [ ] Pinecone index created (dimension=768)
- [ ] Pinecone API key copied
- [ ] Supabase project created
- [ ] Database connection details saved
- [ ] `.env` file created with all keys
- [ ] Configuration verified
- [ ] Backend starts without errors
- [ ] Frontend loads successfully
- [ ] Health check returns "healthy"

---

## 🎓 **Next Steps**

Once all services are configured:

1. **Upload a PDF** - Try the FIFA World Cup PDF
2. **Test text queries** - "What was the host of first World Cup?"
3. **Test table queries** - "How many times did Brazil win?"
4. **Test hybrid queries** - Combine both types

---

## 📞 **Need Help?**

If you get stuck:
1. Check the logs: `tail -f logs/app.log`
2. Verify .env file: `cat .env`
3. Test each service individually
4. Review error messages carefully

---

**Good luck! 🚀**

Once you complete these steps, come back and I'll help you start the servers and test everything!


