"""
TrustGraphed Score Engine
Aggregates all module results into a final trust score
"""

from typing import Dict, Any
from .cce import compute_confidence_score

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

        # Use new scoring logic
        score_data = compute_confidence_score(signals, assertion_type)

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

        return {
            'trust_score': score_data["final_score"] / 100.0,  # Normalize to 0-1
            'trust_level': trust_level_mapping.get(score_data["band"], "VERY LOW"),
            'trust_band': score_data["band"],
            'component_scores': component_scores,
            'insights': insights,
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
            "original": "Content declared as fully original - standard trust evaluation applied",
            "ai": "🔍 TRANSPARENCY BONUS: Honest AI declaration increases trust score (+15%)",
            "copied": "🔍 TRANSPARENCY BONUS: Honest copied content declaration increases trust (+10%)",
            "mixed": "🔍 TRANSPARENCY BONUS: Honest mixed sources declaration increases trust (+12%)",
            "unsure": "⚠️ Content source undeclared - transparency would improve trust score"
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

        # Fabrication insights
        zfp_score = module_results.get('zfp_result', {}).get('authenticity_score', 1.0)
        flags = module_results.get('zfp_result', {}).get('total_flags', 0)
        if flags > 0:
            insights.append(f"Detected {flags} potential fabrication indicators")
        if zfp_score < 0.5:
            insights.append("Content shows signs of potential AI generation or fabrication")

        # Overall score insight
        final_score = score_data["final_score"]
        if final_score < 25:
            insights.append("Overall trust score is very low - recommend additional verification")
        elif final_score < 50:
            insights.append("Overall trust score is low - recommend additional verification")
        elif final_score >= 75:
            insights.append("High trust score - content appears credible")

        return insights

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