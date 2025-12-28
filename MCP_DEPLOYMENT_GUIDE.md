# PowerToChoose MCP Server - Production Deployment Guide

**Last Updated:** December 28, 2025  
**Status:** Production-Ready

---

## Overview

This guide explains how to deploy and run the PowerToChoose MCP server in production mode, enabling the Jupyter notebook to connect via HTTP/SSE transport for reliable, long-running sessions.

---

## Prerequisites

- PowerToChoose MCP server installed at `c:\code\powertochoose-mcp\`
- Virtual environment configured with required packages
- SQLite database populated with electricity plan data (163+ plans)
- Port 8080 available on localhost

---

## Quick Start

### 1. Start the MCP Server

Open a terminal and run:

```powershell
# Navigate to MCP server directory
cd c:\code\powertochoose-mcp

# Start HTTP/SSE server on port 8080
.\.venv\Scripts\python.exe -m powertochoose_mcp.server --http 8080
```

**Expected Output:**
```
PowerToChoose MCP Server starting on http://localhost:8080/sse
Database: powertochoose_mcp.db.operations
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)
```

### 2. Run the Notebook

With the server running in the background terminal:

1. Open `powerplanfinder.ipynb` in Jupyter/VS Code
2. Execute all cells in order
3. The Search Agent (Cell #VSC-b590c9f0) will automatically connect to the MCP server
4. Run test queries to analyze meter data and get plan recommendations

---

## Architecture

### Production Deployment Pattern

```
┌─────────────────────────────────────────────────────────┐
│                    Desktop Machine                       │
│                                                          │
│  ┌─────────────────────┐                                │
│  │ Terminal 1          │                                │
│  │ (Pre-started)       │                                │
│  │                     │                                │
│  │ MCP Server          │                                │
│  │ HTTP/SSE :8080      │                                │
│  │                     │                                │
│  │ [search_plans]      │                                │
│  │ [calculate_cost]    │                                │
│  └──────────┬──────────┘                                │
│             │ HTTP/SSE                                   │
│             ↓                                            │
│  ┌─────────────────────┐                                │
│  │ Terminal 2/Jupyter  │                                │
│  │                     │                                │
│  │ Notebook            │                                │
│  │ - Power Plan Finder │ (Orchestrator)                │
│  │ - Search Agent      │ (A2A ➝ MCP Tools)             │
│  │ - Meter Tool        │ (GitHub CSV)                   │
│  └─────────────────────┘                                │
│                                                          │
│  ┌─────────────────────────────────────────┐            │
│  │ SQLite Database                         │            │
│  │ c:\code\powertochoose-mcp\data\        │            │
│  │   powertochoose.db (163 plans)          │            │
│  └─────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

### Communication Flow

```
User Query
    ↓
Power Plan Finder Agent
    ├─→ get_meter_readings() (FunctionTool)
    │   └─→ Returns usage analysis
    └─→ search_agent (AgentTool - A2A)
        └─→ PowerToChoose MCP (HTTP/SSE)
            ├─→ search_plans(zip_code, classifications)
            └─→ calculate_plan_cost(plan_id)
```

---

## Configuration Details

### MCP Server Settings

**File:** `c:\code\powertochoose-mcp\src\powertochoose_mcp\server.py`

```python
async def main(mode="stdio", port=8080):
    if mode == "http":
        # Create SSE transport
        sse = SseServerTransport("/messages/")
        
        async def handle_sse(request: Request):
            async with sse.connect_sse(...) as streams:
                await app.run(streams[0], streams[1], ...)
            return Response()
        
        starlette_app = Starlette(
            routes=[
                Route("/sse", endpoint=handle_sse, methods=["GET"]),
                Mount("/messages/", app=sse.handle_post_message),
            ]
        )
```

**Endpoints:**
- `GET /sse` - Establishes SSE connection for server-to-client messages
- `POST /messages/?session_id=...` - Client-to-server message channel

### Notebook Connection

**File:** `powerplanfinder.ipynb` Cell #VSC-b590c9f0

```python
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, SseConnectionParams

powertochoose_toolset = McpToolset(
    connection_params=SseConnectionParams(
        url="http://localhost:8080/sse"
    )
)

search_agent = LlmAgent(
    model=Gemini(...),
    tools=[powertochoose_toolset],
    ...
)
```

---

## Verification

### Test MCP Connection

