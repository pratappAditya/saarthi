# Microsoft Store Distribution & Release Guidelines

## Compliance Checklist
1. **User Consent**: Ollama and Nemotron model downloads require explicit user interaction ([Set Up Saarthi AI], [Accept & Install]).
2. **Local Isolation**: All AI processing occurs locally on `127.0.0.1:11434`. Zero cloud LLM APIs.
3. **Packaging**: Desktop Bridge MSIX packaging configuration verified. Dependencies on external runtimes documented in `ollama_store_dependency.md`.
4. **Security Audit**: Zero cloud API keys or hard-coded secrets present in client executable.
