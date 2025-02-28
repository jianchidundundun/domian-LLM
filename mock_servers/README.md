# Mock Scientific Computing Servers

A collection of mock servers for scientific computing software.

## Supported Software

### MATLAB Server
- Port: 8001
- Supported Features:
  - Basic Math Operations (plus, minus, times, divide)
  - Signal Processing (fft, ifft)
  - Filters (lowpass, highpass, bandpass)

## Quick Start

1. Install Dependencies:
```bash
cd mock_servers
poetry install
```

2. Start Server:
```bash
poetry run python src/matlab/server.py
```

3. Run Tests:
```bash
cd tests
./run_tests.sh
```

## API Usage Examples

### MATLAB Function Calls

1. Basic Math Operations
```bash
curl -X POST "http://localhost:8001/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "function": "plus",
    "args": [1, 2]
  }'
```

2. Signal Processing
```bash
curl -X POST "http://localhost:8001/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "function": "fft",
    "args": [[1, 2, 3, 4]]
  }'
```

3. Filters
```bash
curl -X POST "http://localhost:8001/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "function": "lowpass",
    "args": [[1, 2, 3, 4], 0.5]
  }'
```

## Development Guide

### Adding New Features

1. Add new methods in the corresponding class in `src/matlab/server.py`
2. Add test cases in the test file `tests/test_matlab_server.py`

### Error Handling

All API responses follow the following format:
```json
{
    "success": true/false,
    "result": "result data",
    "error": "error message (if any)"
}
```

## Notes

1. All returned numeric arrays will be converted to Python lists
2. Complex numbers will be converted to dictionaries of real and imaginary parts
3. All errors will be caught and returned with a friendly error message 