# Saarthi Release UX Checklist (RC2)

## Overview
This checklist records the user experience and interface release verification results for Saarthi.

---

## Release UX Verification Matrix

| Area | Item Verified | Status | Evidence / Notes |
| :--- | :--- | :--- | :--- |
| **Chat UX** | User / Assistant message distinction | [X] PASS | Distinct bubble colors (`#F59E0B` user tint vs dark obsidian assistant bubble). |
| **Chat UX** | Markdown & Code blocks | [X] PASS | Clean code syntax highlighting, monospace font, copy code button. |
| **Chat UX** | Reasoning Tag Stripping | [X] PASS | Zero `<think>`, `<thinking>`, `Thinking...` tags rendered in assistant bubbles. |
| **Composer** | Keyboard navigation | [X] PASS | `Enter` sends message, `Shift+Enter` inserts newline. |
| **Composer** | Cancellation button | [X] PASS | Active generation turn presents immediate cancellation trigger. |
| **Permissions** | Permission Request Card | [X] PASS | Human-readable action description, risk badge, affected resources, allow once/always/deny options. |
| **Permissions** | Replay Rejection | [X] PASS | Processed permission requests return HTTP 400 when replayed. |
| **Memory UX** | Stored Memory Cards | [X] PASS | Local storage badge, memory category tags, single-click deletion. |
| **Files Workspace** | Active Workspace Root | [X] PASS | Locked to `E:\Saarthi`, breadcrumb navigation, sandboxed access error reporting. |
| **Settings** | User vs Technical Runtime | [X] PASS | `SettingsScreen` and `SystemStatusModal` separate configuration from GPU/Ollama IPC state. |
| **Onboarding** | First-Run Flow | [X] PASS | 5-step interactive onboarding modal with "Skip setup" support. |
| **Error Recovery** | Friendly Error States | [X] PASS | Human-readable recovery messages with clear retry buttons. |
| **Responsive** | Viewport Layouts | [X] PASS | Tested across 1920x1080, 1440x900, 1366x768, 1024x768, tablet, and mobile. |
| **Accessibility** | Keyboard & Contrast | [X] PASS | Visible focus rings, semantic elements, high-contrast dark surfaces. |
| **Performance** | Production Build | [X] PASS | Vite build completes in 348ms, total JS bundle 438 kB. |
| **Branding** | Release Hygiene | [X] PASS | Zero legacy references (`cheeku`, `untitled`, `Lorem ipsum`, `Demo App`). |
