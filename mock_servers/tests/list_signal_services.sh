#!/bin/bash

# Set API base URL
API_BASE="http://127.0.0.1:8000/api/v1"

# Color definitions
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Query MATLAB services in the signal processing field...${NC}\n"

# Query all services in the signal processing field
curl -X GET "$API_BASE/services/signal processing" | json_pp

echo -e "\n${GREEN}Service query completed${NC}" 