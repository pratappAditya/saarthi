# Saarthi Desktop Architecture Specification

## Overview
Saarthi is packaged as a Windows desktop application featuring an automated service lifecycle manager, zero-cloud local AI inference, and sandboxed workstation file tools.

---

## Component Architecture

```text
E:\Saarthi
├── backend
│   ├── app
│   │   ├── agent          # Stateful AgentCore & smart router
│   │   ├── api            # FastAPI REST routes
│   │   ├── config         # Settings & environment validation
│   │   ├── memory         # SQLite memory store & manager
│   │   ├── models         # Ollama provider client
│   │   ├── security       # Path checks & security manager
│   │   ├── tools          # Secure file & terminal tools
│   │   ├── launcher.py    # Production Service Lifecycle Manager
│   │   └── main.py        # FastAPI entrypoint & frontend SPA mount
├── data                   # SQLite database & diagnostic logs
├── docs                   # System architecture specifications
├── frontend               # React 19 + TypeScript + Vite workspace
└── models                 # Local GGUF model files
```
