# Anthropic API Client - Local Server

A complete REST API server that provides full access to the Anthropic SDK capabilities for local deployment on your QNAP NAS.

## Features

- ✅ **Complete SDK Coverage**: All Anthropic SDK features implemented
- ✅ **Message Creation**: Synchronous and asynchronous message handling
- ✅ **Streaming**: Real-time Server-Sent Events (SSE) streaming
- ✅ **Token Counting**: Pre-request token estimation
- ✅ **Batch Processing**: Create, manage, and retrieve message batches
- ✅ **Model Management**: List and retrieve model information
- ✅ **Error Handling**: Comprehensive error handling with proper HTTP status codes
- ✅ **Logging**: Structured logging with request/response tracking
- ✅ **Health Monitoring**: Built-in health checks and metrics

## Quick Start

### 1. Environment Setup

Copy the environment template and configure your API key:

```bash
cp env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

The API will be available at `http://localhost:8000`

### 3. Docker Deployment (QNAP)

```bash
# Build and run with Docker Compose
docker-compose up -d
```

The API will be available at `http://your-qnap-ip:8090`

## API Endpoints

### Core Messages

#### Create Message (Synchronous)
```http
POST /api/v1/messages/create
```

**Request Body:**
```json
{
  "model": "claude-sonnet-4-20250514",
  "messages": [
    {
      "role": "user",
      "content": "Hello, Claude!"
    }
  ],
  "max_tokens": 1024,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "msg_xxx",
    "content": [{"type": "text", "text": "Hello! How can I help you?"}],
    "usage": {"input_tokens": 10, "output_tokens": 8}
  },
  "metadata": {
    "request_id": "req_xxx",
    "processing_time_ms": 1200
  }
}
```

#### Stream Message (Real-time)
```http
POST /api/v1/messages/stream
```

Same request body as create message. Returns Server-Sent Events stream:

```javascript
// JavaScript example
const eventSource = new EventSource('/api/v1/messages/stream', {
  method: 'POST',
  body: JSON.stringify(requestData),
  headers: {'Content-Type': 'application/json'}
});

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Event:', data.type);
  if (data.type === 'text') {
    console.log('Text:', data.text);
  }
};
```

#### Count Tokens
```http
POST /api/v1/messages/count-tokens
```

**Request Body:**
```json
{
  "model": "claude-sonnet-4-20250514",
  "messages": [
    {"role": "user", "content": "Hello, world"}
  ]
}
```

### Batch Processing

#### Create Batch
```http
POST /api/v1/batches/create
```

**Request Body:**
```json
{
  "requests": [
    {
      "custom_id": "request_1",
      "params": {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": "Hello!"}]
      }
    }
  ]
}
```

#### Get Batch Status
```http
GET /api/v1/batches/{batch_id}
```

#### List Batches
```http
GET /api/v1/batches?limit=20
```

#### Cancel Batch
```http
POST /api/v1/batches/{batch_id}/cancel
```

#### Get Batch Results
```http
GET /api/v1/batches/{batch_id}/results
```

### Model Management

#### List Models
```http
GET /api/v1/models
```

#### Get Model Info
```http
GET /api/v1/models/{model_id}
```

### Health & Monitoring

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "clients_initialized": true
}
```

## Supported Models

- `claude-sonnet-4-20250514` (Latest Sonnet 4)
- `claude-3-7-sonnet-20250219` (Claude 3.7 Sonnet)
- `claude-3-5-sonnet-latest`
- `claude-3-opus-latest`
- `claude-3-opus-20240229`

## Advanced Features

### Tool Use
```json
{
  "model": "claude-sonnet-4-20250514",
  "messages": [{"role": "user", "content": "What's the weather?"}],
  "tools": [
    {
      "name": "get_weather",
      "description": "Get weather information",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": {"type": "string"}
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```

### System Messages
```json
{
  "model": "claude-sonnet-4-20250514",
  "messages": [{"role": "user", "content": "Hello!"}],
  "system": "You are a helpful assistant."
}
```

### Streaming Events

The streaming endpoint emits these event types:
- `message_start`: Beginning of response
- `content_block_start`: Start of content block
- `content_block_delta`: Incremental content updates
- `content_block_stop`: End of content block
- `message_delta`: Final message metadata
- `message_stop`: End of message
- `ping`: Connection health check

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Required |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `ANTHROPIC_BASE_URL` | Custom API base URL | SDK default |
| `ANTHROPIC_TIMEOUT` | Request timeout in seconds | 600 |
| `ANTHROPIC_MAX_RETRIES` | Max retry attempts | 2 |

### Docker Configuration

The application is configured for optimal QNAP deployment:

- **Port**: 8090 (follows your port allocation standards)
- **Network**: Uses `solomon_network` (external network)
- **Volumes**: Logs and config directories mounted
- **Health Checks**: Automatic health monitoring
- **Restart Policy**: `unless-stopped` for reliability

## Error Handling

All endpoints return standardized error responses:

```json
{
  "success": false,
  "error": "Detailed error message",
  "metadata": {
    "error_type": "APIError",
    "request_id": "req_xxx"
  }
}
```

### Common Error Types

- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Invalid or missing API key
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server-side issues

## Development

### Project Structure

```
anthropic-api/
├── main.py              # Main FastAPI application
├── app/
│   ├── streaming.py     # SSE streaming implementation
│   ├── models_api.py    # Model management endpoints
│   └── batches_api.py   # Batch processing endpoints
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker container definition
├── docker-compose.yml  # QNAP deployment configuration
└── README.md          # This documentation
```

### Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest
```

### Logging

All requests and responses are logged with structured data:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "event": "Request completed",
  "method": "POST",
  "url": "/api/v1/messages/create",
  "status_code": 200,
  "process_time": "1.234s"
}
```

## Security

- API key authentication required
- Input validation and sanitization
- Request/response logging for audit trails
- Rate limiting to prevent abuse
- HTTPS recommended for production
- No sensitive data in application logs

## API Documentation

Once running, visit `http://your-server:8090/docs` for interactive API documentation with:

- Live request/response examples
- Schema definitions
- Try-it-out functionality
- Complete endpoint documentation

## Support

For issues or questions:

1. Check the health endpoint: `GET /health`
2. Review application logs
3. Verify API key configuration
4. Check network connectivity to Anthropic API

## License

This project is provided as-is for local deployment and testing.
