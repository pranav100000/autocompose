# AutoCompose

A FastAPI server that uses the Model Context Protocol (MCP) to generate MIDI music from text descriptions.

## Overview

AutoCompose allows users to create music by simply describing what they want in natural language. The system uses Claude 3.7 Sonnet (or other LLMs) to interpret the description and generate appropriate MIDI files using selected instruments from a soundfont library.

## Features

- Text-to-Music generation using Claude 3.7 Sonnet LLM
- Outputs separate MIDI files for each instrument, named after their corresponding soundfont
- MCP implementation for structured LLM-to-MIDI conversion
- Instrument selection from over 1200 soundfonts for high-quality instrument sounds
- MIDI file generation with mido
- REST API for integration into other applications

## Architecture

The application is structured as follows:

- **API Layer**: FastAPI endpoints for music generation and file retrieval
- **MCP Layer**: Model Context Protocol implementation with tools for music generation
- **MIDI Service**: Conversion of musical descriptions to MIDI files
- **Soundfont Management**: Selection and usage of instruments from soundfont libraries

## Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) for package management

### Installation

1. Clone the repository
2. Install dependencies:
```bash
uv pip install -r requirements.txt
```

### Setting up Environment Variables

Create a `.env` file in the root directory with the following variables:

```
ANTHROPIC_API_KEY=your_api_key_here
MCP_MODEL_NAME=claude-3-7-sonnet-20240229
MCP_LOG_LEVEL=INFO
```

### Running the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### Generate Music

```
POST /api/generate/music
```

Request body:
```json
{
  "description": "An upbeat jazz tune with piano, bass and drums",
  "key": "C major",
  "tempo": 120,
  "duration": 60
}
```

### Download Generated MIDI

```
GET /api/download/{composition_dir}/{filename}
```

### Get Composition Details

```
GET /api/composition/{composition_dir}
```

### List Soundfonts

```
GET /api/soundfonts?query=optional_search_term
```

## Development

The codebase follows the code style guidelines in `CLAUDE.md`. Use the provided linting and testing commands for development:

```bash
# Format code
black app tests

# Lint code
ruff check app tests

# Type check
mypy app tests

# Run tests
pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.# autocompose
