#!/bin/bash

# =============================================================================
# Sheetaro - Local Development Environment Script
# =============================================================================
#
# This script helps you run the Sheetaro project locally for development.
#
# Usage:
#   ./scripts/run-local.sh [command]
#
# Commands:
#   start       Start all services (default)
#   stop        Stop all services
#   restart     Restart all services
#   logs        Show logs for all services
#   backend     Show backend logs only
#   frontend    Show frontend logs only
#   db          Show database logs only
#   shell       Open a shell in the backend container
#   migrate     Run database migrations
#   seed        Seed the database with test data
#   clean       Stop services and remove volumes
#   status      Show status of all services
#   help        Show this help message
#
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Helper functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Start services
start_services() {
    print_header "Starting Sheetaro Development Environment"
    
    check_docker
    
    print_info "Building and starting containers..."
    docker-compose up -d --build
    
    echo ""
    print_success "Services started successfully!"
    echo ""
    print_info "Access the application at:"
    echo "  • Frontend:  http://localhost:3000"
    echo "  • Backend:   http://localhost:3005"
    echo "  • API Docs:  http://localhost:3005/docs"
    echo "  • MailHog:   http://localhost:8025"
    echo ""
    print_info "Default admin credentials:"
    echo "  • Email: admin@sheetaro.ir"
    echo "  • Password: admin123"
    echo ""
    print_info "To view logs, run: ./scripts/run-local.sh logs"
}

# Stop services
stop_services() {
    print_header "Stopping Sheetaro Services"
    docker-compose down
    print_success "Services stopped"
}

# Restart services
restart_services() {
    print_header "Restarting Sheetaro Services"
    docker-compose restart
    print_success "Services restarted"
}

# Show logs
show_logs() {
    docker-compose logs -f --tail=100
}

# Show backend logs
show_backend_logs() {
    docker-compose logs -f --tail=100 backend
}

# Show frontend logs
show_frontend_logs() {
    docker-compose logs -f --tail=100 frontend
}

# Show database logs
show_db_logs() {
    docker-compose logs -f --tail=100 db
}

# Open shell in backend container
open_shell() {
    print_info "Opening shell in backend container..."
    docker-compose exec backend /bin/bash
}

# Run migrations
run_migrations() {
    print_header "Running Database Migrations"
    docker-compose exec backend alembic upgrade head
    print_success "Migrations completed"
}

# Seed database
seed_database() {
    print_header "Seeding Database"
    print_warning "This will add test data to your database"
    docker-compose exec backend python -c "
from app.core.seed import seed_all
import asyncio
asyncio.run(seed_all())
"
    print_success "Database seeded"
}

# Clean everything
clean_all() {
    print_header "Cleaning Up"
    print_warning "This will stop all services and remove volumes"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v --remove-orphans
        print_success "Cleanup completed"
    else
        print_info "Cleanup cancelled"
    fi
}

# Show status
show_status() {
    print_header "Service Status"
    docker-compose ps
}

# Show help
show_help() {
    cat << EOF
${BLUE}Sheetaro - Local Development Environment${NC}

${GREEN}Usage:${NC}
  ./scripts/run-local.sh [command]

${GREEN}Commands:${NC}
  ${YELLOW}start${NC}       Start all services (default)
  ${YELLOW}stop${NC}        Stop all services
  ${YELLOW}restart${NC}     Restart all services
  ${YELLOW}logs${NC}        Show logs for all services
  ${YELLOW}backend${NC}     Show backend logs only
  ${YELLOW}frontend${NC}    Show frontend logs only
  ${YELLOW}db${NC}          Show database logs only
  ${YELLOW}shell${NC}       Open a shell in the backend container
  ${YELLOW}migrate${NC}     Run database migrations
  ${YELLOW}seed${NC}        Seed the database with test data
  ${YELLOW}clean${NC}       Stop services and remove volumes
  ${YELLOW}status${NC}      Show status of all services
  ${YELLOW}help${NC}        Show this help message

${GREEN}URLs:${NC}
  Frontend:   http://localhost:3000
  Backend:    http://localhost:3005
  API Docs:   http://localhost:3005/docs
  MailHog:    http://localhost:8025

${GREEN}Examples:${NC}
  ./scripts/run-local.sh start      # Start development environment
  ./scripts/run-local.sh logs       # View all logs
  ./scripts/run-local.sh backend    # View backend logs
  ./scripts/run-local.sh migrate    # Run migrations
  ./scripts/run-local.sh shell      # Access backend shell

EOF
}

# Main command handler
case "${1:-start}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        show_logs
        ;;
    backend)
        show_backend_logs
        ;;
    frontend)
        show_frontend_logs
        ;;
    db)
        show_db_logs
        ;;
    shell)
        open_shell
        ;;
    migrate)
        run_migrations
        ;;
    seed)
        seed_database
        ;;
    clean)
        clean_all
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

