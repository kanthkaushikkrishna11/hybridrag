# 📁 HybridRAG Project Structure

**Clean, organized file structure for the Hybrid RAG system**

---

## 📂 **ROOT DIRECTORY**

```
HybridRAG/
├── 📄 README.md                    # Project overview
├── 📄 TESTING_GUIDE.md            # ⭐ START HERE for testing
├── 📄 PROJECT_STRUCTURE.md        # This file - navigation guide
├── 📄 app.py                      # FastAPI backend application
├── 📄 requirements.txt            # Python dependencies
├── 📄 Makefile                    # Build and run commands
│
├── 📁 docs/                       # All documentation
│   ├── 📄 COMPLETE_SYSTEM_OPTIMIZATION_SUMMARY.md  # Full system overview
│   ├── 📄 GROUND_TRUTH_ANALYSIS.md                 # PDF analysis & validation
│   ├── 📄 SYSTEMATIC_VALIDATION_PLAN.md            # Complete test plan
│   ├── 📄 ARCHITECTURE.md                          # System architecture
│   ├── 📁 architecture/           # Detailed architecture docs
│   ├── 📁 setup/                  # Installation guides
│   ├── 📁 validation/             # Validation documentation
│   ├── 📁 fixes/                  # Fix history
│   └── 📁 interview/              # Interview preparation
│
├── 📁 src/                        # Source code
│   └── backend/
│       ├── agents/                # AI agents (Manager, Table, RAG, Combiner)
│       ├── routes/                # API endpoints
│       ├── services/              # Business logic
│       └── utils/                 # Helper utilities
│
├── 📁 frontend-new/               # React + Vite frontend
│   ├── src/
│   │   └── components/
│   │       ├── Chat/              # Chat interface
│   │       ├── Comparison/        # Comparison interface
│   │       ├── Upload/            # PDF upload
│   │       └── Layout/            # Layout components
│   └── package.json
│
├── 📁 scripts/                    # Utility scripts
│   ├── validate_all_queries.py   # Automated validation
│   └── setup/                     # Setup wizards
│
├── 📁 resources/                  # Test data & assets
│   └── The FIFA World Cup_ A Historical Journey-1.pdf  # Test PDF
│
├── 📁 tests/                      # Unit tests
├── 📁 logs_archive/               # Archived logs
└── 📁 venv/                       # Python virtual environment
```

---

## 🎯 **QUICK NAVIGATION**

### **Want to Test the System?**
👉 **`TESTING_GUIDE.md`** - Start here! 15 queries ready to copy-paste

### **Want to Understand the System?**
1. `README.md` - Project overview
2. `docs/ARCHITECTURE.md` - How it works
3. `docs/COMPLETE_SYSTEM_OPTIMIZATION_SUMMARY.md` - Current state

### **Want to Validate Performance?**
1. `docs/GROUND_TRUTH_ANALYSIS.md` - What correct answers should be
2. `docs/SYSTEMATIC_VALIDATION_PLAN.md` - Complete test plan
3. `scripts/validate_all_queries.py` - Automated testing

### **Want to Set Up Locally?**
1. `docs/setup/LOCAL_SETUP_GUIDE.md` - Installation steps
2. `docs/setup/API_SETUP_GUIDE.md` - API configuration
3. `docs/setup/READY_TO_USE.md` - Quick start

### **Want to Understand Fixes?**
1. `docs/fixes/` - All fix documentation
2. `docs/COMPLETE_SYSTEM_OPTIMIZATION_SUMMARY.md` - Latest improvements

---

## 📋 **FILE PURPOSE GUIDE**

### **Root Level Files** (Keep minimal)
- **README.md**: Project introduction and overview
- **TESTING_GUIDE.md**: Practical testing instructions with queries
- **PROJECT_STRUCTURE.md**: This navigation guide
- **app.py**: Backend application entry point
- **requirements.txt**: Python package dependencies
- **Makefile**: Build automation

### **Documentation** (`docs/`)
- **Main docs**: Architecture, validation, optimization summaries
- **Subdirectories**: Organized by topic (setup, fixes, validation, architecture, interview)

### **Source Code** (`src/`)
- **backend/agents/**: AI agent implementations
- **backend/routes/**: FastAPI endpoints
- **backend/services/**: Core business logic
- **backend/utils/**: Shared utilities

### **Frontend** (`frontend-new/`)
- **src/components/**: React components
- **src/services/**: API client
- **src/types/**: TypeScript types

### **Scripts** (`scripts/`)
- **validate_all_queries.py**: Systematic testing
- **setup/**: Installation and configuration wizards

### **Resources** (`resources/`)
- **Test PDFs**: Sample documents for testing
- **Assets**: Images, diagrams, guides

---

## 🧹 **CLEAN STRUCTURE RULES**

### **Keep in Root:**
✅ Essential files: app.py, README.md, requirements.txt, Makefile  
✅ Quick guides: TESTING_GUIDE.md, PROJECT_STRUCTURE.md  
✅ Standard files: .gitignore, .env, LICENSE

### **Move to docs/:**
✅ All Markdown documentation  
✅ Guides, tutorials, explanations  
✅ Architecture documents  
✅ Fix reports and summaries

### **Move to scripts/:**
✅ Python validation scripts  
✅ Setup and automation scripts  
✅ Testing utilities

### **Move to resources/:**
✅ Test PDFs and data files  
✅ Images and diagrams  
✅ Sample files

### **Never in Root:**
❌ Log files (should be in logs/ or logs_archive/)  
❌ Backup files (.bak)  
❌ Temporary files  
❌ Large data files

---

## 🎯 **CURRENT FOCUS**

### **Testing Phase**
📍 You are here: Ready to validate Hybrid RAG improvements

**What to do next:**
1. Open `TESTING_GUIDE.md`
2. Start with **Test 1**, **Test 14**, and **Test 10**
3. Use the Comparison Tab in frontend
4. Validate ≥50% improvement for table/hybrid queries

**Key Documents for Testing:**
- `TESTING_GUIDE.md` - Queries to test
- `docs/GROUND_TRUTH_ANALYSIS.md` - Expected answers
- `docs/COMPLETE_SYSTEM_OPTIMIZATION_SUMMARY.md` - What was improved

---

## 📊 **SYSTEM STATUS**

```
✅ Backend: Running on port 8000
✅ Frontend: Ready on port 5173
✅ PDF: Uploaded and processed
✅ Fixes: All applied
✅ Documentation: Complete
✅ Testing: Ready to start

📍 Next: Run queries from TESTING_GUIDE.md
```

---

## 🔗 **IMPORTANT LINKS**

| Purpose | Document |
|---------|----------|
| **Start Testing** | `TESTING_GUIDE.md` |
| **System Overview** | `README.md` |
| **Architecture** | `docs/ARCHITECTURE.md` |
| **Ground Truth** | `docs/GROUND_TRUTH_ANALYSIS.md` |
| **All Improvements** | `docs/COMPLETE_SYSTEM_OPTIMIZATION_SUMMARY.md` |
| **Validation Plan** | `docs/SYSTEMATIC_VALIDATION_PLAN.md` |
| **Setup Guide** | `docs/setup/LOCAL_SETUP_GUIDE.md` |
| **Comparison Feature** | `docs/COMPARISON_FEATURE_GUIDE.md` |

---

**The project is clean, organized, and ready for systematic testing! 🚀**

