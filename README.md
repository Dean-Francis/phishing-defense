# GenAI-Powered Phishing Defense Platform

Real-time phishing detection using ML/NLP, delivered as a browser extension with analyst dashboard.

## 🎯 Project Goals
- **F1 Score**: ≥ 0.90
- **Recall**: ≥ 0.93 on phishing detection
- **Latency**: < 800ms (cached) / < 2.5s (with LLM)

## 📁 Planned Repository Structure
```
phishing-defense-platform/
├── .github/workflows/      # CI/CD pipelines
├── extension/              # Browser extension (Chrome/Edge MV3)
│   ├── src/               # Extension source code
│   └── public/            # Static assets
├── backend/               # FastAPI service
│   ├── app/              
│   │   ├── api/          # REST endpoints
│   │   ├── models/       # ML models
│   │   ├── detectors/    # Detection logic
│   │   └── core/         # Config, security
│   └── tests/            # Backend tests
├── dashboard/             # React analyst dashboard
│   └── src/
├── models/                # ML model artifacts
│   ├── text-classifier/
│   ├── url-detector/
│   └── training/
├── datasets/              # Data management
│   ├── raw/
│   ├── processed/
│   └── gold-test/
├── docs/                  # Documentation
├── scripts/               # Utilities
│   ├── data-pipeline/
│   └── deployment/
└── docker/                # Docker configurations
```

## 🚀 Quick Start
Coming soon in Week 2...

## 📅 Current Status
**Week 1:** Project setup and infrastructure
- [x] Repository structure planned
- [ ] Docker setup
- [ ] CI/CD pipeline
- [ ] Initial dependencies

## 👥 Team
- **CS-1 (ML):** Model development
- **CS-2 (Full-stack):** Extension, backend, dashboard
- **CyS-1 (Data):** Dataset curation
- **CyS-2 (Security):** Threat modeling, adversarial testing