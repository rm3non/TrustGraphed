"""
TrustGraphed Score Engine
Aggregates all module results into a final trust score
"""

from typing import Dict, Any
from .cce import compute_trust_score

class TrustScoreEngine:
    def __init__(self):
        self.weights = {
            'data_extraction': 0.20,      # SDG quality
            'assertion_integrity': 0.25,  # AIE results
            'confidence_analysis': 0.30,  # CCE results
            'fabrication_detection': 0.25 # ZFP results
        }

    def process(self, module_results: Dict[str, Any], assertion_type: str = "unsure") -> Dict[str, Any]:
        """
        Process all module results and generate final trust score.
        """
        # Extract signals from module results
        signals = self._extract_signals(module_results)

        # Use consolidated scoring logic from CCE
        from .cce import compute_trust_score
        score_data = compute_trust_score(signals, assertion_type)

        # Build component scores for transparency
        component_scores = self._build_component_scores(module_results)

        # Generate insights
        insights = self._generate_insights(module_results, score_data, assertion_type)

        # Map band to trust level
        trust_level_mapping = {
            "High Trust": "HIGH",
            "Verified": "MEDIUM",
            "Low Trust": "LOW", 
            "Unverified": "VERY LOW"
        }

        # Generate disclaimer
        disclaimer = self._generate_disclaimer(module_results, score_data, assertion_type)

        return {
            'trust_score': score_data["final_score"] / 100.0,  # Normalize to 0-1
            'trust_level': trust_level_mapping.get(score_data["band"], "VERY LOW"),
            'trust_band': score_data["band"],
            'component_scores': component_scores,
            'insights': insights,
            'disclaimer': disclaimer,
            'signal_breakdown': score_data["breakdown"],
            'assertion_type': assertion_type,
            'detailed_explanation': {
                'scoring_method': 'Protocol-aligned with assertion type weighting',
                'base_signals': signals,
                'final_breakdown': score_data["breakdown"]
            }
        }

    def _extract_signals(self, module_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract scoring signals from all module results."""
        signals = {
            'assertions': 0,
            'citations': 0,
            'contradictions': 0,
            'author_detected': False,
            'ai_likelihood': 0.0
        }

        # Extract from SDG results
        if 'sdg_result' in module_results:
            sdg = module_results['sdg_result']
            signals['assertions'] = sdg.get('assertions_count', 0)
            signals['citations'] = sdg.get('citations_count', 0)
            signals['author_detected'] = sdg.get('author_detected', False)

        # Extract from AIE results
        if 'aie_result' in module_results:
            aie = module_results['aie_result']
            signals['contradictions'] = aie.get('issues_found', 0)

        # Extract from ZFP results
        if 'zfp_result' in module_results:
            zfp = module_results['zfp_result']
            # Convert authenticity score to AI likelihood (inverse relationship)
            authenticity = zfp.get('authenticity_score', 1.0)
            signals['ai_likelihood'] = max(0.0, 1.0 - authenticity)

        return signals

    def _build_component_scores(self, module_results: Dict[str, Any]) -> Dict[str, float]:
        """Build component scores for display."""
        component_scores = {}

        # Data Extraction (SDG)
        if 'sdg_result' in module_results:
            sdg = module_results['sdg_result']
            component_scores['Data Extraction'] = sdg.get('extraction_confidence', 0.5)

        # Assertion Integrity (AIE)
        if 'aie_result' in module_results:
            aie = module_results['aie_result']
            component_scores['Assertion Integrity'] = aie.get('integrity_score', 0.5)

        # Confidence Analysis (CCE)
        if 'cce_result' in module_results:
            cce = module_results['cce_result']
            component_scores['Confidence Analysis'] = cce.get('overall_confidence', 0.5)

        # Fabrication Detection (ZFP)
        if 'zfp_result' in module_results:
            zfp = module_results['zfp_result']
            component_scores['Fabrication Detection'] = zfp.get('authenticity_score', 0.5)

        return component_scores

    def _generate_insights(self, module_results: Dict[str, Any], score_data: Dict[str, Any], assertion_type: str) -> list:
        """Generate human-readable insights."""
        insights = []

        # Assertion type insight
        assertion_insights = {
            "original": "Content declared as fully original - evaluating claim consistency",
            "ai": "✅ TRANSPARENCY: AI usage openly declared - builds reader trust through honesty",
            "copied": "✅ TRANSPARENCY: Copied content openly declared - builds reader trust through honesty",
            "mixed": "✅ TRANSPARENCY: Mixed sources openly declared - builds reader trust through honesty",
            "unsure": "⚠️ Content source undeclared - readers cannot assess information origin"
        }
        insights.append(assertion_insights.get(assertion_type, "Unknown content declaration"))

        # Citation insights
        citations = module_results.get('sdg_result', {}).get('citations_count', 0)
        if citations == 0:
            insights.append("No citations found - claims may lack supporting evidence")
        elif citations < 3:
            insights.append("Limited citations - additional sources would strengthen credibility")
        else:
            insights.append("Well-cited content with multiple sources")

        # Confidence insights
        confidence = module_results.get('cce_result', {}).get('overall_confidence', 0.5)
        if confidence < 0.4:
            insights.append("Low confidence language detected - claims may be speculative")
        elif confidence > 0.7:
            insights.append("High confidence language - assertions appear well-supported")

        # AI Detection vs Declaration Alignment
        ai_likelihood = module_results.get('zfp_result', {}).get('authenticity_score', 1.0)
        ai_likelihood = 1.0 - ai_likelihood  # Convert to AI likelihood
        
        if assertion_type.lower() == "original" and ai_likelihood > 0.6:
            insights.append("⚠️ TRANSPARENCY MISMATCH: High AI characteristics detected but claimed as original")
        elif assertion_type.lower() in ["ai", "mixed"] and ai_likelihood > 0.4:
            insights.append("✅ DECLARATION ALIGNED: AI characteristics match transparent declaration")
        elif assertion_type.lower() in ["ai", "mixed"] and ai_likelihood < 0.3:
            insights.append("ℹ️ OVER-DISCLOSURE: Minimal AI characteristics detected despite AI declaration")
        
        # Fabrication insights
        flags = module_results.get('zfp_result', {}).get('total_flags', 0)
        if flags > 0:
            insights.append(f"Detected {flags} potential content reliability indicators to review")

        # Overall score insight
        final_score = score_data["final_score"]
        if final_score < 25:
            insights.append("Overall trust score is very low - recommend additional verification")
        elif final_score < 50:
            insights.append("Overall trust score is low - recommend additional verification")
        elif final_score >= 75:
            insights.append("High trust score - content appears credible")

        return insights

    def _generate_disclaimer(self, module_results: Dict[str, Any], score_data: Dict[str, Any], assertion_type: str) -> str:
        """Generate disclaimer statement explaining the score calculation."""
        final_score = score_data["final_score"]
        citations = module_results.get('sdg_result', {}).get('citations_count', 0)
        ai_likelihood = module_results.get('zfp_result', {}).get('authenticity_score', 1.0)
        ai_likelihood = 1.0 - ai_likelihood
        transparency_multiplier = score_data["breakdown"].get("transparency_multiplier", 1.0)
        
        # Build disclaimer based on key factors
        factors = []
        
        # Citation factor
        if citations == 0:
            factors.append("lack of supporting citations")
        elif citations >= 3:
            factors.append("strong citation support")
        else:
            factors.append("limited citation support")
        
        # Transparency factor
        if transparency_multiplier > 1.0:
            factors.append("transparent content declaration")
        elif transparency_multiplier < 1.0:
            factors.append("content source transparency concerns")
        
        # AI alignment factor
        if assertion_type.lower() == "original" and ai_likelihood > 0.6:
            factors.append("potential transparency misalignment")
        elif assertion_type.lower() in ["ai", "mixed"]:
            factors.append("honest AI/mixed content declaration")
        
        # Generate score band explanation
        if final_score >= 75:
            score_explanation = "indicates high trustworthiness"
        elif final_score >= 50:
            score_explanation = "indicates moderate trustworthiness"
        elif final_score >= 25:
            score_explanation = "indicates low trustworthiness"
        else:
            score_explanation = "indicates very low trustworthiness"
        
        # Combine factors
        factor_text = ", ".join(factors)
        
        disclaimer = f"This {final_score:.0f}/100 trust score {score_explanation} based on {factor_text}. " \
                    f"TrustGraphed evaluates content transparency, citation quality, and declaration consistency " \
                    f"to help readers assess information reliability. Scores reflect content characteristics, " \
                    f"not absolute truth claims."
        
        return disclaimer

def evaluate_content(content_text: str, assertion_type: str = "unsure"):
    """
    Full evaluation pipeline for TrustGraphed.
    """
    # This would integrate with your existing pipeline
    # For now, return a basic structure
    signals = {
        'assertions': 5,
        'citations': 2,
        'contradictions': 0,
        'author_detected': True,
        'ai_likelihood': 0.3
    }

    score_data = compute_confidence_score(signals, assertion_type)

    return {
        "trust_score": score_data["final_score"],
        "trust_band": score_data["band"],
        "signal_breakdown": score_data["breakdown"],
        "assertion_type": assertion_type
    }