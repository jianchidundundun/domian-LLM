#!/bin/bash

# Set base URL
BASE_URL="http://localhost:8001"

# Color definitions
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting filter tests...${NC}\n"

# 1. Test low-pass filter
echo "1. Testing low-pass filter..."
curl -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "function": "lowpass",
    "args": [[1.0, 2.0, 1.5, 3.0, 2.5, 2.0, 1.0]],
    "kwargs": {
      "cutoff_freq": 10.0,
      "sampling_rate": 100.0
    }
  }' | json_pp

sleep 1

# 2. Test high-pass filter
echo -e "\n2. Testing high-pass filter..."
curl -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "function": "highpass",
    "args": [[1.0, 2.0, 1.5, 3.0, 2.5, 2.0, 1.0]],
    "kwargs": {
      "cutoff_freq": 20.0,
      "sampling_rate": 100.0
    }
  }' | json_pp

sleep 1

# 3. Test band-pass filter
echo -e "\n3. Testing band-pass filter..."
curl -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "function": "bandpass",
    "args": [[1.0, 2.0, 1.5, 3.0, 2.5, 2.0, 1.0]],
    "kwargs": {
      "low_cutoff": 10.0,
      "high_cutoff": 30.0,
      "sampling_rate": 100.0
    }
  }' | json_pp

echo -e "\n${GREEN}Filter tests completed${NC}" 