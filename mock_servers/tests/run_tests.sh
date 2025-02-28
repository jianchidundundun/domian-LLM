#!/bin/bash

# Set colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Running MATLAB server tests...${NC}\n"

# Run tests
poetry run pytest tests/test_matlab_server.py -v

# Check test results
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed${NC}"
else
    echo -e "\n${RED}Tests failed${NC}"
    exit 1
fi 