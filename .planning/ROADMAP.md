# Roadmap: Phishing Defense System

## Overview

Build a working multi-tier phishing detection demo for graduation. Tier 1 URL detection already exists. Remaining work: train Tier 2 text classifier, integrate Claude LLM for Tier 3 reasoning, expose detection via FastAPI service, deliver browser extension with scan capabilities, and document everything for technical review.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Tier 2 Text Detection** - Train and deploy message content classifier
- [ ] **Phase 2: Fusion & LLM Integration** - Combine signals and add Claude reasoning
- [ ] **Phase 3: API Service** - Expose detection endpoints via FastAPI
- [ ] **Phase 4: Browser Extension** - Build Chrome extension with scan capabilities
- [ ] **Phase 5: Documentation & Validation** - Technical report and evaluation metrics

## Phase Details

### Phase 1: Tier 2 Text Detection
**Goal**: Text messages can be classified as phishing/benign with confidence scores

**Depends on**: Nothing (Tier 1 already complete)

**Requirements**: DET-01, DET-02

**Success Criteria** (what must be TRUE):
  1. Tier 2 model trained on labeled phishing/benign message dataset
  2. Model returns probability score (0-1) for any text input
  3. Inference pipeline handles single messages and batches
  4. Model achieves >85% accuracy on held-out test set

**Plans**: TBD

Plans:
- [ ] 01-01: TBD
- [ ] 01-02: TBD
- [ ] 01-03: TBD

### Phase 2: Fusion & LLM Integration
**Goal**: Multi-tier detection system combines URL and text signals with LLM fallback

**Depends on**: Phase 1

**Requirements**: DET-03, DET-04, DET-05, DET-06, DET-07

**Success Criteria** (what must be TRUE):
  1. Fusion logic accepts Tier 1 URL score and Tier 2 text score, returns combined verdict
  2. Low-confidence cases (both tiers uncertain) escalate to Tier 3 Claude API
  3. Tier 3 returns phishing/safe verdict with 2-3 sentence reasoning
  4. LLM responses cached to reduce API calls and latency
  5. End-to-end detection pipeline processes message with URL and returns final verdict

**Plans**: TBD

Plans:
- [ ] 02-01: TBD
- [ ] 02-02: TBD
- [ ] 02-03: TBD

### Phase 3: API Service
**Goal**: Detection system accessible via production-ready FastAPI endpoints

**Depends on**: Phase 2

**Requirements**: API-01, API-02, API-03, API-04, API-05, API-06

**Success Criteria** (what must be TRUE):
  1. FastAPI service runs with `/analyze` endpoint accepting URL and/or message text
  2. API returns structured JSON with risk level (Low/Medium/High), confidence, and reasoning
  3. API key authentication protects all endpoints
  4. Rate limiting enforced (requests per minute per key)
  5. All requests/responses logged in structured JSON format
  6. Health check endpoint returns service status

**Plans**: TBD

Plans:
- [ ] 03-01: TBD
- [ ] 03-02: TBD
- [ ] 03-03: TBD

### Phase 4: Browser Extension
**Goal**: Users can scan URLs and messages directly from their browser

**Depends on**: Phase 3

**Requirements**: EXT-01, EXT-02, EXT-03, EXT-04, EXT-05, EXT-06, EXT-07

**Success Criteria** (what must be TRUE):
  1. Chrome MV3 extension installable from unpacked files
  2. Extension auto-scans page on load and analyzes visible URLs
  3. Popup has manual scan button that analyzes current page
  4. Paste interface accepts email/message text and submits to API
  5. Results display shows risk level with color coding (red/yellow/green)
  6. Each result includes 2-3 short reasons explaining the verdict
  7. Extension authenticates with API using stored key

**Plans**: TBD

Plans:
- [ ] 04-01: TBD
- [ ] 04-02: TBD
- [ ] 04-03: TBD

### Phase 5: Documentation & Validation
**Goal**: Technical documentation ready for graduation review

**Depends on**: Phase 4

**Requirements**: DOC-01, DOC-02, DOC-03, DOC-04, DOC-05

**Success Criteria** (what must be TRUE):
  1. Dataset card documents training data sources, size, class distribution, and characteristics
  2. Training recipe provides reproducible steps for model training (Tier 1 and Tier 2)
  3. Evaluation report shows precision, recall, F1, ROC-AUC for all tiers on test set
  4. Adversarial test results document edge cases and evasion attempt outcomes
  5. Ops guide covers deployment, configuration, troubleshooting, and API key management

**Plans**: TBD

Plans:
- [ ] 05-01: TBD
- [ ] 05-02: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Tier 2 Text Detection | 0/TBD | Not started | - |
| 2. Fusion & LLM Integration | 0/TBD | Not started | - |
| 3. API Service | 0/TBD | Not started | - |
| 4. Browser Extension | 0/TBD | Not started | - |
| 5. Documentation & Validation | 0/TBD | Not started | - |

---
*Roadmap created: 2026-01-20*
