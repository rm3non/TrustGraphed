
"""
Confidence Computation Engine (CCE)
Assigns confidence scores to assertions based on various factors.
"""

import re
from typing import List, Dict, Any

class ConfidenceComputationEngine:
    def __init__(self):
        self.name = "Confidence Computation Engine"
        self.version = "1.0.0"
        self.confidence_keywords = {
            "high": ["proven", "established", "confirmed", "verified", "certain"],
            "medium": ["likely", "probable", "suggests", "indicates", "appears"],
            "low": ["might", "could", "possibly", "maybe", "perhaps", "unclear"]
        }
    
    def analyze_language_certainty(self, text: str) -> float:
        """Analyze language patterns for certainty indicators."""
        text_lower = text.lower()
        
        high_confidence_count = sum(1 for word in self.confidence_keywords["high"] if word in text_lower)
        medium_confidence_count = sum(1 for word in self.confidence_keywords["medium"] if word in text_lower)
        low_confidence_count = sum(1 for word in self.confidence_keywords["low"] if word in text_lower)
        
        total_indicators = high_confidence_count + medium_confidence_count + low_confidence_count
        
        if total_indicators == 0:
            return 0.7  # Neutral confidence
        
        weighted_score = (high_confidence_count * 1.0 + medium_confidence_count * 0.6 + low_confidence_count * 0.3) / total_indicators
        return min(1.0, weighted_score)
    
    def check_citation_support(self, text: str, citations: List[str]) -> float:
        """Check if assertions are supported by citations."""
        if not citations:
            return 0.4  # Low confidence without citations
        
        words_count = len(text.split())
        citation_ratio = len(citations) / max(1, words_count / 50)  # Citations per ~50 words
        
        return min(1.0, 0.5 + citation_ratio * 0.5)
    
    def compute_assertion_confidence(self, assertion: str, citations: List[str]) -> float:
        """Compute confidence score for a single assertion."""
        language_confidence = self.analyze_language_certainty(assertion)
        citation_confidence = self.check_citation_support(assertion, citations)
        
        # Weighted average
        overall_confidence = (language_confidence * 0.6) + (citation_confidence * 0.4)
        return round(overall_confidence, 3)
    
    def process(self, content: str, assertions: List[str], citations: List[str]) -> Dict[str, Any]:
        """Main processing function."""
        assertion_confidences = []
        
        for assertion in assertions:
            confidence = self.compute_assertion_confidence(assertion, citations)
            assertion_confidences.append({
                "assertion": assertion,
                "confidence_score": confidence
            })
        
        overall_confidence = sum(ac["confidence_score"] for ac in assertion_confidences) / max(1, len(assertion_confidences))
        
        return {
            "module": self.name,
            "assertion_confidences": assertion_confidences,
            "overall_confidence": round(overall_confidence, 3),
            "total_assertions": len(assertions),
            "high_confidence_count": len([ac for ac in assertion_confidences if ac["confidence_score"] > 0.8]),
            "status": "computed"
        }
