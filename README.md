# SecureAgent-ERISA

An enterprise-grade, observable AI Agent Assist system designed to triage, research, and execute compliance workflows for retirement plan administration. This system orchestrates a multi-step execution loop over complex, dense IRS regulations and integrates safely with core corporate CRM infrastructure.

## 🏗️ Architectural Overview
SecureAgent-ERISA is built around a decoupled architecture that separates data ingestion, stateful orchestration, and client delivery.

                +---------------------------------------+
                |        Enterprise UI / Client         |
                +-------------------+-------------------+
                                    | (Streaming API)
                                    v
                +-------------------+-------------------+
                |          FastAPI Gateway              |
                +-------------------+-------------------+
                                    |
                                    v
                +-------------------+-------------------+
                |       LangGraph Orchestrator          |
                +---+---------------+---------------+---+
                    |               |               |
                    v               v               v
    +----------+----------+ +--+---------------+--+ +----------+----------+
    | Deterministic Triage| | Parent-Child RAG     | |  Mock CRM System   |
    | (Structured Output) | | (ChromaDB/pgvector)  | |  (Salesforce API)  |
    +---------------------+ +----------------------+ +---------------------+
                                    ^
                                    | (Out-of-band Ingestion)
                        +----------+----------+
                        | 2026 IRS Regulations|
                        +---------------------+

## Core Components
 1. Hierarchical RAG Pipeline: Resolves accuracy challenges in dense financial regulations using a parent-child chunking approach. Smaller, semantic child chunks point to comprehensive parent structural blocks (e.g., full restriction tables), preserving absolute regulatory context.

 2. Deterministic Triage Layer: Eliminates unpredictable agent behavior. An LLM maps inputs to strict Pydantic states, allowing a localized Python router to execute tools rather than delegating total loop freedom to the model.

 3. Enterprise CRM Gateway: A safe mock API representing transactional CRM systems (e.g., Salesforce) to read client records and append verified compliance/audit trails.

 4. Observability & Telemetry: Out-of-the-box integration with Langfuse to audit prompt chains, token consumption, intermediate agent thoughts, and tool execution latency.


## 🚀 Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package and project manager)
- Python 3.12+ (see `.python-version`)
- Docker and Docker Compose (optional, for Langfuse, ChromaDB, and other services)

### Project layout

```text
SecureAgent/
  pyproject.toml          # dependencies, packaging, and CLI entry point
  src/
    secureagent/          # installable Python package
      cli/                # Typer CLI (serve, chat)
      main.py             # FastAPI app
      api/                # HTTP routes
      services/           # CRM business logic
      agents/             # LangGraph orchestrator
      tools/              # LangChain tools used by the agent
      schemas/            # Pydantic models
    tests/
```

Dependencies and the `secureagent` package are defined in `pyproject.toml`. Running `uv sync` creates a local `.venv` and installs the project in editable mode — no manual `PYTHONPATH` or `requirements.txt` needed.

After changing dependencies or `[project.scripts]` in `pyproject.toml`, run `uv sync` again so the environment and console commands stay in sync. Code-only changes do not require a sync.

### Installation

Clone the repository, install dependencies, and configure environment variables:

```bash
git clone https://github.com/AbeTavarez/SecureAgent-ERISA.git
cd SecureAgent-ERISA

uv sync

cp .env.example .env
```

Ensure your `.env` contains valid configurations for your LLM provider and telemetry dashboards:

```bash
GROQ_API_KEY=gsk_...
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST="http://localhost:3000"
VECTOR_DB_URL="http://localhost:8000"
```

### CLI

The project exposes a single entry point with subcommands:

```bash
uv run secureagent --help
```

#### Serve the CRM API

Start the FastAPI gateway:

```bash
uv run secureagent serve
```

Options:

```bash
uv run secureagent serve --host 127.0.0.1 --port 8000 --reload
```

The API is available at `http://127.0.0.1:8000/api/v1`.

You can also run uvicorn directly:

```bash
uv run uvicorn secureagent.main:app --reload --port 8000
```

#### Run the agent

One-shot prompt (stateless — each invocation uses a fresh session unless you pass `--thread-id`):

```bash
uv run secureagent chat -p "Check CRM health status"
```

Interactive session (multi-turn memory within the same CLI process):

```bash
uv run secureagent chat
```

On startup, the CLI prints a **session thread ID**. All turns in that session share conversation history via a LangGraph in-memory checkpointer. Memory is process-scoped: exiting the CLI clears it.

**Interactive commands**

| Command | Description |
|---------|-------------|
| `/help` | List available chat commands |
| `/clear` or `/reset` | Start a new conversation (assigns a new session thread) |

**Options**

```bash
# Show agent metadata after each reply
uv run secureagent chat -m

# Resume or continue a specific conversation thread
uv run secureagent chat -t "your-thread-id"

# One-shot with a named thread (history accumulates if the same ID is reused)
uv run secureagent chat -p "Look up client 95-1234567" -t "audit-session-1"
```

**Example multi-turn flow**

```bash
uv run secureagent chat
# Session Thread: 3f2a1b4c-...
# You: Look up client with tax ID 95-1234567
# You: What tax ID did I just ask about?
# SecureAgent: (should recall the prior turn)
# You: /clear
# Conversation cleared. New session: 9d8e7f6a-...
```

### Run tests

```bash
uv run pytest
```

## 🛠️ Key Design Patterns

### Conversation memory

Interactive chat persists state between turns using LangGraph's `InMemorySaver` checkpointer. Each session is keyed by a `thread_id` passed in invoke config; the CLI generates one per interactive session (or accepts `-t` / `--thread-id`). One-shot `-p` runs default to a new thread unless a thread ID is supplied.

### State safety & compliance

By declaring an immutable-style list update topology using `Annotated[List[Any], add_messages]`, historical communication integrity is retained within and across turns.

```python
class AgentState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    current_triage: Optional[TriageDecision]
    retrieved_context: List[Dict[str, Any]]
    metadata: Dict[str, Any]
```


## Resources and Links

- [uv project guide](https://docs.astral.sh/uv/guides/projects/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)