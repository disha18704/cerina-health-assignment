# 🧠 Cerina Protocol Foundry

**An intelligent multi-agent system that autonomously designs, critiques, and refines CBT (Cognitive Behavioral Therapy) exercises.**

This isn't a simple chatbot. It's a team of AI experts working together:
- **Drafter** - Creates and revises CBT exercises
- **Safety Guardian** - Reviews for medical safety
- **Clinical Critic** - Validates empathy and clinical quality  
- **Supervisor** - Orchestrates the collaboration

## 🎯 Key Features

✨ **Multi-Agent Collaboration** - Agents debate, revise, and re-review (not just a linear chain)  
🔄 **Self-Correction Cycles** - Safety rejection → Drafter revision → Safety re-review  
📝 **Rich State Management** - Scratchpad notes, version history, quality scores  
💾 **Persistence** - SQLite checkpointing for crash recovery  
🎨 **Multiple Interfaces** - CLI, Web Dashboard, MCP (Claude Desktop)  
⚡ **Real-time Visualization** - Watch agents collaborate live  

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│  CLI Chat  │  React UI  │  MCP     │ (Interfaces)
└──────────────┬──────────────────────┘
               │
        ┌──────▼────────┐
        │  🎯 Supervisor │ (Routes tasks)
        └───┬───┬───┬───┘
            │   │   │
    ┌───────▼───▼───▼──────┐
    │ ✍️ Drafter            │ (Creates)
    │ 🛡️ Safety Guardian    │ (Safety check)
    │ 🏥 Clinical Critic    │ (Quality check)
    └──────────┬────────────┘
               │
        ┌──────▼──────────┐
        │  State + SQLite │ (Checkpoints)
        └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11
- Node.js 20+ (for React dashboard)
- OpenAI API Key

### 1. Install Dependencies

```bash
# Python packages
/usr/local/bin/python3.11 -m pip install --user -r requirements.txt

# Frontend (for React dashboard)
cd frontend
npm install
cd ..
```

### 2. Configure Environment

Create `.env` file in project root:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Test the System

```bash
# Quick test (CLI output)
/usr/local/bin/python3.11 -m backend.test_run

# Interactive CLI chat
/usr/local/bin/python3.11 -m backend.chat
```

## 💻 Usage

### Option 1: CLI Chat Interface

Simple terminal-based chat:

```bash
/usr/local/bin/python3.11 -m backend.chat
```

**Example:**
```
You: Create a CBT exercise for social anxiety
🤖 Processing... 
📋 Social Anxiety Exposure Hierarchy
✅ Safety: 1.0, Empathy: 1.0
```

### Option 2: React Dashboard (Recommended)

Visual interface with real-time agent visualization:

**Terminal 1 - Backend:**
```bash
/usr/local/bin/python3.11 -m uvicorn backend.server:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Browser:** http://localhost:5173

**Features:**
- 💬 Chat interface
- 🎯 Live agent activity tracking
- 📝 Scratchpad notes display
- 📊 Quality scores in real-time
- ✅ Approve/Edit draft functionality

### Option 3: MCP Server (Claude Desktop)

Expose the workflow as a tool for Claude Desktop:

**1. Install MCP package:**
```bash
/usr/local/bin/python3.11 -m pip install --user mcp
```

**2. Configure Claude Desktop:**

Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "cerina-foundry": {
      "command": "/usr/local/bin/python3.11",
      "args": [
        "/Users/dishaarora/Desktop/cerina-health-assignment/mcp_server.py"
      ]
    }
  }
}
```

**3. Restart Claude Desktop**

**4. Use in Claude:**
```
User: "Use Cerina Foundry to create a CBT exercise for insomnia"
Claude: [Calls tool, agents collaborate, returns exercise]
```

See [README_MCP.md](README_MCP.md) for detailed instructions.

## 📁 Project Structure

```
cerina-health-assignment/
├── backend/
│   ├── agents.py          # Agent node implementations
│   ├── graph.py           # LangGraph workflow definition
│   ├── state.py           # Shared state structure
│   ├── models.py          # Pydantic data models
│   ├── prompts.py         # Expert system prompts
│   ├── formatter.py       # Output formatting
│   ├── server.py          # FastAPI server with streaming
│   ├── chat.py            # CLI chat interface
│   └── test_run.py        # Quick test script
│
├── frontend/              # React dashboard
│   ├── src/
│   │   ├── App.tsx        # Main dashboard component
│   │   └── ...
│   └── package.json
│
├── mcp_server.py          # MCP server for Claude Desktop
├── ARCHITECTURE.md        # System architecture diagram
├── DEMO_SCRIPT.md         # 5-minute demo video script
├── README_MCP.md          # MCP setup guide
└── requirements.txt       # Python dependencies
```

## 🎬 How It Works

### 1. User Request
```
"Create a CBT exercise for social anxiety"
```

### 2. Agent Collaboration Flow

