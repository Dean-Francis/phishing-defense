# Requirements: Phishing Defense System

**Defined:** 2026-01-20
**Core Value:** Catch phishing that traditional filters miss — especially AI-generated attacks.

## v1 Requirements

Requirements for graduation demo. Each maps to roadmap phases.

### Detection Models

- [ ] **DET-01**: Tier 2 text classifier trained on labeled phishing/benign messages
- [ ] **DET-02**: Tier 2 model returns confidence score (0-1) for phishing probability
- [ ] **DET-03**: Tier 3 LLM integration calls Claude API for borderline cases
- [ ] **DET-04**: Tier 3 returns verdict (phishing/safe) with 2-3 sentence reasoning
- [ ] **DET-05**: Fusion logic combines Tier 1 URL score and Tier 2 text score
- [ ] **DET-06**: Fusion escalates to Tier 3 when both tiers have low confidence
- [ ] **DET-07**: Response caching for LLM calls to reduce latency and cost

### API Service

- [ ] **API-01**: FastAPI service with `/analyze` endpoint accepting URL and/or message text
- [ ] **API-02**: API returns risk level (Low/Medium/High), confidence, and reasoning
- [ ] **API-03**: API key authentication for all endpoints
- [ ] **API-04**: Rate limiting (requests per minute per API key)
- [ ] **API-05**: Structured JSON logging for all requests/responses
- [ ] **API-06**: Health check endpoint for monitoring

### Browser Extension

- [ ] **EXT-01**: Chrome MV3 extension installable from local files
- [ ] **EXT-02**: Auto-scan runs on page load, analyzes visible URLs
- [ ] **EXT-03**: Manual scan button in extension popup triggers analysis of current page
- [ ] **EXT-04**: Paste interface allows user to submit email/message text for analysis
- [ ] **EXT-05**: Results display shows risk level (Low/Medium/High) with color coding
- [ ] **EXT-06**: Results include 2-3 short reasons explaining the verdict
- [ ] **EXT-07**: Extension communicates with API service via authenticated requests

### Documentation

- [ ] **DOC-01**: Dataset card documenting training data sources, size, and characteristics
- [ ] **DOC-02**: Training recipe with reproducible steps for model training
- [ ] **DOC-03**: Evaluation report with precision, recall, F1, ROC-AUC on test set
- [ ] **DOC-04**: Adversarial test results (edge cases, evasion attempts)
- [ ] **DOC-05**: Ops guide covering deployment, configuration, and troubleshooting

## v2 Requirements

Deferred to post-graduation. Not in current roadmap.

### Dashboard

- **DASH-01**: Web dashboard showing user's scan history
- **DASH-02**: Drill-down view for individual scan details
- **DASH-03**: Trend charts showing detection patterns over time

### Feedback Loop

- **FEED-01**: User can report false negatives (missed phishing)
- **FEED-02**: User can mark false positives (wrongly flagged)
- **FEED-03**: Feedback stored for model retraining

### Advanced Features

- **ADV-01**: User account system with login/signup
- **ADV-02**: Multi-language phishing detection
- **ADV-03**: Edge extension support (separate build)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Web dashboard | Not required for graduation, extension-only demo |
| User feedback loop | Nice-to-have, not essential for detection demo |
| User accounts | Demo doesn't require persistent user identity |
| Mobile app | Browser extension sufficient for demo |
| Real-time email integration | Manual paste workflow meets requirements |
| Multi-language support | English-only simplifies scope |
| Advanced analytics | Basic evaluation metrics sufficient |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DET-01 | TBD | Pending |
| DET-02 | TBD | Pending |
| DET-03 | TBD | Pending |
| DET-04 | TBD | Pending |
| DET-05 | TBD | Pending |
| DET-06 | TBD | Pending |
| DET-07 | TBD | Pending |
| API-01 | TBD | Pending |
| API-02 | TBD | Pending |
| API-03 | TBD | Pending |
| API-04 | TBD | Pending |
| API-05 | TBD | Pending |
| API-06 | TBD | Pending |
| EXT-01 | TBD | Pending |
| EXT-02 | TBD | Pending |
| EXT-03 | TBD | Pending |
| EXT-04 | TBD | Pending |
| EXT-05 | TBD | Pending |
| EXT-06 | TBD | Pending |
| EXT-07 | TBD | Pending |
| DOC-01 | TBD | Pending |
| DOC-02 | TBD | Pending |
| DOC-03 | TBD | Pending |
| DOC-04 | TBD | Pending |
| DOC-05 | TBD | Pending |

**Coverage:**
- v1 requirements: 25 total
- Mapped to phases: 0 (pending roadmap)
- Unmapped: 25

---
*Requirements defined: 2026-01-20*
*Last updated: 2026-01-20 after initial definition*
