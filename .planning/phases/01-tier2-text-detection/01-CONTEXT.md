# Phase 1: Tier 2 Text Detection - Context

**Gathered:** 2026-01-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Train and deploy a transformer-based text classifier for phishing message detection. The model analyzes email/message content and returns a confidence score indicating phishing probability. This complements Tier 1's URL analysis — fusion logic and LLM integration are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Model choice
- Use DistilBERT as the base model — smaller, faster, sufficient accuracy for timeline
- Confidence threshold: 0.85 (match Tier 1 for consistency)
- Include escalation flag for low-confidence predictions (like Tier 1)

### Dataset handling
- Dataset contains mixed content (some full emails with subject+body, some just text snippets)
- Size: 5K-20K samples — adequate for fine-tuning
- Class distribution: balanced (~50/50 phishing vs benign)
- Train/test split: 80/20 (match Tier 1 pattern)

### Code structure
- Create new directory: `tier2_text/` parallel to `tier1_url/`
- Follow tier-based organization pattern

### Claude's Discretion
- Fine-tuning approach: full fine-tune vs freeze-base (decide based on dataset size and early experiments)
- Feature contributions: whether to extract/display which words triggered classification (feasibility TBD)
- Class structure: whether to have separate extractor class or simplified structure (transformers handle tokenization)
- Model artifact location: `tier2_text/models/` or central `models/` directory
- Inference interface: design for consistency with Tier 1 but adapt where needed

</decisions>

<specifics>
## Specific Ideas

- Match Tier 1's inference output structure as closely as possible for easier fusion
- Model should return: score, label, confidence level, escalation flag
- Follow existing patterns from `tier1_url/` for training and inference scripts

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-tier2-text-detection*
*Context gathered: 2026-01-20*
