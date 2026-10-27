# Phase 5K Manual QA & Verification Protocol

## Manual Test Cases

### Test Case 1: Multi-Domain Query Execution
- **Prompt**: *"Analyze these archaeological excavation photographs, compare them with historical records, research similar findings and prepare a report."*
- **Expected Outcome**:
  - `DomainTransitionBadge` displays: `Saarthi: Archaeology → Vision → History → Research → Writing`
  - `CrossDomainWorkflowView` renders 4 steps with step domain tags, confidence scores, and evidence provenance.

### Test Case 2: Explicit Domain Lock
- **Action**: Click domain lock icon on `DomainTransitionBadge`.
- **Expected Outcome**:
  - Lock icon changes to gold locked state.
  - Tooltip confirms: *"Explicitly locked to current domain."*

### Test Case 3: Approval Checkpoint Interception
- **Action**: Initiate a high-risk tool step in a routine or workflow without pre-approval.
- **Expected Outcome**:
  - Workflow pauses with `APPROVAL REQUIRED` badge.
  - Click "Approve Step" or say *"Saarthi, approve this step"* resumes execution.

### Test Case 4: Four-Shell Parity Check
- **Action**: Switch experience shells between Signature, Forge, Pulse, and Aurora.
- **Expected Outcome**:
  - Navigating to "Cross-Domain Workflows" displays `CrossDomainWorkflowView` with consistent task graph data across all 4 themes.
