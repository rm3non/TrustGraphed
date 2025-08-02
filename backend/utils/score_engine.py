
"""
TrustScore Engine
Aggregates results from all modules into a final trust score.
"""

from typing import Dict, Any, List

class TrustScoreEngine:
    def __init__(self):
        self.name = "TrustScore Engine"
        self.version = "1.0.0"
        self.module_weights = {
            "sdg_result": 0.15,      # Source Data Grappler
            "aie_result": 0.25,      # Assertion Integrity Engine
            "cce_result": 0.25,      # Confidence Computation Engine
            "zfp_result": 0.35       # Zero-Fabrication Protocol
        }
    
    def extract_module_score(self, module_result: Dict[str, Any], module_name: str) -> float:
        """Extract numerical score from a module result."""
        if module_name == "sdg_result":
            return module_result.get("extraction_confidence", 0.5)
        elif module_name == "aie_result":
            return module_result.get("integrity_score", 0.5)
        elif module_name == "cce_result":
            return module_result.get("overall_confidence", 0.5)
        elif module_name == "zfp_result":
            return module_result.get("authenticity_score", 0.5)
        else:
            return 0.5
    
    def calculate_weighted_score(self, results: Dict[str, Any]) -> float:
        """Calculate weighted trust score from all module results."""
        total_score = 0.0
        total_weight = 0.0
        
        for module_name, weight in self.module_weights.items():
            if module_name in results:
                score = self.extract_module_score(results[module_name], module_name)
                total_score += score * weight
                total_weight += weight
        
        # Normalize by actual weights used
        if total_weight > 0:
            return total_score / total_weight
        else:
            return 0.5  # Default score
    
    def determine_trust_level(self, score: float) -> str:
        """Determine trust level based on numerical score."""
        if score >= 0.9:
            return "VERY HIGH"
        elif score >= 0.75:
            return "HIGH"
        elif score >= 0.6:
            return "MODERATE"
        elif score >= 0.4:
            return "LOW"
        else:
            return "VERY LOW"
    
    def generate_insights(self, results: Dict[str, Any], trust_score: float) -> List[str]:
        """Generate insights based on module results and trust score."""
        insights = []
        
        # SDG insights
        if "sdg_result" in results:
            sdg = results["sdg_result"]
            if sdg.get("assertions_count", 0) > 10:
                insights.append("Content contains many assertions - thorough fact-checking recommended")
            if sdg.get("citations_count", 0) == 0:
                insights.append("No citations found - claims may lack supporting evidence")
        
        # AIE insights
        if "aie_result" in results:
            aie = results["aie_result"]
            if aie.get("issues_found", 0) > 0:
                insights.append(f"Found {aie['issues_found']} integrity issues that may affect reliability")
        
        # CCE insights
        if "cce_result" in results:
            cce = results["cce_result"]
            if cce.get("overall_confidence", 0) < 0.5:
                insights.append("Low confidence language detected - claims may be speculative")
        
        # ZFP insights
        if "zfp_result" in results:
            zfp = results["zfp_result"]
            if zfp.get("total_flags", 0) > 0:
                insights.append(f"Detected {zfp['total_flags']} potential fabrication indicators")
            if zfp.get("authenticity_score", 1) < 0.5:
                insights.append("Content shows signs of potential AI generation or fabrication")
        
        # Overall insights
        if trust_score < 0.4:
            insights.append("Overall trust score is low - recommend additional verification")
        elif trust_score > 0.8:
            insights.append("Content demonstrates high trustworthiness across multiple dimensions")
        
        return insights[:5]  # Limit to 5 insights
    
    def get_component_scores(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Get individual component scores for display."""
        component_scores = {}
        
        for module_name in self.module_weights.keys():
            if module_name in results:
                score = self.extract_module_score(results[module_name], module_name)
                
                # Convert module names to readable names
                readable_names = {
                    "sdg_result": "Data Extraction",
                    "aie_result": "Assertion Integrity", 
                    "cce_result": "Confidence Analysis",
                    "zfp_result": "Fabrication Detection"
                }
                
                readable_name = readable_names.get(module_name, module_name)
                component_scores[readable_name] = round(score, 3)
        
        return component_scores
    
    def process(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing function."""
        trust_score = self.calculate_weighted_score(results)
        trust_level = self.determine_trust_level(trust_score)
        component_scores = self.get_component_scores(results)
        insights = self.generate_insights(results, trust_score)
        
        return {
            "module": self.name,
            "trust_score": round(trust_score, 3),
            "trust_level": trust_level,
            "component_scores": component_scores,
            "insights": insights,
            "methodology": "Weighted aggregation of 4 core trust evaluation modules",
            "status": "computed"
        }
