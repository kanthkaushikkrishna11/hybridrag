# 🚀 HYBRID RAG - LOCAL SETUP GUIDE

## 📋 PREREQUISITES

### **Required Accounts & API Keys**

1. **Google Gemini AI**
   - Sign up: https://makersuite.google.com/
   - Get API key: https://makersuite.google.com/app/apikey
   - Free tier: 60 requests/minute

2. **Pinecone (Vector Database)**
   - Sign up: https://www.pinecone.io/
   - Free tier: 1 index, 100K vectors
   - Create index with dimension=768

3. **Supabase (PostgreSQL)**
   - Sign up: https://supabase.com/
   - Free tier: 500MB database, 2GB bandwidth
   - Get connection details from Settings > Database

### **System Requirements**

- **Python:** 3.9+ (preferably 3.10 or 3.11)
- **OS:** macOS, Linux, or Windows
- **RAM:** Minimum 4GB (8GB recommended)
- **Disk Space:** 500MB for dependencies

---

## 🛠️ STEP-BY-STEP SETUP

### **Step 1: Clone and Navigate to Project**

```bash
cd /Users/krishnakaushik/hybridrag/HybridRAG
```

---

### **Step 2: Create Virtual Environment**

**Option A: Using make (recommended)**
```bash
make venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows
```

**Option B: Manual**
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

**Verify activation:**
```bash
which python  # Should point to venv/bin/python
python --version  # Should be 3.9+
```

---

### **Step 3: Install Dependencies**

```bash
make install
```

This installs:
- FastAPI, Uvicorn (backend)
- Streamlit (frontend)
- Google Generative AI, Pinecone, LangChain (AI)
- SQLAlchemy, psycopg2 (database)
- PDFPlumber (PDF processing)
- Pytest, Black, Flake8 (dev tools)

**Verify installation:**
```bash
pip list | grep fastapi
pip list | grep streamlit
pip list | grep google-generativeai
```

---

### **Step 4: Configure Environment Variables**

**A. Copy template:**
```bash
cp .env.example .env
```

**B. Edit `.env` file:**
```bash
nano .env  # or use your preferred editor
```

**C. Fill in your credentials:**

```bash
# ===== GOOGLE GEMINI AI =====
GEMINI_API_KEY=AIzaSyCxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_MODEL=gemini-1.5-pro-latest

# ===== PINECONE =====
PINECONE_API_KEY=pcsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PINECONE_INDEX_NAME=hybridrag-index
PINECONE_ENVIRONMENT=gcp-starter

# ===== SUPABASE (POSTGRESQL) =====
DATABASE_HOST=db.xxxxxxxxxxxxxxxxxxxx.supabase.co
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password_here
DATABASE_NAME=postgres

# ===== FASTAPI SERVER =====
HOST=0.0.0.0
PORT=8000
DEBUG=True

# ===== STREAMLIT FRONTEND =====
ENDPOINT=http://localhost:8000
```

**D. Verify configuration:**
```bash
python -c "from src.backend.config import Config; c = Config(); print('✅ Config loaded successfully')"
```

---

### **Step 5: Set Up External Services**

#### **A. Pinecone Index Setup**

1. **Log in to Pinecone:** https://app.pinecone.io/
2. **Create new index:**
   - Name: `hybridrag-index`
   - Dimensions: `768` (for Gemini embeddings)
   - Metric: `cosine`
   - Pod Type: Starter (free tier)

3. **Get API key:**
   - Go to API Keys section
   - Copy your API key
   - Add to `.env` as `PINECONE_API_KEY`

#### **B. Supabase Database Setup**

1. **Log in to Supabase:** https://supabase.com/dashboard
2. **Create new project:**
   - Choose region closest to you
   - Set database password (save it!)
   - Wait for provisioning (~2 minutes)

3. **Get connection details:**
   - Go to Settings > Database
   - Scroll to "Connection string"
   - Copy these values to `.env`:
     - Host: `db.xxxxxxxxxxxxxxxxxxxx.supabase.co`
     - Password: Your database password
     - Port: `5432`
     - Database: `postgres`
     - User: `postgres`

4. **Test connection:**
```bash
psql "postgresql://postgres:your_password@db.xxxxxxxxxxxxxxxxxxxx.supabase.co:5432/postgres"
# Should connect successfully
\q  # to quit
```

