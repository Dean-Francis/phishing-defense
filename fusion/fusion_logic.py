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


if __name__ == "__main__":
    """Comprehensive test cases for FusionLogic

    Tests cover all fusion scenarios:
    1. Both tiers high confidence phishing
    2. Both tiers high confidence benign
    3. Both tiers uncertain (should escalate)
    4. Tier 1 confident, Tier 2 uncertain (should NOT escalate)
    5. Only URL provided (tier2_result=None)
    6. Only text provided (tier1_result=None)
    7. Conflicting tiers (T1 phishing, T2 benign)
    """

    print("=" * 70)
    print("FUSION LOGIC - COMPREHENSIVE TEST CASES")
    print("=" * 70)

    fusion = FusionLogic(weights=(1.0, 1.0), uncertain_zone=(0.3, 0.7))

    # Define test cases
    test_cases = [
        {
            'name': 'Test 1: Both tiers high confidence phishing',
            'tier1': {'score': 0.95, 'label': 'phishing', 'confidence': 'high', 'escalate': False},
            'tier2': {'score': 0.88, 'label': 'phishing', 'confidence': 'high', 'escalate': False},
            'expected_escalate': False,
            'expected_label': 'phishing',
        },
        {
            'name': 'Test 2: Both tiers high confidence benign',
            'tier1': {'score': 0.08, 'label': 'benign', 'confidence': 'high', 'escalate': False},
            'tier2': {'score': 0.12, 'label': 'benign', 'confidence': 'high', 'escalate': False},
            'expected_escalate': False,
            'expected_label': 'benign',
        },
        {
            'name': 'Test 3: Both tiers uncertain (escalate=True)',
            'tier1': {'score': 0.45, 'label': 'benign', 'confidence': 'low', 'escalate': True},
            'tier2': {'score': 0.55, 'label': 'phishing', 'confidence': 'low', 'escalate': True},
            'expected_escalate': True,
            'expected_label': 'phishing',  # 0.5 weighted average
        },
        {
            'name': 'Test 4: Tier 1 confident, Tier 2 uncertain (no escalate)',
            'tier1': {'score': 0.92, 'label': 'phishing', 'confidence': 'high', 'escalate': False},
            'tier2': {'score': 0.50, 'label': 'phishing', 'confidence': 'low', 'escalate': True},
            'expected_escalate': False,  # Only one tier uncertain
            'expected_label': 'phishing',
        },
        {
            'name': 'Test 5: Only URL provided (tier2=None)',
            'tier1': {'score': 0.85, 'label': 'phishing', 'confidence': 'high', 'escalate': False},
            'tier2': None,
            'expected_escalate': False,  # tier1 is confident
            'expected_label': 'phishing',
        },
        {
            'name': 'Test 6: Only text provided (tier1=None)',
            'tier1': None,
            'tier2': {'score': 0.22, 'label': 'benign', 'confidence': 'high', 'escalate': False},
            'expected_escalate': False,  # tier2 is confident
            'expected_label': 'benign',
        },
        {
            'name': 'Test 7: Conflicting tiers (T1=0.9 phishing, T2=0.1 benign)',
            'tier1': {'score': 0.90, 'label': 'phishing', 'confidence': 'high', 'escalate': False},
            'tier2': {'score': 0.10, 'label': 'benign', 'confidence': 'high', 'escalate': False},
            'expected_escalate': False,  # Both confident (even if conflicting)
            'expected_label': 'phishing',  # weighted avg 0.5 -> phishing
        },
    ]

    # Run tests and collect results
    results = []
    all_passed = True

    for tc in test_cases:
        print(f"\n{tc['name']}")
        print("-" * 60)

        try:
            result = fusion.fuse_scores(tier1_result=tc['tier1'], tier2_result=tc['tier2'])

            # Validate output structure
            required_keys = ['score', 'label', 'risk_level', 'confidence', 'escalate', 'metadata']
            missing_keys = [k for k in required_keys if k not in result]
            if missing_keys:
                print(f"  ERROR: Missing keys in output: {missing_keys}")
                all_passed = False
                continue

            # Check escalation
            escalate_match = result['escalate'] == tc['expected_escalate']
            if not escalate_match:
                print(f"  FAIL: Expected escalate={tc['expected_escalate']}, got {result['escalate']}")
                all_passed = False

            # Check label
            label_match = result['label'] == tc['expected_label']
            if not label_match:
                print(f"  FAIL: Expected label={tc['expected_label']}, got {result['label']}")
                all_passed = False

            # Store result for summary table
            t1_score = tc['tier1']['score'] if tc['tier1'] else None
            t2_score = tc['tier2']['score'] if tc['tier2'] else None
            results.append({
                'name': tc['name'],
                't1_score': t1_score,
                't2_score': t2_score,
                'fused': result['score'],
                'risk': result['risk_level'],
                'escalate': result['escalate'],
                'passed': escalate_match and label_match
            })

            print(f"  T1 Score: {t1_score}")
            print(f"  T2 Score: {t2_score}")
            print(f"  Fused Score: {result['score']:.4f}")
            print(f"  Label: {result['label']}")
            print(f"  Risk Level: {result['risk_level']}")
            print(f"  Confidence: {result['confidence']}")
            print(f"  Escalate: {result['escalate']}")
            print(f"  Fusion Method: {result['metadata']['fusion_method']}")
            print(f"  Status: {'PASS' if escalate_match and label_match else 'FAIL'}")

        except Exception as e:
            print(f"  ERROR: {e}")
            all_passed = False

    # Print summary table
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY TABLE")
    print("=" * 70)
    print(f"| {'Test Case':<48} | {'T1':<5} | {'T2':<5} | {'Fused':<6} | {'Risk':<6} | {'Esc':<5} |")
    print(f"|{'-'*50}|{'-'*7}|{'-'*7}|{'-'*8}|{'-'*8}|{'-'*7}|")

    for r in results:
        t1_str = f"{r['t1_score']:.2f}" if r['t1_score'] is not None else "None"
        t2_str = f"{r['t2_score']:.2f}" if r['t2_score'] is not None else "None"
        name_short = r['name'][:48] if len(r['name']) <= 48 else r['name'][:45] + "..."
        print(f"| {name_short:<48} | {t1_str:<5} | {t2_str:<5} | {r['fused']:.4f} | {r['risk']:<6} | {str(r['escalate']):<5} |")

    # Final status
    print("\n" + "=" * 70)
    print("VALIDATION STATUS")
    print("=" * 70)

    passed_count = sum(1 for r in results if r['passed'])
    total_count = len(results)

    if all_passed:
        print(f"[PASS] All {total_count} test cases passed")
        print("[PASS] Output structure valid for all tests")
        print("[PASS] Escalation logic correct (BOTH tiers must be uncertain)")
    else:
        print(f"[FAIL] {passed_count}/{total_count} test cases passed")

    print("\n" + "=" * 70)
    if all_passed:
        print("ALL VALIDATION CHECKS PASSED")
    else:
        print("SOME VALIDATION CHECKS FAILED")
    print("=" * 70)
