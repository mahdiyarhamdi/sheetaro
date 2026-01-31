#!/bin/sh
# husky.sh - Husky shell script for git hooks

# Exit on error
set -e

# Set colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Debug mode (set HUSKY_DEBUG=1 to enable)
if [ "$HUSKY_DEBUG" = "1" ]; then
  set -x
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
  echo "${YELLOW}Warning: Not a git repository, skipping hooks${NC}"
  exit 0
fi

# Skip hooks if HUSKY_SKIP_HOOKS is set
if [ "$HUSKY_SKIP_HOOKS" = "1" ]; then
  echo "${YELLOW}Husky hooks skipped (HUSKY_SKIP_HOOKS=1)${NC}"
  exit 0
fi

# Skip hooks in CI environment (optional)
if [ "$CI" = "true" ]; then
  echo "${YELLOW}CI environment detected, hooks may behave differently${NC}"
fi

