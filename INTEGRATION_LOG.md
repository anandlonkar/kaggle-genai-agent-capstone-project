# PowerToChoose MCP Integration - Planning Log

**Date Started:** December 28, 2025  
**Status:** ✅ **INTEGRATION COMPLETE AND TESTED**  
**Goal:** Replace GoogleSearchTool with PowerToChoose MCP Server

---

## ✅ SUCCESS SUMMARY

**Integration Status:** 🎉 **WORKING END-TO-END**

**Test Results (December 28, 2025):**
- MCP server deployed as HTTP/SSE server on port 8080
- Notebook connected successfully via SSE transport
- Real electricity plan data retrieved from SQLite database (163 plans)
- Multi-agent A2A workflow executed successfully:
  - Power Plan Finder Agent ➝ Search Agent ➝ PowerToChoose MCP ➝ Database
- Meter analysis performed (SM12345678901234 household, 164.4 kWh/month usage)
- Plan recommendations generated with detailed cost calculations
- Total execution time: 44 seconds

**Test Query:**
> "I need help finding the best electricity plan for my home in ZIP code 75074. Please analyze my smart meter data and recommend specific plans that match my usage pattern."

**Plans Recommended:**
1. **Sustainable Days Bundle - 3** (JUST ENERGY) - $24.04/month
2. **Bright Nights 6** (CHARIOT ENERGY) - $28.39/month

**Production Deployment Pattern Confirmed:**
```bash
# Pre-start MCP server in terminal:
c:\code\powertochoose-mcp\.venv\Scripts\python.exe -m powertochoose_mcp.server --http 8080

# Notebook connects via SSE:
McpToolset(connection_params=SseConnectionParams(url="http://localhost:8080/sse"))
```

---

## 🔍 Code Analysis Complete

### Current Architecture (from powerplanfinder.ipynb)

**Cell #VSC-b590c9f0 - Search Agent**
```python
from google.adk.tools.google_search_tool import GoogleSearchTool

search_agent = LlmAgent(
    model=Gemini(...),
    tools=[GoogleSearchTool()],  # ← INTEGRATION POINT
    instruction="""... searches PowerToChoose.org and provider websites ..."""
)
```

**Cell #VSC-9aa49b27 - Power Plan Finder Agent**
```python
from google.adk.tools.agent_tool import AgentTool

search_agent_tool = AgentTool(search_agent)  # A2A communication

power_plan_agent = LlmAgent(
    model=Gemini(...),
    tools=[meter_tool, search_agent_tool],  # Uses Search Agent via A2A
    instruction="""... delegates to search_agent for plan searches ..."""
)
```

**Cell #VSC-6c35c4c4 - MCP Imports Already Present!**
```python
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
```
✅ **Key Discovery:** MCP infrastructure is already imported!

---

## 🎯 Integration Points Identified

### Option A: Replace GoogleSearchTool (Minimal Change)
```python
# Replace this:
tools=[GoogleSearchTool()]

# With this:
tools=[McpToolset(...)]  # PowerToChoose MCP tools
```

**Pros:**
- Preserves A2A architecture
- Search Agent still acts as specialist
- Minimal changes to Power Plan Agent

**Cons:**
- Extra layer (Orchestrator → Search Agent → MCP Tool)
- Search Agent instructions need rewrite

### Option B: Direct MCP Integration (Simplified)
```python
# Power Plan Finder Agent directly uses MCP tools
power_plan_agent = LlmAgent(
    tools=[meter_tool, mcp_powertochoose_toolset]  # No search_agent_tool
)
```

**Pros:**
- Simpler architecture (Orchestrator → MCP Tool)
- One fewer agent to manage
- More efficient (fewer LLM calls)

**Cons:**
- Removes A2A demonstration (was part of capstone design)
- Loses Search Agent specialization

---

## 🛠️ PowerToChoose MCP Server Details

