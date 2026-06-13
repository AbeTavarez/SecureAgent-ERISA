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
1. Prerequisites
    - Python 3.10 or higher

    - Docker and Docker Compose

2. Installation & Environment Setup
Clone the repository and configure your runtime keys:

```bash
git clone https://github.com/AbeTavarez/SecureAgent-ERISA.git
cd secureagent-erisa

### Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt

# Populate environment variables
cp .env.example .env
```

Ensure your .env contains valid configurations for your LLM provider and telemetry dashboards:
```bash
OPENAI_API_KEY=sk-...
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST="http://localhost:3000"
VECTOR_DB_URL="http://localhost:8000"
```

Boot up the FastAPI gateway interface:
```bash
uvicorn src.main:app --reload --port 8000
```

## 🛠️ Key Design Patterns
State Safety & Compliance
By declaring an immutable-style list update topology using Annotated[List[Any], add_messages], historical communication integrity is retained.

```python
class AgentState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    current_triage: Optional[TriageDecision]
    retrieved_context: List[Dict[str, Any]]
    metadata: Dict[str, Any]
```


## Resources and Links

**Testing**
 - https://fastapi.tiangolo.com/tutorial/testing/