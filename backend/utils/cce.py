"""
TrustGraphed Confidence Computation Engine (CCE)
Analyzes content confidence patterns and linguistic uncertainty markers
"""

import re
import string
from typing import Dict, List, Any

class ConfidenceComputationEngine:
    def __init__(self):
        # Uncertainty markers that suggest low confidence
        self.uncertainty_markers = [
            'might', 'maybe', 'possibly', 'could be', 'seems like', 'appears to',
            'suggests', 'indicates', 'likely', 'probably', 'perhaps', 'allegedly',
            'reportedly', 'supposedly', 'presumably', 'potentially', 'may be',
            'seems to', 'appears that', 'it is possible', 'it is likely',
            'some say', 'some believe', 'it is claimed', 'rumored', 'speculated'
        ]

        # High confidence markers
        self.confidence_markers = [
            'definitely', 'certainly', 'clearly', 'obviously', 'undoubtedly',
            'unquestionably', 'absolutely', 'precisely', 'exactly', 'specifically',
            'confirmed', 'verified', 'proven', 'established', 'documented'
        ]

    def process(self, content: str, assertions: List[str] = None, citations: List[str] = None) -> Dict[str, Any]:
        """
        Main processing method for confidence computation.
        """
        if assertions is None:
            assertions = []
        if citations is None:
            citations = []

        # Extract confidence signals
        confidence_signals = self._extract_confidence_signals(content)

        # Analyze assertion confidence
        assertion_confidence = self._analyze_assertion_confidence(assertions)

        # Calculate overall confidence score
        overall_confidence = self._calculate_overall_confidence(
            confidence_signals, assertion_confidence, len(citations)
        )

        return {
            'overall_confidence': overall_confidence,
            'confidence_signals': confidence_signals,
            'assertion_confidence': assertion_confidence,
            'high_confidence_count': len([a for a in assertion_confidence if a > 0.7]),
            'low_confidence_count': len([a for a in assertion_confidence if a < 0.4]),
            'uncertainty_markers_found': confidence_signals.get('uncertainty_count', 0),
            'confidence_markers_found': confidence_signals.get('confidence_count', 0)
        }

    def _extract_confidence_signals(self, content: str) -> Dict[str, Any]:
        """Extract confidence-related signals from content."""
        content_lower = content.lower()

        # Count uncertainty markers
        uncertainty_count = sum(1 for marker in self.uncertainty_markers 
                               if marker in content_lower)

        # Count confidence markers
        confidence_count = sum(1 for marker in self.confidence_markers 
                              if marker in content_lower)

        # Calculate confidence ratio
        total_markers = uncertainty_count + confidence_count
        confidence_ratio = confidence_count / total_markers if total_markers > 0 else 0.5

        # Analyze hedging language
        hedging_patterns = [
            r'\bmight\s+be\b', r'\bcould\s+be\b', r'\bmay\s+be\b',
            r'\bseems?\s+to\b', r'\bappears?\s+to\b', r'\btends?\s+to\b'
        ]

        hedging_count = sum(len(re.findall(pattern, content_lower)) 
                           for pattern in hedging_patterns)

        return {
            'uncertainty_count': uncertainty_count,
            'confidence_count': confidence_count,
            'confidence_ratio': confidence_ratio,
            'hedging_count': hedging_count,
            'total_markers': total_markers
        }

    def _analyze_assertion_confidence(self, assertions: List[str]) -> List[float]:
        """Analyze confidence level of individual assertions."""
        confidence_scores = []

        for assertion in assertions:
            assertion_lower = assertion.lower()

            # Check for uncertainty markers
            uncertainty_score = sum(1 for marker in self.uncertainty_markers 
                                  if marker in assertion_lower)

            # Check for confidence markers
            confidence_score = sum(1 for marker in self.confidence_markers 
                                 if marker in assertion_lower)

            # Base confidence (neutral)
            base_confidence = 0.6

            # Adjust based on markers
            if uncertainty_score > 0:
                base_confidence -= (uncertainty_score * 0.15)
            if confidence_score > 0:
                base_confidence += (confidence_score * 0.2)

            # Clamp between 0 and 1
            final_confidence = max(0.0, min(1.0, base_confidence))
            confidence_scores.append(final_confidence)

        return confidence_scores

    def _calculate_overall_confidence(self, signals: Dict[str, Any], 
                                    assertion_confidence: List[float], 
                                    citation_count: int) -> float:
        """Calculate overall confidence score."""
        if not assertion_confidence:
            base_confidence = 0.5
        else:
            base_confidence = sum(assertion_confidence) / len(assertion_confidence)

        # Adjust for uncertainty markers
        uncertainty_penalty = min(signals['uncertainty_count'] * 0.05, 0.3)
        base_confidence -= uncertainty_penalty

        # Boost for confidence markers
        confidence_boost = min(signals['confidence_count'] * 0.03, 0.2)
        base_confidence += confidence_boost

        # Citation boost
        citation_boost = min(citation_count * 0.1, 0.25)
        base_confidence += citation_boost

        # Hedging penalty
        hedging_penalty = min(signals['hedging_count'] * 0.08, 0.25)
        base_confidence -= hedging_penalty

        return max(0.0, min(1.0, base_confidence))

