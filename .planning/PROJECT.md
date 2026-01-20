# Phishing Defense System

## What This Is

A multi-tier phishing detection system that helps everyday users identify phishing attacks — especially AI-generated ones that bypass traditional filters. Delivered as a browser extension (Chrome/Edge) with auto-scan and manual scan capabilities, backed by a FastAPI service running tiered ML models.

## Core Value

**Catch phishing that traditional filters miss.** When attackers use GenAI to craft convincing messages, this system analyzes both URLs and message content to protect users who can't tell the difference themselves.

## Requirements

### Validated

- [x] URL-based phishing detection using lexical features — existing (Tier 1)
- [x] LightGBM classifier with ~96% AUC on test data — existing
- [x] Confidence scoring with escalation flag for uncertain predictions — existing
- [x] Feature extraction pipeline (entropy, TLD stats, suspicious tokens) — existing

### Active

- [ ] Text classifier for email/message content analysis (Tier 2)
- [ ] Fusion logic combining URL and text signals
- [ ] LLM integration for borderline cases with reasoning (Tier 3)
- [ ] FastAPI service exposing detection endpoints
- [ ] Browser extension with auto-scan and manual scan
- [ ] Basic scan history dashboard for users
- [ ] Evaluation metrics and technical documentation

### Out of Scope

- Full analyst dashboard with trends/queues — not required for graduation, can be basic
- Mobile app — web extension only
- Real-time email integration (IMAP/POP) — manual paste workflow sufficient
- User authentication system — demo doesn't require accounts
- Multi-language phishing detection — English only for v1

## Context

**Graduation Project:** This is a required project for degree completion. Deadline is < 1 month. Must deliver working demo, evaluation metrics, and technical report.

**Existing Codebase:** Tier 1 URL detector already implemented in `tier1_url/` using LightGBM. Achieves ~96% AUC but only catches ~4% of phishing with high confidence — rest escalates to higher tiers.

**Detection Architecture:**
```
Message arrives
    ├─→ Extract URLs → Tier 1 (URL model) → URL score
    └─→ Extract text → Tier 2 (Text model) → Text score
              ↓
         Fusion logic
              ↓
    High confidence either → Final verdict
    Both uncertain → Tier 3 (Claude LLM)
```

**Training Data:**
- Tier 1: CSV with labeled URLs (have)
- Tier 2: CSV with labeled phishing/benign messages (have)

**Target Users:** Everyday users protecting themselves from phishing, not security professionals.

## Constraints

- **Timeline**: < 1 month to graduation presentation
- **Tech Stack**: Python (existing), FastAPI (API), Chrome/Edge MV3 (extension), Hugging Face transformers (Tier 2)
- **LLM Provider**: Anthropic Claude for Tier 3 reasoning
- **Demo Scope**: Must be working end-to-end demo, not just model notebooks
- **Documentation**: Technical dossier required (dataset card, training recipe, evaluation report)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Tiered detection (URL → Text → LLM) | Cost/latency efficient — most cases resolved by cheap models | — Pending |
| Conditional fusion (parallel Tier 1+2) | URLs and text provide independent signals | — Pending |
| Claude for Tier 3 | Strong reasoning for explanations | — Pending |
| Browser extension as primary interface | Reaches everyday users where they browse | — Pending |
| Basic dashboard only | Full analyst tooling not required for graduation | — Pending |

---
*Last updated: 2026-01-20 after initialization*
