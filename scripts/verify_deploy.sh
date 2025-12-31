#!/bin/bash
# Deployment Verification Script for Sheetaro

set -e

# Configuration
SERVER_IP=${SERVER_IP:-"148.251.95.198"}
SERVER_PORT=${SERVER_PORT:-22}
SERVER_USER=${SERVER_USER:-"root"}
API_PORT=${API_PORT:-3005}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Sheetaro Deployment Verification ===${NC}"
echo "Server: $SERVER_USER@$SERVER_IP:$SERVER_PORT"
echo ""

# Function to run remote command
remote_cmd() {
    ssh -o StrictHostKeyChecking=no -p $SERVER_PORT $SERVER_USER@$SERVER_IP "$1"
}

echo -e "${YELLOW}1. Checking Docker Containers...${NC}"
CONTAINERS=$(remote_cmd "cd /root/sheetaro && docker compose -f docker-compose.prod.yml ps --format '{{.Name}} {{.Status}}'" 2>/dev/null)
echo "$CONTAINERS"
echo ""

# Check if all containers are running
if echo "$CONTAINERS" | grep -q "Up"; then
    echo -e "${GREEN}[OK] Containers are running${NC}"
else
    echo -e "${RED}[FAIL] Some containers are not running${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}2. Checking API Health...${NC}"
HEALTH=$(remote_cmd "curl -s http://localhost:$API_PORT/health" 2>/dev/null)
if echo "$HEALTH" | grep -q "ok"; then
    echo -e "${GREEN}[OK] API is healthy${NC}"
else
    echo -e "${RED}[FAIL] API health check failed${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}3. Checking Database Connection...${NC}"
DB_CHECK=$(remote_cmd "cd /root/sheetaro && docker compose -f docker-compose.prod.yml exec -T db pg_isready -U sheetaro" 2>/dev/null)
if echo "$DB_CHECK" | grep -q "accepting connections"; then
    echo -e "${GREEN}[OK] Database is accepting connections${NC}"
else
    echo -e "${RED}[FAIL] Database connection failed${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}4. Checking Redis Connection...${NC}"
REDIS_CHECK=$(remote_cmd "cd /root/sheetaro && docker compose -f docker-compose.prod.yml exec -T redis redis-cli ping" 2>/dev/null)
if echo "$REDIS_CHECK" | grep -q "PONG"; then
    echo -e "${GREEN}[OK] Redis is responding${NC}"
else
    echo -e "${RED}[FAIL] Redis connection failed${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}5. Checking Migration Status...${NC}"
MIGRATION=$(remote_cmd "cd /root/sheetaro && docker compose -f docker-compose.prod.yml exec -T backend alembic current" 2>/dev/null)
echo "$MIGRATION"
echo -e "${GREEN}[OK] Migration status retrieved${NC}"
echo ""

echo -e "${YELLOW}6. Testing API Endpoints...${NC}"
# Test categories
CATEGORIES=$(remote_cmd "curl -s http://localhost:$API_PORT/api/v1/categories" 2>/dev/null)
if [ -n "$CATEGORIES" ]; then
    echo -e "${GREEN}[OK] Categories endpoint working${NC}"
else
    echo -e "${RED}[FAIL] Categories endpoint failed${NC}"
fi

# Test products
PRODUCTS=$(remote_cmd "curl -s http://localhost:$API_PORT/api/v1/products" 2>/dev/null)
if echo "$PRODUCTS" | grep -q "items"; then
    echo -e "${GREEN}[OK] Products endpoint working${NC}"
else
    echo -e "${RED}[FAIL] Products endpoint failed${NC}"
fi

# Test payment card
CARD=$(remote_cmd "curl -s http://localhost:$API_PORT/api/v1/settings/payment-card" 2>/dev/null)
if echo "$CARD" | grep -q "card_number"; then
    echo -e "${GREEN}[OK] Payment card configured${NC}"
else
    echo -e "${YELLOW}[WARN] Payment card not configured${NC}"
fi
echo ""

echo -e "${YELLOW}7. Checking Bot Logs (last 5 lines)...${NC}"
BOT_LOGS=$(remote_cmd "cd /root/sheetaro && docker compose -f docker-compose.prod.yml logs bot --tail 5" 2>/dev/null)
echo "$BOT_LOGS"
echo ""

echo "=================================="
echo -e "${GREEN}Deployment Verification Complete!${NC}"
echo "=================================="

