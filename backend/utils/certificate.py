
"""
Certificate Generator
Generates a JSON or PDF trust certificate.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any

class CertificateGenerator:
    def __init__(self):
        self.name = "Certificate Generator"
        self.version = "1.0.0"
        self.issuer = "TrustGraphed Evaluation System"
    
    def generate_certificate_id(self) -> str:
        """Generate a unique certificate ID."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"TG-{timestamp}"
    
    def create_json_certificate(self, content: str, evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a JSON trust certificate."""
        certificate_id = self.generate_certificate_id()
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Extract key metrics
        trust_score = evaluation_results.get('trust_score', 0.0)
        trust_level = evaluation_results.get('trust_level', 'UNKNOWN')
        component_scores = evaluation_results.get('component_scores', {})
        insights = evaluation_results.get('insights', [])
        
        certificate = {
            "certificate_info": {
                "id": certificate_id,
                "issued_at": timestamp,
                "issuer": self.issuer,
                "version": self.version,
                "type": "Trust Evaluation Certificate"
            },
            "content_info": {
                "content_length": len(content),
                "content_hash": str(hash(content)),  # Simple hash for demo
                "evaluation_timestamp": timestamp
            },
            "trust_evaluation": {
                "overall_trust_score": trust_score,
                "trust_level": trust_level,
                "component_scores": component_scores,
                "insights": insights
            },
            "module_details": {
                "modules_used": [
                    "Source Data Grappler (SDG)",
                    "Assertion Integrity Engine (AIE)",
                    "Confidence Computation Engine (CCE)",
                    "Zero-Fabrication Protocol (ZFP)",
                    "TrustScore Engine"
                ],
                "evaluation_methodology": "Multi-dimensional trust analysis using linguistic patterns, citation analysis, integrity checks, and fabrication detection."
            },
            "validity": {
                "valid_from": timestamp,
                "expires_at": None,  # Certificates don't expire in this demo
                "signature": f"TG_SIG_{certificate_id}"  # Mock signature
            }
        }
        
        return certificate
    
    def format_readable_summary(self, certificate: Dict[str, Any]) -> str:
        """Create a human-readable summary of the certificate."""
        trust_score = certificate["trust_evaluation"]["overall_trust_score"]
        trust_level = certificate["trust_evaluation"]["trust_level"]
        cert_id = certificate["certificate_info"]["id"]
        
        summary = f"""
TrustGraphed Evaluation Certificate
==================================
Certificate ID: {cert_id}
Trust Score: {trust_score}/1.0 ({trust_level})
Issued: {certificate["certificate_info"]["issued_at"]}

Key Findings:
"""
        
        for insight in certificate["trust_evaluation"]["insights"][:3]:  # Top 3 insights
            summary += f"• {insight}\n"
        
        summary += f"\nComponent Scores:\n"
        for component, score in certificate["trust_evaluation"]["component_scores"].items():
            summary += f"• {component.title()}: {score}/1.0\n"
        
        return summary.strip()
    
    def process(self, content: str, evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing function."""
        json_certificate = self.create_json_certificate(content, evaluation_results)
        readable_summary = self.format_readable_summary(json_certificate)
        
        return {
            "module": self.name,
            "certificate": json_certificate,
            "readable_summary": readable_summary,
            "certificate_id": json_certificate["certificate_info"]["id"],
            "status": "generated"
        }
