#!/bin/bash
# API Health Check Script for Sheetaro

BASE_URL=${1:-"http://localhost:3005"}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Sheetaro API Health Check ===${NC}"
echo "Base URL: $BASE_URL"
echo ""

PASSED=0
FAILED=0

check_endpoint() {
    local path=$1
    local expected_status=${2:-200}
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$path" 2>/dev/null)
    
    if [ "$response" == "$expected_status" ]; then
        echo -e "${GREEN}[OK]${NC} $path (HTTP $response)"
        ((PASSED++))
    else
        echo -e "${RED}[FAIL]${NC} $path (Expected: $expected_status, Got: $response)"
        ((FAILED++))
    fi
}

echo "Checking endpoints..."
echo ""

# Health check
check_endpoint "/health"

# Users API
check_endpoint "/api/v1/users/1" 404  # Non-existent user returns 404

# Products API
check_endpoint "/api/v1/products"

# Categories API
check_endpoint "/api/v1/categories"

# Orders API (requires user_id)
check_endpoint "/api/v1/orders?user_id=00000000-0000-0000-0000-000000000000"

# Settings API
check_endpoint "/api/v1/settings/payment-card"

# Payments API
check_endpoint "/api/v1/payments/pending-approval"

echo ""
echo "=================================="
echo -e "Results: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}"
echo "=================================="

if [ $FAILED -gt 0 ]; then
    exit 1
fi
exit 0