#### **C. Google Gemini AI Setup**

1. **Get API key:** https://makersuite.google.com/app/apikey
2. **Enable Gemini API:**
   - Click "Get API Key"
   - Create new key or use existing
3. **Test API key:**
```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
# Should return a response
```

---

### **Step 6: Verify Database Schema**

The application will auto-create tables when you upload your first PDF, but you can verify the connection:

```bash
python -c "
from src.backend.config import Config
import psycopg2

config = Config()
conn = psycopg2.connect(config.database_url)
print('✅ Database connection successful')
conn.close()
"
```

---

### **Step 7: Start the Backend Server**

**Option A: Using make (recommended)**
```bash
make run-backend
```

**Option B: Direct uvicorn**
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test backend:**
```bash
# In a new terminal
curl http://localhost:8000/
# Should return: {"message": "PDF Assistant API", ...}

curl http://localhost:8000/health
# Should return: {"status": "healthy", "services": {...}}
```

---

### **Step 8: Start the Frontend (Streamlit)**

**In a new terminal:**

```bash
# Activate venv
source venv/bin/activate

# Start Streamlit
make run-frontend
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Access the app:** http://localhost:8501

---

### **Step 9: Test the Full Pipeline**

#### **A. Upload a PDF**

1. **Open Streamlit:** http://localhost:8501
2. **Upload test PDF:** Use `The FIFA World Cup_ A Historical Journey-1.pdf`
3. **Wait for processing:** Should see progress bars
4. **Check summary:** Should show:
   - ✅ Text chunks stored in Pinecone
   - ✅ Tables stored in PostgreSQL
   - ✅ Schemas generated

#### **B. Test Text-Only Query**

**Query:** "What was the host nation for the first World Cup?"

**Expected Flow:**
1. Manager Agent classifies as "rag"
2. RAG Agent searches Pinecone
3. Returns: "Uruguay was chosen as the first host nation in 1930."

**Test via API:**
```bash
curl -X POST http://localhost:8000/answer \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What was the host nation for the first World Cup?",
    "pdf_uuid": "YOUR_PDF_UUID_FROM_UPLOAD"
  }'
```

#### **C. Test Table-Only Query**

**Query:** "How many World Cup matches ended in a draw?"

**Expected Flow:**
1. Manager Agent classifies as "table"
2. Table Agent generates SQL: `SELECT COUNT(*) WHERE home_score = away_score`
3. Executes on PostgreSQL
4. Returns: "14 matches ended in a draw."

#### **D. Test Hybrid Query**

**Query:** "How many times did Brazil win the World Cup and what leagues exist in Europe?"

**Expected Flow:**
1. Manager Agent classifies as "both"
2. Splits into sub-queries:
   - Table: "How many times did Brazil win?"
   - RAG: "What European leagues exist?"
3. Table Agent: Queries PostgreSQL → "5 times"
4. RAG Agent: Searches Pinecone → "Premier League, La Liga..."
5. Combiner Agent: Merges both responses

---

### **Step 10: Verify Data Storage**

#### **A. Check Pinecone Vectors**

```bash
python -c "
from pinecone import Pinecone
import os

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index('hybridrag-index')
stats = index.describe_index_stats()
print(f'✅ Total vectors: {stats.total_vector_count}')
"
```

#### **B. Check PostgreSQL Tables**

```bash
psql "postgresql://postgres:your_password@db.xxxxxxxxxxxxxxxxxxxx.supabase.co:5432/postgres" -c "\dt"
# Should show dynamically created tables like: pdf_abc123_world_cup
```

#### **C. Check table_schema.json**

```bash
cat src/backend/utils/table_schema.json
# Should show generated schemas
```

---

## 🧪 TROUBLESHOOTING

### **Issue 1: "ModuleNotFoundError: No module named 'src'"**

**Solution:**
```bash
export PYTHONPATH=$(pwd)
# Add to ~/.zshrc or ~/.bashrc:
echo "export PYTHONPATH=$(pwd)" >> ~/.zshrc
```

---

### **Issue 2: "Connection to database failed"**

**Diagnosis:**
```bash
psql "postgresql://postgres:your_password@db.xxxxxxxxxxxxxxxxxxxx.supabase.co:5432/postgres"
```

**Possible causes:**
- ❌ Wrong password in `.env`
- ❌ Supabase project paused (free tier)
- ❌ IP address not whitelisted (check Supabase > Settings > Database > Connection Pooling)

**Solution:**
- Verify credentials in Supabase dashboard
- Restart Supabase project if paused
- Add your IP to allowlist

---

### **Issue 3: "Pinecone index not found"**

**Solution:**
```bash
# Check index name in Pinecone dashboard
# Update PINECONE_INDEX_NAME in .env
# Restart backend server
```

---

### **Issue 4: "Gemini API quota exceeded"**

**Error:** `429 Too Many Requests`

**Solution:**
- Free tier: 60 requests/minute
- Wait 1 minute between tests
- Consider upgrading to paid tier

---

### **Issue 5: "Port 8000 already in use"**

**Solution:**
```bash
# Find process using port
lsof -ti:8000
# Kill process
kill -9 $(lsof -ti:8000)
# Or use different port
PORT=8001 make run-backend
```

---

## 🎯 COMMON COMMANDS

```bash
# Start backend
make run-backend

