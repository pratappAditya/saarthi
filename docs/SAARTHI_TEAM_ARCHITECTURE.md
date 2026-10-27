# Saarthi Teams Architecture Specification (Commercially Frozen)

## Overview
Saarthi Teams is fully implemented in the codebase (`team_service.py`, `organizations_api.py`), but commercially frozen (`TEAMS_PUBLIC_SALE = False`).

## Architecture Features
- **Organizations & Workspaces**: Multi-tenant workspace partitioning.
- **Member Management**: Role-based access control (`OWNER`, `ADMIN`, `MEMBER`, `VIEWER`).
- **Shared Team Memory**: Cross-user knowledge base and shared document vaults.
- **Team Agents & Routines**: Shared automated agent workflows and scheduled routines.
- **Team Audit Trail**: Immutable logging of all team workspace activity.
