
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
        """Calculate weighted trust score with hard enforcement rules."""
        # CRITICAL ENFORCEMENT RULES - Check for deal-breakers first
        
        # Rule 1: Zero citations with substantial content = untrusted
        if "cce_result" in results:
            cce = results["cce_result"]
            if cce.get("average_citation_support", 0) == 0.0 and cce.get("high_confidence_count", 0) == 0:
                return 0.1  # Near-zero score for uncited content
        
        # Rule 2: High AI generation risk = untrusted
        if "cce_result" in results:
            cce = results["cce_result"]
            if cce.get("ai_generation_risk", "LOW") == "HIGH":
                return 0.15  # Very low score for likely AI content
        
        # Rule 3: Multiple trapdoors triggered = untrusted
        if "cce_result" in results:
            cce = results["cce_result"]
            trapdoors = cce.get("trapdoors_triggered", [])
            if len(trapdoors) >= 2:
                return 0.2  # Low score for multiple red flags
        
        # Rule 4: Low authenticity with no citations = fabricated
        if "zfp_result" in results and "cce_result" in results:
            zfp = results["zfp_result"]
            cce = results["cce_result"]
            if (zfp.get("authenticity_score", 1) < 0.3 and 
                cce.get("average_citation_support", 0) == 0.0):
                return 0.05  # Extremely low for likely fabrication
        
        # If no deal-breakers, calculate weighted score
        total_score = 0.0
        total_weight = 0.0
        
        for module_name, weight in self.module_weights.items():
            if module_name in results:
                score = self.extract_module_score(results[module_name], module_name)
                total_score += score * weight
                total_weight += weight
        
        # Normalize by actual weights used
        if total_weight > 0:
            base_score = total_score / total_weight
            
            # Apply additional penalties for borderline cases
            if "cce_result" in results:
                cce = results["cce_result"]
                if cce.get("ai_generation_risk", "LOW") == "MEDIUM":
                    base_score *= 0.7  # 30% penalty for medium AI risk
            
            return base_score
        else:
            return 0.1  # Very low default score
    
    def determine_trust_level(self, score: float) -> str:
        """Determine trust level based on numerical score with stricter thresholds."""
        if score >= 0.85:
            return "VERY HIGH"
        elif score >= 0.65:
            return "HIGH"
        elif score >= 0.45:
            return "MODERATE"
        elif score >= 0.25:
            return "LOW"
        elif score >= 0.1:
            return "VERY LOW"
        else:
            return "UNVERIFIABLE"
    
    def generate_detailed_explanation(self, results: Dict[str, Any], trust_score: float) -> Dict[str, Any]:
        """Generate detailed explanations for the trust score computation."""
        explanations = {
            "overall_explanation": self._explain_overall_score(trust_score),
            "component_explanations": {},
            "methodology_details": self._get_methodology_details(),
            "score_breakdown": self._get_score_breakdown(results),
            "recommendations": self._generate_recommendations(results, trust_score)
        }
        
        # Generate detailed explanations for each component
        for module_name in self.module_weights.keys():
            if module_name in results:
                explanations["component_explanations"][module_name] = self._explain_component(
                    module_name, results[module_name]
                )
        
        return explanations
    
    def _explain_overall_score(self, trust_score: float) -> str:
        """Explain what the overall trust score means."""
        if trust_score >= 0.9:
            return f"Score {trust_score:.3f}/1.0 (VERY HIGH): This content demonstrates exceptional trustworthiness across all evaluation dimensions. The assertions are well-supported, logically consistent, and show minimal risk of fabrication."
        elif trust_score >= 0.75:
            return f"Score {trust_score:.3f}/1.0 (HIGH): This content shows strong trustworthiness indicators. Most assertions appear reliable with good supporting evidence and minimal fabrication risk."
        elif trust_score >= 0.6:
            return f"Score {trust_score:.3f}/1.0 (MODERATE): This content has mixed trustworthiness signals. Some aspects are reliable, but there may be unsupported claims or moderate fabrication risk requiring additional verification."
        elif trust_score >= 0.4:
            return f"Score {trust_score:.3f}/1.0 (LOW): This content shows concerning trust indicators. Many assertions may be unsupported, contradictory, or show signs of fabrication. Careful verification is recommended."
        else:
            return f"Score {trust_score:.3f}/1.0 (VERY LOW): This content has significant trustworthiness issues including potential fabrication, contradictions, or unsupported claims. Use with extreme caution."
    
    def _explain_component(self, module_name: str, module_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed explanation for each component."""
        if module_name == "sdg_result":
            return {
                "name": "Source Data Grappler (SDG)",
                "weight": "15%",
                "score": module_result.get("extraction_confidence", 0.5),
                "explanation": f"Analyzed {module_result.get('assertions_count', 0)} assertions and found {module_result.get('citations_count', 0)} citations. This component evaluates how well structured and extractable the content's claims are.",
                "impact": "Higher scores indicate well-structured content with clear, identifiable assertions.",
                "details": {
                    "assertions_found": module_result.get('assertions_count', 0),
                    "citations_found": module_result.get('citations_count', 0),
                    "what_this_means": "More citations and well-formed assertions indicate better documentation and potential verifiability."
                }
            }
        elif module_name == "aie_result":
            return {
                "name": "Assertion Integrity Engine (AIE)",
                "weight": "25%",
                "score": module_result.get("integrity_score", 0.5),
                "explanation": f"Detected {module_result.get('issues_found', 0)} integrity issues including contradictions, redundancies, and unsupported claims. This heavily weighted component checks for logical consistency.",
                "impact": "Issues found here significantly impact trust score as they indicate potential reliability problems.",
                "details": {
                    "issues_found": module_result.get('issues_found', 0),
                    "contradictions": len(module_result.get('contradictions', [])),
                    "redundancies": len(module_result.get('redundancies', [])),
                    "what_this_means": "Contradictions and unsupported claims are red flags for content reliability and factual accuracy."
                }
            }
        elif module_name == "cce_result":
            return {
                "name": "Confidence Computation Engine (CCE)",
                "weight": "25%",
                "score": module_result.get("overall_confidence", 0.5),
                "explanation": f"Analyzed language patterns and citation support. Found {module_result.get('high_confidence_count', 0)} high-confidence assertions out of total analyzed. User declared content as: '{module_result.get('content_assertion', 'unknown')}'.",
                "impact": "Confident language with proper citation support increases trustworthiness significantly.",
                "details": {
                    "high_confidence_assertions": module_result.get('high_confidence_count', 0),
                    "medium_confidence_assertions": module_result.get('medium_confidence_count', 0),
                    "low_confidence_assertions": module_result.get('low_confidence_count', 0),
                    "citation_support_score": module_result.get('average_citation_support', 0),
                    "what_this_means": "Tentative language ('might', 'could') without citations suggests speculative content."
                }
            }
        elif module_name == "zfp_result":
            return {
                "name": "Zero-Fabrication Protocol (ZFP)",
                "weight": "35% (Highest)",
                "score": module_result.get("authenticity_score", 0.5),
                "explanation": f"Detected {module_result.get('total_flags', 0)} fabrication indicators with authenticity score of {module_result.get('authenticity_score', 0):.3f}. This is the most heavily weighted component.",
                "impact": "As the highest-weighted component, fabrication indicators have the strongest impact on final trust score.",
                "details": {
                    "ai_artifacts_found": len(module_result.get('ai_artifacts', [])),
                    "suspicious_patterns": len(module_result.get('suspicious_patterns', [])),
                    "fact_density": module_result.get('fact_density', 0),
                    "fabrication_risk": module_result.get('fabrication_risk', 0),
                    "what_this_means": "AI-generated content indicators, vague statistics, and low fact density suggest potential fabrication."
                }
            }
        
        return {"name": module_name, "explanation": "Unknown component"}
    
    def _get_methodology_details(self) -> Dict[str, Any]:
        """Explain the evaluation methodology in detail."""
        return {
            "approach": "Multi-dimensional weighted aggregation",
            "components": {
                "Source Data Grappler (15%)": "Extracts and counts assertions, citations, and structural elements",
                "Assertion Integrity Engine (25%)": "Detects contradictions, redundancies, and unsupported claims",
                "Confidence Computation Engine (25%)": "Analyzes certainty language and citation support",
                "Zero-Fabrication Protocol (35%)": "Identifies AI-generated content and fabrication indicators"
            },
            "weighting_rationale": {
                "why_zfp_highest": "Fabrication detection receives highest weight (35%) because fabricated content poses the greatest risk to trustworthiness",
                "why_aie_cce_equal": "Integrity and confidence are equally weighted (25% each) as both are critical for reliable information",
                "why_sdg_lowest": "Data extraction receives lowest weight (15%) as it measures structure rather than veracity"
            },
            "score_calculation": "Final score = (SDG×0.15) + (AIE×0.25) + (CCE×0.25) + (ZFP×0.35)"
        }
    
    def _get_score_breakdown(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Provide numerical breakdown of score calculation."""
        breakdown = {}
        total_weighted_score = 0
        
        for module_name, weight in self.module_weights.items():
            if module_name in results:
                score = self.extract_module_score(results[module_name], module_name)
                weighted_contribution = score * weight
                total_weighted_score += weighted_contribution
                
                readable_names = {
                    "sdg_result": "Source Data Grappler",
                    "aie_result": "Assertion Integrity Engine",
                    "cce_result": "Confidence Computation Engine",
                    "zfp_result": "Zero-Fabrication Protocol"
                }
                
                breakdown[readable_names[module_name]] = {
                    "raw_score": round(score, 3),
                    "weight": f"{weight*100:.0f}%",
                    "weighted_contribution": round(weighted_contribution, 3),
                    "calculation": f"{score:.3f} × {weight} = {weighted_contribution:.3f}"
                }
        
        breakdown["final_calculation"] = {
            "total_weighted_score": round(total_weighted_score, 3),
            "formula": " + ".join([f"{v['weighted_contribution']:.3f}" for v in breakdown.values() if isinstance(v, dict) and 'weighted_contribution' in v])
        }
        
        return breakdown
    
    def _generate_recommendations(self, results: Dict[str, Any], trust_score: float) -> List[str]:
        """Generate specific recommendations based on the analysis."""
        recommendations = []
        
        # Overall score recommendations
        if trust_score < 0.4:
            recommendations.append("🚨 HIGH PRIORITY: Verify all claims through independent sources before using this content")
            recommendations.append("📋 Consider fact-checking each assertion individually")
        elif trust_score < 0.6:
            recommendations.append("⚠️ MODERATE CAUTION: Cross-reference key claims with authoritative sources")
        elif trust_score > 0.8:
            recommendations.append("✅ HIGH CONFIDENCE: Content appears trustworthy but always verify critical information")
        
        # Component-specific recommendations
        if "sdg_result" in results:
            sdg = results["sdg_result"]
            if sdg.get("citations_count", 0) == 0:
                recommendations.append("📚 Add supporting citations to improve verifiability")
        
        if "aie_result" in results:
            aie = results["aie_result"]
            if aie.get("issues_found", 0) > 0:
                recommendations.append(f"🔍 Review and resolve {aie['issues_found']} logical consistency issues found")
        
        if "cce_result" in results:
            cce = results["cce_result"]
            if cce.get("overall_confidence", 0) < 0.5:
                recommendations.append("💬 Strengthen language confidence with more definitive statements and evidence")
        
        if "zfp_result" in results:
            zfp = results["zfp_result"]
            if zfp.get("total_flags", 0) > 0:
                recommendations.append(f"🤖 Investigate {zfp['total_flags']} potential AI-generation or fabrication indicators")
        
        return recommendations
    
    def generate_insights(self, results: Dict[str, Any], trust_score: float) -> List[str]:
        """Generate quick insights (keeping original for backward compatibility)."""
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
        detailed_explanation = self.generate_detailed_explanation(results, trust_score)
        
        return {
            "module": self.name,
            "trust_score": round(trust_score, 3),
            "trust_level": trust_level,
            "component_scores": component_scores,
            "insights": insights,
            "detailed_explanation": detailed_explanation,
            "methodology": "Weighted aggregation of 4 core trust evaluation modules",
            "status": "computed"
        }
