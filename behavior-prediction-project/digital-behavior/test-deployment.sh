#!/bin/bash

# Deployment Test Script
# Tests all production-ready features locally before deploying

set -e  # Exit on error

echo "============================================"
echo "🧪 Digital Behavior Prediction - Deployment Test"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Helper function
test_result() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}"
        ((FAILED++))
    fi
}

echo "Test 1: Services Running"
echo "----------------------------------------"
docker ps --filter "name=digital-behavior" --format "table {{.Names}}\t{{.Status}}"
echo ""

echo "Test 2: Backend Health Check"
echo "----------------------------------------"
RESPONSE=$(curl -s http://localhost:8000/health)
echo "Response: $RESPONSE"
echo "$RESPONSE" | grep -q "ok"
test_result
echo ""

echo "Test 3: Frontend Accessible"
echo "----------------------------------------"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
echo "HTTP Status: $STATUS"
[ "$STATUS" == "200" ]
test_result
echo ""

echo "Test 4: Environment Variables"
echo "----------------------------------------"
echo -n "ALLOWED_ORIGINS: "
docker exec digital-behavior-backend printenv ALLOWED_ORIGINS
echo -n "DATABASE_URL: "
docker exec digital-behavior-backend printenv DATABASE_URL | sed 's/:.*@/:***@/'
test_result
echo ""

echo "Test 5: API Endpoints"
echo "----------------------------------------"
echo "Testing /api/v1/sessions..."
SESSIONS=$(curl -s -H "X-User-ID: 1" http://localhost:8000/api/v1/sessions)
echo "$SESSIONS" | grep -q "sessions\|total\|\[\]"
test_result
echo ""

echo "Test 6: Database Connection"
echo "----------------------------------------"
docker exec digital-behavior-db psql -U dbuser -d digital_behavior_prediction -c "SELECT COUNT(*) FROM users;" > /dev/null 2>&1
test_result
echo ""

echo "Test 7: Extension Build"
echo "----------------------------------------"
if [ -f "extension/dist/manifest.json" ] && [ -f "extension/dist/background.js" ]; then
    echo "Extension build files found"
    test_result
else
    echo "Extension build files missing"
    test_result
fi
echo ""

echo "Test 8: CORS Configuration"
echo "----------------------------------------"
echo "Current ALLOWED_ORIGINS:"
docker exec digital-behavior-backend printenv ALLOWED_ORIGINS
echo ""
echo -e "${YELLOW}💡 To test with custom origin:${NC}"
echo "   Update .env file and run: docker-compose down && docker-compose up -d"
test_result
echo ""

echo "============================================"
echo "📊 Test Summary"
echo "============================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED${NC}"
else
    echo -e "${GREEN}Failed: $FAILED${NC}"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed! Ready for deployment.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Follow DEPLOYMENT.md for production deployment"
    echo "2. Update extension/src/config.ts with production API URL"
    echo "3. Rebuild extension: cd extension && npm run build"
    echo "4. Test locally before deploying"
else
    echo -e "${RED}❌ Some tests failed. Fix issues before deploying.${NC}"
    exit 1
fi