**Location:** `c:\code\powertochoose-mcp\`

**MCP Tools Available:**
1. **search_plans** (ZIP code + optional classification filters)
   - Input: `{"zip_code": "75035", "classifications": ["green", "ev"]}`
   - Output: List of plans with full details (provider, rates, terms, etc.)

2. **calculate_plan_cost** (detailed cost breakdown)
   - Input: `{"plan_id": "abc123"}`
   - Output: Costs at 500/1000/2000 kWh tiers with breakdowns

**Connection Method:**
```python
StdioConnectionParams(
    command="python",
    args=["-m", "powertochoose_mcp"],
    env={"DATABASE_PATH": "c:\\code\\powertochoose-mcp\\data\\powertochoose.db"}
)
```

**Data Available:** 163 real plans from ZIP 75074 (can expand to 7 North Texas ZIP codes)

---

## 📋 Clarification Questions Log

### Question #1: Architecture Choice ✅ ANSWERED
**Question:** Should we preserve the A2A pattern (keep Search Agent as intermediary) or simplify by giving Power Plan Finder Agent direct access to MCP tools?

**Context:**
- Original capstone demonstrates A2A communication (Orchestrator → Search Agent → GoogleSearch)
- Simplification would be Orchestrator → MCP Tool (more efficient, fewer hops)
- Preserving A2A maintains capstone's architectural demonstration value

**User Response:** Option A - Preserve A2A architecture

**Decision:** Keep Search Agent as intermediary between Power Plan Finder and MCP tools

---

### Question #2: ZIP Code Handling ✅ ANSWERED
**Question:** How should we determine the ZIP code for plan searches?

**Options:**
- A) Extract from meter data filename/metadata (if available)
- B) Ask user to provide ZIP code explicitly
- C) Use meter analysis to infer location, then ask for confirmation
- D) Default to 75035 (Frisco) for demo, make it configurable

**User Response:** Option B - Ask user explicitly

**Decision:** User provides ZIP code in their query (e.g., "Find me plans in ZIP 75035"). Future enhancement: extract from smart meter data when available.

---

### Question #3: Smart Meter MCP Server ✅ ANSWERED
**Question:** The architecture document mentions a Smart Meter MCP server. Should we:

**Options:**
- A) Keep current setup (meter data from GitHub CSVs)
- B) Build Smart Meter MCP server in future phase
- C) Both (PowerToChoose now, Smart Meter later)

**Current:** Meter data from `get_meter_readings()` function fetching GitHub CSVs

**User Response:** Option A - Keep current approach

**Decision:** Maintain GitHub CSV fetching for meter data. Focus integration effort on PowerToChoose MCP only.

---

## 📝 Implementation Plan (FINALIZED - Ready to Execute)

### Phase 1: MCP Connection Setup ✅ COMPLETE
**Cell modified:** #VSC-b590c9f0 (Search Agent creation)

**Changes:**
1. Create `StdioConnectionParams` for PowerToChoose MCP server
2. Create `McpToolset` wrapping the MCP connection
3. Replace `GoogleSearchTool()` with the MCP toolset

**Code:**
```python
# PowerToChoose MCP Connection
powertochoose_params = StdioConnectionParams(
    command="python",
    args=["-m", "powertochoose_mcp"],
    env={"DATABASE_PATH": "c:\\code\\powertochoose-mcp\\data\\powertochoose.db"}
)

powertochoose_toolset = McpToolset(
    server_params=StdioServerParameters(
        command=powertochoose_params.command,
        args=powertochoose_params.args,
        env=powertochoose_params.env
    )
)

