# Phase 2: Fusion & LLM Integration - Context

**Gathered:** 2026-01-22
**Updated:** 2026-01-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Multi-tier detection system that combines Tier 1 URL scores and Tier 2 text scores into a unified verdict, with escalation to Claude LLM (Tier 3) for uncertain cases. Returns final phishing/safe verdict with reasoning.

</domain>

<decisions>
## Implementation Decisions

### Fusion Logic
- Weighted average of URL and text scores
- Weights: Claude's discretion based on model performance analysis
- Final threshold: 0.5 (50%+ probability = phishing)
- Single-input handling: Use available score alone if only URL or only text provided
- Conflicting tiers: Claude's discretion based on which model has better calibration

### Risk Level Output
- Three levels: Low / Medium / High
- Balanced mapping: 0-0.4 Low, 0.4-0.6 Medium, 0.6+ High
- Return alongside numeric score for flexibility

### LLM Prompt Design
- Context: Include tier scores + ask Claude for independent analysis
- Response format: Structured JSON with {verdict, confidence, reasoning}
- Model: Haiku for development, Sonnet option for final demo
- Reasoning format: 2-3 bullet points listing specific red flags or safe indicators

### Escalation Criteria
- Trigger: Both tiers must be in uncertain zone (not just one)
- Uncertain zone: 0.3-0.7 for development, 0.25-0.75 for final demo
- Fallback: If LLM unavailable, use fused Tier 1+2 score, mark as "no LLM review"
- Force option: `force_llm=True` flag to always get Claude's analysis

### Caching Strategy
- Cache key: Hash of URL + message text combined (exact match)
- TTL: 24 hours
- Storage: SQLite file (persists across restarts)
- Bypass option: `skip_cache=True` flag for fresh analysis

### API Key Configuration
- Claude API key from environment variable: ANTHROPIC_API_KEY
- Standard for deployment, no config file needed

### Claude's Discretion
- Optimal fusion weights based on Tier 1 and Tier 2 model performance
- How to handle conflicting tier scores
- SQLite schema design
- Error handling and retry logic
- Prompt engineering for best Claude responses

</decisions>

<specifics>
## Specific Ideas

- Haiku for development keeps API costs low during iteration
- Bullet points for reasoning are more scannable in UI than paragraphs
- SQLite cache survives server restarts, important for production demo

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-fusion-llm-integration*
*Context gathered: 2026-01-22*
