# Saarthi Frontend UI & UX Audit Report

## Overview
This document audits the frontend component architecture, layout consistency, and user experience across all views in Saarthi.

---

## Component Mapping & Findings

| View / Component | Current State | Identified UX Issues | Severity | Recommended Solution | RC2 Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **App Shell** (`App.tsx`) | Tabbed navigation rail + main workspace + collapsible context panel. | Header title height and border contrast can be inconsistent on small viewports. | LOW | Standardize header flex layout and responsive padding tokens. | PASS WITH FIX |
| **Navigation Rail** (`NavigationRail.tsx`) | Vertical navigation icons for Chat, Memory, Files, Settings. | Inactive icons lack clear hover tooltips on narrow viewports. | LOW | Add accessible tooltips and clear active state indicators. | PASS WITH FIX |
| **Chat Canvas** (`ChatCanvas.tsx`) | Message list + floating composer + tool result cards. | Auto-scroll on long responses occasionally needs smooth scroll lock. | MEDIUM | Refine scroll anchor ref and auto-scroll behavior. | PASS WITH FIX |
| **Composer** | Textarea with Enter send and Shift+Enter newline. | Needs explicit cancellation button state during active generation turns. | MEDIUM | Show clear "Cancel generation" button during active execution. | PASS WITH FIX |
| **Permission Card** (`PermissionModal.tsx`) | Modal/card asking confirmation for `USER_CONFIRMATION` tools. | Technical wording can be simplified for non-technical users. | MEDIUM | Add human-readable risk description with expandable technical details. | PASS WITH FIX |
| **Memory UI** (`MemoryScreen.tsx`) | Searchable memory card list with delete actions. | Needs explicit local-privacy badge emphasizing on-device storage. | LOW | Add privacy badge ("Stored locally in SQLite"). | PASS WITH FIX |
| **Files Workspace** (`FilesScreen.tsx`) | Directory list with file preview drawer. | Breadcrumb path navigation can wrap awkwardly on narrow screens. | LOW | Truncate breadcrumbs with ellipsis for long paths. | PASS WITH FIX |
| **Settings / Runtime** (`SettingsScreen.tsx`) | Settings cards + system status modal. | User preferences mixed with technical diagnostic details. | LOW | Separate User Preferences tab from Technical Runtime Diagnostics tab. | PASS WITH FIX |
| **Onboarding** (`FirstRunOnboarding.tsx`) | 3-step modal overview of Saarthi. | Needs explicit "Skip Onboarding" button for returning users. | LOW | Add "Skip setup" option storing completion in local storage. | PASS WITH FIX |