# Start frontend
make run-frontend

# Run both (parallel)
make run-all

# Test health
curl http://localhost:8000/health

# View logs (backend)
tail -f logs/app.log

# Clean cache
make clean

# Run tests
make test

# Lint code
make lint

# Format code
make format

# Data management
make data-summary        # View current data
make clear-data          # Clear all data (with confirmation)
make data-manager        # Interactive menu
```

---

## 📊 DATA MANAGEMENT

### **View Current Data**

```bash
make data-summary
```

**Output:**
```
📊 Current Data Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Pinecone Vectors:
  • Total vectors: 1,234
  • Namespaces: default

🗄️  PostgreSQL Tables:
  • pdf_abc123_world_cup (25 rows)
  • pdf_def456_revenue_data (102 rows)
```

---

### **Clear All Data**

```bash
make clear-data
```

**Confirmation prompt:**
```
⚠️  WARNING: This will delete ALL data!
  • Pinecone: All vectors
  • PostgreSQL: All tables
  • Schemas: table_schema.json

Type 'yes' to confirm:
```

---

## 🔍 DEBUGGING

### **Enable Debug Logging**

In `.env`:
```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

### **Check Application Logs**

```bash
# Backend logs
tail -f logs/app.log

# Uvicorn logs
tail -f logs/uvicorn.log
```

### **Test Individual Components**

```bash
# Test RAG Agent
python -c "
from src.backend.agents.rag_agent import ChatbotAgent
agent = ChatbotAgent()
result = agent.answer_question('What is the capital of France?')
print(result)
"

# Test Table Agent
python -c "
from src.backend.agents.table_agent import TableAgent
agent = TableAgent()
result = agent.process_query('Count all records', 'your_pdf_uuid')
print(result)
"

# Test Manager Agent
python src/backend/test_manager_agent.py
```

---

## 📚 NEXT STEPS

1. **Read the architecture:** `ARCHITECTURE_DEEP_DIVE.md`
2. **Prepare for interview:** `INTERVIEW_PREP_GUIDE.md`
3. **Explore codebase:** Start with `src/backend/__init__.py`
4. **Run tests:** `make test`
5. **Try custom PDFs:** Upload your own documents

---

## 🆘 GETTING HELP

- **Documentation:** Check `docs/` folder
- **API Reference:** http://localhost:8000/docs (when server running)
- **Logs:** `logs/app.log`
- **GitHub Issues:** Create issue in repository

---

## ✅ SUCCESS CHECKLIST

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list` shows all packages)
- [ ] `.env` file configured with valid credentials
- [ ] Pinecone index created (dimension=768)
- [ ] Supabase database accessible
- [ ] Gemini API key working
- [ ] Backend server starts without errors
- [ ] Frontend loads at http://localhost:8501
- [ ] Health check returns "healthy"
- [ ] PDF upload works
- [ ] Text queries return answers
- [ ] Table queries execute SQL
- [ ] Hybrid queries combine responses

---

**🎉 Congratulations! Your Hybrid RAG system is now running locally!**

*For interview preparation, review `INTERVIEW_PREP_GUIDE.md` with project-specific examples.*


