#!/bin/bash

# Section 12 Verification Script
# This script runs all verification steps for Section 12 completion

set -e  # Exit on error

echo "=================================================="
echo "Section 12 Verification Script"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1 passed${NC}"
    else
        echo -e "${RED}✗ $1 failed${NC}"
        exit 1
    fi
}

# Change to frontend directory
cd "$(dirname "$0")"

echo "Step 1: Type Checking"
echo "--------------------"
npm run type-check
print_status "Type checking"
echo ""

echo "Step 2: Linting"
echo "--------------------"
npm run lint
print_status "Linting"
echo ""

echo "Step 3: Unit Tests"
echo "--------------------"
npm run test:run
print_status "Unit tests"
echo ""

echo "Step 4: Accessibility Tests"
echo "--------------------"
npm run test:a11y
print_status "Accessibility tests"
echo ""

echo "Step 5: Build"
echo "--------------------"
npm run build
print_status "Build"
echo ""

echo "Step 6: Bundle Size Check"
echo "--------------------"
echo "Main bundle sizes:"
ls -lh dist/assets/*.js | grep -E "(index|vendor)" || true
echo ""
TOTAL_SIZE=$(du -sh dist/ | cut -f1)
echo "Total dist size: $TOTAL_SIZE"
echo ""

echo "Step 7: E2E Tests (Optional - requires Playwright)"
echo "--------------------"
read -p "Run E2E tests? This requires Playwright browsers installed. (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    npm run test:e2e
    print_status "E2E tests"
else
    echo -e "${YELLOW}⊘ E2E tests skipped${NC}"
fi
echo ""

echo "Step 8: Lighthouse Audit (Optional)"
echo "--------------------"
read -p "Run Lighthouse audit? This requires the preview server. (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    npm run lighthouse
    print_status "Lighthouse audit"
else
    echo -e "${YELLOW}⊘ Lighthouse audit skipped${NC}"
fi
echo ""

echo "Step 9: Docker Build (Optional)"
echo "--------------------"
read -p "Test Docker build? This requires Docker installed. (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker build -t neo-alexandria-frontend-test .
    print_status "Docker build"
    
    echo "Testing container..."
    docker run -d -p 8081:80 --name neo-test neo-alexandria-frontend-test
    sleep 3
    
    HEALTH_CHECK=$(curl -s http://localhost:8081/health)
    if [ "$HEALTH_CHECK" = "healthy" ]; then
        echo -e "${GREEN}✓ Health check passed${NC}"
    else
        echo -e "${RED}✗ Health check failed${NC}"
    fi
    
    docker stop neo-test
    docker rm neo-test
    docker rmi neo-alexandria-frontend-test
else
    echo -e "${YELLOW}⊘ Docker build skipped${NC}"
fi
echo ""

echo "=================================================="
echo -e "${GREEN}Section 12 Verification Complete!${NC}"
echo "=================================================="
echo ""
echo "Summary:"
echo "  ✓ Type checking passed"
echo "  ✓ Linting passed"
echo "  ✓ Unit tests passed"
echo "  ✓ Accessibility tests passed"
echo "  ✓ Build successful"
echo ""
echo "Next steps:"
echo "  1. Review SECTION12_CHECKLIST.md"
echo "  2. Review DEPLOYMENT.md for deployment instructions"
echo "  3. Deploy to staging environment"
echo "  4. Conduct user acceptance testing"
echo "  5. Deploy to production"
echo ""
