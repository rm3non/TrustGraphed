"""
TrustGraphed Confidence Computation Engine (CCE)
Consolidated scoring logic with rule-based penalties and assertion type weighting
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

def compute_trust_score(signals: dict, assertion_type: str = "unsure") -> dict:
    """
    CONSOLIDATED TrustScore computation with rule-based penalties and trapdoors.

    Parameters:
        signals (dict): Extracted content signals
            - assertions: int (count of assertions found)
            - citations: int (count of citations found) 
            - contradictions: int (logical contradictions detected)
            - author_detected: bool (author/metadata present)
            - ai_likelihood: float (0-1, AI generation probability)
        assertion_type (str): User declaration - original, ai, copied, mixed, unsure

    Returns:
        dict: {final_score, band, breakdown, insights}
    """

    # ========== RULE-BASED SCORING SYSTEM ==========
    
    # Initialize breakdown dictionary
    breakdown = {}

    # ========== BASE SCORING (0-100 points) ==========
    base_score = 60  # Start with higher neutral baseline for more reasonable ranges

    # ========== ASSERTION SCORING (Max +20 points) ==========
    assertions = signals.get("assertions", 0)
    if assertions > 0:
        # More generous assertion scoring with better progression
        assertion_score = min(assertions * 2.5, 20)
        base_score += assertion_score
        breakdown["assertion_contribution"] = assertion_score

    # ========== CITATION SCORING (Max +20 points) ==========
    citations = signals.get("citations", 0)
    if citations > 0:
        # Improved citation scoring with better progression
        if citations == 1:
            citation_score = 10
        elif citations == 2:
            citation_score = 15
        elif citations >= 3:
            citation_score = 20
        else:
            citation_score = min(citations * 6, 20)

        base_score += citation_score
        breakdown["citation_contribution"] = citation_score

    # ========== AUTHOR/METADATA BONUS (+10 points) ==========
    if signals.get("author_detected", False):
        base_score += 10
        breakdown["author_bonus"] = 10

    # ========== CONTRADICTION PENALTY (Max -30 points) ==========
    contradictions = signals.get("contradictions", 0)
    if contradictions > 0:
        contradiction_penalty = min(contradictions * 10, 30)
        base_score -= contradiction_penalty
        breakdown["contradiction_penalty"] = contradiction_penalty

    # ========== TRANSPARENCY ALIGNMENT VERIFICATION ==========
    ai_likelihood = signals.get("ai_likelihood", 0)
    transparency_penalty = 0

    # Penalize misalignment between declaration and detected characteristics
    if assertion_type.lower() == "original" and ai_likelihood > 0.6:
        # High AI likelihood but claimed as original = transparency issue
        transparency_penalty = int(ai_likelihood * 20)  # Up to 20 point penalty
        breakdown["transparency_alignment_penalty"] = transparency_penalty
        base_score -= transparency_penalty

    # ========== HARD TRAPDOORS (Zero-Fabrication Enforcement) ==========
    # Trapdoor 1: No citations + No author = Fabrication risk
    if citations == 0 and not signals.get("author_detected", False):
        if assertion_type.lower() in ["ai", "mixed"]:
            # More lenient for honest AI declaration
            base_score = min(base_score, 40)
        else:
            # Standard trapdoor for undeclared content
            base_score = min(base_score, 25)
        breakdown["trapdoor_applied"] = True

    # Trapdoor 2: High AI + Original claim = Max 30 points
    if assertion_type.lower() == "original" and ai_likelihood > 0.7:
        base_score = min(base_score, 30)
        breakdown["trapdoor_applied"] = True

    # ========== ASSERTION TYPE TRANSPARENCY MULTIPLIERS ==========
    transparency_multipliers = {
        "original": 1.0,     # Standard evaluation 
        "ai": 1.10,          # 10% BONUS for transparent AI declaration
        "copied": 1.10,      # 10% BONUS for transparent copied content declaration
        "mixed": 1.15,       # 15% BONUS for transparent mixed sources declaration  
        "unsure": 0.70       # 30% PENALTY for undeclared content - encourages transparency
    }

    transparency_multiplier = transparency_multipliers.get(assertion_type.lower(), 0.80)
    breakdown["transparency_multiplier"] = transparency_multiplier

    # Apply transparency multiplier
    final_score = base_score * transparency_multiplier

    # Clamp final score between 0 and 100
    final_score = max(0, min(100, round(final_score, 1)))
    breakdown["final_score"] = final_score

    # ========== TRUST BAND CLASSIFICATION ==========
    if final_score >= 75:
        band = "High Trust"
        trust_level = "HIGH"
    elif final_score >= 50:
        band = "Verified" 
        trust_level = "MEDIUM"
    elif final_score >= 25:
        band = "Low Trust"
        trust_level = "LOW"
    else:
        band = "Unverified"
        trust_level = "VERY LOW"

    # ========== GENERATE INSIGHTS ==========
    insights = []

    # Citation insights
    if citations == 0:
        insights.append("⚠️ No citations found - claims lack supporting evidence")
    elif citations == 1:
        insights.append("📄 Single citation found - additional sources would strengthen credibility")
    elif citations >= 3:
        insights.append("✅ Well-cited content with multiple supporting sources")

    # Transparency insights  
    if assertion_type.lower() in ["ai", "copied", "mixed"]:
        insights.append("✅ TRANSPARENCY: Content sources openly declared - builds reader trust")
    elif assertion_type.lower() == "unsure":
        insights.append("⚠️ Content source undeclared - readers cannot assess information origin")

    # AI alignment insights
    if assertion_type.lower() == "original" and ai_likelihood > 0.6:
        insights.append("🚨 TRANSPARENCY MISMATCH: High AI characteristics detected but claimed as original")

    # Trapdoor insights
    if breakdown["trapdoor_applied"]:
        insights.append("⛔ TRAPDOOR ACTIVATED: Critical trust factors missing - score capped")

    # Overall score insight
    if final_score >= 75:
        insights.append("🎯 High trust score - content demonstrates strong credibility indicators")
    elif final_score < 25:
        insights.append("📉 Very low trust score - recommend additional verification before use")

    return {
        "final_score": final_score,
        "band": band,
        "trust_level": trust_level,
        "breakdown": breakdown,
        "insights": insights,
        "assertion_type": assertion_type,
        "scoring_method": "Rule-based with transparency weighting and fabrication trapdoors"
    }

# Legacy function name for backward compatibility
def compute_confidence_score(signals: dict, assertion_type: str = "unsure") -> dict:
    """Backward compatibility wrapper for compute_trust_score."""
    return compute_trust_score(signals, assertion_type)