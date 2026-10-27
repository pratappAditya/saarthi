# Saarthi Nemotron Recommendation Engine Specifications

## Selection Algorithm
The `NemotronRecommendationService` evaluates the user's `HardwareProfile` against the catalog:
1. Filter catalog by system RAM, VRAM, and storage constraints.
2. Select highest safe tier in hierarchy: `ULTRA` > `SUPER` > `PRO` > `STANDARD`.
3. If specs satisfy Ultra (16GB+ RAM & 6GB+ VRAM), recommend `ULTRA`.
4. If specs satisfy Super/Pro (8GB-16GB RAM), recommend `SUPER` or `PRO`.
5. If specs are constrained (6GB RAM), recommend `STANDARD`.
6. Return structured output with detailed compatibility notes per tier.
