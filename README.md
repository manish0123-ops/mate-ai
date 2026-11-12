# MATE — Metacognitive Adaptive Thinking Engine

**A personal AI assistant exploring memory, contextual understanding, self-reflection, and adaptive intelligence.**

🌐 **Live Demo:** https://manish0123-ops.github.io/mate-ai/

💻 **Technology:** Python · Flask · Ollama · SQLite · JavaScript

MATE is an experimental, privacy-conscious personal AI assistant designed to explore persistent memory, context-aware interactions, self-reflection, and measurable improvement.

The project uses a locally running language model through Ollama and a Python-based application architecture.

## Vision

The goal of MATE is to develop a personal AI system that can:

- Store and retrieve information using persistent memory.
- Recall relevant context during conversations.
- Reflect on previous tasks and outcomes.
- Track capabilities and improvement goals.
- Evaluate performance using recorded test results.
- Discover potential relationships between stored memories.
- Interact with desktop applications and productivity tools.

## Current Features

### Local AI Integration
- Ollama integration.
- Local language-model communication.
- Flask-based chat API.
- Streamlit-based interface prototype.

### Cognitive Architecture
- Persistent memory using SQLite.
- Semantic memory retrieval using embeddings.
- Memory importance scoring.
- Memory consolidation and lifecycle management.
- Contradiction tracking and resolution.
- Memory relationship discovery.
- Self-model and capability tracking.
- Task reflection and evaluation.
- Learning-plan management.

### Productivity Integrations
- Desktop application control.
- Calendar management.
- Email integration.
- Reminders.

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| AI runtime | Ollama |
| Language model | Llama 3.2 3B |
| Embeddings | nomic-embed-text |
| Backend | Flask |
| Prototype UI | Streamlit |
| Database | SQLite |
| Semantic retrieval | Embeddings and cosine similarity |

## Architecture

```text
             User
              |
              v
        MATE Interface
         Flask / UI
              |
              v
         AI Integration
              |
              v
         Local Ollama
              |
              v
      Cognitive Architecture
              |
    +---------+---------+
    |         |         |
  Memory  Reflection  Evaluation
    |         |         |
    +---------+---------+
              |
              v
          SQLite DB
```

## Getting Started

### Requirements

- Python 3.10 or later.
- Ollama installed.
- Git.
- A compatible local Ollama model.

### Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/mate-ai.git
cd mate-ai
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Download the required Ollama models:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Start Ollama, then run the application:

```bash
python server.py
```

Open:

```text
http://127.0.0.1:5000
```

## Project Structure

```text
MATE/
├── cognitive/
│   ├── memory.py
│   ├── semantic_search.py
│   ├── embeddings.py
│   ├── self_model.py
│   ├── reflection.py
│   ├── evaluator.py
│   ├── learning.py
│   ├── consolidation.py
│   ├── contradictions.py
│   └── relationship_discovery.py
├── static/
├── templates/
├── server.py
├── ai_brain.py
├── mate.py
├── mate_app.py
├── requirements.txt
└── README.md
```

## Development Status

MATE is an ongoing experimental project.

Its cognitive components are under active development and testing. Memory retrieval, relationship discovery, reflection, and evaluation are engineering experiments rather than evidence of human-like consciousness or general intelligence.

## Privacy and Security

MATE is designed around local AI processing.

- Language-model inference is intended to run locally through Ollama.
- Memory is stored locally using SQLite.
- Do not commit personal databases, credentials, API keys, or private configuration files.
- Desktop, email, and calendar integrations should be reviewed and secured before external deployment.

## Future Development

- Improved contextual memory.
- Better memory relationship reasoning.
- Reliable self-evaluation and benchmarking.
- Permission-controlled automation.
- Improved conversational interface.
- More robust privacy and security controls.

## Author

**Manish Reddy**

Software Engineering | AI | Python |