def compute_confidence_score(signals: dict, assertion_type: str = "unsure") -> dict:
    """
    Compute a TrustScore based on extracted signals and user-declared assertion type.

    Parameters:
        signals (dict): A dictionary of extracted content signals:
            - assertions: int
            - citations: int
            - contradictions: int
            - author_detected: bool
            - ai_likelihood: float (0-1)
        assertion_type (str): User declaration - original, ai, copied, mixed, unsure.

    Returns:
        dict: { final_score, breakdown, band }
    """

    # ---------- Base Score from Content Signals ----------
    base_score = 50  # Start with baseline score for having content

    # --- Citation Weight (Max 40 Points) ---
    if signals.get("citations", 0) > 0:
        citation_score = min(signals["citations"] * 8, 40)
        base_score += citation_score

    # --- Author/Metadata Bonus (Max +10) ---
    if signals.get("author_detected", False):
        base_score += 10

    # --- Contradiction Penalty (Max -30) ---
    contradiction_penalty = min(signals.get("contradictions", 0) * 10, 30)
    base_score -= contradiction_penalty

    # ---------- Transparency-Aware AI Handling ----------
    # Adjust AI penalty based on content declaration honesty
    ai_likelihood = signals.get("ai_likelihood", 0)
    
    if assertion_type.lower() in ["ai", "mixed"]:
        # If user honestly declares AI/mixed content, reduce AI penalty significantly
        ai_penalty = int(ai_likelihood * 8)  # Reduced penalty for honest declaration
    else:
        # Standard penalty for undeclared or claimed original content
        ai_penalty = int(ai_likelihood * 20)
    
    base_score -= ai_penalty

    # ---------- Trapdoor Logic (Zero-Fabrication) ----------
    if signals.get("citations", 0) == 0 and not signals.get("author_detected", False):
        # No provenance = score floor, but less harsh for declared AI content
        if assertion_type.lower() in ["ai", "mixed"]:
            base_score = min(base_score, 40)  # Higher floor for honest AI declaration
        else:
            base_score = min(base_score, 25)  # Standard floor

    # ---------- Transparency Rewards (Honesty Bonus) ----------
    # Reward honest content declaration - transparency increases trust
    transparency_multipliers = {
        "original": 1.0,     # Standard score for claimed original content
        "ai": 1.20,          # 20% BONUS for honestly declaring AI content
        "copied": 1.15,      # 15% BONUS for honestly declaring copied content  
        "mixed": 1.18,       # 18% BONUS for honestly declaring mixed sources
        "unsure": 0.80       # 20% penalty for refusing to declare
    }
    
    transparency_multiplier = transparency_multipliers.get(assertion_type.lower(), 0.80)
    final_score = max(0, min(100, base_score * transparency_multiplier))

    # ---------- Score Banding ----------
    if final_score >= 75:
        band = "High Trust"
    elif final_score >= 50:
        band = "Verified"
    elif final_score >= 25:
        band = "Low Trust"
    else:
        band = "Unverified"

    # ---------- Breakdown for Transparency ----------
    breakdown = {
        "base_signals_score": base_score,
        "citations_contribution": citation_score if signals.get("citations", 0) > 0 else 0,
        "author_bonus": 10 if signals.get("author_detected", False) else 0,
        "contradiction_penalty": contradiction_penalty,
        "ai_likelihood_penalty": ai_penalty,
        "transparency_multiplier": transparency_multiplier,
        "final_score": final_score
    }

    return {
        "final_score": final_score,
        "band": band,
        "breakdown": breakdown
    }

    # ---------- Assertion Type Adjustment ----------
    base_score = apply_assertion_penalty(base_score, assertion_type)

    # Clamp final score between 0 and 100
    final_score = max(0, min(100, round(base_score, 2)))

    # ---------- Determine Score Band ----------
    if final_score >= 75:
        band = "High Trust"
    elif final_score >= 50:
        band = "Verified"
    elif final_score >= 25:
        band = "Low Trust"
    else:
        band = "Unverified"

    # ---------- Return Detailed Breakdown ----------
    return {
        "final_score": final_score,
        "band": band,
        "breakdown": {
            "citations_score": citation_score,
            "contradiction_penalty": contradiction_penalty,
            "ai_penalty": ai_penalty,
            "assertion_type": assertion_type
        }
    }


def apply_assertion_penalty(score: float, assertion_type: str) -> float:
    """
    Adjust score based on user-declared assertion type.
    """
    penalties = {
        "original": 1.0,
        "ai": 0.85,
        "copied": 0.7,
        "mixed": 0.8,
        "unsure": 0.6
    }
    return score * penalties.get(assertion_type.lower(), 0.7)