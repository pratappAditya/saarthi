# Microsoft Store Compatibility Audit — Local Runtime & Ollama Dependency

## Overview
Saarthi is packaged for distribution via the Microsoft Store target (MSIX / Centennial Desktop Bridge).

## Store Policy & Technical Constraints
1. **Third-Party Executable Installation**: Microsoft Store Policies (10.2 / 10.5) prohibit applications from silently bundling or executing unauthorized silent installers.
2. **Elevated Privileges**: Store packages run in virtualized containerized environments and cannot silently elevate privileges (`runas` UAC) without user interaction.
3. **Privacy & Security**: Users must explicitly grant consent before installing local software runtimes or downloading model binary weights.

## Saarthi Architecture Compliance Solution
- Saarthi uses an official, user-consented installation flow.
- If Ollama is absent, Saarthi displays an explicit confirmation dialog detailing what will be installed, download origin (`https://ollama.com`), storage footprint (~500MB runtime), and local privacy guarantees.
- Upon approval, Saarthi guides the user through launching the official installer executable or downloads model weights directly into the user's standard local Ollama directory.
- No third-party software is installed silently or without authorization.
