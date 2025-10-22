# AI Agent Instructions for The Alignment Management Game

## Project Overview
This is a web-based game focused on alignment management, implemented as a client-server application with a WebSocket-based communication protocol.

## Architecture

### Backend (`/backend`)
- Python-based WebSocket server using `websockets` library
- Main components:
  - `backend.py`: Core WebSocket server and message handling
  - `protocol.py`: Message types and data structures definition
  - `handlers/`: Message-specific handler implementations
  - `assets/`: Game assets storage

### Frontend (`/frontend`)
- Browser-based client using vanilla JavaScript
- Main components:
  - `app.js`: WebSocket client and game initialization
  - `DrawCanvas.js`: Canvas-based rendering
  - `index.html`: Main game interface

## Communication Protocol

### Message Format
```javascript
{
  "messagetype": "<MessageType>",  // Defined in protocol.py
  "numbers": [],                   // Numeric parameters
  "texts": []                      // Text parameters
}
```

### Key Message Types
Defined in `protocol.py`:
- `SHOWSTART`
- `SHOWSTRATEGY`
- `SHOWPROCESS`
- `SHOWCONTROL`
- `SHOWORGANIZATION`
- `SHOWINFORMATION`
- `RUNSIMULATION`

## Development Patterns

### Adding New Features
1. Define message type in `protocol.py`
2. Create handler in `handlers/handle_[MESSAGETYPE].py`
3. Register handler in `handlers/__init__.py`
4. Add frontend handler in `app.js`

### Asset Management
- Backend assets in `backend/assets/`
- Assets are served base64-encoded via WebSocket
- Use `read_asset_b64()` helper in `backend.py`

### Error Handling
- Backend uses structured JSON error responses
- Always include "type": "error" and "error": "<message>"
- Handler errors are caught and logged centrally

### Environment
- Development: `localhost:8765` WebSocket
- Production: `wss://api.thealignmentgame.com/`

## Key Files for Common Tasks
- Protocol changes: `protocol.py`
- New message handlers: `handlers/_template.py`
- UI updates: `frontend/index.html` and `styles.css`
- Canvas rendering: `frontend/DrawCanvas.js`