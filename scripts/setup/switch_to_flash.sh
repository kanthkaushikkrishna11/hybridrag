#!/bin/bash

# Automated script to switch from gemini-2.5-pro to gemini-1.5-flash
# This resolves quota issues by using a model with higher rate limits

echo "🔄 Switching all Gemini models from 2.5-pro to 1.5-flash..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# File 1: manager_agent.py
echo "${YELLOW}Updating manager_agent.py...${NC}"
sed -i.bak 's/model="gemini-2\.5-pro"/model="gemini-1.5-flash"/' src/backend/agents/manager_agent.py
if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Updated manager_agent.py${NC}"
else
    echo "❌ Failed to update manager_agent.py"
fi

# File 2: combiner_agent.py
echo "${YELLOW}Updating combiner_agent.py...${NC}"
sed -i.bak 's/model="gemini-2\.5-pro"/model="gemini-1.5-flash"/' src/backend/agents/combiner_agent.py
if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Updated combiner_agent.py${NC}"
else
    echo "❌ Failed to update combiner_agent.py"
fi

# File 3: rag_agent.py
echo "${YELLOW}Updating rag_agent.py...${NC}"
sed -i.bak 's/GenerativeModel("gemini-2\.5-pro")/GenerativeModel("gemini-1.5-flash")/' src/backend/agents/rag_agent.py
if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Updated rag_agent.py${NC}"
else
    echo "❌ Failed to update rag_agent.py"
fi

# File 4: table_agent.py
echo "${YELLOW}Updating table_agent.py...${NC}"
sed -i.bak 's/model="gemini-2\.5-pro"/model="gemini-1.5-flash"/' src/backend/agents/table_agent.py
if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Updated table_agent.py${NC}"
else
    echo "❌ Failed to update table_agent.py"
fi

# File 5: pdf_processor.py
echo "${YELLOW}Updating pdf_processor.py...${NC}"
sed -i.bak "s/GenerativeModel('gemini-2\.5-pro')/GenerativeModel('gemini-1.5-flash')/" src/backend/utils/pdf_processor.py
if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Updated pdf_processor.py${NC}"
else
    echo "❌ Failed to update pdf_processor.py"
fi

echo ""
echo "${GREEN}✅ All files updated successfully!${NC}"
echo ""
echo "📋 Backup files created with .bak extension (in case you need to revert)"
echo ""
echo "🔄 Next steps:"
echo "1. Restart your backend:"
echo "   ${YELLOW}python app.py${NC}"
echo ""
echo "2. Test the health endpoint:"
echo "   ${YELLOW}curl http://localhost:8010/health${NC}"
echo ""
echo "3. Try a query to verify it works!"
echo ""
echo "Model switch complete! 🎉"
echo "gemini-1.5-flash has 30x higher rate limits (1500 requests/day vs 50)"

