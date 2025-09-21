### Local Development

1. **Build the Docker image:**
   ```bash
   docker build -t python-executor .
   ```

2. **Run the service:**
   ```bash
   docker run -p 8080:8080 python-executor
   ```

3. **Test with cURL:**
   ```bash
   curl -X POST http://localhost:8080/execute \
     -H "Content-Type: application/json" \
     -d '{"script": "def main(): return {\"message\": \"Hello World\", \"result\": 42}"}'
   ```

### Cloud Run Deployment

The service is designed to be deployed on Google Cloud Run. Here's an example cURL request to the deployed service:

```bash
curl -X POST https://YOUR_CLOUD_RUN_URL/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main(): return {\"message\": \"Hello from Cloud Run!\", \"calculation\": 2 + 2}"}'
```

## API Reference

### POST /execute

Executes a Python script and returns the result of the `main()` function.

**Request Body:**
```json
{
  "script": "def main(): return {'hello': 'world'}"
}
```

**Response:**
```json
{
  "result": {"hello": "world"},
  "stdout": "Script executed successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid script or missing main() function
- `500 Internal Server Error`: Execution failed or timeout

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Examples

### Basic Example
```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main(): return {\"greeting\": \"Hello World\"}"}'
```

### Using Pandas
```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "
import pandas as pd
import numpy as np

def main():
    df = pd.DataFrame({\"A\": [1, 2, 3], \"B\": [4, 5, 6]})
    return {
        \"shape\": df.shape,
        \"sum\": df.sum().to_dict(),
        \"mean\": df.mean().to_dict()
    }
"
  }'
```

### Mathematical Calculation
```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "
import numpy as np

def main():
    arr = np.array([1, 2, 3, 4, 5])
    return {
        \"array\": arr.tolist(),
        \"sum\": float(np.sum(arr)),
        \"mean\": float(np.mean(arr)),
        \"std\": float(np.std(arr))
    }
"
  }'
```
## Requirements

- Docker
- Python 3.11+
- nsjail (included in Docker image)

## Error Handling

The service handles various error scenarios:

- **Missing main() function**: Returns 400 with descriptive error
- **Invalid JSON return**: Returns 400 if main() doesn't return valid JSON
- **Execution timeout**: Returns 500 if script runs longer than 30 seconds
- **Resource limits**: Returns 500 if script exceeds memory/file limits
- **Malicious code**: Sandboxed execution prevents system damage

## Development

### Project Structure
```
.
├── app.py              # Flask application
├── python.config       # nsjail configuration
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container definition
├── .dockerignore      # Docker ignore file
└── README.md          # This file
```

### Building and Testing
```bash
# Build image
docker build -t python-executor .

# Run locally
docker run -p 8080:8080 python-executor

# Test health endpoint
curl http://localhost:8080/health

# Test execution endpoint
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main(): return {\"test\": \"success\"}"}'
```