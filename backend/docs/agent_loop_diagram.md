# Agent Loop Diagram

```mermaid
flowchart TD
    A[User Request / API /chat] --> B[AgentCore.handle_message]
    B --> C{Cancelled or Pre-cancelled?}
    C -- Yes --> D[Return Cancelled Response]
    C -- No --> E{Memory Command?}
    E -- Yes --> F[Process Memory Command & Return]
    E -- No --> G[Store User Message & Start Loop]
    G --> H[Check Cancellation & Iteration Count]
    H -- Iteration Limit / Cancelled --> I[Return Cancelled or Limit Error]
    H -- Valid Iteration --> J[Retrieve History & Tool Routing]
    J --> K[Model.generate_response]
    K --> L[clean_reasoning]
    L --> M{Tool Call Detected?}
    M -- Yes --> N[Parse & Validate Tool Call Blocks]
    N --> O{For Each Valid Tool Call}
    O --> P{Permission Required?}
    P -- Yes (USER_CONFIRMATION) --> Q[Raise PermissionRequiredException]
    P -- No (SAFE / READ_ONLY) --> R[ToolExecutor.execute_tool with 30s Timeout (Worker Thread Offloading for Sync Tools)]
    R --> S{Timed Out / Error?}
    S -- Yes --> T[Inject TOOL_TIMEOUT / EXECUTION_ERROR Result]
    S -- No --> U[Inject Tool Result Data]
    T --> V[Next Tool / Loop Continue]
    U --> V
    V --> H
    M -- No --> W[Clean Final Response & Store in History]
    W --> X[Return ChatResponse]
```
