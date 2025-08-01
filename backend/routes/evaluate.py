
"""
TrustGraphed Evaluation Routes
"""

from flask import Blueprint, request, jsonify
from ..utils.sdg import SourceDataGrappler
from ..utils.aie import AssertionIntegrityEngine
from ..utils.cce import ConfidenceComputationEngine
from ..utils.zfp import ZeroFabricationProtocol
from ..utils.score_engine import TrustScoreEngine
from ..utils.certificate import CertificateGenerator

evaluate_bp = Blueprint('evaluate', __name__)

@evaluate_bp.route('/evaluate', methods=['POST'])
def evaluate_content():
    """
    Main evaluation endpoint - processes content through all 6 TrustGraphed modules.
    """
    try:
        # Get content from request
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({"error": "Missing 'content' field in request body"}), 400
        
        content = data['content']
        if not content or len(content.strip()) < 10:
            return jsonify({"error": "Content must be at least 10 characters long"}), 400
        
        # Initialize all modules
        sdg = SourceDataGrappler()
        aie = AssertionIntegrityEngine()
        cce = ConfidenceComputationEngine()
        zfp = ZeroFabricationProtocol()
        score_engine = TrustScoreEngine()
        certificate_gen = CertificateGenerator()
        
        # Process through pipeline
        results = {}
        
        # Step 1: Extract assertions and citations
        sdg_result = sdg.process(content)
        results['sdg_result'] = sdg_result
        
        # Step 2: Check assertion integrity
        assertions = sdg_result.get('assertions', [])
        aie_result = aie.process(content, assertions)
        results['aie_result'] = aie_result
        
        # Step 3: Compute confidence scores
        citations = sdg_result.get('citations', [])
        cce_result = cce.process(content, assertions, citations)
        results['cce_result'] = cce_result
        
        # Step 4: Check for fabrication
        zfp_result = zfp.process(content)
        results['zfp_result'] = zfp_result
        
        # Step 5: Generate final trust score
        score_result = score_engine.process(results)
        results['score_result'] = score_result
        
        # Step 6: Generate certificate
        cert_result = certificate_gen.process(content, score_result)
        results['certificate_result'] = cert_result
        
        # Build response
        response = {
            "status": "success",
            "content_length": len(content),
            "trust_evaluation": {
                "trust_score": score_result['trust_score'],
                "trust_level": score_result['trust_level'],
                "component_scores": score_result['component_scores'],
                "insights": score_result['insights']
            },
            "certificate_id": cert_result['certificate_id'],
            "module_results": {
                "source_data_grappler": {
                    "assertions_found": sdg_result['assertions_count'],
                    "citations_found": sdg_result['citations_count'],
                    "extraction_confidence": sdg_result['extraction_confidence']
                },
                "assertion_integrity": {
                    "integrity_score": aie_result['integrity_score'],
                    "issues_found": aie_result['issues_found']
                },
                "confidence_computation": {
                    "overall_confidence": cce_result['overall_confidence'],
                    "high_confidence_assertions": cce_result['high_confidence_count']
                },
                "zero_fabrication": {
                    "authenticity_score": zfp_result['authenticity_score'],
                    "fabrication_risk": zfp_result['fabrication_risk'],
                    "flags_detected": zfp_result['total_flags']
                }
            },
            "certificate": cert_result['certificate'],
            "readable_summary": cert_result['readable_summary']
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Evaluation failed: {str(e)}"
        }), 500

@evaluate_bp.route('/evaluate/health', methods=['GET'])
def evaluate_health():
    """Health check for evaluation service."""
    return jsonify({
        "status": "healthy",
        "service": "TrustGraphed Evaluation Pipeline",
        "modules": [
            "Source Data Grappler",
            "Assertion Integrity Engine", 
            "Confidence Computation Engine",
            "Zero-Fabrication Protocol",
            "TrustScore Engine",
            "Certificate Generator"
        ]
    })
