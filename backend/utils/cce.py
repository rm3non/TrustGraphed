
"""
Confidence Computation Engine (CCE)
Computes confidence scores for assertions based on supporting evidence.
"""

from typing import List, Dict, Any
import re

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
            return 0.3  # Low confidence without citations
        
        words = len(text.split())
        citation_density = len(citations) / max(1, words / 50)  # Citations per 50 words
        return min(1.0, citation_density * 0.8 + 0.2)
    
    def compute_assertion_confidence(self, assertion: str, citations: List[str]) -> float:
        """Compute confidence score for a single assertion."""
        language_confidence = self.analyze_language_certainty(assertion)
        citation_support = self.check_citation_support(assertion, citations)
        
        # Weighted average
        confidence = (language_confidence * 0.6 + citation_support * 0.4)
        return min(1.0, confidence)
    
    def process(self, content: str, assertions: List[str], citations: List[str]) -> Dict[str, Any]:
        """Main processing function."""
        if not assertions:
            return {
                "module": self.name,
                "overall_confidence": 0.5,
                "assertion_confidences": [],
                "high_confidence_count": 0,
                "medium_confidence_count": 0,
                "low_confidence_count": 0,
                "average_citation_support": 0.0,
                "status": "processed"
            }
        
        assertion_confidences = []
        for assertion in assertions:
            confidence = self.compute_assertion_confidence(assertion, citations)
            assertion_confidences.append({
                "assertion": assertion[:100] + "..." if len(assertion) > 100 else assertion,
                "confidence": round(confidence, 3)
            })
        
        # Categorize confidence levels
        high_confidence = [c for c in assertion_confidences if c["confidence"] >= 0.8]
        medium_confidence = [c for c in assertion_confidences if 0.5 <= c["confidence"] < 0.8]
        low_confidence = [c for c in assertion_confidences if c["confidence"] < 0.5]
        
        overall_confidence = sum(c["confidence"] for c in assertion_confidences) / len(assertion_confidences)
        citation_support = self.check_citation_support(content, citations)
        
        return {
            "module": self.name,
            "overall_confidence": round(overall_confidence, 3),
            "assertion_confidences": assertion_confidences[:5],  # Limit for demo
            "high_confidence_count": len(high_confidence),
            "medium_confidence_count": len(medium_confidence),
            "low_confidence_count": len(low_confidence),
            "average_citation_support": round(citation_support, 3),
            "status": "processed"
        }
