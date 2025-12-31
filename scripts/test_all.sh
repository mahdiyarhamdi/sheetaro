#!/bin/bash
# Comprehensive test runner for Sheetaro

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Sheetaro Test Suite ===${NC}"
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/../backend"

echo -e "${YELLOW}=== Running Backend Unit Tests ===${NC}"
if pytest tests/unit -v --tb=short; then
    echo -e "${GREEN}[PASS] Unit tests${NC}"
else
    echo -e "${RED}[FAIL] Unit tests${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}=== Running Backend Integration Tests ===${NC}"
if pytest tests/integration -v --tb=short; then
    echo -e "${GREEN}[PASS] Integration tests${NC}"
else
    echo -e "${RED}[FAIL] Integration tests${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}=== Running Backend E2E Tests ===${NC}"
if pytest tests/e2e -v --tb=short; then
    echo -e "${GREEN}[PASS] E2E tests${NC}"
else
    echo -e "${RED}[FAIL] E2E tests${NC}"
    exit 1
fi
echo ""

echo -e "${GREEN}=== All Tests Passed! ===${NC}"

