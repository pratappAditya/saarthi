# Saarthi Safe Model Upgrade & Automatic Rollback System

## Upgrade & Model Switching Protocol

To prevent leaving Saarthi without a functional local AI model during updates, model switching implements an atomic rollback pattern:

```
Active Working Model (Model A)
            ↓
User Initiates Upgrade to Model B
            ↓
Download Model B in Background (Model A remains active)
            ↓
Verify Model B Download Integrity
            ↓
Run Health Verification Test on Model B
            │
    ┌───────┴───────┐
 [Success]      [Failure]
    │               │
Activate Model B  Rollback Automatically to Model A
                    Show Actionable Diagnostics to User
```

## Deletion Safety Rules
- Active working model cannot be deleted from disk unless another approved model is active.
- Unused models can be deleted through `Settings -> AI & Model` to recover disk space.