# Updated Search Agent
search_agent = LlmAgent(
    model=Gemini(model_name="gemini-2.0-flash-exp", http_options=retry_config),
    name="search_agent",
    tools=[powertochoose_toolset],  # ← MCP tools instead of GoogleSearchTool
    instruction="""... updated instructions ..."""
)
```

### Phase 2: Search Agent Instructions Update ✅ COMPLETE
**Cell modified:** #VSC-b590c9f0 + #VSC-b0c606f8 (markdown documentation)

**New instructions:**
```python
instruction="""You are a research assistant specialized in finding electricity plans from the PowerToChoose database for Texas.

You have access to two MCP tools:
1. search_plans: Search for electricity plans by ZIP code with optional filters
2. calculate_plan_cost: Get detailed cost breakdown for a specific plan

When asked to find electricity plans:

1. EXTRACT ZIP CODE from user query (required!)
   - User will provide ZIP code (e.g., "75035", "75074")
   - If missing, ask: "What ZIP code should I search in?"

2. IDENTIFY FILTERS from usage analysis:
   - If "EV" or "electric vehicle" mentioned → filter: ["ev"]
   - If "renewable" or "green" mentioned → filter: ["green"]
   - If "time-of-use" or "peak/off-peak" mentioned → filter: ["time_of_use"]
   - Multiple filters allowed: ["green", "ev"]

3. CALL search_plans tool:
   Parameters: {"zip_code": "75035", "classifications": ["green"]}
   Returns: List of plans with provider, name, rates, terms, features

4. FOR EACH RECOMMENDED PLAN, call calculate_plan_cost:
   Parameters: {"plan_id": "plan_abc123"}
   Returns: Detailed costs at 500, 1000, 2000 kWh tiers

5. RETURN structured results:
   PLAN 1: [Plan Name]
   Provider: [Name]
   Plan ID: [ID for cost calculations]
   Rate Structure: [From search_plans]
   Estimated Costs:
     - 500 kWh/month: $[amount] (from calculate_plan_cost)
     - 1000 kWh/month: $[amount]
     - 2000 kWh/month: $[amount]
   Contract Term: [Length]
   Features: [Green %, EV-friendly, etc.]
   
Always provide plan_id so the orchestrator can do additional cost calculations if needed."""
)
```

### Phase 3: Power Plan Finder Instructions Update ✅ COMPLETE
**Cell modified:** #VSC-9aa49b27 + #VSC-b59f0bf6 (markdown documentation)

**Update workflow in instructions:**
```python
instruction="""You are an expert energy advisor helping users find the best electricity plan based on their actual usage data.

WORKFLOW:
1. Use get_meter_readings to analyze the customer's smart meter data
   - Review overall consumption statistics
   - Examine time-of-day patterns (4-hour intervals)
   - Check weekend vs weekday differences
   - Assess seasonal trends

2. Identify the optimal plan TYPE based on usage characteristics:
   - TIME-OF-USE: High peak-to-off-peak ratio (>2x), EV charging, flexible schedule
   - FIXED-RATE: Consistent usage throughout day (<1.5x ratio), predictable patterns
   - SEASONAL/VARIABLE: High seasonal variation (>2x), fluctuating needs
   - EV CHARGING PLANS: Overnight charging patterns (>20+ kWh in 00:00-04:00 slot)
   - GREEN/RENEWABLE: Any household wanting renewable energy

3. ASK USER FOR ZIP CODE if not provided:
   "To search for electricity plans, I need your ZIP code. What ZIP code should I search in?"

4. Use search_agent to find specific plans:
   - Request format: "Search for [plan type] electricity plans in ZIP [code]"
   - If user wants green energy: "Search for green electricity plans in ZIP 75035"
   - If EV owner: "Search for EV electricity plans in ZIP 75035"
   - Can combine: "Search for green EV electricity plans in ZIP 75035"

5. Analyze results and calculate customer-specific costs:
   - Search agent returns costs at 500/1000/2000 kWh tiers
   - Use customer's actual average daily usage to interpolate
   - Formula: monthly_cost = (daily_avg_kwh * 30) → find closest tier
   - Example: If customer uses 18.7 kWh/day = 561 kWh/month
     → Use 500 kWh tier cost + interpolate to 1000 kWh tier

6. Provide DETAILED RECOMMENDATIONS (2-3 plans):
   - **Plan Name & Provider**
   - **Rate Structure** (from search results)
   - **Your Monthly Cost**: $[calculated amount]
     (Show: "[daily avg] kWh/day × 30 = [monthly] kWh → $[cost]")
   - **Why It Fits**: Match to usage patterns
     (e.g., "Your peak usage at 20:00 aligns with free night hours")
   - **Contract Terms**: Length, cancellation fees
   - **Annual Savings**: Compare to baseline rate
   - **Features**: Green %, EV charging, time-of-use details

IMPORTANT NOTES:
- User must provide ZIP code (ask if missing)
- Reference specific usage data in recommendations
- Use actual plan costs from search_agent (not estimates)
- Show calculation steps for transparency"""
)
```

### Phase 4: Test Query Update ✅ COMPLETE
**Cell modified:** #VSC-33e2528d (Test execution)

**Updated query includes ZIP code:**
```python
"I need help finding the best electricity plan for my home in ZIP code 75074. 
Please analyze my smart meter data and recommend specific plans that match my usage pattern."
```

### Phase 5: Testing Checklist ⚠️ BLOCKED - Jupyter Limitation
**Issue:** Cannot use stdio transport from Jupyter notebooks

**Root Cause:** Jupyter notebooks don't support file descriptors (`fileno`) which MCP's stdio transport requires for subprocess communication.

**Error:** `UnsupportedOperation: fileno` when trying to start MCP server subprocess

**Solutions:**
1. **Option A - HTTP/SSE MCP Server** (Recommended for notebook environment)
   - Deploy PowerToChoose MCP as HTTP server using Streamable HTTP
   - Update connection to use `SseConnectionParams` instead of `StdioConnectionParams`
   - Allows testing directly in notebook

2. **Option B - External MCP Server** (Quick test)
   - Run MCP server in separate terminal before notebook
   - Requires server to be externally managed
   - Not ideal for notebook demos

3. **Option C - Python Script** (Works perfectly)
   - Run complete test outside notebook environment
   - Use the async agent creation pattern from documentation
   - No stdio limitations

**Status:** Integration code is complete and correct, but requires deployment pattern change for notebook compatibility

### Phase 6: Documentation Updates
- [ ] Update architecture diagram in markdown cell
- [ ] Add MCP setup instructions before code
- [ ] Document new dependencies (none - already imported!)
- [ ] Add troubleshooting section

---

## 🚧 Current Blockers

**ALL RESOLVED** ✅

- ✅ Notebook code reviewed
- ✅ Integration points identified  
- ✅ Architecture decision made (preserve A2A)
- ✅ ZIP code handling decided (ask user explicitly)
- ✅ Meter data approach decided (keep GitHub CSVs)

**READY TO IMPLEMENT** 🚀

---

## ✅ Success Criteria

### Completed ✅
- [x] PowerToChoose MCP server code integrated into notebook
- [x] Search Agent configured with McpToolset (correct API)
- [x] Power Plan Finder Agent instructions updated for MCP workflow
- [x] Agent-to-Agent (A2A) architecture preserved
- [x] All agent creation cells execute successfully
- [x] Meter analysis tool working (tested: SMKIDS household)
- [x] ZIP code handling implemented (user provides in query)
- [x] No code changes outside kaggle-genai-agent-capstone-project directory
- [x] Documentation updated with MCP integration details

### Blocked by Jupyter Limitation ⚠️
- [ ] MCP server connection (stdio not supported in notebooks)
- [ ] End-to-end test with real electricity plan data
- [ ] Cost calculations using actual plan data
- [ ] Recommendations with PowerToChoose database

### Next Steps to Complete Integration
1. **Deploy PowerToChoose MCP as HTTP server** (see Phase 5 solutions)
2. **Update connection_params** to use SseConnectionParams
3. **Test complete workflow** with all 5 household types

---

## 🔍 Key Insights

1. **MCP Already Imported:** Capstone has MCP infrastructure ready (McpToolset, StdioConnectionParams)
2. **Clean A2A Pattern:** Search Agent is well-defined specialist - could map cleanly to MCP tools
3. **Structured Data Flow:** Power Plan Finder expects structured plan data - matches MCP output format
4. **ZIP Code Challenge:** Current implementation doesn't explicitly handle ZIP codes - need to add this
5. **Cost Calculation Alignment:** Capstone estimates costs, MCP has exact calculator - perfect match

---

**Next Action:** Wait for user response to Question #1 (Architecture Choice)