After starting the server, check logs for:

```
INFO:     127.0.0.1:XXXXX - "GET /sse HTTP/1.1" 200 OK
INFO:     127.0.0.1:XXXXX - "POST /messages/?session_id=... HTTP/1.1" 202 Accepted
```

Each POST request indicates an MCP tool call (search_plans or calculate_plan_cost).

### Test Query

```python
# Run in notebook test cell
runner.query("I need help finding the best electricity plan for my home in ZIP code 75074. Please analyze my smart meter data and recommend specific plans that match my usage pattern.")
```

**Expected Results:**
- Meter analysis performed
- ZIP code extracted
- Plans searched with classifications
- Cost calculations for multiple usage tiers
- Detailed recommendations with reasoning

---

## Troubleshooting

### Server Won't Start

**Error:** `Address already in use`

**Solution:** Kill existing process on port 8080
```powershell
Get-Process python | Where-Object { $_.Path -like '*powertochoose-mcp*' } | Stop-Process
```

### Notebook Can't Connect

**Error:** `ConnectionError: Failed to create MCP session`

**Check:**
1. Server is running: `http://localhost:8080/sse` should be accessible
2. No firewall blocking localhost:8080
3. Correct URL in `SseConnectionParams(url=...)`

### No Plans Found

**Error:** Search returns empty results

**Check:**
1. Database has data: `sqlite3 data/powertochoose.db "SELECT COUNT(*) FROM plans;"`
2. ZIP code is supported (75035, 75074, 75024, 75093, 75034, 75033, 75070)
3. Check server logs for SQL errors

---

## Performance

**Tested Performance (Dec 28, 2025):**
- Server startup: <2 seconds
- SSE connection establishment: <100ms
- search_plans query: ~1-2 seconds (163 plans scanned)
- calculate_plan_cost: <500ms per plan
- End-to-end test query: 44 seconds (including LLM inference time)

**Database Size:**
- SQLite file: ~2-5 MB (163 plans with full details)
- WAL mode enabled for safe concurrent access

---

## Maintenance

### Daily Operations

**No maintenance required** - Server runs continuously until stopped.

### Weekly Tasks

1. Check database plan count: Should remain ~163 plans per ZIP code
2. Review server logs for errors: `grep ERROR server.log`
3. Monitor disk usage: `data/` folder size

### Monthly Tasks

1. Update plan data via scraper (not yet implemented in MVP)
2. Archive old request logs if enabled
3. Check for MCP SDK updates: `pip install --upgrade mcp`

---

## Production Enhancements (Future)

### Option 1: Docker Deployment

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
COPY data/ ./data/
CMD ["python", "-m", "powertochoose_mcp.server", "--http", "8080"]
```

**Run:**
```bash
docker build -t powertochoose-mcp .
docker run -p 8080:8080 -v ./data:/app/data powertochoose-mcp
```

### Option 2: Windows Service

Use `nssm` (Non-Sucking Service Manager) to run MCP server as Windows service:

```powershell
nssm install PowerToChooseMCP "c:\code\powertochoose-mcp\.venv\Scripts\python.exe"
nssm set PowerToChooseMCP AppParameters "-m powertochoose_mcp.server --http 8080"
nssm set PowerToChooseMCP AppDirectory "c:\code\powertochoose-mcp"
nssm start PowerToChooseMCP
```

### Option 3: Cloud Deployment

Deploy to Oracle Cloud Free Tier, Google Cloud Run, or Azure Container Instances:

1. Containerize with Docker
2. Push to container registry
3. Deploy with environment variables for database path
4. Update notebook to use public URL instead of localhost

---

## Security Considerations

### Current (Localhost Only)

- ✅ No authentication required (not exposed to internet)
- ✅ No sensitive data (public electricity plan pricing)
- ✅ SQLite file permissions: User-only access

### If Exposing to Internet

- ⚠️ Add authentication (API keys or OAuth)
- ⚠️ Enable HTTPS/TLS encryption
- ⚠️ Rate limiting to prevent abuse
- ⚠️ CORS configuration for web clients

---

## Support

**Repository:** `c:\code\powertochoose-mcp\`  
**Documentation:** See `ARCHITECTURE.md` and `.github\copilot-instructions.md`  
**Issues:** Check INTEGRATION_LOG.md for known issues

---

**Status:** ✅ Production-ready deployment pattern validated December 28, 2025
