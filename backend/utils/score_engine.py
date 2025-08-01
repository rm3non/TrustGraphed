
"""
TrustScore Engine
Aggregates module outputs into a final trust score.
"""

from typing import Dict, Any

class TrustScoreEngine:
    def __init__(self):
        self.name = "TrustScore Engine"
        self.version = "1.0.0"
        self.weights = {
            "source_data": 0.15,
            "integrity": 0.25,
            "confidence": 0.25,
            "authenticity": 0.35
        }
    
    def normalize_score(self, score: float) -> float:
        """Ensure score is between 0 and 1."""
        return max(0.0, min(1.0, score))
    
    def calculate_trust_score(self, module_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the final trust score from all module results."""
        
        # Extract scores from each module
        source_score = 0.8  # Default if SDG data is present
        if 'sdg_result' in module_results:
            sdg_data = module_results['sdg_result']
            source_score = sdg_data.get('extraction_confidence', 0.8)
        
        integrity_score = 0.8  # Default
        if 'aie_result' in module_results:
            aie_data = module_results['aie_result']
            integrity_score = aie_data.get('integrity_score', 0.8)
        
        confidence_score = 0.7  # Default
        if 'cce_result' in module_results:
            cce_data = module_results['cce_result']
            confidence_score = cce_data.get('overall_confidence', 0.7)
        
        authenticity_score = 0.8  # Default
        if 'zfp_result' in module_results:
            zfp_data = module_results['zfp_result']
            authenticity_score = zfp_data.get('authenticity_score', 0.8)
        
        # Calculate weighted trust score
        trust_score = (
            source_score * self.weights["source_data"] +
            integrity_score * self.weights["integrity"] +
            confidence_score * self.weights["confidence"] +
            authenticity_score * self.weights["authenticity"]
        )
        
        trust_score = self.normalize_score(trust_score)
        
        # Determine trust level
        if trust_score >= 0.8:
            trust_level = "HIGH"
        elif trust_score >= 0.6:
            trust_level = "MEDIUM"
        elif trust_score >= 0.4:
            trust_level = "LOW"
        else:
            trust_level = "VERY_LOW"
        
        return {
            "trust_score": round(trust_score, 3),
            "trust_level": trust_level,
            "component_scores": {
                "source_data": round(source_score, 3),
                "integrity": round(integrity_score, 3),
                "confidence": round(confidence_score, 3),
                "authenticity": round(authenticity_score, 3)
            },
            "weights_used": self.weights
        }
    
    def generate_insights(self, trust_score: float, module_results: Dict[str, Any]) -> List[str]:
        """Generate human-readable insights about the trust evaluation."""
        insights = []
        
        if trust_score >= 0.8:
            insights.append("Content shows high trustworthiness across all evaluated dimensions.")
        elif trust_score >= 0.6:
            insights.append("Content shows moderate trustworthiness with some areas for improvement.")
        else:
            insights.append("Content shows significant trust concerns that should be addressed.")
        
        # Add specific insights based on module results
        if 'zfp_result' in module_results:
            zfp_data = module_results['zfp_result']
            if zfp_data.get('total_flags', 0) > 0:
                insights.append(f"Detected {zfp_data['total_flags']} potential fabrication indicators.")
        
        if 'aie_result' in module_results:
            aie_data = module_results['aie_result']
            if aie_data.get('issues_found', 0) > 0:
                insights.append(f"Found {aie_data['issues_found']} integrity issues (contradictions/redundancies).")
        
        return insights
    
    def process(self, module_results: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing function."""
        score_data = self.calculate_trust_score(module_results)
        insights = self.generate_insights(score_data["trust_score"], module_results)
        
        return {
            "module": self.name,
            "trust_score": score_data["trust_score"],
            "trust_level": score_data["trust_level"],
            "component_scores": score_data["component_scores"],
            "weights_used": score_data["weights_used"],
            "insights": insights,
            "status": "computed"
        }