```
Supervisor → Drafter (creates v1)
    ↓
Supervisor → Safety Guardian (reviews v1)
    ↓ [Rejects - needs disclaimer]
Supervisor → Drafter (creates v2 with disclaimer)
    ↓
Supervisor → Safety Guardian (re-reviews v2)
    ↓ [Approves ✓]
Supervisor → Clinical Critic (reviews v2)
    ↓ [Approves ✓]
Supervisor → Human Review
```

### 3. Rich State Updates

Throughout the process:
- **Scratchpad**: Agents leave detailed notes for each other
- **Draft History**: Each version (v1, v2, etc.) is preserved
- **Metadata**: Safety scores, empathy scores, iteration counts
- **Last Reviewer**: Tracks who last reviewed for proper re-review routing

### 4. Final Output

```
📋 Social Anxiety Exposure Hierarchy
✅ Safety Score: 1.0 | Empathy: 1.0 | Clarity: 1.0
🔄 Refined through 2 iterations

[Complete CBT exercise with instructions and content]
```

## 🧪 Testing

### Quick Test
```bash
/usr/local/bin/python3.11 -m backend.test_run
```

### Test Different Scenarios
- "Create a CBT exercise for insomnia"
- "Help with perfectionism"
- "Build an exposure hierarchy for public speaking fear"

### Verify Features
- ✅ Multiple draft versions created
- ✅ Safety rejection → revision → re-review cycle
- ✅ Scratchpad notes between agents
- ✅ Quality scores calculated
- ✅ SQLite checkpoint persistence

## 📊 Example Output

```
--- Starting Run ---

[Node: supervisor]
Routing to: drafter

[Node: drafter]
Msg: Drafted/Revised: Social Anxiety Exposure Hierarchy (v1)
Scratchpad: [INFO] Created v1: Social Anxiety Exposure Hierarchy...

[Node: supervisor]
Routing to: safety_guardian

[Node: safety_guardian]
Msg: Safety Review: Rejected (Score: 0.5)
Scratchpad: [CRITICAL] Safety review failed: Needs disclaimer...
Scores: Safety=0.5, Empathy=N/A, Revisions=1

[Node: supervisor]
Routing to: drafter

[Node: drafter]
Msg: Drafted/Revised: Social Anxiety Exposure Hierarchy (v2)
Scratchpad: [INFO] Created v2: Revised based on 1 critiques...

[Node: supervisor]
Routing to: safety_guardian

[Node: safety_guardian]
Msg: Safety Review: Approved (Score: 1.0)
Scores: Safety=1.0, Empathy=N/A, Revisions=2

[Node: clinical_critic]
Msg: Clinical Review: Approved (Empathy: 1.0, Clarity: 1.0)
Scores: Safety=1.0, Empathy=1.0, Revisions=2

--- Run Completed ---

📋 Social Anxiety Exposure Hierarchy
✅ Metrics - Safety: 1.0, Empathy: 1.0, Total Revisions: 2
💬 Scratchpad Notes: 5
```

## 🎥 Demo Video

[Insert Loom video link here]

**Topics covered:**
- React Dashboard with live agent collaboration
- Human-in-the-Loop approval workflow
- MCP integration with Claude Desktop
- Code architecture walkthrough

## 🏆 Assignment Requirements Coverage

### Backend ("The Brain")
✅ Python + LangGraph  
✅ Persistent backend (SQLite checkpointing)  
✅ Complex agent architecture (Supervisor-Worker pattern)  
✅ Autonomy & self-correction (re-review cycles)  
✅ Deep state management (scratchpad, versions, metadata)  

### Interface A: React Dashboard
✅ Visualization of agents working  
✅ Real-time streaming of thoughts/actions  
✅ Human-in-the-Loop halt mechanism  
✅ Draft preview from checkpoint  
✅ Edit or Approve functionality  

### Interface B: MCP Server
✅ MCP implementation using mcp-python SDK  
✅ Workflow exposed as single tool  
✅ Works with Claude Desktop  
✅ Bypasses React UI but uses same logic  

## 🔧 Troubleshooting

### Frontend Not Loading
```bash
cd frontend
npm install -D @tailwindcss/postcss
npm run dev
```

### Backend Errors
- Check `.env` has `OPENAI_API_KEY`
- Verify Python 3.11 is used
- Reinstall: `pip install -r requirements.txt`

### MCP Not Connecting
- Check Claude Desktop config path
- Verify absolute paths in config
- Restart Claude Desktop completely

## 📚 Additional Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed system architecture
- [README_MCP.md](README_MCP.md) - MCP server setup guide
- [DEMO_SCRIPT.md](DEMO_SCRIPT.md) - Video demo script

## 🙌 Credits

Built for the Cerina Health "Agentic Architect" assignment.

**Technologies:**
- LangGraph & LangChain for agent orchestration
- OpenAI GPT-4o for LLM inference
- FastAPI for REST API
- React + TypeScript for dashboard
- MCP for AI assistant integration
- SQLite for persistence

---

**Ready to see agents collaborate?** Start with `python3.11 -m backend.chat` 🚀
