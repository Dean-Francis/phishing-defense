"""Fusion logic for combining Tier 1 and Tier 2 phishing detection scores

This module implements weighted score fusion and escalation logic for the
multi-tier phishing detection system. It accepts result dictionaries from
Tier 1 (URL) and Tier 2 (text) detectors and produces a unified verdict.
"""

from typing import Dict, Any, Optional, Tuple


class FusionLogic:
    """Combines Tier 1 (URL) and Tier 2 (text) detection scores into unified verdict

    Attributes:
        weights: Tuple of (tier1_weight, tier2_weight) for weighted averaging
        uncertain_zone: Tuple of (low_bound, high_bound) defining uncertainty range

    The fusion logic:
    - Weighted average when both tiers provided
    - Single tier score when only one available
    - Escalation when BOTH tiers are in uncertain zone (or single tier is uncertain)
    """

    def __init__(self, weights: Tuple[float, float] = (1.0, 1.0),
                 uncertain_zone: Tuple[float, float] = (0.3, 0.7)) -> None:
        """Initialize FusionLogic with configurable weights and uncertainty bounds

        Args:
            weights: (tier1_weight, tier2_weight) for weighted average calculation
            uncertain_zone: (low_bound, high_bound) defining the uncertainty range
                           Scores in this range trigger escalation consideration
        """
        self.weights = weights
        self.uncertain_zone = uncertain_zone

    def _validate_tier_result(self, result: Dict[str, Any], tier_name: str) -> None:
        """Validate that a tier result has required structure

        Args:
            result: The tier result dictionary to validate
            tier_name: Name of the tier for error messages (e.g., 'Tier 1', 'Tier 2')

        Raises:
            ValueError: If result is missing required keys or has invalid values
        """
        required_keys = ['score', 'label', 'confidence', 'escalate']
        for key in required_keys:
            if key not in result:
                raise ValueError(f"{tier_name} result missing required key: {key}")
        if not 0.0 <= result['score'] <= 1.0:
            raise ValueError(f"{tier_name} score must be 0-1, got {result['score']}")

    def _is_uncertain(self, score: float) -> bool:
        """Check if a score falls within the uncertain zone

        Args:
            score: Phishing probability score (0-1)

        Returns:
            True if score is in uncertain zone, False otherwise
        """
        low, high = self.uncertain_zone
        return low <= score <= high

    def _calculate_risk_level(self, score: float) -> str:
        """Map score to risk level category

        Risk level mapping (from CONTEXT.md):
        - 0.0 - 0.4: 'Low'
        - 0.4 - 0.6: 'Medium'
        - 0.6 - 1.0: 'High'

        Args:
            score: Fused phishing probability score (0-1)

        Returns:
            Risk level string: 'Low', 'Medium', or 'High'
        """
        if score < 0.4:
            return 'Low'
        elif score < 0.6:
            return 'Medium'
        else:
            return 'High'

    def fuse_scores(self, tier1_result: Optional[Dict[str, Any]] = None,
                    tier2_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fuse Tier 1 and Tier 2 detection scores into unified verdict

        Handles three cases:
        - Both tiers provided: Weighted average of scores
        - Only tier1: Use tier1 score alone
        - Only tier2: Use tier2 score alone
        - Neither: Raise ValueError

        Escalation logic (from CONTEXT.md):
        - Escalate ONLY when BOTH tiers are uncertain (0.3-0.7 range)
        - If only one tier provided, escalate if that tier is uncertain
        - Mark confidence='high' when NOT escalating, 'low' when escalating

        Args:
            tier1_result: Result dict from Tier 1 URL detector (optional)
            tier2_result: Result dict from Tier 2 text detector (optional)

        Returns:
            Fused result dictionary with:
            - score: float, combined phishing probability 0-1
            - label: str, 'phishing' or 'benign' (threshold 0.5)
            - risk_level: str, 'Low' (0-0.4), 'Medium' (0.4-0.6), 'High' (0.6+)
            - confidence: str, 'high' or 'low'
            - escalate: bool, True if both tiers in uncertain zone
            - metadata: dict with tier scores, weights, and fusion method

        Raises:
            ValueError: If neither tier result is provided
        """
        # Validate inputs
        if tier1_result is None and tier2_result is None:
            raise ValueError("At least one tier result must be provided")

        if tier1_result is not None:
            self._validate_tier_result(tier1_result, 'Tier 1')

        if tier2_result is not None:
            self._validate_tier_result(tier2_result, 'Tier 2')

        # Extract scores
        tier1_score = tier1_result['score'] if tier1_result else None
        tier2_score = tier2_result['score'] if tier2_result else None

        # Calculate fused score based on available inputs
        if tier1_score is not None and tier2_score is not None:
            # Both tiers: weighted average
            w1, w2 = self.weights
            fused_score = (w1 * tier1_score + w2 * tier2_score) / (w1 + w2)
            fusion_method = 'weighted_average'

            # Escalate only if BOTH tiers are uncertain
            escalate = self._is_uncertain(tier1_score) and self._is_uncertain(tier2_score)

        elif tier1_score is not None:
            # Only tier1 available
            fused_score = tier1_score
            fusion_method = 'tier1_only'

            # Single tier: escalate if uncertain
            escalate = self._is_uncertain(tier1_score)

        else:
            # Only tier2 available
            fused_score = tier2_score
            fusion_method = 'tier2_only'

            # Single tier: escalate if uncertain
            escalate = self._is_uncertain(tier2_score)

        # Determine label (phishing if >= 0.5)
        label = 'phishing' if fused_score >= 0.5 else 'benign'

        # Determine risk level
        risk_level = self._calculate_risk_level(fused_score)

        # Confidence is high when NOT escalating, low when escalating
        confidence = 'low' if escalate else 'high'

        return {
            'score': fused_score,
            'label': label,
            'risk_level': risk_level,
            'confidence': confidence,
            'escalate': escalate,
            'metadata': {
                'tier1_score': tier1_score,
                'tier2_score': tier2_score,
                'weights': self.weights,
                'fusion_method': fusion_method
            }
        }
