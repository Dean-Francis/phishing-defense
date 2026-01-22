"""Fusion module for multi-tier phishing detection

Combines Tier 1 (URL) and Tier 2 (text) detection scores into unified verdicts
with risk levels and escalation criteria for Tier 3 LLM review.

Also provides the PhishingDetectionPipeline for end-to-end orchestration.
"""

from fusion.fusion_logic import FusionLogic
from fusion.pipeline import PhishingDetectionPipeline

__all__ = ['FusionLogic', 'PhishingDetectionPipeline']
