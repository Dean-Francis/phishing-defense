"""Tier 3 LLM-based phishing detection module.

Provides expert-level phishing analysis using Claude API for cases where
Tier 1 (URL) and Tier 2 (Text) detectors are uncertain.

Exports:
    ClaudePhishingDetector: Main detector class with analyze() method
    LLMCache: SQLite-based response caching for reduced API costs
"""

from tier3_llm.tier3_inference import ClaudePhishingDetector
from tier3_llm.tier3_cache import LLMCache

__all__ = ['ClaudePhishingDetector', 'LLMCache']
