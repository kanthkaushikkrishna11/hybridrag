# ✅ CORRECT PORTS AND URLS

## 🎯 Your Application URLs

### Backend (FastAPI)
- **Port**: `8010`
- **URL**: `http://localhost:8010`
- **Status**: ✅ **RUNNING**
- **Process**: Python (PID: 48061, 82283)

### Frontend (React/TypeScript/Vite)
- **Port**: `7000`
- **URL**: `http://localhost:7000`
- **Status**: ✅ **RUNNING**
- **Process**: Node/Vite (PID: 60431)

---

## 🚀 How to Access

### Open Your Browser:
```
http://localhost:7000
```

### API is at:
```
http://localhost:8010
```

---

## ⚠️ IMPORTANT NOTE

**DO NOT use `localhost:5173`** - That was my mistake!

Your Vite configuration is set to port **7000**:

```typescript
// vite.config.ts
server: {
  port: 7000,
  host: 'localhost',
  open: true,
}
```

---

## ✅ Everything is Already Running!

You don't need to start anything. Both services are active:

1. ✅ Backend on port 8010
2. ✅ Frontend on port 7000

**Just open `http://localhost:7000` in your browser!**

---

## 🎯 To Use the Comparison Feature:

1. **Go to**: `http://localhost:7000`
2. **Upload a PDF** using the sidebar
3. **Click** the toggle: `[💬 Normal Chat] [🔍 Comparison Demo]`
4. **Select** "🔍 Comparison Demo"
5. **Enter a question** or click a suggested one
6. **Click** "🚀 Run Comparison"
7. **View** side-by-side results!

---

## 🔧 If You Need to Restart Frontend:

```bash
cd /Users/krishnakaushik/hybridrag/HybridRAG/frontend-new
npm run dev
```

It will automatically start on port 7000.

---

## 🔧 If You Need to Restart Backend:

```bash
cd /Users/krishnakaushik/hybridrag/HybridRAG
source venv/bin/activate
python app.py
```

It will start on port 8010.

---

## 📊 Quick Port Check Commands:

### Check Frontend (port 7000):
```bash
lsof -i :7000
```

### Check Backend (port 8010):
```bash
lsof -i :8010
```

### Check All Running Services:
```bash
ps aux | grep -E "(vite|python|streamlit)" | grep -v grep
```

---

## 🎉 Summary

**Both services are already running!**

- Backend: ✅ `http://localhost:8010`
- Frontend: ✅ `http://localhost:7000`

**Just open `http://localhost:7000` and start using the comparison feature!** 🚀

