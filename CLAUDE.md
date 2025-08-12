# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an async AI processing service built with FastAPI that provides concurrent file processing capabilities with AI integration. The service accepts prompts with optional file uploads and processes them through an AI model (configured for DeepSeek Reasoner by default).

## Development Commands

### Package Management (UV)
- `uv sync` - Install/update dependencies and sync the environment
- `uv add <package>` - Add a new dependency
- `uv remove <package>` - Remove a dependency
- `uv run <command>` - Run commands in the project environment

### Code Quality
- `uv run ruff check` - Run linting with Ruff
- `uv run ruff format` - Format code with Ruff
- `uv run ruff check --fix` - Auto-fix linting issues

### Running the Application
- `uv run python src/main.py` - Run the development server
- `uv run uvicorn src.main:app --reload` - Run with uvicorn directly

### Testing
No specific test framework is currently configured. When adding tests, update this section.

## Architecture

### Core Structure
- **FastAPI Application**: Async web service with CORS middleware and request logging
- **Dependency Injection**: Services are injected through FastAPI's dependency system
- **Configuration Management**: Centralized settings using Pydantic Settings with environment variables

### Key Components

**Services Layer**:
- `AIService` (src/services/ai_service.py) - Handles OpenAI-compatible API communication with async client
- `FileProcessorService` (src/services/file_processor.py) - Processes uploaded files concurrently using asyncio.gather

**Configuration** (src/core/config.py):
- Environment-based configuration using Pydantic Settings
- Supports multiple AI models through BASE_URL/API_KEY configuration
- File processing limits and allowed extensions are configurable

**API Routes** (src/routes/process.py):
- `/process` - Main endpoint accepting multipart form data (prompt + optional files)
- `/health` - Health check endpoint
- `/` - Root endpoint with service information

**Data Models** (src/models/schemas.py):
- Pydantic models for request/response validation
- `OutputFormat` enum supporting JSON and TEXT responses

### Key Features
- **Concurrent File Processing**: Multiple files are processed simultaneously using asyncio
- **Flexible Output Formats**: Supports both JSON and plain text responses
- **Comprehensive Error Handling**: HTTP exceptions with detailed error messages
- **File Type Validation**: Configurable allowed extensions and size limits
- **Request Logging**: Automatic logging of request processing times

### Environment Variables
Required:
- `BASE_URL` - AI service endpoint
- `API_KEY` - AI service authentication key

Optional (with defaults):
- `AI_MODEL` - Model name (default: deepseek-reasoner)
- `MAX_FILE_SIZE_MB` - File size limit (default: 10)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `LOG_LEVEL` - Logging level (default: info)

## Code Style
- Uses Ruff for linting and formatting
- Single quotes for strings
- Python 3.13+ type hints
- Async/await patterns throughout