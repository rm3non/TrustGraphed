
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
            "high": ["proven", "established", "confirmed", "verified", "certain", "documented", "according to"],
            "medium": ["likely", "probable", "suggests", "indicates", "appears", "research shows"],
            "low": ["might", "could", "possibly", "maybe", "perhaps", "unclear", "seems", "appears to"]
        }
        
        # AI generation indicators
        self.ai_markers = [
            "comprehensive overview", "it's important to note", "furthermore", "moreover",
            "in conclusion", "to summarize", "key takeaways", "in summary",
            "as an ai", "i don't have access", "i cannot", "i'm not able to"
        ]
        
        # Fabrication red flags
        self.fabrication_flags = [
            "studies show", "research indicates", "experts agree", "it is well known",
            "many believe", "according to sources", "data suggests"
        ]
    
    def analyze_language_certainty(self, text: str) -> float:
        """Analyze language patterns for certainty indicators."""
        text_lower = text.lower()
        
        high_confidence_count = sum(1 for word in self.confidence_keywords["high"] if word in text_lower)
        medium_confidence_count = sum(1 for word in self.confidence_keywords["medium"] if word in text_lower)
        low_confidence_count = sum(1 for word in self.confidence_keywords["low"] if word in text_lower)
        
        total_indicators = high_confidence_count + medium_confidence_count + low_confidence_count
        
        if total_indicators == 0:
            return 0.3  # Lower default for no confidence indicators
        
        weighted_score = (high_confidence_count * 1.0 + medium_confidence_count * 0.6 + low_confidence_count * 0.3) / total_indicators
        return min(1.0, weighted_score)
    
    def check_citation_support(self, text: str, citations: List[str]) -> float:
        """Check if assertions are supported by citations with hard thresholds."""
        if not citations or len(citations) == 0:
            return 0.0  # HARD TRAPDOOR: No citations = 0 score
        
        words = len(text.split())
        if words > 100 and len(citations) == 0:
            return 0.0  # HARD TRAPDOOR: Long content without citations
            
        citation_density = len(citations) / max(1, words / 50)  # Citations per 50 words
        return min(1.0, citation_density * 0.8 + 0.2)
    
    def detect_ai_generation_markers(self, text: str) -> float:
        """Detect AI generation patterns - returns penalty score (0 = likely AI, 1 = likely human)."""
        text_lower = text.lower()
        
        ai_marker_count = sum(1 for marker in self.ai_markers if marker in text_lower)
        fabrication_flag_count = sum(1 for flag in self.fabrication_flags if flag in text_lower)
        
        # Check for repetitive structures typical of AI
        sentences = text.split('.')
        if len(sentences) > 5:
            # Check for repetitive sentence starts
            starts = [s.strip()[:20].lower() for s in sentences if s.strip()]
            unique_starts = len(set(starts))
            repetition_ratio = unique_starts / len(starts) if starts else 1
            
            if repetition_ratio < 0.7:  # High repetition
                ai_marker_count += 2
        
        # Penalty calculation
        total_penalties = ai_marker_count + fabrication_flag_count
        if total_penalties == 0:
            return 1.0
        
        # Strong penalty for AI indicators
        penalty_score = max(0.0, 1.0 - (total_penalties * 0.3))
        return penalty_score
    
    def check_provenance_markers(self, text: str) -> float:
        """Check for human authorship and provenance markers."""
        text_lower = text.lower()
        
        human_markers = [
            "i interviewed", "i observed", "i witnessed", "in my experience",
            "i conducted", "our research", "we found", "our study",
            "personal communication", "field notes", "interview with"
        ]
        
        source_markers = [
            "doi:", "isbn:", "http://", "https://", "www.",
            "published in", "journal of", "proceedings of",
            "university of", "institute of", "according to [source]"
        ]
        
        human_count = sum(1 for marker in human_markers if marker in text_lower)
        source_count = sum(1 for marker in source_markers if marker in text_lower)
        
        provenance_score = min(1.0, (human_count * 0.3 + source_count * 0.2))
        return provenance_score
    
    def apply_hard_trapdoors(self, text: str, citations: List[str]) -> Dict[str, Any]:
        """Apply hard rule-based trapdoors that can force score to 0."""
        trapdoors = {
            "triggered": False,
            "reasons": [],
            "force_score": None
        }
        
        # TRAPDOOR 1: No citations for substantial content
        if len(text.split()) > 50 and len(citations) == 0:
            trapdoors["triggered"] = True
            trapdoors["reasons"].append("Substantial content (>50 words) with zero citations")
            trapdoors["force_score"] = 0.0
        
        # TRAPDOOR 2: High AI generation probability
        ai_score = self.detect_ai_generation_markers(text)
        if ai_score < 0.3:
            trapdoors["triggered"] = True
            trapdoors["reasons"].append("High probability of AI generation detected")
            trapdoors["force_score"] = 0.1  # Near-zero but not absolute zero
        
        # TRAPDOOR 3: No provenance markers in academic/factual content
        if len(text.split()) > 100:
            provenance = self.check_provenance_markers(text)
            if provenance == 0.0:
                trapdoors["triggered"] = True
                trapdoors["reasons"].append("No provenance or authorship markers found")
                if trapdoors["force_score"] is None:
                    trapdoors["force_score"] = 0.2
        
        # TRAPDOOR 4: Vague attribution without specifics
        vague_patterns = [
            r"studies show", r"research indicates", r"experts say",
            r"it is known", r"sources suggest", r"data shows"
        ]
        
        vague_count = sum(1 for pattern in vague_patterns if re.search(pattern, text.lower()))
        if vague_count > 2:
            trapdoors["triggered"] = True
            trapdoors["reasons"].append(f"Multiple vague attributions ({vague_count}) without specific sources")
            if trapdoors["force_score"] is None:
                trapdoors["force_score"] = 0.15
        
        return trapdoors
    
    def compute_assertion_confidence(self, assertion: str, citations: List[str]) -> float:
        """Compute confidence score for a single assertion with hard rules."""
        # Apply trapdoors first
        trapdoors = self.apply_hard_trapdoors(assertion, citations)
        if trapdoors["triggered"] and trapdoors["force_score"] is not None:
            return trapdoors["force_score"]
        
        language_confidence = self.analyze_language_certainty(assertion)
        citation_support = self.check_citation_support(assertion, citations)
        ai_authenticity = self.detect_ai_generation_markers(assertion)
        provenance = self.check_provenance_markers(assertion)
        
        # Weighted calculation with authenticity as critical factor
        confidence = (
            language_confidence * 0.2 +  # Reduced weight
            citation_support * 0.4 +     # High weight for citations
            ai_authenticity * 0.3 +      # High weight for authenticity
            provenance * 0.1              # Provenance bonus
        )
        
        return min(1.0, confidence)
    
    def process(self, content: str, assertions: List[str], citations: List[str]) -> Dict[str, Any]:
        """Main processing function with enhanced rule-based logic."""
        if not assertions:
            return {
                "module": self.name,
                "overall_confidence": 0.1,  # Very low for no assertions
                "assertion_confidences": [],
                "high_confidence_count": 0,
                "medium_confidence_count": 0,
                "low_confidence_count": 0,
                "average_citation_support": 0.0,
                "trapdoors_triggered": [],
                "ai_generation_risk": "unknown",
                "status": "processed"
            }
        
        # Check global trapdoors
        global_trapdoors = self.apply_hard_trapdoors(content, citations)
        
        assertion_confidences = []
        trapdoors_triggered = []
        
        for assertion in assertions:
            confidence = self.compute_assertion_confidence(assertion, citations)
            assertion_confidences.append({
                "assertion": assertion[:100] + "..." if len(assertion) > 100 else assertion,
                "confidence": round(confidence, 3)
            })
            
            # Track individual trapdoors
            assertion_trapdoors = self.apply_hard_trapdoors(assertion, citations)
            if assertion_trapdoors["triggered"]:
                trapdoors_triggered.extend(assertion_trapdoors["reasons"])
        
        # Categorize confidence levels
        high_confidence = [c for c in assertion_confidences if c["confidence"] >= 0.8]
        medium_confidence = [c for c in assertion_confidences if 0.5 <= c["confidence"] < 0.8]
        low_confidence = [c for c in assertion_confidences if c["confidence"] < 0.5]
        
        # Calculate overall confidence with global penalties
        base_confidence = sum(c["confidence"] for c in assertion_confidences) / len(assertion_confidences)
        
        # Apply global trapdoor
        if global_trapdoors["triggered"] and global_trapdoors["force_score"] is not None:
            overall_confidence = global_trapdoors["force_score"]
            trapdoors_triggered.extend(global_trapdoors["reasons"])
        else:
            overall_confidence = base_confidence
        
        # Determine AI generation risk
        ai_score = self.detect_ai_generation_markers(content)
        if ai_score < 0.3:
            ai_risk = "HIGH"
        elif ai_score < 0.6:
            ai_risk = "MEDIUM"
        else:
            ai_risk = "LOW"
        
        citation_support = self.check_citation_support(content, citations)
        
        return {
            "module": self.name,
            "overall_confidence": round(overall_confidence, 3),
            "assertion_confidences": assertion_confidences[:5],  # Limit for demo
            "high_confidence_count": len(high_confidence),
            "medium_confidence_count": len(medium_confidence),
            "low_confidence_count": len(low_confidence),
            "average_citation_support": round(citation_support, 3),
            "trapdoors_triggered": list(set(trapdoors_triggered))[:3],  # Unique, limited
            "ai_generation_risk": ai_risk,
            "provenance_score": round(self.check_provenance_markers(content), 3),
            "status": "processed"
        }
